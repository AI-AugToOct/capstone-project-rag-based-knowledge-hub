"use client"

import { useEffect, useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { getAccessToken } from "@/lib/supabase"

interface Document {
  doc_id: number
  title: string
  visibility: string
  project_id?: string | null
  created_at?: string | null
}

export default function ManagerInterface() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [uploadStatus, setUploadStatus] = useState("")
  const [documents, setDocuments] = useState<Document[]>([])
  const [isUploading, setIsUploading] = useState(false)
  const [visibility, setVisibility] = useState<string>("Public")
  const [projectId, setProjectId] = useState<string>("")

  // Handle file selection
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setSelectedFile(e.target.files[0])
      setUploadStatus("") // Clear previous status
    }
  }

  // Handle file upload to backend
  const handleUpload = async () => {
    if (!selectedFile) {
      setUploadStatus("⚠️ Please select a file first.")
      return
    }

    setIsUploading(true)
    setUploadStatus("📤 Uploading and indexing...")

    try {
      // Get JWT token
      const token = await getAccessToken()
      if (!token) {
        setUploadStatus("⚠️ Please log in first.")
        setIsUploading(false)
        return
      }

      // Prepare form data
      const formData = new FormData()
      formData.append("file", selectedFile)
      formData.append("visibility", visibility)
      if (projectId.trim()) {
        formData.append("project_id", projectId.trim())
      }

      // Upload file
      const res = await fetch("http://127.0.0.1:8000/api/upload", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      })

      if (res.ok) {
        const data = await res.json()
        setUploadStatus(
          `✅ ${data.message}\n` +
          `📄 Document ID: ${data.doc_id}\n` +
          `📊 Chunks created: ${data.chunks_created}/${data.total_chunks}`
        )
        setSelectedFile(null)
        setProjectId("")
        fetchDocuments() // refresh list after upload
      } else {
        const error = await res.json().catch(() => ({ detail: "Upload failed" }))
        setUploadStatus(`❌ ${error.detail}`)
      }
    } catch (err: any) {
      console.error(err)
      setUploadStatus(`⚠️ Error: ${err.message}`)
    } finally {
      setIsUploading(false)
    }
  }

  // Fetch uploaded documents
  const fetchDocuments = async () => {
    try {
      // Get JWT token
      const token = await getAccessToken()
      if (!token) {
        console.log("Not logged in, skipping document fetch")
        return
      }

      const res = await fetch("http://127.0.0.1:8000/api/documents", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })

      if (res.ok) {
        const data = await res.json()
        if (Array.isArray(data)) {
          setDocuments(data)
        }
      } else {
        console.error("Failed to fetch documents:", res.status)
      }
    } catch (err) {
      console.error("Error fetching documents:", err)
    }
  }

  useEffect(() => {
    fetchDocuments()
  }, [])

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-6">Manager Interface - Upload Documents</h1>

      {/* Upload Section */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Upload a new file</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label htmlFor="file">File (PDF, DOCX, TXT, MD)</Label>
            <input
              id="file"
              type="file"
              onChange={handleFileChange}
              accept=".pdf,.docx,.txt,.md"
              disabled={isUploading}
              className="w-full mt-1"
            />
            {selectedFile && (
              <p className="text-xs text-muted-foreground mt-1">
                Selected: {selectedFile.name}
              </p>
            )}
          </div>

          <div>
            <Label htmlFor="visibility">Visibility</Label>
            <Select value={visibility} onValueChange={setVisibility} disabled={isUploading}>
              <SelectTrigger id="visibility" className="w-full">
                <SelectValue placeholder="Select visibility" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="Public">Public (all employees)</SelectItem>
                <SelectItem value="Private">Private (project members only)</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div>
            <Label htmlFor="project_id">Project ID (optional)</Label>
            <Input
              id="project_id"
              type="text"
              value={projectId}
              onChange={(e) => setProjectId(e.target.value)}
              placeholder="e.g., atlas-project"
              disabled={isUploading}
            />
            <p className="text-xs text-muted-foreground mt-1">
              Leave empty for general knowledge base
            </p>
          </div>

          <Button onClick={handleUpload} disabled={isUploading || !selectedFile} className="w-32">
            {isUploading ? "Uploading..." : "Upload"}
          </Button>

          {uploadStatus && (
            <p
              className={`text-sm whitespace-pre-wrap ${
                uploadStatus.startsWith("✅")
                  ? "text-green-600"
                  : uploadStatus.startsWith("❌")
                  ? "text-red-600"
                  : "text-yellow-600"
              }`}
            >
              {uploadStatus}
            </p>
          )}
        </CardContent>
      </Card>

      {/* Uploaded Documents */}
      <Card>
        <CardHeader>
          <CardTitle>Uploaded Documents</CardTitle>
        </CardHeader>
        <CardContent>
          {documents.length === 0 ? (
            <p className="text-sm text-gray-500">No documents uploaded yet.</p>
          ) : (
            <div className="space-y-2">
              {documents.map((doc) => (
                <div key={doc.doc_id} className="p-3 border rounded-lg">
                  <div className="flex justify-between items-start">
                    <div>
                      <p className="font-medium text-sm">{doc.title}</p>
                      <p className="text-xs text-muted-foreground">
                        ID: {doc.doc_id} • {doc.visibility}
                        {doc.project_id && ` • Project: ${doc.project_id}`}
                      </p>
                    </div>
                    {doc.created_at && (
                      <p className="text-xs text-muted-foreground">
                        {new Date(doc.created_at).toLocaleDateString()}
                      </p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
