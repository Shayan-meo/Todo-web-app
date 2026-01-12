"use client";

import axios from "axios";
import type { ChatMessage, ChatResponse } from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
});

apiClient.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("todo_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

// Chat API
export const chatApi = {
  sendMessage: (message: string) =>
    apiClient.post<ChatResponse>("/ai/chat", { message }),
  getHistory: () => apiClient.get<ChatMessage[]>("/ai/chat/history"),
  clearHistory: () => apiClient.delete("/ai/chat/history"),
};
