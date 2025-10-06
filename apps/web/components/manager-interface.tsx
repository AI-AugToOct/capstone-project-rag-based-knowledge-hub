"use client"

import { useEffect, useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export default function ManagerInterface() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [customName, setCustomName] = useState("") // <-- حقل الاسم المخصص
  const [visibility, setVisibility] = useState("Public")
  const [allowedProjects, setAllowedProjects] = useState("")
  const [uploadStatus, setUploadStatus] = useState("")
  const [documents, setDocuments] = useState<any[]>([])

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setSelectedFile(e.target.files[0])
      setUploadStatus("")
    }
  }

  const handleUpload = async () => {
    if (!selectedFile) {
      setUploadStatus("⚠️ Please select a file first.")
      return
    }

    const formData = new FormData()
    formData.append("file", selectedFile)
    formData.append("visibility", visibility)
    if (visibility === "Private") formData.append("allowed_projects", allowedProjects)
    if (customName.trim()) formData.append("custom_name", customName.trim()) // <-- الاسم المخصص

    try {
      const res = await fetch("http://127.0.0.1:8000/api/upload", {
        method: "POST",
        body: formData,
        headers: {
          Authorization: `Bearer manager_test_token`
        }
      })

      if (!res.ok) {
        const text = await res.text()
        throw new Error(text || "Upload failed")
      }

      setUploadStatus("✅ File uploaded successfully!")
      setSelectedFile(null)
      setCustomName("") // إعادة تعيين الاسم المخصص
      setAllowedProjects("")
      fetchDocuments()
    } catch (err: any) {
      console.error(err)
      setUploadStatus(`❌ Upload failed: ${err.message}`)
    }
  }

  const fetchDocuments = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/api/documents", {
        headers: { Authorization: "Bearer manager_test_token" }
      })
      if (!res.ok) throw new Error("Failed to fetch documents")
      const data = await res.json()
      if (Array.isArray(data)) setDocuments(data)
    } catch (err) {
      console.error("Error fetching documents:", err)
    }
  }

  useEffect(() => { fetchDocuments() }, [])

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-6">Manager Interface - Upload Documents</h1>

      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Upload a new file</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-col gap-4">
          <input type="file" onChange={handleFileChange} />

          <input
            type="text"
            placeholder="Custom File Name (optional)"
            value={customName}
            onChange={(e) => setCustomName(e.target.value)}
            className="border rounded p-2"
          />

          <select
            value={visibility}
            onChange={(e) => setVisibility(e.target.value)}
            className="border rounded p-2"
          >
            <option value="Public">Public</option>
            <option value="Private">Private</option>
          </select>

          {visibility === "Private" && (
            <input
              type="text"
              placeholder="Allowed Projects (comma-separated)"
              value={allowedProjects}
              onChange={(e) => setAllowedProjects(e.target.value)}
              className="border rounded p-2"
            />
          )}

          <Button onClick={handleUpload} className="w-32">Upload</Button>

          {uploadStatus && (
            <p
              className={`text-sm ${
                uploadStatus.startsWith("✅") ? "text-green-600"
                : uploadStatus.startsWith("❌") ? "text-red-600"
                : "text-yellow-600"
              }`}
            >
              {uploadStatus}
            </p>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Uploaded Documents</CardTitle>
        </CardHeader>
        <CardContent>
          {documents.length === 0 ? (
            <p className="text-sm text-gray-500">No documents uploaded yet.</p>
          ) : (
            <ul className="list-disc list-inside space-y-1">
              {documents.map((doc) => (
                <li key={doc.doc_id} className="text-sm text-gray-700">
                  {doc.title} {doc.uri ? `- ${doc.uri}` : ""} ({doc.visibility})
                </li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
