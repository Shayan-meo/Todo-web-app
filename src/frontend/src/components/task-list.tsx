"use client";

import { useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import dayjs from "dayjs";
import { CheckCircle2, Circle, Edit, Trash2, Clock, Flag, Bell } from "lucide-react";
import { Task } from "@/lib/types";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
} from "@/components/ui/card";

interface TaskListProps {
  tasks: Task[];
  onToggleComplete: (taskId: number, isCompleted: boolean) => void;
  onDelete: (taskId: number) => void;
  onEdit: (task: Task) => void;
}

const taskVariants = {
  hidden: { opacity: 0, y: 10 },
  visible: { opacity: 1, y: 0 },
  exit: { opacity: 0, x: -20 },
};

import { ClipboardList } from "lucide-react";

// ... existing imports

export function TaskList({ tasks, onToggleComplete, onDelete, onEdit }: TaskListProps) {
  const sortedTasks = useMemo(() => {
    // Sort logic:
    // 1. Incomplete tasks first
    // 2. High priority > Medium > Normal > Low
    // 3. Newest created first (as tie-breaker)

    // Priority weight map (higher is more important)
    const priorityWeight: Record<string, number> = {
      "High": 4,
      "Medium": 3,
      "Normal": 2,
      "Low": 1
    };

    return [...tasks].sort((a, b) => {
      // 1. Completion status
      if (a.is_completed !== b.is_completed) {
        return Number(a.is_completed) - Number(b.is_completed); // 0 (incomplete) before 1 (complete)
      }

      // 2. Priority (only for incomplete tasks usually, but useful for history too)
      const weightA = priorityWeight[a.priority || "Normal"] || 2;
      const weightB = priorityWeight[b.priority || "Normal"] || 2;

      if (weightA !== weightB) {
        return weightB - weightA; // Higher weight first
      }

      // 3. Date (Newest first)
      return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
    });
  }, [tasks]);

  const getPriorityBadge = (priority?: string) => {
    switch(priority) {
      case "High":
        return <span className="inline-flex items-center gap-1 rounded-full bg-red-900/40 px-2 py-0.5 text-xs font-medium text-red-400 border border-red-500/20">High</span>;
      case "Medium":
        return <span className="inline-flex items-center gap-1 rounded-full bg-orange-900/40 px-2 py-0.5 text-xs font-medium text-orange-400 border border-orange-500/20">Medium</span>;
      case "Low":
        return <span className="inline-flex items-center gap-1 rounded-full bg-blue-900/40 px-2 py-0.5 text-xs font-medium text-blue-400 border border-blue-500/20">Low</span>;
      default:
        return null;
    }
  };

  if (!tasks.length) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="rounded-xl border border-dashed border-slate-700 bg-slate-900/40 p-12 text-center"
      >
        <div className="flex justify-center mb-6">
          <div className="relative">
            <div className="absolute inset-0 bg-indigo-500/20 rounded-full blur-xl animate-pulse" />
            <ClipboardList className="relative h-16 w-16 text-indigo-400" />
          </div>
        </div>
        <h3 className="text-2xl font-bold tracking-tight text-slate-100 mb-2">
          No tasks found
        </h3>
        <p className="text-slate-400 max-w-[300px] mx-auto mb-6">
          Your productivity journey starts here. Add your first task to stay organized.
        </p>
      </motion.div>
    );
  }

  return (
    <AnimatePresence mode="popLayout">
      <ul className="space-y-4">
        {sortedTasks.map((task, index) => (
          <motion.li
            key={task.id}
            variants={taskVariants}
            initial="hidden"
            animate="visible"
            exit="exit"
            transition={{ delay: index * 0.05 }}
            layout
          >
            <Card className={`border-slate-800 bg-slate-900/40 transition-all hover:-translate-y-[2px] hover:shadow-lg hover:shadow-indigo-500/10 ${
              task.is_completed ? "opacity-60" : ""
            }`}>
              <CardContent className="p-4">
                <div className="flex items-start gap-3">
                  <motion.button
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.95 }}
                    className="mt-1 flex-shrink-0 text-slate-500 hover:text-indigo-400 transition-colors"
                    onClick={() => onToggleComplete(task.id, !task.is_completed)}
                    aria-label={task.is_completed ? "Mark incomplete" : "Mark complete"}
                  >
                    {task.is_completed ? (
                      <CheckCircle2 className="h-5 w-5 text-emerald-500" />
                    ) : (
                      <Circle className="h-5 w-5" />
                    )}
                  </motion.button>

                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className="text-xs font-mono text-slate-500 bg-slate-800 px-1.5 py-0.5 rounded">
                            #{task.id}
                          </span>
                          <h3 className={`font-semibold transition-all ${
                            task.is_completed
                              ? "line-through text-slate-500"
                              : "text-slate-100"
                          }`}>
                            {task.title}
                          </h3>
                          {getPriorityBadge(task.priority)}
                        </div>
                      </div>
                      <span className="flex-shrink-0 text-xs text-slate-500 flex items-center gap-1 whitespace-nowrap ml-2">
                        <Clock className="h-3 w-3" />
                        {dayjs(task.updated_at).format("MMM D, HH:mm")}
                      </span>
                    </div>

                    {task.description && (
                      <p className={`mt-2 text-sm transition-all ${
                        task.is_completed
                          ? "text-slate-600"
                          : "text-slate-400"
                      }`}>
                        {task.description}
                      </p>
                    )}

                    {task.reminder_time && !task.is_completed && (
                      <div className="mt-2 flex items-center gap-1.5 text-xs font-medium text-amber-500/90">
                        <Bell className="h-3.5 w-3.5" />
                        <span>Remind: {dayjs(task.reminder_time).format("MMM D, h:mm A")}</span>
                      </div>
                    )}

                    <div className="mt-3 flex gap-2">
                      <Button
                        variant="ghost"
                        size="sm"
                        className="h-8 gap-1 text-slate-500 hover:text-slate-100 hover:bg-slate-800"
                        onClick={() => onEdit(task)}
                      >
                        <Edit className="h-4 w-4" />
                        <span className="hidden sm:inline">Edit</span>
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        className="h-8 gap-1 text-slate-500 hover:text-red-400 hover:bg-red-900/20"
                        onClick={() => onDelete(task.id)}
                      >
                        <Trash2 className="h-4 w-4" />
                        <span className="hidden sm:inline">Delete</span>
                      </Button>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.li>
        ))}
      </ul>
    </AnimatePresence>
  );
}
