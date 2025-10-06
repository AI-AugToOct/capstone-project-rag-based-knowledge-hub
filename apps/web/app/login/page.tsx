"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { Mail, Lock } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { supabase } from "@/lib/supabase"

export default function LoginPage() {
  const router = useRouter()
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")
    setLoading(true)

    try {
      // DEV MODE: Bypass Supabase Auth and use pre-generated JWT tokens
      if (password === "dev") {
        console.log('[DEV LOGIN] Dev mode activated');

        // Map of test emails to their JWT tokens
        const testTokens: Record<string, string> = {
          "test@company.com": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1NTBlODQwMC1lMjliLTQxZDQtYTcxNi00NDY2NTU0NDAwMDAiLCJyb2xlIjoiYXV0aGVudGljYXRlZCIsImF1ZCI6ImF1dGhlbnRpY2F0ZWQiLCJpYXQiOjE3NTk3Njc5MzYsImV4cCI6MTc5MTMwMzkzNn0.8vC4cYpNNBLrf77R6bQC4TxMP5mBl8LLzt9bhQwx4mc",
          "sarah.chen@company.com": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2NjBlODQwMC1lMjliLTQxZDQtYTcxNi00NDY2NTU0NDAwMDEiLCJyb2xlIjoiYXV0aGVudGljYXRlZCIsImF1ZCI6ImF1dGhlbnRpY2F0ZWQiLCJpYXQiOjE3NTk3Njc5NDYsImV4cCI6MTc5MTMwMzk0Nn0.wpuG1XWu8ALVP9Dt50jv5dXkIdtexKiHnBxGqpvwgSw"
        }

        const token = testTokens[email.toLowerCase()]
        if (token) {
          console.log('[DEV LOGIN] Token found for:', email);

          // Set JWT token in separate dev key (won't be cleared by Supabase)
          console.log('[DEV LOGIN] Setting dev-auth-token in localStorage');
          localStorage.setItem('dev-auth-token', token);

          // Verify it was set
          const verify = localStorage.getItem('dev-auth-token');
          console.log('[DEV LOGIN] Token stored successfully:', !!verify);

          console.log('[DEV LOGIN] Redirecting to home...');
          router.push("/")
          return
        } else {
          console.log('[DEV LOGIN] Email not found:', email);
          setError("Email not found in test users. Use test@company.com or sarah.chen@company.com")
          setLoading(false)
          return
        }
      }

      // PRODUCTION: Use real Supabase Auth
      const { data, error: authError } = await supabase.auth.signInWithPassword({
        email,
        password,
      })

      if (authError) {
        setError(authError.message)
        return
      }

      if (data.session) {
        // Successfully logged in, redirect to home
        router.push("/")
      }
    } catch (err: any) {
      setError(err.message || "Login failed. Please try again.")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="bg-white rounded-lg shadow-md p-8">
          {/* Logo and Title */}
          <div className="text-center mb-8">
            <div className="w-12 h-12 bg-blue-600 rounded-lg mx-auto mb-4 flex items-center justify-center">
              <span className="text-white font-bold text-xl">K</span>
            </div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">KnowledgeHub</h1>
            <h2 className="text-xl font-semibold text-gray-700">Welcome Back</h2>
          </div>

          {/* Error Message */}
          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-sm text-red-600">{error}</p>
            </div>
          )}

          {/* Login Form */}
          <form onSubmit={handleLogin} className="space-y-5">
            {/* Email Field */}
            <div className="space-y-2">
              <Label htmlFor="email" className="text-sm font-medium text-gray-700">
                Email Address
              </Label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
                <Input
                  id="email"
                  type="email"
                  placeholder="you@company.com"
                  className="pl-10 h-11"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  disabled={loading}
                />
              </div>
            </div>

            {/* Password Field */}
            <div className="space-y-2">
              <Label htmlFor="password" className="text-sm font-medium text-gray-700">
                Password
              </Label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
                <Input
                  id="password"
                  type="password"
                  placeholder="Enter your password"
                  className="pl-10 h-11"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  disabled={loading}
                />
              </div>
            </div>

            {/* Forgot Password Link */}
            <div className="flex justify-end">
              <Link href="#" className="text-sm text-blue-600 hover:text-blue-700 font-medium">
                Forgot Password?
              </Link>
            </div>

            {/* Sign In Button */}
            <Button
              type="submit"
              className="w-full h-11 bg-blue-600 hover:bg-blue-700 text-white font-medium"
              disabled={loading}
            >
              {loading ? "Signing in..." : "Sign In"}
            </Button>

            {/* Employee Notice */}
            <div className="text-center text-sm text-gray-500">
              Employee access only. Contact IT if you need help.
            </div>
          </form>

          {/* Dev/Testing Note */}
          {process.env.NODE_ENV === "development" && (
            <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <p className="text-xs font-semibold text-blue-800 mb-2">🔧 Dev Mode Login</p>
              <p className="text-xs text-blue-700 mb-2">
                Use password <code className="bg-blue-100 px-1 py-0.5 rounded">dev</code> with any test email:
              </p>
              <ul className="text-xs text-blue-700 space-y-1">
                <li>• test@company.com (Regular Employee)</li>
                <li>• sarah.chen@company.com (Manager)</li>
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
