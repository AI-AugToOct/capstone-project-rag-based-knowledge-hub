"use client"

import { LayoutGrid, Sparkles, FileText, Handshake, Search, Filter, ArrowUpRight, FileIcon } from "lucide-react"
import Image from "next/image"
import Link from "next/link"
import { useState } from "react"
import { motion } from "framer-motion"

interface Handover {
  id: string
  projectName: string
  personName: string
  personRole: string
  personAvatar: string
  date: string
  status: "Pending" | "Completed"
  files: { name: string; icon: string }[]
}

export function HandoversSection() {
  const [activeNav, setActiveNav] = useState("HandOvers")
  const [searchQuery, setSearchQuery] = useState("")

  const navItems = [
    { name: "Home", icon: LayoutGrid, href: "/home" },
    { name: "Chatbot", icon: Sparkles, href: "/chatbot" },
    { name: "Documents", icon: FileText, href: "/documents" },
    { name: "HandOvers", icon: Handshake, href: "/handovers" },
  ]

  const receivedHandovers: Handover[] = [
    {
      id: "1",
      projectName: "New Website Redesign",
      personName: "Sarah Khan",
      personRole: "Marketing Manager",
      personAvatar: "/professional-avatar.png",
      date: "1 hour ago",
      status: "Pending",
      files: [
        { name: "Project_Brief.pdf", icon: "pdf" },
        { name: "Design_Timeline.pdf", icon: "pdf" },
      ],
    },
    {
      id: "2",
      projectName: "Mobile App Development",
      personName: "Ahmed Ali",
      personRole: "Product Manager",
      personAvatar: "/professional-avatar.png",
      date: "3 hours ago",
      status: "Completed",
      files: [
        { name: "Requirements.docx", icon: "doc" },
        { name: "Wireframes.pdf", icon: "pdf" },
      ],
    },
  ]

  const sentHandovers: Handover[] = [
    {
      id: "3",
      projectName: "System Migration Plan",
      personName: "Omar Amari",
      personRole: "IT Manager",
      personAvatar: "/professional-avatar.png",
      date: "2 hours ago",
      status: "Pending",
      files: [
        { name: "Migration_Plan.docx", icon: "doc" },
        { name: "Timeline.pdf", icon: "pdf" },
      ],
    },
    {
      id: "4",
      projectName: "Security Audit Report",
      personName: "Fatima Hassan",
      personRole: "Security Lead",
      personAvatar: "/professional-avatar.png",
      date: "5 hours ago",
      status: "Completed",
      files: [
        { name: "Audit_Report.pdf", icon: "pdf" },
        { name: "Recommendations.docx", icon: "doc" },
      ],
    },
  ]

  const cardVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: (i: number) => ({
      opacity: 1,
      y: 0,
      transition: {
        delay: i * 0.1,
        duration: 0.5,
        ease: "easeOut",
      },
    }),
  }

  const HandoverCard = ({ handover, index }: { handover: Handover; index: number }) => (
    <motion.div
      custom={index}
      initial="hidden"
      animate="visible"
      variants={cardVariants}
      whileHover={{ y: -4, transition: { duration: 0.2 } }}
      className="group rounded-2xl bg-white p-6 shadow-sm transition-shadow hover:shadow-lg"
    >
      {/* Header with person info */}
      <div className="mb-4 flex items-start justify-between">
        <div className="flex items-center gap-3">
          <div className="relative h-12 w-12 overflow-hidden rounded-full bg-gray-200">
            <Image
              src={handover.personAvatar || "/placeholder.svg"}
              alt={handover.personName}
              fill
              className="object-cover"
            />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900">{handover.personName}</h3>
            <p className="text-sm text-gray-500">{handover.personRole}</p>
          </div>
        </div>
        <ArrowUpRight className="h-5 w-5 text-[#3E4DF9] opacity-0 transition-opacity group-hover:opacity-100" />
      </div>

      {/* Project name */}
      <h4 className="mb-2 text-xl font-bold text-gray-900">{handover.projectName}</h4>

      {/* Date and status */}
      <div className="mb-4 flex items-center gap-3">
        <span className="text-sm text-gray-500">{handover.date}</span>
        <span
          className={`rounded-full px-3 py-1 text-xs font-medium ${
            handover.status === "Completed" ? "bg-green-100 text-green-700" : "bg-yellow-100 text-yellow-700"
          }`}
        >
          {handover.status}
        </span>
      </div>

      {/* Files */}
      <div className="space-y-2">
        {handover.files.map((file, idx) => (
          <div
            key={idx}
            className="flex items-center gap-2 rounded-lg bg-[#3E4DF9]/5 p-3 transition-colors hover:bg-[#3E4DF9]/10"
          >
            <FileIcon className="h-5 w-5 text-[#3E4DF9]" />
            <span className="flex-1 text-sm text-gray-700">{file.name}</span>
            <ArrowUpRight className="h-4 w-4 text-[#3E4DF9]" />
          </div>
        ))}
      </div>
    </motion.div>
  )

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
          {/* Header with search and filter */}
          <div className="mb-8 flex items-center justify-between">
            <div className="flex flex-1 items-center gap-4">
              <div className="relative flex-1 max-w-xl">
                <Search className="absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search handovers..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full rounded-xl border border-gray-200 py-3 pl-12 pr-4 text-gray-900 placeholder-gray-400 focus:border-[#3E4DF9] focus:outline-none focus:ring-2 focus:ring-[#3E4DF9]/20"
                />
              </div>
              <button className="rounded-xl border border-gray-200 bg-white p-3 text-gray-600 transition-colors hover:bg-gray-50">
                <Filter className="h-5 w-5" />
              </button>
            </div>
            <div className="ml-4 flex items-center gap-3">
              <div className="relative h-10 w-10 overflow-hidden rounded-full bg-gray-200">
                <Image src="/professional-avatar.png" alt="User" fill className="object-cover" />
              </div>
            </div>
          </div>

          {/* Page title with filter/sort options */}
          <div className="mb-6 flex items-center justify-between">
            <h1 className="text-4xl font-bold text-gray-900">Handover</h1>
            <div className="flex items-center gap-4 text-sm text-gray-600">
              <button className="font-medium hover:text-[#3E4DF9]">Filter</button>
              <button className="font-medium hover:text-[#3E4DF9]">Sort</button>
              <button className="rounded-lg border border-gray-200 p-2 hover:bg-gray-50">
                <LayoutGrid className="h-4 w-4" />
              </button>
            </div>
          </div>

          {/* Two-column layout for Received and Sent */}
          <div className="grid gap-8 md:grid-cols-2">
            {/* Received Handovers */}
            <div>
              <h2 className="mb-4 text-2xl font-bold text-gray-900">Received</h2>
              <div className="space-y-4">
                {receivedHandovers.map((handover, index) => (
                  <HandoverCard key={handover.id} handover={handover} index={index} />
                ))}
              </div>
            </div>

            {/* Sent Handovers */}
            <div>
              <h2 className="mb-4 text-2xl font-bold text-gray-900">Sent</h2>
              <div className="space-y-4">
                {sentHandovers.map((handover, index) => (
                  <HandoverCard key={handover.id} handover={handover} index={index + receivedHandovers.length} />
                ))}
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
