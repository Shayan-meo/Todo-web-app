"use client";

import { useCallback, useState } from "react";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { motion } from "framer-motion";
import { apiClient } from "@/lib/api-client";
import { saveToken } from "@/lib/auth";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  CheckCircle2,
  AlertCircle,
  Loader2,
} from "lucide-react";

const schema = z.object({
  email: z.string().email({ message: "Enter a valid email" }),
  password: z.string().min(6, { message: "Password must be at least 6 characters" }),
});

interface AuthFormProps {
  mode: "login" | "register";
}

type FormData = z.infer<typeof schema>;

export function AuthForm({ mode }: AuthFormProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const router = useRouter();

  const { register, handleSubmit, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
  });

  const onSubmit = useCallback(async (data: FormData) => {
    console.log("[Auth] Form submitted, email:", data.email);
    setLoading(true);
    setError(null);
    setSuccessMessage(null);

    try {
      if (mode === "register") {
        console.log("[Auth] Registering user...");
        await apiClient.post("/auth/register", data);
        setSuccessMessage("Account created! You can now log in.");
        console.log("[Auth] Registration successful");
      } else {
        console.log("[Auth] Logging in...");
        const response = await apiClient.post(
          "/auth/login",
          new URLSearchParams({
            username: data.email,
            password: data.password,
          }),
          {
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
          }
        );
        console.log("[Auth] Login response received:", response.data);

        const { access_token, expires_at } = response.data;
        console.log("[Auth] Token received, length:", access_token?.length);

        if (!access_token) {
          throw new Error("No token received from server");
        }

        const expiresAt = expires_at
          ? (typeof expires_at === "string" ? expires_at : new Date(expires_at).toISOString())
          : new Date(Date.now() + 60 * 60 * 1000).toISOString();
        console.log("[Auth] Saving token, expiresAt:", expiresAt, "token length:", access_token?.length);

        saveToken(access_token, expiresAt);
        console.log("[Auth] Token saved to localStorage");

        const savedToken = localStorage.getItem("todo_token");
        console.log("[Auth] Token verification, saved token exists:", !!savedToken);

        router.push("/dashboard");
      }
    } catch (err: any) {
      console.error("[Auth] Error:", err.message || err);
      const message = err.response?.data?.detail || err.message || "Something went wrong";
      setError(message);
    } finally {
      setLoading(false);
    }
  }, [mode, router]);

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div className="space-y-2">
        <Label htmlFor="email" className="text-white text-sm font-medium">Email</Label>
        <Input
          id="email"
          type="email"
          placeholder="you@example.com"
          {...register("email")}
          className={`h-11 bg-slate-800 border-slate-700 text-white placeholder:text-slate-500 focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500/50 ${errors.email ? "border-red-500" : ""}`}
        />
        {errors.email && (
          <motion.p
            initial={{ opacity: 0, y: -5 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-sm text-red-400 flex items-center gap-1"
          >
            <AlertCircle className="h-4 w-4" />
            {errors.email.message}
          </motion.p>
        )}
      </div>

      <div className="space-y-2">
        <Label htmlFor="password" className="text-white text-sm font-medium">Password</Label>
        <Input
          id="password"
          type="password"
          placeholder="••••••••"
          {...register("password")}
          className={`h-11 bg-slate-800 border-slate-700 text-white placeholder:text-slate-500 focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500/50 ${errors.password ? "border-red-500" : ""}`}
        />
        {errors.password && (
          <motion.p
            initial={{ opacity: 0, y: -5 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-sm text-red-400 flex items-center gap-1"
          >
            <AlertCircle className="h-4 w-4" />
            {errors.password.message}
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

      {successMessage && (
        <motion.div
          initial={{ opacity: 0, y: -5 }}
          animate={{ opacity: 1, y: 0 }}
          className="rounded-lg bg-emerald-500/10 border border-emerald-500/30 px-4 py-3 text-sm text-emerald-400 flex items-start gap-2"
        >
          <CheckCircle2 className="h-5 w-5 flex-shrink-0 mt-0.5" />
          <span>{successMessage}</span>
        </motion.div>
      )}

      <Button
        type="submit"
        disabled={loading}
        className="w-full h-11 text-base font-medium bg-emerald-600 hover:bg-emerald-700 text-white shadow-lg shadow-emerald-500/20 transition-colors"
      >
        {loading ? (
          <>
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            Please wait...
          </>
        ) : mode === "login" ? (
          "Sign in"
        ) : (
          "Create account"
        )}
      </Button>
    </form>
  );
}
