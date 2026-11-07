import { useState, useRef, useEffect } from "react";
import { useWorkspace } from "../../context/WorkspaceContext";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import {
  Send,
  Paperclip,
  User,
  Copy,
  Check,
  BookOpen,
  FolderKanban,
  ExternalLink,
  Loader2,
} from "lucide-react";

export function ChatView() {
  const {
    activeWorkspace,
    activeDocuments,
    activeConversation,
    sendMessage,
    suggestedPrompts,
    setPreviewDocument,
    settings,
    setActiveView,
    isChatLoading,
  } = useWorkspace();

  const [inputPrompt, setInputPrompt] = useState("");
  const [copiedId, setCopiedId] = useState(null);
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [activeConversation?.messages]);

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleSend = () => {
    if (!inputPrompt.trim()) return;
    void sendMessage(inputPrompt);
    setInputPrompt("");
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  };

  const handleCopy = (content, id) => {
    navigator.clipboard.writeText(content);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const handleOpenCitationDoc = (citation) => {
    const matchedDoc = activeDocuments.find((d) => d.fileName === citation.fileName);
    if (matchedDoc) {
      setPreviewDocument({
        ...matchedDoc,
        excerpt: citation.excerpt,
        page: citation.page,
        chunkId: citation.chunkId,
        isIndexed: true,
      });
    } else {
      setPreviewDocument({
        fileName: citation.fileName,
        title: citation.fileName,
        fileType: citation.fileName.split(".").pop() || "text",
        status: "Indexed",
        isIndexed: true,
        page: citation.page,
        chunkId: citation.chunkId,
        excerpt: citation.excerpt,
      });
    }
  };

  const messages = activeConversation?.messages || [];
  const hasMessages = messages.length > 0;

  return (
    <div className="relative flex h-[calc(100vh-3.5rem)] flex-col justify-between overflow-hidden bg-background">
      {/* Messages area or Empty State */}
      <div className="flex-1 overflow-y-auto">
        {!hasMessages ? (
          /* Empty Chat Welcome State */
          <div className="mx-auto flex h-full max-w-2xl flex-col items-center justify-center px-4 py-8 text-center animate-in fade-in-50 duration-300">
            <h1 className="text-2xl sm:text-3xl font-semibold tracking-tight text-foreground">
              Hi, what do you wanna explore today? Let's dig in!
            </h1>

            {/* Workspace Context Tag */}
            <div className="mt-4 flex flex-wrap items-center justify-center gap-2">
              <Badge variant="secondary" className="gap-1.5 px-2.5 py-1 text-xs">
                <FolderKanban className="size-3 text-primary" />
                <span>Workspace: {activeWorkspace?.name}</span>
              </Badge>
            </div>
            <div className="mt-6 grid w-full gap-2 sm:grid-cols-2">
              {suggestedPrompts.slice(0, 4).map((prompt) => (
                <button
                  key={prompt}
                  type="button"
                  onClick={() => {
                    setInputPrompt(prompt);
                    void sendMessage(prompt);
                  }}
                  disabled={isChatLoading || !activeWorkspace}
                  className="rounded-xl border border-border/70 bg-card px-3 py-2 text-left text-xs text-muted-foreground transition-colors hover:border-primary/50 hover:text-foreground disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {prompt}
                </button>
              ))}
            </div>
          </div>
        ) : (
          /* Conversation Message Stream */
          <div className="mx-auto max-w-3xl px-4 py-6 space-y-6">
            {/* Thread Header Banner */}
            <div className="flex items-center justify-between border-b border-border/60 pb-3 text-xs text-muted-foreground">
              <div className="flex items-center gap-2">
                <span className="font-semibold text-foreground text-sm">
                  {activeConversation?.title || "Conversation"}
                </span>
                <span className="text-muted-foreground">•</span>
                <span>{messages.length} messages</span>
              </div>
              <Badge variant="outline" className="text-[10px] px-2 py-0.5">
                Workspace: {activeWorkspace?.name}
              </Badge>
            </div>

            {/* Messages */}
            {messages.map((msg) => {
              const isUser = msg.role === "user";
              return (
                <div
                  key={msg.id}
                  className={`flex gap-3 sm:gap-4 ${
                    isUser ? "justify-end" : "justify-start"
                  } animate-in fade-in-50 duration-200`}
                >
                  <div
                    className={`group relative max-w-[85%] sm:max-w-[78%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                      isUser
                        ? "bg-primary text-primary-foreground shadow-xs"
                        : "bg-card border border-border/70 text-card-foreground shadow-xs"
                    }`}
                  >
                    {/* Role header & Timestamp */}
                    <div className="flex items-center justify-between gap-4 mb-1 text-[11px] opacity-75">
                      <span className="font-medium">
                        {isUser ? "You" : "Retriev"}
                      </span>
                      <span>{msg.timestamp}</span>
                    </div>

                    {/* Content */}
                    <div className={`prose prose-sm max-w-none ${isUser ? "text-primary-foreground" : "text-foreground"}`}>
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>
                        {msg.content}
                      </ReactMarkdown>
                    </div>

                    {/* Citations Box (for assistant responses) */}
                    {msg.citations && msg.citations.length > 0 && (
                      <div className="mt-3.5 pt-3 border-t border-border/60">
                        <div className="flex items-center gap-1.5 text-[11px] font-semibold text-muted-foreground mb-2">
                          <BookOpen className="size-3 text-primary" />
                          <span>Retrieved Evidence & Sources</span>
                        </div>
                        <div className="flex flex-wrap gap-2">
                          {msg.citations.map((cit, cIdx) => (
                            <button
                              key={cIdx}
                              onClick={() => handleOpenCitationDoc(cit)}
                              className="group/cit flex items-center gap-1.5 rounded-lg border border-border/80 bg-background/80 px-2.5 py-1 text-[11px] text-foreground transition-colors hover:border-primary/50 hover:bg-muted/80 text-left"
                              title={`Inspect excerpt from ${cit.fileName}`}
                            >
                              <span className="flex size-4 items-center justify-center rounded bg-primary/10 text-[9px] font-bold text-primary">
                                {cit.sourceNumber || cIdx + 1}
                              </span>
                              <span className="font-medium truncate max-w-37.5">
                                {cit.fileName}
                              </span>
                              {cit.page && (
                                <span className="text-muted-foreground text-[10px]">
                                  p. {cit.page}
                                </span>
                              )}
                              <ExternalLink className="size-2.5 text-muted-foreground opacity-60 group-hover/cit:opacity-100" />
                            </button>
                          ))}
                        </div>
                      </div>
                    )}
                    {msg.metadata && (
                      <div className="mt-3 flex flex-wrap gap-2 text-[10px] text-muted-foreground">
                        <span>Retrieved chunks: {msg.metadata.retrievedChunks}</span>
                        <span>•</span>
                        <span>Execution: {Math.round(msg.metadata.executionTimeMs)} ms</span>
                        <span>•</span>
                        <span>Provider: {msg.metadata.provider}</span>
                      </div>
                    )}

                    {/* Copy action on hover */}
                    {!isUser && (
                      <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
                        <Button
                          variant="ghost"
                          size="icon-xs"
                          onClick={() => handleCopy(msg.content, msg.id)}
                          className="size-6 text-muted-foreground hover:text-foreground"
                          title="Copy text"
                        >
                          {copiedId === msg.id ? (
                            <Check className="size-3 text-emerald-500" />
                          ) : (
                            <Copy className="size-3" />
                          )}
                        </Button>
                      </div>
                    )}
                  </div>

                  {isUser && (
                    <div className="flex size-7 shrink-0 items-center justify-center rounded-lg bg-muted text-foreground font-semibold text-xs ring-1 ring-foreground/10 mt-1">
                      <User className="size-3.5" />
                    </div>
                  )}
                </div>
              );
            })}
            {isChatLoading && (
              <div className="flex items-center gap-2 text-xs text-muted-foreground">
                <Loader2 className="size-3.5 animate-spin text-primary" />
                <span>Assistant is thinking...</span>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Composer Section */}
      <div className="relative border-t border-border/80 bg-background/95 p-3 sm:p-4 backdrop-blur-md">
        <div className="mx-auto max-w-3xl">
          <div className="relative rounded-2xl border border-border/80 bg-card shadow-sm transition-all focus-within:border-primary/50 focus-within:ring-2 focus-within:ring-primary/20">
            {/* Upper Toolbar / Status in input */}
            <div className="flex items-center justify-between px-3 pt-2 text-[11px] text-muted-foreground border-b border-border/40 pb-1.5">
              <div className="flex items-center gap-2">
                <span className="flex items-center gap-1 font-medium text-foreground">
                  <FolderKanban className="size-3 text-primary" />
                  {activeWorkspace?.name || "Workspace"}
                </span>
                <span>•</span>
                <span className="text-[10px]">
                  {activeDocuments.length} docs in scope
                </span>
              </div>
              <div className="flex items-center gap-1.5">
                <Badge
                  variant="outline"
                  className="text-[10px] h-4 font-mono px-1.5 text-muted-foreground border-border/60"
                >
                  {settings.provider} : {settings.model}
                </Badge>
              </div>
            </div>

            {/* Textarea */}
            <Textarea
              ref={textareaRef}
              value={inputPrompt}
              onChange={(e) => setInputPrompt(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={`Ask a question grounded in ${activeWorkspace?.name || "this workspace"}...`}
              rows={2}
              className="min-h-14.5 max-h-40 w-full resize-none border-0 bg-transparent px-3 py-2 text-sm shadow-none focus-visible:ring-0 placeholder:text-muted-foreground/70"
              disabled={isChatLoading}
            />

            {/* Bottom Actions Bar */}
            <div className="flex items-center justify-between px-3 pb-2 pt-1">
              <div className="flex items-center gap-1">
                <Button
                  variant="ghost"
                  size="icon-xs"
                  onClick={() => setActiveView("documents")}
                  className="size-7 text-muted-foreground hover:text-foreground"
                  title="Manage workspace documents"
                >
                  <Paperclip className="size-3.5" />
                </Button>
                <span className="text-[10px] text-muted-foreground hidden sm:inline">
                  Enter to send, Shift+Enter for new line
                </span>
              </div>

              <div className="flex items-center gap-2">
                <Button
                  variant="default"
                  size="sm"
                  onClick={handleSend}
                  disabled={!inputPrompt.trim() || isChatLoading || !activeWorkspace}
                  className="h-7 gap-1 px-3 text-xs shadow-xs"
                >
                  {isChatLoading ? <Loader2 className="size-3 animate-spin" /> : <Send className="size-3" />}
                </Button>
              </div>
            </div>
          </div>

          <div className="mt-1.5 text-center text-[10px] text-muted-foreground">
            Retriev answers are grounded in local workspace files. External model calls occur only when a cloud provider is selected.
          </div>
        </div>
      </div>
    </div>
  );
}
