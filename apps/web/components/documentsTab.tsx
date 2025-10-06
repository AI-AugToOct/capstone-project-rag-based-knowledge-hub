import { useEffect, useState } from "react"

export default function DocumentsTab({ isManager, token }: { isManager: boolean, token: string }) {
  const [documents, setDocuments] = useState<any[]>([])
  const userId = 2 // مثال: ID المستخدم الحالي

  const fetchDocuments = async () => {
    const res = await fetch("http://127.0.0.1:8000/api/documents")
    const data = await res.json()
    if (Array.isArray(data)) {
      if (isManager) {
        setDocuments(data) // Manager يرى كل شيء
      } else {
        // فلترة المستندات العامة أو الخاصة بالمستخدم
        setDocuments(data.filter(doc => {
          if (doc.visibility === "Public") return true
          if (doc.visibility === "Private" && doc.allowed_user_ids?.includes(userId)) return true
          return false
        }))
      }
    }
  }

  useEffect(() => { fetchDocuments() }, [])

  return (
    <div className="p-6">
      <h2 className="text-xl font-semibold mb-4">Documents</h2>
      {documents.length === 0 ? (
        <p>No documents available</p>
      ) : (
        <ul className="list-disc list-inside">
          {documents.map(doc => (
            <li key={doc.doc_id}>{doc.title} - {doc.visibility}</li>
          ))}
        </ul>
      )}
    </div>
  )
}
