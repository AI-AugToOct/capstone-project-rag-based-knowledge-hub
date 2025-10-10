"use client"

import type React from "react"

import { useState } from "react"
import { X, AlertCircle, Copy, Check } from "lucide-react"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { useRouter } from "next/navigation"

// DEV MODE: Test credentials from seed data
const DEV_CREDENTIALS = {
  employee: {
    email: "employee@company.com",
    password: "dev",
    token: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1NTBlODQwMC1lMjliLTQxZDQtYTcxNi00NDY2NTU0NDAwMDAiLCJyb2xlIjoiYXV0aGVudGljYXRlZCIsImF1ZCI6ImF1dGhlbnRpY2F0ZWQiLCJpYXQiOjE3NTk3OTgyODUsImV4cCI6MTc5MTMzNDI4NX0.8z3c9MoZDQuG0fULmD_GzlIP3qBIqli8ug-sbWgvRYI",
    name: "John Employee"
  },
  manager: {
    email: "manager@company.com",
    password: "dev",
    token: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2NjBlODQwMC1lMjliLTQxZDQtYTcxNi00NDY2NTU0NDAwMDEiLCJyb2xlIjoiYXV0aGVudGljYXRlZCIsImF1ZCI6ImF1dGhlbnRpY2F0ZWQiLCJpYXQiOjE3NTk3OTgzNjUsImV4cCI6MTc5MTMzNDM2NX0.Wd-9HrmWDV1nAN86etsoSzK7T0f19uXfzr-SKL4F7Qw",
    name: "Sarah Manager"
  }
}

export function LoginForm() {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState("")
  const [showCredentials, setShowCredentials] = useState(false)
  const [copiedField, setCopiedField] = useState<string | null>(null)
  const router = useRouter()

  const handleCopy = (text: string, field: string) => {
    navigator.clipboard.writeText(text)
    setCopiedField(field)
    setTimeout(() => setCopiedField(null), 2000)
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setError("")

    console.log("[Login] Attempting login:", email)

    // Check employee credentials
    if (email === DEV_CREDENTIALS.employee.email && password === DEV_CREDENTIALS.employee.password) {
      console.log("[Login] Employee login successful")
      localStorage.setItem('dev-auth-token', DEV_CREDENTIALS.employee.token)
      localStorage.setItem('user-name', DEV_CREDENTIALS.employee.name)
      router.push("/home")
      return
    }

    // Check manager credentials
    if (email === DEV_CREDENTIALS.manager.email && password === DEV_CREDENTIALS.manager.password) {
      console.log("[Login] Manager login successful")
      localStorage.setItem('dev-auth-token', DEV_CREDENTIALS.manager.token)
      localStorage.setItem('user-name', DEV_CREDENTIALS.manager.name)
      router.push("/manager")
      return
    }

    // Invalid credentials
    console.log("[Login] Invalid credentials")
    setError("Invalid email or password")
  }

  return (
    <div className="relative z-10 w-full max-w-2xl rounded-3xl bg-white p-12 shadow-2xl">
      {/* Dev Credentials Info Button */}
      <div className="absolute left-8 top-8">
        <div className="relative">
          <AlertCircle
            className="h-6 w-6 text-[#3E4DF9] cursor-pointer transition-colors hover:text-[#3240D9]"
            onClick={() => setShowCredentials(!showCredentials)}
          />

          {/* Tooltip */}
          {showCredentials && (
            <>
              {/* Backdrop to close on click outside */}
              <div
                className="fixed inset-0 z-40"
                onClick={() => setShowCredentials(false)}
              />
              <div className="absolute left-0 top-8 w-72 rounded-lg bg-gray-900 p-4 text-white shadow-xl z-50">
              <p className="mb-3 text-xs font-semibold text-gray-300">DEV CREDENTIALS</p>

              {/* Employee */}
              <div className="mb-3 space-y-1">
                <p className="text-xs font-semibold text-[#8B92FF]">Employee:</p>
                <div className="flex items-center justify-between">
                  <span className="text-sm font-mono">employee@company.com</span>
                  <button
                    onClick={() => handleCopy("employee@company.com", "employee-email")}
                    className="ml-2 rounded p-1 hover:bg-gray-800 transition-colors"
                  >
                    {copiedField === "employee-email" ? (
                      <Check className="h-3 w-3 text-green-400" />
                    ) : (
                      <Copy className="h-3 w-3 text-gray-400" />
                    )}
                  </button>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm font-mono">dev</span>
                  <button
                    onClick={() => handleCopy("dev", "employee-pass")}
                    className="ml-2 rounded p-1 hover:bg-gray-800 transition-colors"
                  >
                    {copiedField === "employee-pass" ? (
                      <Check className="h-3 w-3 text-green-400" />
                    ) : (
                      <Copy className="h-3 w-3 text-gray-400" />
                    )}
                  </button>
                </div>
              </div>

              {/* Manager */}
              <div className="space-y-1">
                <p className="text-xs font-semibold text-[#8B92FF]">Manager:</p>
                <div className="flex items-center justify-between">
                  <span className="text-sm font-mono">manager@company.com</span>
                  <button
                    onClick={() => handleCopy("manager@company.com", "manager-email")}
                    className="ml-2 rounded p-1 hover:bg-gray-800 transition-colors"
                  >
                    {copiedField === "manager-email" ? (
                      <Check className="h-3 w-3 text-green-400" />
                    ) : (
                      <Copy className="h-3 w-3 text-gray-400" />
                    )}
                  </button>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm font-mono">dev</span>
                  <button
                    onClick={() => handleCopy("dev", "manager-pass")}
                    className="ml-2 rounded p-1 hover:bg-gray-800 transition-colors"
                  >
                    {copiedField === "manager-pass" ? (
                      <Check className="h-3 w-3 text-green-400" />
                    ) : (
                      <Copy className="h-3 w-3 text-gray-400" />
                    )}
                  </button>
                </div>
              </div>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Close button */}
      <button className="absolute right-8 top-8 text-gray-400 transition-colors hover:text-gray-600" aria-label="Close">
        <X className="h-6 w-6" />
      </button>

      <div className="mx-auto max-w-md">
        <h1 className="mb-12 text-center text-5xl font-bold text-[#3E4DF9]">Good Morning!</h1>

        <form onSubmit={handleSubmit} className="space-y-6">
          <Input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="h-14 rounded-xl border-gray-200 bg-white px-6 text-base placeholder:text-gray-400"
            required
          />

          <Input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="h-14 rounded-xl border-gray-200 bg-white px-6 text-base placeholder:text-gray-400"
            required
          />

          {error && (
            <div className="rounded-lg bg-red-50 p-3 text-sm text-red-600">
              {error}
            </div>
          )}

          <div className="pt-6">
            <Button
              type="submit"
              className="h-14 w-full rounded-full bg-[#3E4DF9] text-lg font-medium text-white transition-all hover:bg-[#3240D9] hover:shadow-lg"
            >
              Log in
            </Button>
          </div>
        </form>
      </div>
    </div>
  )
}
