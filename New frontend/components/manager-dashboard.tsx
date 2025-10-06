"use client"

import type React from "react"

import { Upload, FileText } from "lucide-react"
import Image from "next/image"
import Link from "next/link"
import { useState } from "react"

export function ManagerDashboard() {
  const [activeNav, setActiveNav] = useState("Uploads")

  const navItems = [
    { name: "Uploads", icon: Upload, href: "/manager" },
    { name: "Documents", icon: FileText, href: "/manager/documents" },
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
              <Image src="/professional-avatar.png" alt="Manager" fill className="object-cover" />
            </div>
            <div>
              <h2 className="text-lg font-bold">Omar Saad</h2>
              <p className="text-sm text-white/80">AI Department Manager</p>
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

          {/* Upload Section */}
          <UploadSection />
        </div>
      </main>
    </div>
  )
}

function UploadSection() {
  const [visibility, setVisibility] = useState<"public" | "private">("public")
  const [selectedProject, setSelectedProject] = useState("")
  const [uploadedFiles, setUploadedFiles] = useState([
    { name: "Leave.Policy.docx", type: "DOC", color: "bg-blue-500" },
    { name: "Rich.fent Fulshm", type: "PDF", color: "bg-red-500" },
    { name: "Employee Handbook.pdf", type: "FIFF", color: "bg-orange-500" },
  ])

  const projects = ["Marketing Campaign", "Website Redesign", "Mobile App Development", "HR System Upgrade"]

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (files && files.length > 0) {
      const newFiles = Array.from(files).map((file) => ({
        name: file.name,
        type: file.name.split(".").pop()?.toUpperCase() || "FILE",
        color: "bg-purple-500",
      }))
      setUploadedFiles([...uploadedFiles, ...newFiles])
    }
  }

  return (
    <div className="space-y-8">
      {/* Upload Document Card */}
      <div className="rounded-2xl bg-white p-8 shadow-sm">
        <h2 className="mb-6 text-2xl font-bold">Upload Document</h2>

        {/* Visibility Selection */}
        <div className="mb-6 flex gap-4">
          <button
            onClick={() => setVisibility("public")}
            className={`rounded-lg px-6 py-2 font-medium transition-all ${
              visibility === "public"
                ? "bg-[#3E4DF9] text-white shadow-md"
                : "bg-gray-100 text-gray-600 hover:bg-gray-200"
            }`}
          >
            Public
          </button>
          <button
            onClick={() => setVisibility("private")}
            className={`rounded-lg px-6 py-2 font-medium transition-all ${
              visibility === "private"
                ? "bg-[#3E4DF9] text-white shadow-md"
                : "bg-gray-100 text-gray-600 hover:bg-gray-200"
            }`}
          >
            Private
          </button>
        </div>

        {/* Project Selection (only for Private) */}
        {visibility === "private" && (
          <div className="mb-6">
            <label className="mb-2 block text-sm font-medium text-gray-700">Select Project</label>
            <select
              value={selectedProject}
              onChange={(e) => setSelectedProject(e.target.value)}
              className="w-full rounded-lg border border-gray-200 px-4 py-3 focus:border-[#3E4DF9] focus:outline-none focus:ring-2 focus:ring-[#3E4DF9]/20"
            >
              <option value="">Choose a project...</option>
              {projects.map((project) => (
                <option key={project} value={project}>
                  {project}
                </option>
              ))}
            </select>
          </div>
        )}

        {/* Upload Area */}
        <div className="relative rounded-2xl border-2 border-dashed border-gray-300 bg-gray-50 p-12 text-center transition-colors hover:border-[#3E4DF9] hover:bg-[#3E4DF9]/5">
          <input
            type="file"
            multiple
            onChange={handleFileUpload}
            className="absolute inset-0 h-full w-full cursor-pointer opacity-0"
            accept=".pdf,.doc,.docx"
          />
          <Upload className="mx-auto mb-4 h-12 w-12 text-[#3E4DF9]" />
          <p className="mb-4 text-lg text-gray-600">Drag and drop file here</p>
          <button className="rounded-lg bg-[#3E4DF9] px-8 py-3 font-medium text-white transition-all hover:bg-[#3240D9] hover:shadow-lg">
            Browse File
          </button>
        </div>
      </div>

      {/* Uploaded Files */}
      <div className="rounded-2xl bg-white p-8 shadow-sm">
        <h2 className="mb-6 text-2xl font-bold">Uploaded Files</h2>
        <div className="space-y-3">
          {uploadedFiles.map((file, index) => (
            <div
              key={index}
              className="flex items-center justify-between rounded-xl border border-gray-200 bg-white p-4 transition-all hover:border-[#3E4DF9] hover:shadow-md"
            >
              <div className="flex items-center gap-4">
                <div className={`flex h-12 w-12 items-center justify-center rounded-lg ${file.color} text-white`}>
                  <span className="text-xs font-bold">{file.type}</span>
                </div>
                <span className="font-medium text-gray-800">{file.name}</span>
              </div>
              <button className="text-gray-400 transition-colors hover:text-[#3E4DF9]">
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
