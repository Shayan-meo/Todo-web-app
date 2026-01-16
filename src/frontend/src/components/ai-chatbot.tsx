"use client";

import { useEffect, useRef, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { MessageSquare, X, Send, Trash2, Sparkles, CheckCircle2 } from "lucide-react";
import { toast } from "sonner";
import { chatApi } from "@/lib/api-client";
import { ChatMessage } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export function AIChatbot() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isHistoryLoaded, setIsHistoryLoaded] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const scrollContainerRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    const loadHistory = async () => {
      try {
        const response = await chatApi.getHistory();
        setMessages(response.data);
        setIsHistoryLoaded(true);
      } catch (error) {
        console.error("Failed to load chat history:", error);
        setIsHistoryLoaded(true);
      }
    };

    if (isOpen && !isHistoryLoaded) {
      loadHistory();
    }
  }, [isOpen, isHistoryLoaded]);

  const handleSendMessage = async (message: string) => {
    if (!message.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      id: Date.now(),
      user_id: 0,
      role: "user",
      content: message,
      created_at: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      // 1. Setup optimistic assistant message
      const assistantId = Date.now() + 1;
      const assistantMessage: ChatMessage = {
        id: assistantId,
        user_id: 0,
        role: "assistant",
        content: "", // Content will stream in
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, assistantMessage]);

      // 2. Start Streaming Request
      const token = localStorage.getItem("todo_token");
      const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

      const response = await fetch(`${BASE_URL}/ai/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify({ message }),
      });

      if (!response.ok) throw new Error("Network response was not ok");
      if (!response.body) throw new Error("No response body");

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let accumulatedContent = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split("\n");

        for (const line of lines) {
          if (!line.trim()) continue;
          try {
            const event = JSON.parse(line);

            if (event.type === "token") {
              accumulatedContent += event.content;
              setMessages((prev) =>
                prev.map((msg) =>
                  msg.id === assistantId ? { ...msg, content: accumulatedContent } : msg
                )
              );
            } else if (event.type === "action_result") {
              // Handle database mutations (notifications & refresh)
              const dbMutationActions = ["add_task", "update_task", "delete_task"];

              if (event.action_taken && dbMutationActions.includes(event.action_taken)) {
                const actionMessages: Record<string, string> = {
                  add_task: "Task Added",
                  update_task: "Task Updated",
                  delete_task: "Task Deleted",
                };

                toast.success(actionMessages[event.action_taken] || "Action Completed", {
                  duration: 2000,
                });

                if (typeof window !== "undefined") {
                  window.dispatchEvent(
                    new CustomEvent("tasksUpdated", {
                      detail: { action: event.action_taken },
                    })
                  );
                }
              }
            } else if (event.type === "error") {
               console.error("Stream Error:", event.content);
               toast.error("Error from AI: " + event.content);
            }
          } catch (e) {
            console.warn("Failed to parse stream chunk:", line);
          }
        }
      }
    } catch (error: any) {
      console.error("Failed to send message:", error);
      toast.error("Oops! Something went wrong");

      // Update the empty message to show error
      setMessages((prev) =>
        prev.map((msg, i) =>
          i === prev.length - 1 && msg.role === "assistant" && !msg.content
            ? { ...msg, content: "Sorry, connection failed. Please try again." }
            : msg
        )
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleQuickAction = (action: string) => {
    handleSendMessage(action);
  };

  const handleClearHistory = async () => {
    try {
      await chatApi.clearHistory();
      setMessages([]);
      toast.success("Chat history cleared!");
    } catch (error) {
      console.error("Failed to clear history:", error);
      toast.error("Failed to clear history");
    }
  };

  const quickActions = [
    "Show today's tasks",
    "Mere kitne tasks baaki hain?",
    "Meeting add karo sham 5 baje",
    "Add task: Complete report",
  ];

  return (
    <>
      {/* Chat Button */}
      <motion.button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-6 z-50 group"
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.95 }}
        animate={{
          boxShadow: [
            "0 0 0 0 rgba(99, 102, 241, 0)",
            "0 0 0 10px rgba(99, 102, 241, 0.4)",
            "0 0 0 20px rgba(99, 102, 241, 0)"
          ]
        }}
        transition={{
          boxShadow: {
            duration: 2,
            repeat: Infinity,
            repeatType: "loop"
          }
        }}
        aria-label="Open AI Chat"
      >
        <div className="relative flex h-14 w-14 items-center justify-center rounded-full bg-gradient-to-br from-indigo-500 to-violet-500 text-white shadow-xl shadow-indigo-500/50 backdrop-blur-md border border-white/20">
          <Sparkles className="h-6 w-6" />
        </div>
      </motion.button>

      {/* Chat Sidebar */}
      <AnimatePresence>
        {isOpen && (
          <>
            {/* Backdrop */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setIsOpen(false)}
              className="fixed inset-0 z-50 bg-black/20 backdrop-blur-sm"
            />

            {/* Sidebar */}
            <motion.div
              initial={{ x: "-100%" }}
              animate={{ x: 0 }}
              exit={{ x: "-100%" }}
              transition={{ type: "spring", damping: 25, stiffness: 300 }}
              className="fixed left-0 top-0 bottom-0 z-[51] w-full max-w-md"
            >
              <div className="flex h-full">
                <div className="flex-1 glass-strong border-r border-white/10 flex flex-col">
                  {/* Header */}
                  <div className="flex items-center justify-between p-4 border-b border-white/10">
                    <div className="flex items-center gap-2">
                      <MessageSquare className="h-5 w-5 text-indigo-500" />
                      <h2 className="text-lg font-semibold text-foreground">AI Assistant</h2>
                    </div>
                    <div className="flex gap-2">
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={handleClearHistory}
                        className="h-8 w-8 text-muted-foreground hover:text-destructive"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => setIsOpen(false)}
                        className="h-8 w-8"
                      >
                        <X className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>

                  {/* Messages */}
                  <div
                    ref={scrollContainerRef}
                    className="flex-1 overflow-y-auto p-4 scrollbar-thin"
                  >
                    <div className="space-y-4">
                      {messages.length === 0 ? (
                        <motion.div
                          initial={{ opacity: 0, scale: 0.95 }}
                          animate={{ opacity: 1, scale: 1 }}
                          className="text-center py-12"
                        >
                          <Sparkles className="h-12 w-12 mx-auto text-muted-foreground/50 mb-4" />
                          <h3 className="text-lg font-medium text-foreground mb-2">
                            Welcome to AI Assistant
                          </h3>
                          <p className="text-sm text-muted-foreground mb-6">
                            Ask me anything about your tasks. I understand English and Roman Urdu!
                          </p>
                          <div className="space-y-2 text-left max-w-xs mx-auto">
                            <p className="text-xs text-muted-foreground">Try saying:</p>
                            {quickActions.slice(0, 3).map((action) => (
                              <button
                                key={action}
                                onClick={() => handleQuickAction(action)}
                                className="w-full text-left px-3 py-2 text-sm text-muted-foreground hover:text-foreground hover:bg-accent rounded-md transition-colors"
                              >
                                &ldquo;{action}&rdquo;
                              </button>
                            ))}
                          </div>
                        </motion.div>
                      ) : (
                        <AnimatePresence mode="popLayout">
                          {messages.map((message) => (
                            <motion.div
                              key={message.id}
                              initial={{ opacity: 0, y: 10 }}
                              animate={{ opacity: 1, y: 0 }}
                              exit={{ opacity: 0, scale: 0.95 }}
                              layout
                              className={`flex ${
                                message.role === "user" ? "justify-end" : "justify-start"
                              }`}
                            >
                              <div
                                className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                                  message.role === "user"
                                    ? "bg-gradient-to-br from-indigo-500 to-violet-500 text-white shadow-lg shadow-indigo-500/20"
                                    : "bg-card/80 backdrop-blur-xl border border-white/20 text-foreground shadow-lg shadow-black/5"
                                }`}
                              >
                                <p className="text-sm whitespace-pre-wrap break-words">
                                  {message.content}
                                </p>
                              </div>
                            </motion.div>
                          ))}
                          {isLoading && (
                            <motion.div
                              initial={{ opacity: 0, y: 10 }}
                              animate={{ opacity: 1, y: 0 }}
                              className="flex justify-start"
                            >
                              <div className="bg-card/80 backdrop-blur-xl border border-white/20 rounded-2xl px-4 py-3 shadow-lg shadow-black/5">
                                <div className="flex items-center gap-2">
                                  <div className="flex gap-1">
                                    <div className="w-2 h-2 bg-muted-foreground/50 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                                    <div className="w-2 h-2 bg-muted-foreground/50 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                                    <div className="w-2 h-2 bg-muted-foreground/50 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
                                  </div>
                                  <span className="text-xs text-muted-foreground">AI is thinking...</span>
                                </div>
                              </div>
                            </motion.div>
                          )}
                        </AnimatePresence>
                      )}
                      <div ref={messagesEndRef} />
                    </div>
                  </div>

                  {messages.length > 0 && (
                    <div className="p-4 border-t border-white/10">
                      <p className="text-xs text-muted-foreground mb-2">Quick actions:</p>
                      <div className="flex flex-wrap gap-2">
                        {quickActions.slice(0, 3).map((action) => (
                          <button
                            key={action}
                            onClick={() => handleQuickAction(action)}
                            className="px-3 py-1.5 text-xs font-medium bg-secondary/50 hover:bg-secondary text-secondary-foreground rounded-full transition-colors"
                          >
                            {action}
                          </button>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Input */}
                  <div className="p-4 border-t border-white/10">
                    <form
                      onSubmit={(e) => {
                        e.preventDefault();
                        handleSendMessage(input);
                      }}
                      className="flex gap-2"
                    >
                      <Input
                        type="text"
                        placeholder="Type a message..."
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        disabled={isLoading}
                        className="flex-1"
                      />
                      <Button
                        type="submit"
                        disabled={isLoading || !input.trim()}
                        size="icon"
                        className="h-10 w-10 bg-gradient-to-br from-indigo-500 to-violet-500 hover:opacity-90"
                      >
                        {isLoading ? (
                          <div className="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
                        ) : (
                          <Send className="h-4 w-4" />
                        )}
                      </Button>
                    </form>
                  </div>
                </div>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </>
  );
}