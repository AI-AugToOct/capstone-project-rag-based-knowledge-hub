"use client"

import { useEffect, useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export default function ManagerInterface() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [uploadStatus, setUploadStatus] = useState("")
  const [documents, setDocuments] = useState<string[]>([])

  // Handle file selection
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setSelectedFile(e.target.files[0])
    }
  }

  // Handle file upload to backend
  const handleUpload = async () => {
    if (!selectedFile) {
      setUploadStatus("⚠️ Please select a file first.")
      return
    }

    const formData = new FormData()
    formData.append("file", selectedFile)

    try {
      const res = await fetch("http://127.0.0.1:8000/upload", {
        method: "POST",
        body: formData,
      })

      if (res.ok) {
        setUploadStatus("✅ File uploaded successfully!")
        setSelectedFile(null)
        fetchDocuments() // refresh list after upload
      } else {
        setUploadStatus("❌ Upload failed.")
      }
    } catch (err) {
      console.error(err)
      setUploadStatus("⚠️ Error connecting to backend.")
    }
  }

  // Fetch uploaded documents
  const fetchDocuments = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/documents")
      const data = await res.json()
      if (Array.isArray(data)) {
        setDocuments(data)
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
        <CardContent className="flex flex-col gap-4">
          <input type="file" onChange={handleFileChange} />
          <Button onClick={handleUpload} className="w-32">
            Upload
          </Button>
          {uploadStatus && (
            <p
              className={`text-sm ${
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
            <ul className="list-disc list-inside space-y-1">
              {documents.map((doc, index) => (
                <li key={index} className="text-sm text-gray-700">
                  {doc}
                </li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
