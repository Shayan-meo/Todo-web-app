"use client";

import { useRouter } from "next/navigation";
import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { apiClient } from "@/lib/api-client";
import { clearToken, isTokenValid } from "@/lib/auth";
import { Task } from "@/lib/types";
import { TaskForm } from "@/components/task-form";
import { TaskList } from "@/components/task-list";
import { WhatsAppButton } from "@/components/whatsapp-button";
import { AIChatbot } from "@/components/ai-chatbot";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import {
  CheckCircle2,
  LayoutDashboard,
  LogOut,
  Plus,
  RefreshCw,
  Sparkles,
} from "lucide-react";

export default function DashboardPage() {
  const router = useRouter();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editingTask, setEditingTask] = useState<Task | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);

  useEffect(() => {
    if (!isTokenValid()) {
      clearToken();
      router.push("/login");
      return;
    }

    const fetchTasks = async () => {
      setLoading(true);
      try {
        const response = await apiClient.get<Task[]>("/tasks");
        setTasks(response.data);
      } catch (err: any) {
        setError(err.response?.data?.detail || "Failed to load tasks");
      } finally {
        setLoading(false);
      }
    };

    fetchTasks();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    try {
      const response = await apiClient.get<Task[]>("/tasks");
      setTasks(response.data);
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to refresh tasks");
    } finally {
      setIsRefreshing(false);
    }
  };

  const handleAddTask = async (values: { title: string; description?: string }) => {
    const response = await apiClient.post<Task>("/tasks", values);
    setTasks((prev) => [response.data, ...prev]);
  };

  const handleUpdateTask = async (values: { title: string; description?: string }) => {
    if (!editingTask) return;
    const response = await apiClient.put<Task>(`/tasks/${editingTask.id}`, values);
    setTasks((prev) => prev.map((task) => (task.id === editingTask.id ? response.data : task)));
    setEditingTask(null);
  };

  const handleToggleComplete = async (taskId: number, isCompleted: boolean) => {
    const response = await apiClient.put<Task>(`/tasks/${taskId}`, { is_completed: isCompleted });
    setTasks((prev) => prev.map((task) => (task.id === taskId ? response.data : task)));
  };

  const handleDeleteTask = async (taskId: number) => {
    await apiClient.delete(`/tasks/${taskId}`);
    setTasks((prev) => prev.filter((task) => task.id !== taskId));
  };

  const completedCount = useMemo(() => tasks.filter((task) => task.is_completed).length, [tasks]);
  const completionPercentage = tasks.length > 0 ? Math.round((completedCount / tasks.length) * 100) : 0;
  const pendingCount = tasks.length - completedCount;

  const SidebarItem = ({ icon: Icon, label }: { icon: any; label: string }) => (
    <Button variant="ghost" className="w-full justify-start gap-3 h-11">
      <Icon className="h-4 w-4" />
      <span>{label}</span>
    </Button>
  );

  if (loading) {
    return (
      <div className="flex min-h-[calc(100vh-4rem)]">
        {/* Loading Sidebar */}
        <aside className="hidden w-64 border-r bg-white/50 dark:bg-slate-900/50 glass-subtle lg:block">
          <div className="p-4 space-y-2">
            <Skeleton className="h-11 w-full" />
            <Skeleton className="h-11 w-full" />
            <Skeleton className="h-11 w-full" />
          </div>
        </aside>

        {/* Loading Content */}
        <main className="flex-1 p-6">
          <div className="max-w-7xl mx-auto">
            <div className="mb-8">
              <Skeleton className="h-8 w-64 mb-2" />
              <Skeleton className="h-5 w-96" />
            </div>

            <div className="grid gap-6 lg:grid-cols-[1fr,400px]">
              <div className="space-y-4">
                {[1, 2, 3].map((i) => (
                  <Card key={i} className="glass-card">
                    <CardContent className="p-4">
                      <Skeleton className="h-6 w-3/4 mb-2" />
                      <Skeleton className="h-4 w-full" />
                    </CardContent>
                  </Card>
                ))}
              </div>

              <Card className="glass-card">
                <CardHeader>
                  <Skeleton className="h-6 w-32 mb-2" />
                  <Skeleton className="h-4 w-48" />
                </CardHeader>
                <CardContent className="space-y-4">
                  <Skeleton className="h-10 w-full" />
                  <Skeleton className="h-10 w-full" />
                  <Skeleton className="h-10 w-full" />
                </CardContent>
              </Card>
            </div>
          </div>
        </main>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex min-h-[calc(100vh-4rem)] items-center justify-center">
        <Card className="max-w-md w-full glass-card border-red-500/20">
          <CardHeader>
            <CardTitle className="text-red-500">Error Loading Tasks</CardTitle>
            <CardDescription>{error}</CardDescription>
          </CardHeader>
          <CardContent className="flex gap-3">
            <Button onClick={handleRefresh} disabled={isRefreshing}>
              <RefreshCw className={`mr-2 h-4 w-4 ${isRefreshing ? "animate-spin" : ""}`} />
              Retry
            </Button>
            <Link href="/logout">
              <Button variant="outline">Logout</Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="flex min-h-[calc(100vh-4rem)]">
      {/* Sidebar */}
      <aside className="hidden w-64 border-r bg-white/50 dark:bg-slate-900/50 glass-subtle lg:block">
        <div className="flex h-full flex-col">
          <div className="p-6">
            <div className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
              <Sparkles className="h-4 w-4" />
              <span>Navigation</span>
            </div>
          </div>

          <nav className="flex-1 px-4 space-y-1">
            <SidebarItem icon={LayoutDashboard} label="Dashboard" />
          </nav>

          <div className="p-4 border-t">
            <Link href="/logout">
              <Button variant="ghost" className="w-full justify-start gap-3 h-11 text-destructive hover:text-destructive">
                <LogOut className="h-4 w-4" />
                <span>Logout</span>
              </Button>
            </Link>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 p-6">
        {/* WhatsApp Contact Button */}
        <WhatsAppButton />
        {/* AI Chatbot */}
        <AIChatbot />
        <div className="max-w-7xl mx-auto space-y-6">
          {/* Header */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between"
          >
            <div>
              <h1 className="text-3xl font-bold tracking-tight text-slate-900 dark:text-white">
                Dashboard
              </h1>
              <p className="text-muted-foreground mt-1">
                Manage your tasks and stay organized
              </p>
            </div>
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="icon"
                onClick={handleRefresh}
                disabled={isRefreshing}
              >
                <RefreshCw className={`h-4 w-4 ${isRefreshing ? "animate-spin" : ""}`} />
              </Button>
              <Link href="/logout" className="hidden sm:block">
                <Button variant="outline">
                  <LogOut className="mr-2 h-4 w-4" />
                  Logout
                </Button>
              </Link>
            </div>
          </motion.div>

          {/* Stats Cards */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="grid gap-4 sm:grid-cols-3"
          >
            <Card className="glass-card">
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium">Total Tasks</CardTitle>
                <Plus className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{tasks.length}</div>
                <p className="text-xs text-muted-foreground mt-1">
                  All tasks in your list
                </p>
              </CardContent>
            </Card>

            <Card className="glass-card">
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium">Pending</CardTitle>
                <RefreshCw className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-amber-500">{pendingCount}</div>
                <p className="text-xs text-muted-foreground mt-1">
                  Tasks awaiting completion
                </p>
              </CardContent>
            </Card>

            <Card className="glass-card">
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium">Completed</CardTitle>
                <CheckCircle2 className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-emerald-500">{completedCount}</div>
                <p className="text-xs text-muted-foreground mt-1">
                  {completionPercentage}% completion rate
                </p>
              </CardContent>
            </Card>
          </motion.div>

          {/* Main Content Grid */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="grid gap-6 lg:grid-cols-[1fr,400px]"
          >
            {/* Task List */}
            <div className="space-y-4">
              <div>
                <h2 className="text-xl font-semibold text-slate-900 dark:text-white">
                  Your Tasks
                </h2>
                <p className="text-sm text-muted-foreground mt-1">
                  {tasks.length === 0 ? "No tasks yet. Create your first task!" : `${completedCount} of ${tasks.length} completed`}
                </p>
              </div>
              <TaskList
                tasks={tasks}
                onToggleComplete={handleToggleComplete}
                onDelete={handleDeleteTask}
                onEdit={setEditingTask}
              />
            </div>

            {/* Task Form */}
            <div>
              <Card className="glass-card sticky top-24">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Plus className="h-5 w-5" />
                    {editingTask ? "Edit Task" : "Add New Task"}
                  </CardTitle>
                  <CardDescription>
                    {editingTask ? "Update your task details below" : "Create a new task to get started"}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <TaskForm
                    key={editingTask?.id || "new"}
                    initialValues={editingTask ? { title: editingTask.title, description: editingTask.description || "" } : undefined}
                    onSubmit={editingTask ? handleUpdateTask : handleAddTask}
                    submitLabel={editingTask ? "Update Task" : "Add Task"}
                  />
                  {editingTask && (
                    <Button
                      variant="ghost"
                      className="w-full mt-4"
                      onClick={() => setEditingTask(null)}
                    >
                      Cancel Editing
                    </Button>
                  )}
                </CardContent>
              </Card>
            </div>
          </motion.div>
        </div>
      </main>
    </div>
  );
}
