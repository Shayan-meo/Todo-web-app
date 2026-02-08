"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  AlertCircle,
  Loader2,
  Flag,
} from "lucide-react";

const taskSchema = z.object({
  title: z.string().min(1, "Title is required"),
  description: z.string().optional(),
  priority: z.enum(["High", "Medium", "Normal", "Low"]),
});

type TaskFormValues = z.infer<typeof taskSchema>;

interface TaskFormProps {
  initialValues?: TaskFormValues;
  onSubmit: (values: TaskFormValues) => Promise<void>;
  submitLabel?: string;
}

export function TaskForm({ initialValues, onSubmit, submitLabel = "Save task" }: TaskFormProps) {
  const {
    register,
    handleSubmit,
    reset,
    setValue,
    watch,
    formState: { errors, isSubmitting },
  } = useForm<TaskFormValues>({
    resolver: zodResolver(taskSchema),
    defaultValues: {
      title: initialValues?.title ?? "",
      description: initialValues?.description ?? "",
      priority: initialValues?.priority ?? "Normal",
    },
  });

  const priority = watch("priority");

  const [error, setError] = useState<string | null>(null);

  const submitHandler = async (values: TaskFormValues) => {
    setError(null);
    try {
      await onSubmit(values);
      reset();
    } catch (err: any) {
      setError(err.message || "Failed to save task");
    }
  };

  const getPriorityColor = (p: string) => {
    switch (p) {
      case "High": return "text-red-500";
      case "Medium": return "text-orange-400";
      case "Low": return "text-cyan-400";
      default: return "text-slate-300";
    }
  };

  return (
    <form onSubmit={handleSubmit(submitHandler)} className="space-y-4">
      <div className="space-y-2">
        <Label htmlFor="task-title" className="text-white text-sm font-medium">Title</Label>
        <Input
          id="task-title"
          type="text"
          placeholder="Add a new task..."
          {...register("title")}
          className={`h-11 bg-slate-800 border-slate-700 text-white placeholder:text-slate-500 focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500/50 ${errors.title ? "border-red-500" : ""}`}
        />
        {errors.title && (
          <motion.p
            initial={{ opacity: 0, y: -5 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-sm text-red-400 flex items-center gap-1"
          >
            <AlertCircle className="h-4 w-4" />
            {errors.title.message}
          </motion.p>
        )}
      </div>

      <div className="space-y-2">
        <Label htmlFor="task-priority" className="text-white text-sm font-medium">Priority</Label>
        <Select
          value={priority}
          onValueChange={(value: any) => setValue("priority", value)}
        >
          <SelectTrigger id="task-priority" className="bg-slate-800 border-slate-700 text-white focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500/50">
            <div className="flex items-center gap-2">
              <Flag className={`h-4 w-4 ${getPriorityColor(priority)}`} />
              <SelectValue placeholder="Select priority" />
            </div>
          </SelectTrigger>
          <SelectContent className="bg-slate-900 border-slate-700">
            <SelectItem value="High" className="font-medium">
              <div className="flex items-center gap-2">
                <div className="h-2 w-2 rounded-full bg-red-500" />
                <span className="text-red-400">High Priority</span>
              </div>
            </SelectItem>
            <SelectItem value="Medium" className="font-medium">
              <div className="flex items-center gap-2">
                <div className="h-2 w-2 rounded-full bg-orange-400" />
                <span className="text-orange-400">Medium Priority</span>
              </div>
            </SelectItem>
            <SelectItem value="Normal">
              <div className="flex items-center gap-2">
                <div className="h-2 w-2 rounded-full bg-slate-400" />
                <span className="text-slate-300">Normal Priority</span>
              </div>
            </SelectItem>
            <SelectItem value="Low">
              <div className="flex items-center gap-2">
                <div className="h-2 w-2 rounded-full bg-cyan-400" />
                <span className="text-cyan-400">Low Priority</span>
              </div>
            </SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div className="space-y-2">
        <Label htmlFor="task-description" className="text-white text-sm font-medium">
          Description <span className="text-slate-400">(optional)</span>
        </Label>
        <Textarea
          id="task-description"
          placeholder="Add task details..."
          rows={3}
          {...register("description")}
          className="bg-slate-800 border-slate-700 text-white placeholder:text-slate-500 focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500/50"
        />
        {errors.description && (
          <motion.p
            initial={{ opacity: 0, y: -5 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-sm text-red-400 flex items-center gap-1"
          >
            <AlertCircle className="h-4 w-4" />
            {errors.description.message}
          </motion.p>
        )}
      </div>

      {error && (
        <motion.div
          initial={{ opacity: 0, y: -5 }}
          animate={{ opacity: 1, y: 0 }}
          className="rounded-lg bg-red-500/10 border border-red-500/30 px-4 py-3 text-sm text-red-400 flex items-start gap-2"
        >
          <AlertCircle className="h-5 w-5 flex-shrink-0 mt-0.5" />
          <span>{error}</span>
        </motion.div>
      )}

      <Button
        type="submit"
        disabled={isSubmitting}
        className="w-full h-11 bg-emerald-600 hover:bg-emerald-700 text-white font-medium transition-colors"
      >
        {isSubmitting ? (
          <>
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            Saving...
          </>
        ) : (
          submitLabel
        )}
      </Button>
    </form>
  );
}
