"use client"

import { useState } from "react"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"
import {
  Home,
  MessageSquare,
  Calendar,
  FolderKanban,
  FileText,
  Users,
  Settings,
  HelpCircle,
  Paperclip,
  Send,
} from "lucide-react"
import { cn } from "@/lib/utils"
import { DocumentsTab } from "@/components/documents-tab"
import { ProjectsTab } from "@/components/projects-tab"
import { MeetingsTab } from "@/components/meetings-tab"
import { HomeDashboard } from "@/components/home-dashboard"

type TabType = "home" | "chat" | "meetings" | "projects" | "documents" | "directory" | "settings"

interface Message {
  id: number
  sender: "ai" | "user"
  content: string
  actions?: Array<{ label: string; type: string }>
}

export default function KnowledgeHub() {
  const [activeTab, setActiveTab] = useState<TabType>("home")
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      sender: "ai",
      content: "Welcome to your KnowledgeHub assistant. How can I help you today?",
    },
    {
      id: 2,
      sender: "user",
      content: "Summarize the Q3 financial report.",
    },
    {
      id: 3,
      sender: "ai",
      content: "Please provide access to the Q3 report first. Would you like me to find it in the Documents tab?",
      actions: [{ label: "View Q3 Report in Documents", type: "document" }],
    },
  ])
  const [inputMessage, setInputMessage] = useState("")

  const navItems = [
    { id: "home" as TabType, label: "Home", icon: Home },
    { id: "chat" as TabType, label: "Chat", icon: MessageSquare },
    { id: "meetings" as TabType, label: "Meetings", icon: Calendar },
    { id: "projects" as TabType, label: "Projects/Tasks", icon: FolderKanban },
    { id: "documents" as TabType, label: "Documents", icon: FileText },
    { id: "directory" as TabType, label: "Team Directory", icon: Users },
    { id: "settings" as TabType, label: "Settings", icon: Settings },
  ]

  const handleSendMessage = () => {
    if (!inputMessage.trim()) return

    const newMessage: Message = {
      id: messages.length + 1,
      sender: "user",
      content: inputMessage,
    }

    setMessages([...messages, newMessage])
    setInputMessage("")

    // Simulate AI response
    setTimeout(() => {
      const aiResponse: Message = {
        id: messages.length + 2,
        sender: "ai",
        content: "I understand your request. Let me help you with that.",
        actions: [
          { label: "Create Meeting", type: "meeting" },
          { label: "Suggest a New Meeting", type: "meeting" },
        ],
      }
      setMessages((prev) => [...prev, aiResponse])
    }, 1000)
  }

  return (
    <div className="flex h-screen bg-background">
      {/* Left Sidebar */}
      <aside className="w-64 border-r border-border bg-card flex flex-col">
        {/* Top Section */}
        <div className="p-6 border-b border-border">
          <h1 className="text-xl font-semibold mb-4 text-foreground">KnowledgeHub</h1>
          <div className="flex items-center gap-3">
            <Avatar>
              <AvatarImage src="/professional-woman-diverse.png" />
              <AvatarFallback>JD</AvatarFallback>
            </Avatar>
            <div>
              <p className="text-sm font-medium text-foreground">Jane Doe</p>
              <p className="text-xs text-muted-foreground">Product Manager</p>
            </div>
          </div>
        </div>

        {/* Main Navigation */}
        <nav className="flex-1 p-4">
          <ul className="space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon
              return (
                <li key={item.id}>
                  <button
                    onClick={() => setActiveTab(item.id)}
                    className={cn(
                      "w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors",
                      activeTab === item.id
                        ? "bg-primary text-primary-foreground"
                        : "text-muted-foreground hover:bg-accent hover:text-accent-foreground",
                    )}
                  >
                    <Icon className="h-5 w-5" />
                    {item.label}
                  </button>
                </li>
              )
            })}
          </ul>
        </nav>

        {/* Bottom Section */}
        <div className="p-4 border-t border-border">
          <button className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors">
            <HelpCircle className="h-4 w-4" />
            Help
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col">
        {activeTab === "home" ? (
          <HomeDashboard />
        ) : activeTab === "chat" ? (
          <>
            {/* Chat Header */}
            <header className="border-b border-border bg-card px-6 py-4">
              <h2 className="text-lg font-semibold text-foreground">AI Assistant</h2>
            </header>

            {/* Chat Messages */}
            <ScrollArea className="flex-1 p-6">
              <div className="max-w-4xl mx-auto space-y-4">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={cn("flex", message.sender === "user" ? "justify-end" : "justify-start")}
                  >
                    <div
                      className={cn(
                        "max-w-[70%] rounded-2xl px-4 py-3",
                        message.sender === "ai" ? "bg-[#F0F4F9] text-foreground" : "bg-[#E0E7FF] text-foreground",
                      )}
                    >
                      <p className="text-sm leading-relaxed">{message.content}</p>

                      {/* Dynamic Interactive Elements */}
                      {message.actions && message.actions.length > 0 && (
                        <div className="mt-3 flex flex-wrap gap-2">
                          {message.actions.map((action, idx) => (
                            <Button key={idx} variant="outline" size="sm" className="text-xs bg-white hover:bg-gray-50">
                              {action.label}
                            </Button>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </ScrollArea>

            {/* Chat Input */}
            <div className="border-t border-border bg-card p-4">
              <div className="max-w-4xl mx-auto">
                <div className="flex items-end gap-2 bg-background border border-border rounded-xl p-2">
                  <Button variant="ghost" size="icon" className="shrink-0 text-muted-foreground hover:text-foreground">
                    <Paperclip className="h-5 w-5" />
                  </Button>

                  <Input
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter" && !e.shiftKey) {
                        e.preventDefault()
                        handleSendMessage()
                      }
                    }}
                    placeholder="Message the AI assistant..."
                    className="flex-1 border-0 bg-transparent focus-visible:ring-0 focus-visible:ring-offset-0 resize-none min-h-[40px]"
                  />

                  <Button onClick={handleSendMessage} size="icon" className="shrink-0 rounded-lg">
                    <Send className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </div>
          </>
        ) : activeTab === "documents" ? (
          <DocumentsTab />
        ) : activeTab === "projects" ? (
          <ProjectsTab />
        ) : activeTab === "meetings" ? (
          <MeetingsTab />
        ) : (
          <div className="flex-1 flex items-center justify-center p-6">
            <div className="text-center max-w-md">
              <h2 className="text-2xl font-semibold mb-3 text-foreground">
                {activeTab === "directory" && "Team Directory"}
                {activeTab === "settings" && "Settings"}
              </h2>
              <p className="text-muted-foreground leading-relaxed">
                {activeTab === "directory" &&
                  "Find employee contact information and team details. The AI can help you connect with colleagues."}
                {activeTab === "settings" && "Customize your preferences and account settings."}
              </p>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}
