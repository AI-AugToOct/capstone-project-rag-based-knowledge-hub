"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export default function HomeDashboard() {
  type NotionTask = {
    name: string
    status: string
    start?: string | null
    due?: string | null
    milestone?: string | null
  }

  const [notionTasks, setNotionTasks] = useState<NotionTask[]>([])

  useEffect(() => {
    async function fetchTasks() {
      try {
        const response = await fetch("http://127.0.0.1:8000/notion-tasks")
        const data = await response.json()
        setNotionTasks(data)
      } catch (error) {
        console.error("Failed to fetch tasks:", error)
      }
    }
    fetchTasks()
  }, [])

  return (
    <div className="flex-1 flex flex-col bg-[#FAFBFC] p-8">
      <h1 className="text-2xl font-bold mb-6">📌 Project Tasks Board</h1>

      {notionTasks.length === 0 ? (
        <p className="text-gray-500">No tasks found. Connect Notion or upload tasks.</p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {notionTasks.map((task, idx) => (
            <Card key={idx} className="shadow-sm border-gray-200">
              <CardHeader>
                <CardTitle className="text-base font-semibold text-gray-900">
                  {task.name}
                </CardTitle>
              </CardHeader>
              <CardContent className="text-sm space-y-1 text-gray-700">
                <p><span className="font-medium">Status:</span> {task.status}</p>
                <p><span className="font-medium">Start:</span> {task.start || "N/A"}</p>
                <p><span className="font-medium">Due:</span> {task.due || "N/A"}</p>
                <p><span className="font-medium">Milestone:</span> {task.milestone || "N/A"}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
