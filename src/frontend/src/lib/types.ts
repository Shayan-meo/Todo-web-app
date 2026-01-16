export interface Task {
  id: number;
  user_id: number;
  title: string;
  description?: string | null;
  priority?: string;
  reminder_time?: string | null;
  is_completed: boolean;
  created_at: string;
  updated_at: string;
}

export interface TaskInput {
  title: string;
  description?: string | null;
  priority?: string;
  reminder_time?: string | null;
}

export interface TaskUpdateInput {
  title?: string;
  description?: string | null;
  is_completed?: boolean;
  priority?: string;
  reminder_time?: string | null;
}

export interface ChatMessage {
  id: number;
  user_id: number;
  role: "user" | "assistant";
  content: string;
  created_at: string;
}

export interface ChatResponse {
  message: string;
  action_taken?: string;
  action_result?: Record<string, unknown>;
}
