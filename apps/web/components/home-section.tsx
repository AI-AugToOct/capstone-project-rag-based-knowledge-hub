"use client"

import { LayoutGrid, Sparkles, FileText, Handshake } from "lucide-react"
import Image from "next/image"
import Link from "next/link"
import { useState, useEffect } from "react"
import { getNotionTasks } from "@/lib/api"

export function HomeSection() {
  const [activeNav, setActiveNav] = useState("Home")
  const [tasks, setTasks] = useState<Array<{
    name: string
    status: string
    start: string
    due: string
    milestone: string
  }>>([])
  const [loading, setLoading] = useState(true)

  const navItems = [
    { name: "Home", icon: LayoutGrid, href: "/home" },
    { name: "Chatbot", icon: Sparkles, href: "/chatbot" },
    { name: "Documents", icon: FileText, href: "/documents" },
    { name: "HandOvers", icon: Handshake, href: "/handovers" },
  ]

  useEffect(() => {
    async function fetchTasks() {
      try {
        const data = await getNotionTasks()
        setTasks(data)
      } catch (error) {
        console.error("Failed to fetch tasks:", error)
      } finally {
        setLoading(false)
      }
    }
    fetchTasks()
  }, [])

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

          {/* Tasks Table */}
          <div className="rounded-2xl bg-white p-8 shadow-sm">
            {loading ? (
              <div className="flex min-h-[400px] items-center justify-center">
                <div className="text-center">
                  <div className="mb-4 h-8 w-8 animate-spin rounded-full border-4 border-[#3E4DF9] border-t-transparent mx-auto" />
                  <p className="text-gray-500">Loading tasks...</p>
                </div>
              </div>
            ) : tasks.length === 0 ? (
              <div className="flex min-h-[400px] items-center justify-center text-gray-400">
                <div className="text-center">
                  <LayoutGrid className="mx-auto mb-4 h-16 w-16 text-gray-300" />
                  <p className="text-lg">No tasks found</p>
                </div>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b-2 border-gray-200">
                      <th className="pb-4 text-left font-semibold text-gray-700">Task Name</th>
                      <th className="pb-4 text-left font-semibold text-gray-700">Status</th>
                      <th className="pb-4 text-left font-semibold text-gray-700">Start Date</th>
                      <th className="pb-4 text-left font-semibold text-gray-700">Due Date</th>
                      <th className="pb-4 text-left font-semibold text-gray-700">Milestone</th>
                    </tr>
                  </thead>
                  <tbody>
                    {tasks.map((task, index) => (
                      <tr key={index} className="border-b border-gray-100 hover:bg-gray-50 transition-colors">
                        <td className="py-4 text-gray-900">{task.name}</td>
                        <td className="py-4">
                          <span className={`inline-block rounded-full px-3 py-1 text-sm font-medium ${
                            task.status === "Completed" ? "bg-green-100 text-green-800" :
                            task.status === "In Progress" ? "bg-blue-100 text-blue-800" :
                            "bg-gray-100 text-gray-800"
                          }`}>
                            {task.status}
                          </span>
                        </td>
                        <td className="py-4 text-gray-600">{task.start}</td>
                        <td className="py-4 text-gray-600">{task.due}</td>
                        <td className="py-4 text-gray-700">{task.milestone}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}
