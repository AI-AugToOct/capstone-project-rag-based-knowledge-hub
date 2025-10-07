"use client"

import type React from "react"

import { Upload, FileText, Download } from "lucide-react"
import Image from "next/image"
import Link from "next/link"
import { useState, useEffect } from "react"
import { uploadDocument, listDocuments } from "@/lib/api"

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
  const [visibility, setVisibility] = useState<"Public" | "Private">("Public")
  const [selectedProject, setSelectedProject] = useState("")
  const [uploading, setUploading] = useState(false)
  const [uploadStatus, setUploadStatus] = useState<string | null>(null)
  const [uploadedFiles, setUploadedFiles] = useState<Array<{
    doc_id: number
    title: string
    visibility: string
    project_id: string | null
    created_at: string | null
    uri: string | null
  }>>([])
  const [loadingDocs, setLoadingDocs] = useState(true)

  // Real projects from DB
  const projects = ["demo-project", "atlas-api", "phoenix-ui", "internal-tools"]

  // Fetch uploaded documents on mount
  useEffect(() => {
    async function fetchDocs() {
      try {
        const docs = await listDocuments()
        setUploadedFiles(docs)
      } catch (error) {
        console.error("Failed to fetch documents:", error)
      } finally {
        setLoadingDocs(false)
      }
    }
    fetchDocs()
  }, [])

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (!files || files.length === 0) return

    setUploading(true)
    setUploadStatus(null)

    try {
      // Upload first file (can extend to handle multiple)
      const file = files[0]

      // Validate project selection for private docs
      if (visibility === "Private" && !selectedProject) {
        setUploadStatus("Please select a project for private documents")
        setUploading(false)
        return
      }

      const result = await uploadDocument(
        file,
        visibility === "Private" ? selectedProject : undefined,
        visibility
      )

      setUploadStatus(`✅ Successfully uploaded "${result.title}" - ${result.chunks_created} chunks created!`)

      // Refresh documents list
      const docs = await listDocuments()
      setUploadedFiles(docs)

      // Reset form
      e.target.value = ""
    } catch (error: any) {
      setUploadStatus(`❌ Upload failed: ${error.message}`)
    } finally {
      setUploading(false)
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
            onClick={() => setVisibility("Public")}
            className={`rounded-lg px-6 py-2 font-medium transition-all ${
              visibility === "Public"
                ? "bg-[#3E4DF9] text-white shadow-md"
                : "bg-gray-100 text-gray-600 hover:bg-gray-200"
            }`}
          >
            Public
          </button>
          <button
            onClick={() => setVisibility("Private")}
            className={`rounded-lg px-6 py-2 font-medium transition-all ${
              visibility === "Private"
                ? "bg-[#3E4DF9] text-white shadow-md"
                : "bg-gray-100 text-gray-600 hover:bg-gray-200"
            }`}
          >
            Private
          </button>
        </div>

        {/* Project Selection (only for Private) */}
        {visibility === "Private" && (
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

        {/* Status Message */}
        {uploadStatus && (
          <div className={`mb-4 rounded-lg p-4 ${uploadStatus.startsWith('✅') ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'}`}>
            {uploadStatus}
          </div>
        )}

        {/* Upload Area */}
        <div className={`relative rounded-2xl border-2 border-dashed border-gray-300 bg-gray-50 p-12 text-center transition-colors ${uploading ? 'opacity-50 pointer-events-none' : 'hover:border-[#3E4DF9] hover:bg-[#3E4DF9]/5'}`}>
          <input
            type="file"
            onChange={handleFileUpload}
            className="absolute inset-0 h-full w-full cursor-pointer opacity-0"
            accept=".pdf,.doc,.docx"
            disabled={uploading}
          />
          {uploading ? (
            <>
              <div className="mb-4 h-12 w-12 animate-spin rounded-full border-4 border-[#3E4DF9] border-t-transparent mx-auto" />
              <p className="text-lg text-gray-600">Uploading and processing...</p>
            </>
          ) : (
            <>
              <Upload className="mx-auto mb-4 h-12 w-12 text-[#3E4DF9]" />
              <p className="mb-4 text-lg text-gray-600">Drag and drop file here</p>
              <button type="button" className="rounded-lg bg-[#3E4DF9] px-8 py-3 font-medium text-white transition-all hover:bg-[#3240D9] hover:shadow-lg">
                Browse File
              </button>
            </>
          )}
        </div>
      </div>

      {/* Uploaded Files */}
      <div className="rounded-2xl bg-white p-8 shadow-sm">
        <h2 className="mb-6 text-2xl font-bold">Uploaded Documents ({uploadedFiles.length})</h2>
        {loadingDocs ? (
          <div className="flex items-center justify-center py-12">
            <div className="h-8 w-8 animate-spin rounded-full border-4 border-[#3E4DF9] border-t-transparent" />
          </div>
        ) : uploadedFiles.length === 0 ? (
          <div className="py-12 text-center text-gray-400">
            <FileText className="mx-auto mb-4 h-16 w-16 text-gray-300" />
            <p>No documents uploaded yet</p>
          </div>
        ) : (
          <div className="space-y-3">
            {uploadedFiles.map((file) => {
              const ext = file.title.split('.').pop()?.toUpperCase() || 'FILE'
              const color = ext === 'PDF' ? 'bg-red-500' : ext === 'DOCX' || ext === 'DOC' ? 'bg-blue-500' : 'bg-purple-500'

              return (
                <div
                  key={file.doc_id}
                  className="flex items-center justify-between rounded-xl border border-gray-200 bg-white p-4 transition-all hover:border-[#3E4DF9] hover:shadow-md"
                >
                  <div className="flex items-center gap-4">
                    <div className={`flex h-12 w-12 items-center justify-center rounded-lg ${color} text-white`}>
                      <span className="text-xs font-bold">{ext}</span>
                    </div>
                    <div>
                      <p className="font-medium text-gray-800">{file.title}</p>
                      <p className="text-sm text-gray-500">
                        {file.project_id || 'General'} • {file.visibility}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="text-sm text-gray-500">
                      {file.created_at ? new Date(file.created_at).toLocaleDateString() : 'N/A'}
                    </div>
                    {file.uri && file.uri.startsWith('http') && (
                      <a
                        href={file.uri}
                        download
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-2 rounded-lg bg-[#3E4DF9] px-4 py-2 text-sm font-medium text-white transition-all hover:bg-[#3240D9] hover:shadow-lg"
                      >
                        <Download className="h-4 w-4" />
                        Download
                      </a>
                    )}
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}
