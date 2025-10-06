"use client"

import type React from "react"

import { useState } from "react"
import { X } from "lucide-react"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { useRouter } from "next/navigation"

export function LoginForm() {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const router = useRouter()

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    console.log("[v0] Login submitted:", { email, password })

    if (email === "manager@aweid.com" && password === "Admin123") {
      console.log("[v0] Manager login detected, redirecting to manager dashboard")
      router.push("/manager")
    } else {
      console.log("[v0] Regular user login, redirecting to home")
      router.push("/home")
    }
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
