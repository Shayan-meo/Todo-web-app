"use client"

import Link from "next/link";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  CheckCircle2,
  LayoutDashboard,
  Sparkles,
  ShieldCheck,
  Zap,
} from "lucide-react";

export default function Home() {
  const features = [
    {
      icon: <LayoutDashboard className="h-6 w-6" />,
      title: "Intuitive Dashboard",
      description: "Clean, minimalist interface designed for pure productivity",
    },
    {
      icon: <Zap className="h-6 w-6" />,
      title: "Lightning Fast",
      description: "Built with performance in mind for instant task operations",
    },
    {
      icon: <ShieldCheck className="h-6 w-6" />,
      title: "Secure & Private",
      description: "Your data is protected with enterprise-grade encryption",
    },
    {
      icon: <Sparkles className="h-6 w-6" />,
      title: "Premium Design",
      description: "Refined aesthetic with elegant dark mode and smooth transitions",
    },
  ];

  return (
    <div className="relative overflow-hidden">
      {/* Animated Background Gradients */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <motion.div
          className="absolute -top-40 -right-40 w-96 h-96 bg-emerald-500/10 rounded-full blur-3xl"
          animate={{
            scale: [1, 1.2, 1],
            opacity: [0.2, 0.4, 0.2],
          }}
          transition={{
            duration: 8,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        />
        <motion.div
          className="absolute -bottom-40 -left-40 w-96 h-96 bg-emerald-400/10 rounded-full blur-3xl"
          animate={{
            scale: [1, 1.2, 1],
            opacity: [0.2, 0.4, 0.2],
          }}
          transition={{
            duration: 8,
            repeat: Infinity,
            ease: "easeInOut",
            delay: 2,
          }}
        />
      </div>

      {/* Hero Section */}
      <section className="relative px-4 py-20 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-4xl text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="space-y-6"
          >
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="inline-flex items-center gap-2 rounded-full bg-emerald-500/10 px-4 py-2 text-sm font-medium text-emerald-400 border border-emerald-500/30 backdrop-blur-sm"
            >
              <Sparkles className="h-4 w-4" />
              <span>Premium Task Management</span>
            </motion.div>

            <h1 className="text-5xl font-bold tracking-tight text-white sm:text-6xl md:text-7xl">
              Organize Your Life,{" "}
              <span className="text-gradient">
                Effortlessly
              </span>
            </h1>

            <p className="mx-auto max-w-2xl text-lg text-slate-300">
              Experience premium task management with an elegant, minimalist interface
              and powerful productivity features designed for modern teams and individuals.
            </p>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.4 }}
              className="flex flex-col gap-4 sm:flex-row sm:justify-center"
            >
              <Button
                asChild
                size="lg"
                className="h-12 px-8 text-base font-medium bg-emerald-600 hover:bg-emerald-700 text-white shadow-lg shadow-emerald-500/20"
              >
                <Link href="/register">
                  <CheckCircle2 className="mr-2 h-5 w-5" />
                  Create an account
                </Link>
              </Button>
              <Button
                asChild
                size="lg"
                variant="outline"
                className="h-12 px-8 text-base font-medium border-slate-700 text-white hover:bg-slate-800/50"
              >
                <Link href="/login">Sign in</Link>
              </Button>
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section className="relative px-4 py-16 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-7xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.6 }}
            className="text-center mb-12"
          >
            <h2 className="text-3xl font-bold tracking-tight text-white sm:text-4xl">
              Everything You Need
            </h2>
            <p className="mt-4 text-lg text-slate-300">
              Powerful features to keep you organized and focused on what matters
            </p>
          </motion.div>

          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
            {features.map((feature, index) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.8 + index * 0.1 }}
              >
                <Card className="glass-card h-full transition-all duration-300 hover:scale-105 hover:shadow-xl hover:shadow-emerald-500/10 hover:border-emerald-500/50">
                  <CardHeader>
                    <div className="mb-2 inline-flex h-12 w-12 items-center justify-center rounded-lg bg-emerald-600 text-white shadow-lg shadow-emerald-500/20">
                      {feature.icon}
                    </div>
                    <CardTitle className="text-xl text-white">{feature.title}</CardTitle>
                    <CardDescription className="text-base text-slate-300">
                      {feature.description}
                    </CardDescription>
                  </CardHeader>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="relative px-4 py-16 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-4xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 1.2 }}
          >
            <Card className="glass-card border-emerald-500/30">
              <CardHeader className="text-center pb-6">
                <CardTitle className="text-3xl font-bold text-white">
                  Ready to Get Started?
                </CardTitle>
                <CardDescription className="text-lg mt-2 text-slate-300">
                  Join thousands of users who trust Todo-App for professional task management
                </CardDescription>
              </CardHeader>
              <CardContent className="flex flex-col gap-4 sm:flex-row sm:justify-center pb-6">
                <Button
                  asChild
                  size="lg"
                  className="h-12 px-8 text-base font-medium bg-emerald-600 hover:bg-emerald-700 text-white shadow-lg shadow-emerald-500/20"
                >
                  <Link href="/register">Create Free Account</Link>
                </Button>
              </CardContent>
            </Card>
          </motion.div>
        </div>
      </section>
    </div>
  );
}
