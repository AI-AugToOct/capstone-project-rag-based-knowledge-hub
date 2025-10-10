"use client"

import { Upload, FileText, Download } from "lucide-react"
import Image from "next/image"
import Link from "next/link"
import { useState, useEffect } from "react"
import { listDocuments } from "@/lib/api"

export default function ManagerDocumentsPage() {
  const [activeNav, setActiveNav] = useState("Documents")
  const [documents, setDocuments] = useState<Array<{
    doc_id: number
    title: string
    visibility: string
    project_id: string | null
    created_at: string | null
    uri: string | null
  }>>([])
  const [loading, setLoading] = useState(true)

  const navItems = [
    { name: "Uploads", icon: Upload, href: "/manager" },
    { name: "Documents", icon: FileText, href: "/manager/documents" },
  ]

  useEffect(() => {
    async function fetchDocs() {
      try {
        const data = await listDocuments()
        setDocuments(data)
      } catch (error) {
        console.error("Failed to fetch documents:", error)
      } finally {
        setLoading(false)
      }
    }
    fetchDocs()
  }, [])

  return (
    <div className="flex min-h-screen bg-gray-50">
      {/* Manager Sidebar */}
      <aside className="relative w-64 bg-gradient-to-b from-[#5B62FF] via-[#4651F9] to-[#3E4DF9] text-white">
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
          <div className="mb-12 flex items-center gap-3">
            <div className="relative h-12 w-12 overflow-hidden rounded-full bg-white">
              <Image src="/professional-avatar.png" alt="Manager" fill className="object-cover" />
            </div>
            <div>
              <h2 className="text-lg font-bold">Omar Saad</h2>
              <p className="text-sm text-white/80">AI Department Manager</p>
            </div>
          </div>

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
          <h1 className="mb-8 text-4xl font-bold text-[#3E4DF9]">Documents</h1>

          <div className="rounded-2xl bg-white p-8 shadow-sm">
            {loading ? (
              <div className="flex min-h-[400px] items-center justify-center">
                <div className="text-center">
                  <div className="mb-4 h-8 w-8 animate-spin rounded-full border-4 border-[#3E4DF9] border-t-transparent mx-auto" />
                  <p className="text-gray-500">Loading documents...</p>
                </div>
              </div>
            ) : documents.length === 0 ? (
              <div className="flex min-h-[400px] items-center justify-center text-gray-400">
                <div className="text-center">
                  <FileText className="mx-auto mb-4 h-16 w-16 text-gray-300" />
                  <p className="text-lg">No documents found</p>
                </div>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b-2 border-gray-200">
                      <th className="pb-4 text-left font-semibold text-gray-700">Title</th>
                      <th className="pb-4 text-left font-semibold text-gray-700">Project</th>
                      <th className="pb-4 text-left font-semibold text-gray-700">Visibility</th>
                      <th className="pb-4 text-left font-semibold text-gray-700">Created</th>
                      <th className="pb-4 text-left font-semibold text-gray-700">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {documents.map((doc) => (
                      <tr key={doc.doc_id} className="border-b border-gray-100 hover:bg-gray-50 transition-colors">
                        <td className="py-4 text-gray-900">{doc.title}</td>
                        <td className="py-4 text-gray-600">{doc.project_id || "General"}</td>
                        <td className="py-4">
                          <span className={`inline-block rounded-full px-3 py-1 text-sm font-medium ${
                            doc.visibility === "Public" ? "bg-green-100 text-green-800" : "bg-blue-100 text-blue-800"
                          }`}>
                            {doc.visibility}
                          </span>
                        </td>
                        <td className="py-4 text-gray-600">
                          {doc.created_at ? new Date(doc.created_at).toLocaleDateString() : "N/A"}
                        </td>
                        <td className="py-4">
                          {doc.uri && doc.uri.startsWith('http') && (
                            <a
                              href={doc.uri}
                              download
                              target="_blank"
                              rel="noopener noreferrer"
                              className="inline-flex items-center gap-2 rounded-lg bg-[#3E4DF9] px-4 py-2 text-sm font-medium text-white transition-all hover:bg-[#3240D9] hover:shadow-lg"
                            >
                              <Download className="h-4 w-4" />
                              Download
                            </a>
                          )}
                        </td>
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
