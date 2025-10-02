import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Search, Upload, FileText, FileSpreadsheet, File, MoreVertical } from "lucide-react"

const documents = [
  {
    id: 1,
    name: "Q3 Financial Report.pdf",
    type: "pdf",
    lastModified: "Oct 1, 2025",
    size: "2.4 MB",
  },
  {
    id: 2,
    name: "Employee Handbook 2025.docx",
    type: "word",
    lastModified: "Sep 28, 2025",
    size: "1.8 MB",
  },
  {
    id: 3,
    name: "Project Budget Tracker.xlsx",
    type: "spreadsheet",
    lastModified: "Sep 25, 2025",
    size: "856 KB",
  },
  {
    id: 4,
    name: "Marketing Strategy Q4.pdf",
    type: "pdf",
    lastModified: "Sep 20, 2025",
    size: "3.2 MB",
  },
  {
    id: 5,
    name: "Team Meeting Notes.docx",
    type: "word",
    lastModified: "Sep 15, 2025",
    size: "524 KB",
  },
]

function getFileIcon(type: string) {
  switch (type) {
    case "pdf":
      return <FileText className="h-5 w-5 text-red-500" />
    case "word":
      return <FileText className="h-5 w-5 text-blue-500" />
    case "spreadsheet":
      return <FileSpreadsheet className="h-5 w-5 text-green-500" />
    default:
      return <File className="h-5 w-5 text-gray-500" />
  }
}

export function DocumentsTab() {
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
            <Button className="gap-2">
              <Upload className="h-4 w-4" />
              Upload File
            </Button>
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
                  <TableHead className="font-semibold">Last Modified</TableHead>
                  <TableHead className="font-semibold">File Size</TableHead>
                  <TableHead className="font-semibold w-20">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {documents.map((doc) => (
                  <TableRow key={doc.id} className="hover:bg-muted/30">
                    <TableCell>
                      <div className="flex items-center gap-3">
                        {getFileIcon(doc.type)}
                        <span className="font-medium text-foreground">{doc.name}</span>
                      </div>
                    </TableCell>
                    <TableCell className="text-muted-foreground">{doc.lastModified}</TableCell>
                    <TableCell className="text-muted-foreground">{doc.size}</TableCell>
                    <TableCell>
                      <Button variant="ghost" size="icon" className="h-8 w-8">
                        <MoreVertical className="h-4 w-4 text-muted-foreground" />
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </div>
      </div>
    </div>
  )
}
