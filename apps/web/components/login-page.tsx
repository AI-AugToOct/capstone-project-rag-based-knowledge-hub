"use client"

import Image from "next/image"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { useState } from "react"

interface LoginPageProps {
  onLogin: (email: string, password: string) => void
}

export default function LoginPage({ onLogin }: LoginPageProps) {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")

  const handleLogin = () => {
    onLogin(email, password)
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-white">
      <div className="flex flex-col md:flex-row w-full max-w-5xl items-center">
        {/* Left Side - Login Form */}
        <div className="flex-1 flex flex-col justify-center items-center px-8 py-12">
          <h1 className="text-3xl font-extrabold text-gray-900 mb-2">KnowledgeHub</h1>
          <h2 className="text-2xl font-medium text-gray-800 mb-10">Welcome</h2>

          <div className="w-full max-w-sm space-y-4">
            <Input
              type="email"
              placeholder="E-mail"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="h-12 border-gray-300 focus:ring-0 focus:border-gray-400"
            />
            <Input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="h-12 border-gray-300 focus:ring-0 focus:border-gray-400"
            />
            <Button
              type="button"
              onClick={handleLogin}
              className="w-full h-12 text-white text-lg font-medium rounded-full"
              style={{ backgroundColor: "#70CFDC" }}
            >
              Log In
            </Button>
          </div>
        </div>

        {/* Right Side - Character Image */}
        <div
          className="flex-1 flex justify-center items-center p-8"
          style={{ backgroundColor: "#70CFDC", borderRadius: "2rem" }}
        >
          <div className="overflow-hidden rounded-2xl" style={{ width: 400, height: 600 }}>
            <Image
              src="/Charachter.png"
              alt="Character"
              width={400}
              height={400}
              className="object-cover w-full h-full"
            />
          </div>
        </div>
      </div>
    </div>
  )
}
