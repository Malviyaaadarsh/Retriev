import { useState } from "react";
import { toast } from "sonner";
import { useWorkspace } from "../../context/WorkspaceContext";
import { useSettings } from "../../context/SettingsContext";
import { MODEL_OPTIONS } from "../../config/settings";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import {
  Sliders,
  Cpu,
  Layers,
  HardDrive,
  Monitor,
  Check,
  Info,
} from "lucide-react";

export function SettingsDialog() {
  const { isSettingsOpen, setIsSettingsOpen } = useWorkspace();
  const { settings, updateSettings } = useSettings();
  const [formState, setFormState] = useState(settings);
  const [savedSuccess, setSavedSuccess] = useState(false);

  const updateField = (field, value) => {
    setFormState((previous) => ({ ...previous, [field]: value }));
  };

  const handleProviderChange = (provider) => {
    updateField("provider", provider);
    updateField("model", MODEL_OPTIONS[provider][0]);
  };

  const handleSave = () => {
    const model = formState.model.trim();
    const chunkSize = Number(formState.chunkSize);
    const chunkOverlap = Number(formState.chunkOverlap);
    const topK = Number(formState.topK);

    if (!model || (formState.provider === "gemini" && !formState.apiKey?.trim())) {
      toast.error("API Key Required");
      return;
    }
    if (chunkSize <= 0 || chunkOverlap < 0 || topK < 1) {
      toast.error("Enter a valid model, chunk size, overlap, and Top-K value.");
      return;
    }

    updateSettings({
      ...formState,
      model,
      chunkSize,
      chunkOverlap,
      topK,
      temperature: Number(formState.temperature),
    });
    setSavedSuccess(true);
    toast.success("Settings Saved");
    setTimeout(() => {
      setSavedSuccess(false);
      setIsSettingsOpen(false);
    }, 800);
  };

  const handleOpenChange = (open) => {
    if (open) {
      setFormState(settings);
      setSavedSuccess(false);
    }
    setIsSettingsOpen(open);
  };

  return (
    <Dialog open={isSettingsOpen} onOpenChange={handleOpenChange}>
      <DialogContent className="sm:max-w-xl p-0 overflow-hidden rounded-2xl border-border bg-card">
        <DialogHeader className="p-4 sm:p-5 border-b border-border/80 bg-muted/30">
          <div className="flex items-center gap-2.5">
            <div className="flex size-8 items-center justify-center rounded-lg bg-primary/10 text-primary">
              <Sliders className="size-4" />
            </div>
            <div>
              <DialogTitle className="text-base font-semibold text-foreground">Retriev Settings</DialogTitle>
              <DialogDescription className="text-xs text-muted-foreground">
                Configure providers, retrieval behavior, and appearance.
              </DialogDescription>
            </div>
          </div>
        </DialogHeader>

        <div className="p-4 sm:p-5">
          <Tabs defaultValue="provider" className="w-full">
            <TabsList className="grid w-full grid-cols-4 mb-4 bg-muted/60 p-1">
              <TabsTrigger value="provider" className="text-xs gap-1">
                <Cpu className="size-3.5" /><span>LLM</span>
              </TabsTrigger>
              <TabsTrigger value="retrieval" className="text-xs gap-1">
                <Layers className="size-3.5" /><span>Retrieval</span>
              </TabsTrigger>
              <TabsTrigger value="appearance" className="text-xs gap-1">
                <Monitor className="size-3.5" /><span>Appearance</span>
              </TabsTrigger>
            </TabsList>

            <TabsContent value="provider" className="space-y-4 pt-1">
              <div>
                <label className="text-xs font-semibold text-foreground block mb-1.5">LLM Provider</label>
                <div className="grid grid-cols-2 gap-2">
                  {[
                    { id: "gemini", name: "Gemini", badge: "Cloud" },
                    { id: "ollama", name: "Ollama", badge: "Local" },
                  ].map((provider) => (
                    <button
                      key={provider.id}
                      type="button"
                      onClick={() => handleProviderChange(provider.id)}
                      className={`rounded-xl border p-2.5 text-xs transition-all ${
                        formState.provider === provider.id
                          ? "border-primary bg-primary/5 text-foreground font-medium"
                          : "border-border/80 bg-muted/20 text-muted-foreground hover:bg-muted/50"
                      }`}
                    >
                      <span className="block">{provider.name}</span>
                      <span className="text-[10px] text-muted-foreground">{provider.badge}</span>
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="text-xs font-semibold text-foreground block mb-1.5">Model</label>
                <select
                  value={MODEL_OPTIONS[formState.provider].includes(formState.model) ? formState.model : ""}
                  onChange={(event) => updateField("model", event.target.value)}
                  className="w-full h-9 rounded-md border border-input bg-background px-3 text-xs"
                >
                  <option value="">Custom model</option>
                  {MODEL_OPTIONS[formState.provider].map((model) => <option key={model}>{model}</option>)}
                </select>
                <Input
                  value={formState.model}
                  onChange={(event) => updateField("model", event.target.value)}
                  placeholder="Enter a custom model name"
                  className="text-xs h-9 mt-2"
                />
                {formState.provider === "gemini" && (
                  <Input
                    type="password"
                    value={formState.apiKey || ""}
                    onChange={(event) => updateField("apiKey", event.target.value)}
                    placeholder="Gemini API key (AIza...)"
                    className="text-xs h-9 mt-2 font-mono"
                  />
                )}
              </div>

              <div>
                <div className="flex justify-between items-center mb-1">
                  <label className="text-xs font-semibold text-foreground">Temperature ({formState.temperature})</label>
                  <span className="text-[10px] text-muted-foreground">0.0 - 1.0</span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.05"
                  value={formState.temperature}
                  onChange={(event) => updateField("temperature", Number(event.target.value))}
                  className="w-full accent-primary"
                />
              </div>
            </TabsContent>

            <TabsContent value="retrieval" className="space-y-4 pt-1">
              <div>
                <label className="text-xs font-semibold text-foreground block mb-1">Embedding Model</label>
                <Input value={formState.embeddingModel} readOnly className="text-xs h-9 font-mono" />
                <div className="flex flex-wrap gap-2 mt-2">
                  <Badge variant="outline" className="text-[10px]">Sentence Transformers</Badge>
                  <Badge variant="outline" className="text-[10px]">384 dimensions</Badge>
                  <Badge variant="outline" className="text-[10px]">Runs locally</Badge>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <Field label="Chunk Size" value={formState.chunkSize} onChange={(value) => updateField("chunkSize", value)} />
                <Field label="Chunk Overlap" value={formState.chunkOverlap} onChange={(value) => updateField("chunkOverlap", value)} />
              </div>
              <div>
                <div className="flex justify-between mb-1">
                  <label className="text-xs font-semibold text-foreground">Top-K ({formState.topK})</label>
                  <span className="text-[10px] text-muted-foreground">1 - 20</span>
                </div>
                <input type="range" min="1" max="20" step="1" value={formState.topK} onChange={(event) => updateField("topK", Number(event.target.value))} className="w-full accent-primary" />
              </div>
              <p className="text-[11px] text-muted-foreground flex items-center gap-1.5">
                <Info className="size-3.5" /> Changes take effect during future indexing operations.
              </p>
            </TabsContent>
            <TabsContent value="appearance" className="space-y-4 pt-1">
              <label className="text-xs font-semibold text-foreground block">Theme</label>
              <div className="grid grid-cols-2 gap-2">
                {["dark", "light"].map((theme) => (
                  <button key={theme} type="button" onClick={() => updateField("theme", theme)} className={`rounded-xl border p-3 text-xs capitalize ${formState.theme === theme ? "border-primary bg-primary/5 font-medium" : "border-border/80"}`}>
                    {theme}
                  </button>
                ))}
              </div>
            </TabsContent>
          </Tabs>
        </div>

        <DialogFooter className="p-4 sm:p-5 border-t border-border/80 bg-muted/20 flex items-center justify-between">
          <div className="text-xs text-emerald-500">
            {savedSuccess && <span className="flex items-center gap-1.5"><Check className="size-3.5" /> Settings saved</span>}
          </div>
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={() => setIsSettingsOpen(false)} className="text-xs">Cancel</Button>
            <Button size="sm" onClick={handleSave} className="text-xs">Save Changes</Button>
          </div>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

function Field({ label, value, onChange }) {
  return (
    <div>
      <label className="text-xs font-semibold text-foreground block mb-1">{label}</label>
      <Input type="number" min="0" value={value} onChange={(event) => onChange(Number(event.target.value))} className="text-xs h-9" />
    </div>
  );
}

function InfoRow({ label, value }) {
  return (
    <div className="flex items-center justify-between rounded-lg border border-border/70 bg-muted/20 px-3 py-2.5 text-xs">
      <span className="text-muted-foreground">{label}</span>
      <span className="font-medium text-foreground">{value}</span>
    </div>
  );
}
