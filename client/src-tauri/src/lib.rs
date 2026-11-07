use std::{
    fs::{self, File, OpenOptions},
    io::{Read, Write},
    net::{TcpListener, TcpStream},
    path::{Path, PathBuf},
    process::{Child, Command, Stdio},
    sync::{
        Arc, Mutex,
        atomic::{AtomicBool, Ordering},
    },
    thread,
    time::{Duration, Instant},
};

use tauri::{AppHandle, Manager, RunEvent, path::BaseDirectory};

const BACKEND_PORT: u16 = 8000;
const READINESS_TIMEOUT: Duration = Duration::from_secs(60);

#[derive(Clone)]
struct StartupRuntime {
    child: Arc<Mutex<Option<Child>>>,
    lock_path: Arc<Mutex<Option<PathBuf>>>,
    shutting_down: Arc<AtomicBool>,
}

fn backend_executable(app: &AppHandle) -> Result<PathBuf, Box<dyn std::error::Error>> {
    if cfg!(debug_assertions) {
        Ok(PathBuf::from(env!("CARGO_MANIFEST_DIR"))
            .join("../../dist/RetrievBackend/RetrievBackend.exe"))
    } else {
        Ok(app
            .path()
            .resolve("RetrievBackend/RetrievBackend.exe", BaseDirectory::Resource)?)
    }
}

fn backend_is_ready() -> bool {
    let address = format!("127.0.0.1:{BACKEND_PORT}");
    let Ok(socket_address) = address.parse() else {
        return false;
    };
    let Ok(mut stream) = TcpStream::connect_timeout(&socket_address, Duration::from_millis(250))
    else {
        return false;
    };

    let request = format!(
        "GET /api/ready HTTP/1.1\r\nHost: 127.0.0.1:{BACKEND_PORT}\r\nConnection: close\r\n\r\n"
    );
    if stream.write_all(request.as_bytes()).is_err() {
        return false;
    }

    let mut response = String::new();
    if stream.read_to_string(&mut response).is_err() {
        return false;
    }
    response.starts_with("HTTP/1.1 200") || response.starts_with("HTTP/1.0 200")
}

fn port_is_available() -> bool {
    TcpListener::bind(("127.0.0.1", BACKEND_PORT)).is_ok()
}

fn append_log(path: &Path, message: &str) -> std::io::Result<()> {
    let mut log = OpenOptions::new().create(true).append(true).open(path)?;
    writeln!(log, "{message}")?;
    log.flush()
}

fn acquire_backend_lock(data_root: &Path) -> Result<PathBuf, Box<dyn std::error::Error>> {
    let lock_path = data_root.join("backend.lock");
    match OpenOptions::new()
        .write(true)
        .create_new(true)
        .open(&lock_path)
    {
        Ok(mut lock) => {
            writeln!(lock, "pid={}", std::process::id())?;
            Ok(lock_path)
        }
        Err(error) if error.kind() == std::io::ErrorKind::AlreadyExists => {
            if backend_is_ready() {
                Err("Retriev is already running with an active backend".into())
            } else {
                fs::remove_file(&lock_path)?;
                let mut lock = OpenOptions::new()
                    .write(true)
                    .create_new(true)
                    .open(&lock_path)?;
                writeln!(lock, "pid={}", std::process::id())?;
                Ok(lock_path)
            }
        }
        Err(error) => Err(error.into()),
    }
}

fn wait_for_backend(
    child: &Arc<Mutex<Option<Child>>>,
    log_path: &Path,
) -> Result<(), Box<dyn std::error::Error>> {
    let started = Instant::now();
    while started.elapsed() < READINESS_TIMEOUT {
        {
            let mut process = child.lock().map_err(|_| "backend process lock poisoned")?;
            if let Some(child) = process.as_mut() {
                if let Some(status) = child.try_wait()? {
                    return Err(format!(
                        "Retriev backend exited before readiness with status {status}. See {}",
                        log_path.display()
                    )
                    .into());
                }
            }
        }

        if backend_is_ready() {
            return Ok(());
        }
        thread::sleep(Duration::from_millis(250));
    }

    Err(format!(
        "Retriev backend did not become ready within {} seconds. See {}",
        READINESS_TIMEOUT.as_secs(),
        log_path.display()
    )
    .into())
}

fn monitor_backend(child: Arc<Mutex<Option<Child>>>, log_path: PathBuf) {
    thread::spawn(move || {
        loop {
            let exited = {
                let mut process = match child.lock() {
                    Ok(process) => process,
                    Err(_) => return,
                };
                let Some(process) = process.as_mut() else {
                    return;
                };
                match process.try_wait() {
                    Ok(Some(status)) => {
                        let _ = append_log(
                            &log_path,
                            &format!("Backend exited unexpectedly with status {status}"),
                        );
                        true
                    }
                    Ok(None) => false,
                    Err(error) => {
                        let _ = append_log(
                            &log_path,
                            &format!("Unable to monitor backend process: {error}"),
                        );
                        true
                    }
                }
            };
            if exited {
                if let Ok(mut process) = child.lock() {
                    process.take();
                }
                return;
            }
            thread::sleep(Duration::from_secs(1));
        }
    });
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    let app = tauri::Builder::default()
        .manage(StartupRuntime {
            child: Arc::new(Mutex::new(None)),
            lock_path: Arc::new(Mutex::new(None)),
            shutting_down: Arc::new(AtomicBool::new(false)),
        })
        .invoke_handler(tauri::generate_handler![])
        .setup(|app| {
            app.handle().plugin(tauri_plugin_dialog::init())?;
            if cfg!(debug_assertions) {
                app.handle().plugin(
                    tauri_plugin_log::Builder::default()
                        .level(log::LevelFilter::Info)
                        .build(),
                )?;
            }

            let data_root = app.path().app_local_data_dir()?;
            fs::create_dir_all(&data_root)?;
            let logs_dir = data_root.join("logs");
            fs::create_dir_all(&logs_dir)?;
            let log_path = logs_dir.join("backend.log");
            append_log(
                &log_path,
                &format!(
                    "Starting backend | data_root={} | port={BACKEND_PORT}",
                    data_root.display()
                ),
            )?;

            let app_handle = app.handle().clone();
            let data_root_for_thread = data_root.clone();
            let log_path_for_thread = log_path.clone();
            let runtime = app.state::<StartupRuntime>().inner().clone();
            thread::spawn(move || {
                if backend_is_ready() {
                    let _ =
                        append_log(&log_path_for_thread, "Using an already-ready local backend");
                    return;
                }
                let lock_path = match acquire_backend_lock(&data_root_for_thread) {
                    Ok(path) => path,
                    Err(error) => {
                        let _ = append_log(
                            &log_path_for_thread,
                            &format!("Backend startup error: {error}"),
                        );
                        return;
                    }
                };
                if runtime.shutting_down.load(Ordering::Acquire) {
                    let _ = fs::remove_file(&lock_path);
                    return;
                }
                if !port_is_available() {
                    let _ = fs::remove_file(&lock_path);
                    let _ = append_log(
                        &log_path_for_thread,
                        &format!("Backend port {BACKEND_PORT} is already in use."),
                    );
                    return;
                }
                let executable = match backend_executable(&app_handle) {
                    Ok(executable) => executable,
                    Err(error) => {
                        let _ = fs::remove_file(&lock_path);
                        let _ = append_log(
                            &log_path_for_thread,
                            &format!("Backend path error: {error}"),
                        );
                        return;
                    }
                };
                if !executable.is_file() {
                    let _ = fs::remove_file(&lock_path);
                    let _ = append_log(
                        &log_path_for_thread,
                        &format!("Backend executable not found: {}", executable.display()),
                    );
                    return;
                }
                let Some(backend_dir) = executable.parent() else {
                    let _ = fs::remove_file(&lock_path);
                    let _ = append_log(
                        &log_path_for_thread,
                        "Could not determine backend directory",
                    );
                    return;
                };
                let mut command = Command::new(&executable);
                command
                    .current_dir(backend_dir)
                    .env("RETRIEV_DATA_ROOT", &data_root_for_thread)
                    .env("RETRIEV_PORT", BACKEND_PORT.to_string());
                let stdout = match File::options()
                    .create(true)
                    .append(true)
                    .open(&log_path_for_thread)
                {
                    Ok(file) => file,
                    Err(error) => {
                        let _ = fs::remove_file(&lock_path);
                        let _ = append_log(
                            &log_path_for_thread,
                            &format!("Backend log error: {error}"),
                        );
                        return;
                    }
                };
                let stderr = match stdout.try_clone() {
                    Ok(file) => file,
                    Err(error) => {
                        let _ = fs::remove_file(&lock_path);
                        let _ = append_log(
                            &log_path_for_thread,
                            &format!("Backend log error: {error}"),
                        );
                        return;
                    }
                };
                command
                    .stdout(Stdio::from(stdout))
                    .stderr(Stdio::from(stderr));
                let child = match command.spawn() {
                    Ok(child) => child,
                    Err(error) => {
                        let _ = fs::remove_file(&lock_path);
                        let _ = append_log(
                            &log_path_for_thread,
                            &format!("Backend spawn error: {error}"),
                        );
                        return;
                    }
                };
                if let Ok(mut process) = runtime.child.lock() {
                    *process = Some(child);
                }
                if let Ok(mut path) = runtime.lock_path.lock() {
                    *path = Some(lock_path.clone());
                }
                if let Err(error) = wait_for_backend(&runtime.child, &log_path_for_thread) {
                    if let Ok(mut process) = runtime.child.lock() {
                        if let Some(mut process) = process.take() {
                            let _ = process.kill();
                            let _ = process.wait();
                        }
                    }
                    let _ = fs::remove_file(&lock_path);
                    let _ = append_log(
                        &log_path_for_thread,
                        &format!("Backend readiness error: {error}"),
                    );
                    return;
                }
                let _ = append_log(&log_path_for_thread, "Backend readiness confirmed");
                monitor_backend(Arc::clone(&runtime.child), log_path_for_thread);
            });

            Ok(())
        })
        .build(tauri::generate_context!())
        .expect("Failed to initialize Retriev");

    app.run(|handle, event| {
        if let RunEvent::Exit = event {
            if let Some(state) = handle.try_state::<StartupRuntime>() {
                state.shutting_down.store(true, Ordering::Release);
                if let Ok(mut process) = state.child.lock() {
                    if let Some(mut child) = process.take() {
                        let _ = child.kill();
                        let _ = child.wait();
                    }
                }
                if let Ok(mut lock_path) = state.lock_path.lock() {
                    if let Some(path) = lock_path.take() {
                        let _ = fs::remove_file(path);
                    }
                }
            }
        }
    });
}
