"use client"

import type React from "react"

import { useState } from "react"
import { X } from "lucide-react"
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
  const router = useRouter()

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
      {/* Close button */}
      <button className="absolute left-8 top-8 text-gray-400 transition-colors hover:text-gray-600" aria-label="Close">
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

          <div className="mt-4 text-center text-sm text-gray-500">
            <p>Dev Credentials:</p>
            <p>employee@company.com / dev</p>
            <p>manager@company.com / dev</p>
          </div>
        </form>
      </div>
    </div>
  )
}
