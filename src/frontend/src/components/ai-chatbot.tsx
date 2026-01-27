"use client";

import React, { useEffect, useRef, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  MessageSquare, X, Send, Trash2, Sparkles, 
  Loader2, Bot, Layout, ListTodo, CheckCircle2,
  AlertCircle, History
} from "lucide-react";
import { toast } from "sonner";
import { chatApi } from "@/lib/api-client";
import { ChatMessage } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

// --- STRICT TYPESCRIPT INTERFACES ---
interface ChatResponse {
  content: string;
  action_taken?: "add_task" | "update_task" | "delete_task" | "list_tasks" | null;
  priority_detected?: string;
}

export function AIChatbot() {
  // --- STATE MANAGEMENT ---
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isHistoryLoaded, setIsHistoryLoaded] = useState(false);
  
  // --- REFS ---
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const scrollContainerRef = useRef<HTMLDivElement>(null);

  // --- UTILITIES ---
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // --- HISTORY LOADING ---
  useEffect(() => {
    const loadHistory = async () => {
      if (!isOpen || isHistoryLoaded) return;
      
      try {
        const response = await chatApi.getHistory();
        // Sorting messages chronologically
        const sortedHistory = (response.data || []).sort((a: any, b: any) => 
          new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
        );
        setMessages(sortedHistory);
        setIsHistoryLoaded(true);
      } catch (error) {
        console.error("Chat History Error:", error);
        toast.error("Could not load previous chats");
        setIsHistoryLoaded(true);
      }
    };

    loadHistory();
  }, [isOpen, isHistoryLoaded]);

  // --- MESSAGE HANDLING ---
  const handleSendMessage = async (messageText: string) => {
    if (!messageText.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      id: Date.now(),
      user_id: 0, // Placeholder
      role: "user",
      content: messageText,
      created_at: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
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
        body: JSON.stringify({ message: messageText }),
      });

      if (!response.ok) {
        if (response.status === 400) {
          throw new Error("Daily AI Limit Reached (Reset at 5 AM PKT)");
        }
        throw new Error("Connection error. Please try again.");
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
        
        setMessages((prev) => [...prev, assistantMessage]);

        // --- PREMIUM ACTION FEEDBACK ---
        if (data.action_taken && ["add_task", "update_task", "delete_task"].includes(data.action_taken)) {
          const actionText = data.action_taken.replace('_', ' ').toUpperCase();
          
          toast.success(actionText, {
            description: data.priority_detected ? `Priority: ${data.priority_detected}` : "Task State Synchronized",
            icon: <CheckCircle2 className="h-4 w-4 text-emerald-500" />,
            className: "glass-strong border-emerald-500/30"
          });

          // Trigger Refresh Event
          window.dispatchEvent(new CustomEvent("tasksUpdated", { 
            detail: { action: data.action_taken } 
          }));
        }
      }
    } catch (error: any) {
      toast.error(error.message || "Something went wrong");
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearHistory = async () => {
    try {
      await chatApi.clearHistory();
      setMessages([]);
      toast.info("Conversation history cleared");
    } catch (error) {
      toast.error("Failed to clear history");
    }
  };

  const quickActions = [
    { label: "Show Tasks", icon: <ListTodo className="h-3 w-3" />, cmd: "Show my pending tasks" },
    { label: "Urgent Add", icon: <AlertCircle className="h-3 w-3" />, cmd: "Add urgent task: Fix the code" },
    { label: "History", icon: <History className="h-3 w-3" />, cmd: "What did I do yesterday?" },
  ];

  return (
    <>
      {/* --- NEURAL TRIGGER BUTTON --- */}
      <motion.button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-6 z-50 p-[2px] rounded-full bg-gradient-to-tr from-indigo-500 via-purple-500 to-pink-500"
        whileHover={{ scale: 1.1, rotate: 5 }}
        whileTap={{ scale: 0.95 }}
        animate={{
          boxShadow: [
            "0 0 0 0 rgba(99, 102, 241, 0.4)",
            "0 0 0 15px rgba(99, 102, 241, 0)",
          ]
        }}
        transition={{ boxShadow: { duration: 2, repeat: Infinity } }}
      >
        <div className="bg-[#0a0a0a] rounded-full p-4 backdrop-blur-3xl border border-white/10">
          <Sparkles className="h-6 w-6 text-indigo-400" />
        </div>
      </motion.button>

      <AnimatePresence>
        {isOpen && (
          <>
            {/* Backdrop Blur */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setIsOpen(false)}
              className="fixed inset-0 z-50 bg-black/40 backdrop-blur-md"
            />

            {/* Main Chat Container */}
            <motion.div
              initial={{ x: "100%", opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              exit={{ x: "100%", opacity: 0 }}
              transition={{ type: "spring", damping: 30, stiffness: 300 }}
              className="fixed right-0 top-0 bottom-0 z-[51] w-full max-w-md glass-strong border-l border-white/10 shadow-2xl flex flex-col"
            >
              {/* --- HEADER --- */}
              <div className="p-6 border-b border-white/10 flex items-center justify-between bg-white/5">
                <div className="flex items-center gap-4">
                  <div className="p-2.5 rounded-2xl bg-indigo-500/20 border border-indigo-500/30">
                    <Bot className="h-6 w-6 text-indigo-400" />
                  </div>
                  <div>
                    <h2 className="text-xl font-bold tracking-tight text-white">Advanced AI Task Assistant</h2>
                    <div className="flex items-center gap-1.5">
                      <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
                      <p className="text-[10px] text-zinc-500 uppercase tracking-[0.2em] font-bold">Intelligent Assistant Ready</p>
                    </div>
                  </div>
                </div>
                <div className="flex gap-2">
                  <Button variant="ghost" size="icon" onClick={handleClearHistory} className="h-9 w-9 rounded-xl hover:bg-white/5 text-zinc-500 hover:text-red-400">
                    <Trash2 className="h-4 w-4" />
                  </Button>
                  <Button variant="ghost" size="icon" onClick={() => setIsOpen(false)} className="h-9 w-9 rounded-xl hover:bg-white/5">
                    <X className="h-5 w-5 text-zinc-500" />
                  </Button>
                </div>
              </div>

              {/* --- CHAT VIEWPORT --- */}
              <div 
                className="flex-1 overflow-y-auto p-6 space-y-6 scrollbar-hide"
                ref={scrollContainerRef}
              >
                {messages.length === 0 && !isLoading && (
                  <div className="h-full flex flex-col items-center justify-center text-center space-y-4 opacity-50">
                    <Layout className="h-12 w-12 text-zinc-700" />
                    <p className="text-sm text-zinc-500">How can I help you today?</p>
                  </div>
                )}

                {messages.map((msg) => (
                  <motion.div
                    key={msg.id}
                    initial={{ opacity: 0, y: 15 }}
                    animate={{ opacity: 1, y: 0 }}
                    className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
                  >
                    <div className={`max-w-[85%] rounded-2xl px-5 py-3.5 text-sm leading-relaxed whitespace-pre-wrap ${
                      msg.role === "user" 
                        ? "bg-indigo-600 text-white shadow-xl shadow-indigo-600/20 rounded-tr-none" 
                        : "bg-white/5 border border-white/10 text-zinc-200 backdrop-blur-xl rounded-tl-none"
                    }`}>
                      {msg.content}
                    </div>
                  </motion.div>
                ))}

                {isLoading && (
                  <div className="flex gap-3 items-center px-2">
                    <Loader2 className="h-4 w-4 animate-spin text-indigo-500" />
                    <span className="text-[10px] uppercase tracking-widest text-zinc-500 font-bold">Processing Request...</span>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>

              {/* --- INPUT & QUICK ACTIONS --- */}
              <div className="p-6 border-t border-white/10 bg-black/40 space-y-4">
                <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-hide">
                  {quickActions.map((action) => (
                    <button
                      key={action.label}
                      onClick={() => handleSendMessage(action.cmd)}
                      className="flex items-center gap-2 flex-shrink-0 px-4 py-2 rounded-xl bg-white/5 border border-white/10 text-zinc-400 hover:text-white hover:bg-white/10 transition-all text-xs font-medium"
                    >
                      {action.icon}
                      {action.label}
                    </button>
                  ))}
                </div>

                <form 
                  onSubmit={(e) => { e.preventDefault(); handleSendMessage(input); }}
                  className="relative group"
                >
                  <Input 
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Ask me anything..."
                    className="bg-white/5 border-white/10 h-14 rounded-2xl pr-14 focus:border-indigo-500/50 transition-all text-white placeholder:text-zinc-600"
                    disabled={isLoading}
                  />
                  <Button 
                    type="submit" 
                    disabled={!input.trim() || isLoading}
                    className="absolute right-2 top-2 h-10 w-10 rounded-xl bg-indigo-600 hover:bg-indigo-500 transition-colors shadow-lg shadow-indigo-600/20"
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