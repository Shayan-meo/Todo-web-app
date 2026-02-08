"use client"

import Link from "next/link";
import { motion } from "framer-motion";
import { AuthForm } from "@/components/auth-form";
import { UserPlus } from "lucide-react";

export default function RegisterPage() {
  return (
    <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center px-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-md"
      >
        {/* Header */}
        <div className="text-center mb-8">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-emerald-600 text-white shadow-lg shadow-emerald-500/20 mb-4"
          >
            <UserPlus className="h-8 w-8" />
          </motion.div>
          <h1 className="text-3xl font-bold tracking-tight text-white mb-2">
            Create Account
          </h1>
          <p className="text-slate-300">
            Join Todo-App and start organizing your life
          </p>
        </div>

        {/* Card */}
        <div className="glass-card rounded-xl p-8 border-slate-700">
          <AuthForm mode="register" />
        </div>

        {/* Footer */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="mt-6 text-center"
        >
          <p className="text-sm text-slate-400">
            Already have an account?{" "}
            <Link
              href="/login"
              className="font-semibold text-emerald-400 hover:text-emerald-300 transition-colors"
            >
              Sign in
            </Link>
          </p>
        </motion.div>
      </motion.div>
    </div>
  );
}
