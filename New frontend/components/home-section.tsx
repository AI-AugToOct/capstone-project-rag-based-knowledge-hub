"use client"

import { LayoutGrid, Sparkles, FileText, Handshake } from "lucide-react"
import Image from "next/image"
import Link from "next/link"
import { useState } from "react"

export function HomeSection() {
  const [activeNav, setActiveNav] = useState("Home")

  const navItems = [
    { name: "Home", icon: LayoutGrid, href: "/home" },
    { name: "Chatbot", icon: Sparkles, href: "/chatbot" },
    { name: "Documents", icon: FileText, href: "/documents" },
    { name: "HandOvers", icon: Handshake, href: "/handovers" },
  ]

  return (
    <div className="flex min-h-screen bg-gray-50">
      {/* Sidebar */}
      <aside className="relative w-64 bg-gradient-to-b from-[#5B62FF] via-[#4651F9] to-[#3E4DF9] text-white">
        {/* Decorative wave on the right edge */}
        <div className="absolute right-0 top-0 h-full w-12 overflow-hidden">
          <svg
            viewBox="0 0 100 800"
            className="h-full w-full"
            preserveAspectRatio="none"
            style={{ transform: "translateX(50%)" }}
          >
            <path
              d="M0,0 Q30,100 0,200 T0,400 T0,600 T0,800 L100,800 L100,0 Z"
              fill="url(#sidebarGradient)"
              opacity="0.3"
            />
            <defs>
              <linearGradient id="sidebarGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#8B92FF" />
                <stop offset="100%" stopColor="#5B62FF" />
              </linearGradient>
            </defs>
          </svg>
        </div>

        <div className="relative z-10 flex h-full flex-col p-6">
          {/* Profile Section */}
          <div className="mb-12 flex items-center gap-3">
            <div className="relative h-12 w-12 overflow-hidden rounded-full bg-white">
              <Image src="/professional-avatar.png" alt="Omar Saad" fill className="object-cover" />
            </div>
            <div>
              <h2 className="text-lg font-bold">Omar Saad</h2>
              <p className="text-sm text-white/80">AI developer</p>
            </div>
          </div>

          {/* Navigation */}
          <nav className="space-y-2">
            {navItems.map((item) => {
              const Icon = item.icon
              const isActive = activeNav === item.name

              return (
                <Link
                  key={item.name}
                  href={item.href}
                  onClick={() => setActiveNav(item.name)}
                  className={`flex items-center gap-3 rounded-xl px-4 py-3 transition-all ${
                    isActive ? "bg-white text-[#3E4DF9] shadow-lg" : "text-white hover:bg-white/10"
                  }`}
                >
                  <Icon className="h-5 w-5" />
                  <span className="font-medium">{item.name}</span>
                </Link>
              )
            })}
          </nav>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 p-8">
        <div className="mx-auto max-w-7xl">
          <h1 className="mb-8 text-4xl font-bold text-[#3E4DF9]">Project Tasks Board</h1>

          {/* Empty content area for future Notion API integration */}
          <div className="rounded-2xl bg-white p-8 shadow-sm">
            <div className="flex min-h-[500px] items-center justify-center text-gray-400">
              <div className="text-center">
                <LayoutGrid className="mx-auto mb-4 h-16 w-16 text-gray-300" />
                <p className="text-lg">Tasks will be displayed here</p>
                <p className="mt-2 text-sm">Notion API integration coming soon</p>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
