"use client";

import { useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import dayjs from "dayjs";
import { CheckCircle2, Circle, Edit, Trash2, Clock } from "lucide-react";
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

export function TaskList({ tasks, onToggleComplete, onDelete, onEdit }: TaskListProps) {
  const sortedTasks = useMemo(() => {
    return [...tasks].sort((a, b) => Number(a.is_completed) - Number(b.is_completed));
  }, [tasks]);

  if (!tasks.length) {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="rounded-xl border-2 border-dashed bg-card/50 p-12 text-center"
      >
        <Circle className="mx-auto h-12 w-12 text-muted-foreground/50 mb-4" />
        <p className="text-lg font-medium text-foreground">Sukoon hi sukoon! Koi pending task nahi hai.</p>
        <p className="text-sm text-muted-foreground/70 mt-1">Create your first task to get started!</p>
      </motion.div>
    );
  }

  return (
    <AnimatePresence mode="popLayout">
      <ul className="space-y-3">
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
            <Card className={`glass-card transition-all hover:scale-[1.01] ${
              task.is_completed ? "opacity-60" : ""
            }`}>
              <CardContent className="p-4">
                <div className="flex items-start gap-3">
                  <motion.button
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.95 }}
                    className="mt-1 flex-shrink-0 text-muted-foreground hover:text-primary transition-colors"
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
                      <h3 className={`font-semibold transition-all ${
                        task.is_completed
                          ? "line-through text-muted-foreground"
                          : "text-foreground"
                      }`}>
                        {task.title}
                      </h3>
                      <span className="flex-shrink-0 text-xs text-muted-foreground flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        {dayjs(task.updated_at).format("MMM D, HH:mm")}
                      </span>
                    </div>

                    {task.description && (
                      <p className={`mt-2 text-sm transition-all ${
                        task.is_completed
                          ? "text-muted-foreground/60"
                          : "text-muted-foreground"
                      }`}>
                        {task.description}
                      </p>
                    )}

                    <div className="mt-3 flex gap-2">
                      <Button
                        variant="ghost"
                        size="sm"
                        className="h-8 gap-1 text-muted-foreground hover:text-foreground"
                        onClick={() => onEdit(task)}
                      >
                        <Edit className="h-4 w-4" />
                        <span className="hidden sm:inline">Edit</span>
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        className="h-8 gap-1 text-destructive hover:text-destructive hover:bg-destructive/10"
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
