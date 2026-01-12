import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { ThemeProvider } from "@/components/theme-provider";
import { ThemeToggle } from "@/components/theme-toggle";
import { Toaster } from "sonner";
import Link from "next/link";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Todo-App | Premium Task Management",
  description: "Manage your todos with elegance and efficiency",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${inter.className} antialiased`}>
        <ThemeProvider
          defaultTheme="system"
          storageKey="todo-app-theme"
        >
          <Toaster position="top-right" richColors />
          <div className="min-h-screen bg-gradient-to-br from-slate-50 via-indigo-50/30 to-violet-50/30 dark:from-slate-950 dark:via-indigo-950/20 dark:to-violet-950/20">
            {/* Premium Header with Glassmorphism */}
            <header className="sticky top-0 z-50 glass-subtle border-b border-white/10 dark:border-white/5">
              <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
                <div className="flex h-16 items-center justify-between">
                  {/* Logo */}
                  <Link href="/" className="flex items-center space-x-2">
                    <h1 className="text-2xl font-bold text-gradient bg-gradient-to-r from-indigo-600 to-violet-600 dark:from-indigo-400 dark:to-violet-400 bg-clip-text text-transparent">
                      Todo-App
                    </h1>
                  </Link>

                  {/* Navigation */}
                  <nav className="flex items-center space-x-4">
                    <Link
                      href="/"
                      className="text-sm font-medium text-muted-foreground transition-colors hover:text-foreground"
                    >
                      Home
                    </Link>
                    <Link
                      href="/dashboard"
                      className="text-sm font-medium text-muted-foreground transition-colors hover:text-foreground"
                    >
                      Dashboard
                    </Link>
                    <ThemeToggle />
                  </nav>
                </div>
              </div>
            </header>

            {/* Main Content */}
            <main className="flex-1">
              {children}
            </main>
          </div>
        </ThemeProvider>
      </body>
    </html>
  );
}
