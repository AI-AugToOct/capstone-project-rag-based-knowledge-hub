"use client"

import { LayoutGrid, Sparkles, FileText, Handshake, Search, Filter } from "lucide-react"
import Image from "next/image"
import Link from "next/link"
import { useState } from "react"
import { motion } from "framer-motion"

interface Document {
  id: string
  name: string
  owner: string
  date: string
  size: string
  type: "pdf" | "doc" | "xls"
  department?: string
}

const sampleDocuments: Document[] = [
  {
    id: "1",
    name: "Remote Work Policy",
    owner: "Ahmed Ali",
    date: "Apr 21",
    size: "420 KB",
    type: "pdf",
    department: "HR",
  },
  {
    id: "2",
    name: "Project Plan - Marketing",
    owner: "Sarah Khan",
    date: "Apr 25",
    size: "50 KB",
    type: "pdf",
    department: "Marketing",
  },
  {
    id: "3",
    name: "Annual Performance Report",
    owner: "Feb Klahh",
    date: "Feb 3",
    size: "12 MB",
    type: "pdf",
    department: "HR",
  },
  {
    id: "4",
    name: "Training Materials",
    owner: "Ali Algahfani",
    date: "Jan 22",
    size: "20 KB",
    type: "pdf",
    department: "Training",
  },
  {
    id: "5",
    name: "Client Contracts",
    owner: "Ahmed Alim",
    date: "Jan 14",
    size: "350 KB",
    type: "pdf",
    department: "Legal",
  },
  {
    id: "6",
    name: "Budget Report Q1",
    owner: "Omar Saad",
    date: "Mar 15",
    size: "2.5 MB",
    type: "pdf",
    department: "Finance",
  },
  {
    id: "7",
    name: "Employee Handbook",
    owner: "Sarah Khan",
    date: "Feb 28",
    size: "1.8 MB",
    type: "pdf",
    department: "HR",
  },
]

const getIconColor = (index: number) => {
  const colors = ["bg-red-500", "bg-purple-500", "bg-teal-500", "bg-blue-500", "bg-pink-500"]
  return colors[index % colors.length]
}

export function DocumentsSection() {
  const [activeNav, setActiveNav] = useState("Documents")
  const [searchQuery, setSearchQuery] = useState("")
  const [filterType, setFilterType] = useState("All")
  const [sortBy, setSortBy] = useState("date")

  const navItems = [
    { name: "Home", icon: LayoutGrid, href: "/home" },
    { name: "Chatbot", icon: Sparkles, href: "/chatbot" },
    { name: "Documents", icon: FileText, href: "/documents" },
    { name: "HandOvers", icon: Handshake, href: "/handovers" },
  ]

  const filteredDocuments = sampleDocuments.filter((doc) => doc.name.toLowerCase().includes(searchQuery.toLowerCase()))

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
          {/* Header with Search and Filters */}
          <div className="mb-8 rounded-2xl bg-white p-6 shadow-sm">
            <div className="mb-6 flex items-center gap-4">
              <div className="relative flex-1">
                <Search className="absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search documents..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full rounded-xl border border-gray-200 py-3 pl-12 pr-4 focus:border-[#3E4DF9] focus:outline-none focus:ring-2 focus:ring-[#3E4DF9]/20"
                />
              </div>
              <button className="rounded-xl border border-gray-200 p-3 hover:bg-gray-50">
                <Filter className="h-5 w-5 text-gray-600" />
              </button>
            </div>

            <div className="flex items-center justify-between">
              <h2 className="text-xl font-semibold text-gray-800">All Documents</h2>
              <div className="flex items-center gap-4">
                <select
                  value={filterType}
                  onChange={(e) => setFilterType(e.target.value)}
                  className="rounded-lg border border-gray-200 px-4 py-2 text-sm focus:border-[#3E4DF9] focus:outline-none focus:ring-2 focus:ring-[#3E4DF9]/20"
                >
                  <option value="All">Type</option>
                  <option value="PDF">PDF</option>
                  <option value="DOC">DOC</option>
                </select>
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value)}
                  className="rounded-lg border border-gray-200 px-4 py-2 text-sm focus:border-[#3E4DF9] focus:outline-none focus:ring-2 focus:ring-[#3E4DF9]/20"
                >
                  <option value="date">Date</option>
                  <option value="name">Name</option>
                  <option value="size">Size</option>
                </select>
                <button className="rounded-lg border border-gray-200 px-4 py-2 text-sm hover:bg-gray-50">Sort</button>
              </div>
            </div>
          </div>

          {/* Documents Table */}
          <div className="rounded-2xl bg-white shadow-sm">
            <div className="overflow-hidden">
              {/* Table Header */}
              <div className="grid grid-cols-12 gap-4 border-b border-gray-200 bg-gray-50 px-6 py-4 text-sm font-semibold text-gray-700">
                <div className="col-span-5">File Name</div>
                <div className="col-span-3">Owner</div>
                <div className="col-span-2">Date</div>
                <div className="col-span-2 text-right">Size</div>
              </div>

              {/* Table Body */}
              <div className="divide-y divide-gray-100">
                {filteredDocuments.map((doc, index) => (
                  <motion.div
                    key={doc.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3, delay: index * 0.05 }}
                    className="grid grid-cols-12 gap-4 px-6 py-4 transition-all hover:bg-gray-50"
                  >
                    <div className="col-span-5 flex items-center gap-3">
                      <div className={`flex h-10 w-10 items-center justify-center rounded-lg ${getIconColor(index)}`}>
                        <FileText className="h-5 w-5 text-white" />
                      </div>
                      <span className="font-medium text-gray-900">{doc.name}</span>
                    </div>
                    <div className="col-span-3 flex items-center text-gray-600">{doc.owner}</div>
                    <div className="col-span-2 flex items-center text-gray-600">{doc.date}</div>
                    <div className="col-span-2 flex items-center justify-end text-gray-600">{doc.size}</div>
                  </motion.div>
                ))}
              </div>
            </div>

            {/* Empty State */}
            {filteredDocuments.length === 0 && (
              <div className="flex min-h-[300px] items-center justify-center">
                <div className="text-center">
                  <FileText className="mx-auto mb-4 h-16 w-16 text-gray-300" />
                  <p className="text-lg text-gray-400">No documents found</p>
                  <p className="mt-2 text-sm text-gray-400">Try adjusting your search or filters</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}
