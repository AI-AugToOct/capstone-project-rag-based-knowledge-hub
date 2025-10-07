"use client"

import { useEffect, useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import {
  Search,
  FileText,
  FileSpreadsheet,
  File,
  MoreVertical,
  Download,
  BookOpen,
} from "lucide-react"

function getFileIcon(filename: string) {
  const ext = filename.split(".").pop()?.toLowerCase()
  switch (ext) {
    case "pdf":
      return <FileText className="h-5 w-5 text-red-500" />
    case "docx":
      return <FileText className="h-5 w-5 text-blue-500" />
    case "xlsx":
    case "csv":
      return <FileSpreadsheet className="h-5 w-5 text-green-500" />
    default:
      return <File className="h-5 w-5 text-gray-500" />
  }
}

export function DocumentsTab() {
  const [documents, setDocuments] = useState<string[]>([])
  const [loading, setLoading] = useState(false)
  const [selectedSummary, setSelectedSummary] = useState<string | null>(null)

  // Fetch documents from backend
  useEffect(() => {
    async function fetchDocuments() {
      try {
        const res = await fetch("http://127.0.0.1:8000/documents")
        const data = await res.json()
        if (Array.isArray(data)) {
          setDocuments(data)
        }
      } catch (error) {
        console.error("Error fetching documents:", error)
      }
    }
    fetchDocuments()
  }, [])

  // Generate summary for a file
  const handleGenerateSummary = async (filename: string) => {
    setLoading(true)
    setSelectedSummary(null)
    try {
      const res = await fetch(`http://127.0.0.1:8000/summary/${filename}`)
      const data = await res.json()
      setSelectedSummary(data.summary || "No summary available")
    } catch (error) {
      console.error("Error generating summary:", error)
    } finally {
      setLoading(false)
    }
  }

  // Download PDF summary
  const handleDownload = (filename: string) => {
    window.open(`http://127.0.0.1:8000/download/${filename}`, "_blank")
  }

  return (
    <div className="flex-1 flex flex-col">
      {/* Header */}
      <header className="border-b border-border bg-card px-6 py-4">
        <div className="flex items-center justify-between gap-4">
          <h2 className="text-lg font-semibold text-foreground">Documents</h2>
          <div className="flex items-center gap-3">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input placeholder="Search files..." className="pl-9 w-64 bg-background" />
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 p-6 bg-background overflow-auto">
        <div className="max-w-6xl mx-auto">
          <div className="bg-card rounded-lg border border-border overflow-hidden">
            <Table>
              <TableHeader>
                <TableRow className="bg-muted/50">
                  <TableHead className="font-semibold">Name</TableHead>
                  <TableHead className="font-semibold w-40">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {documents.map((doc, index) => (
                  <TableRow key={index} className="hover:bg-muted/30">
                    <TableCell>
                      <div className="flex items-center gap-3">
                        {getFileIcon(doc)}
                        <span className="font-medium text-foreground">{doc}</span>
                      </div>
                    </TableCell>
                    <TableCell className="flex gap-2">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleGenerateSummary(doc)}
                        disabled={loading}
                      >
                        <BookOpen className="h-4 w-4 mr-1" />
                        {loading ? "Loading..." : "Summary"}
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleDownload(doc)}
                      >
                        <Download className="h-4 w-4 mr-1" />
                        PDF
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-8 w-8"
                      >
                        <MoreVertical className="h-4 w-4 text-muted-foreground" />
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>

          {/* Show summary */}
          {selectedSummary && (
            <div className="mt-6 p-4 border rounded bg-gray-50">
              <h3 className="font-semibold mb-2">Summary</h3>
              <p className="text-sm whitespace-pre-line">{selectedSummary}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
