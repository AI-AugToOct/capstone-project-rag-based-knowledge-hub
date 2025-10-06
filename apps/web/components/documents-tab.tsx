"use client"
import { useEffect, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

interface Document {
  doc_id: number
  title: string
  uri: string
}

export default function DocumentsTab() {
  const [documents, setDocuments] = useState<Document[]>([])

  const fetchDocuments = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/api/documents")
      if (!res.ok) throw new Error("Failed to fetch documents")
      const data = await res.json()
      if (Array.isArray(data)) setDocuments(data)
    } catch (err) {
      console.error("Error fetching documents:", err)
    }
  }

  useEffect(() => {
    fetchDocuments()
  }, [])

  return (
    <div className="p-8">
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
                  {doc.title} {doc.uri ? `- ${doc.uri}` : ""}
                </li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
