"use client";

import React, { useEffect, useRef, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { MessageSquare, X, Send, Trash2, Sparkles, Loader2 } from "lucide-react";
import { toast } from "sonner";
import { chatApi } from "@/lib/api-client";
import { ChatMessage } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

// --- TYPESCRIPT INTERFACES (Fixes 'any' errors) ---
interface ChatResponse {
  content: string;
  action_taken?: string | null;
  priority_detected?: string;
}

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
        console.error("Chat history failed:", error);
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

    setMessages((prev: ChatMessage[]) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
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

      if (!response.ok) {
        if (response.status === 400) {
          throw new Error("API Limit reached. Please try tomorrow.");
        }
        throw new Error("Connection failed");
      }

      const data: ChatResponse = await response.json();

      if (data && data.content) {
        const assistantMessage: ChatMessage = {
          id: Date.now() + 1,
          user_id: 0,
          role: "assistant",
          content: data.content,
          created_at: new Date().toISOString(),
        };
        
        setMessages((prev: ChatMessage[]) => [...prev, assistantMessage]);

        // --- ENHANCED ACTION HANDLING ---
        const mutationActions = ["add_task", "update_task", "delete_task"];
        if (data.action_taken && mutationActions.includes(data.action_taken)) {
          
          // Toast with Priority Insight
          const toastMsg = data.priority_detected 
            ? `Task added with ${data.priority_detected} priority!` 
            : "Action Completed Successfully";

          toast.success(toastMsg, {
            icon: <Sparkles className="h-4 w-4 text-indigo-400" />,
            className: "glass-strong border-indigo-500/50 text-foreground"
          });

          // Re-fetch tasks without full page refresh
          window.dispatchEvent(new CustomEvent("tasksUpdated", { detail: { action: data.action_taken } }));
        }
      }
    } catch (error: any) {
      toast.error(error.message || "Oops! AI is sleeping.");
    } finally {
      setIsLoading(false);
    }
  };

  const quickActions = [
    "Add urgent task: Fix the code",
    "Mere pending tasks dikhao",
    "Mark ID 1 as complete",
  ];

  return (
    <>
      {/* Premium Floating Neural Button */}
      <motion.button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-6 z-50 p-[2px] rounded-full bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 shadow-lg shadow-indigo-500/40"
        whileHover={{ scale: 1.1, rotate: 5 }}
        whileTap={{ scale: 0.9 }}
      >
        <div className="bg-[#0a0a0a] rounded-full p-4 backdrop-blur-3xl border border-white/10">
          <Sparkles className="h-6 w-6 text-indigo-400 animate-pulse" />
        </div>
      </motion.button>

      <AnimatePresence>
        {isOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setIsOpen(false)}
              className="fixed inset-0 z-50 bg-black/40 backdrop-blur-md"
            />

            <motion.div
              initial={{ x: "100%", opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              exit={{ x: "100%", opacity: 0 }}
              className="fixed right-0 top-0 bottom-0 z-[51] w-full max-w-md glass-strong border-l border-white/10 shadow-2xl flex flex-col"
            >
              {/* Premium Header */}
              <div className="p-6 border-b border-white/10 flex items-center justify-between bg-white/5">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-xl bg-indigo-500/20 border border-indigo-500/30">
                    <MessageSquare className="h-5 w-5 text-indigo-400" />
                  </div>
                  <div>
                    <h2 className="text-lg font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-zinc-500">
                      Neural Assistant
                    </h2>
                    <p className="text-[10px] text-indigo-400 uppercase tracking-widest font-semibold">Active Matrix</p>
                  </div>
                </div>
                <Button variant="ghost" size="icon" onClick={() => setIsOpen(false)} className="rounded-full hover:bg-white/10">
                  <X className="h-5 w-5" />
                </Button>
              </div>

              {/* Chat Area */}
              <div className="flex-1 overflow-y-auto p-6 space-y-6 scrollbar-hide">
                {messages.map((msg) => (
                  <motion.div
                    key={msg.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
                  >
                    <div className={`max-w-[85%] rounded-2xl px-5 py-3 text-sm leading-relaxed ${
                      msg.role === "user" 
                        ? "bg-indigo-600 text-white shadow-lg shadow-indigo-600/20" 
                        : "glass-card border border-white/10 text-zinc-200"
                    }`}>
                      {msg.content}
                    </div>
                  </motion.div>
                ))}
                {isLoading && (
                  <div className="flex gap-2 text-zinc-500 text-xs items-center px-2 italic">
                    <Loader2 className="h-3 w-3 animate-spin" /> Neural is processing...
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>

              {/* Input Zone */}
              <div className="p-6 border-t border-white/10 bg-black/20">
                <div className="flex flex-wrap gap-2 mb-4">
                  {quickActions.map(action => (
                    <button 
                      key={action}
                      onClick={() => handleSendMessage(action)}
                      className="text-[10px] px-3 py-1.5 rounded-full border border-white/5 bg-white/5 hover:bg-white/10 text-zinc-400 transition-all"
                    >
                      {action}
                    </button>
                  ))}
                </div>
                <form 
                  onSubmit={(e: React.FormEvent) => { e.preventDefault(); handleSendMessage(input); }}
                  className="relative group"
                >
                  <Input 
                    value={input}
                    onChange={(e: React.ChangeEvent<HTMLInputElement>) => setInput(e.target.value)}
                    placeholder="Ask your assistant..."
                    className="bg-white/5 border-white/10 h-12 rounded-xl pr-12 focus:border-indigo-500/50 transition-all"
                  />
                  <Button 
                    type="submit" 
                    disabled={!input.trim()}
                    className="absolute right-1 top-1 h-10 w-10 rounded-lg bg-indigo-600 hover:bg-indigo-500"
                  >
                    <Send className="h-4 w-4" />
                  </Button>
                </form>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </>
  );
}