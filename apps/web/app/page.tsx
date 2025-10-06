"use client"

import { useState } from "react"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"
import {
  Home,
  MessageSquare,
  FileText,
  HelpCircle,
  Paperclip,
  Send,
} from "lucide-react"
import { cn } from "@/lib/utils"
import { DocumentsTab } from "@/components/documents-tab"
import HomeDashboard from "@/components/home-dashboard"
import LoginPage from "@/components/login-page"

type TabType = "home" | "chat" | "documents"

interface Message {
  id: number
  sender: "ai" | "user"
  content: string
  actions?: Array<{ label: string; type: string }>
}

export default function KnowledgeHub() {
  const [isLoggedIn, setIsLoggedIn] = useState(false)
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
      content:
        "Please provide access to the Q3 report first. Would you like me to find it in the Documents tab?",
      actions: [{ label: "View Q3 Report in Documents", type: "document" }],
    },
  ])
  const [inputMessage, setInputMessage] = useState("")

  const navItems = [
    { id: "home" as TabType, label: "Home", icon: Home },
    { id: "chat" as TabType, label: "Chat", icon: MessageSquare },
    { id: "documents" as TabType, label: "Documents", icon: FileText },
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

  if (!isLoggedIn) {
    return <LoginPage onLogin={() => setIsLoggedIn(true)} />
  }

  return (
    <div className="flex h-screen bg-background">
      {/* Sidebar */}
      <aside className="w-64 border-r border-border bg-card flex flex-col">
        <div className="p-6 border-b border-border">
          <h1 className="text-xl font-semibold mb-4" style={{ color: "#70CFDC" }}>
            KnowledgeHub
          </h1>
          <div className="flex items-center gap-3">
            <Avatar>
              <AvatarImage src="/professional-woman-diverse.png" />
              <AvatarFallback>اسم</AvatarFallback>
            </Avatar>
            <div>
              <p className="text-sm font-medium" style={{ color: "#70CFDC" }}>
                اسم المستخدم
              </p>
              <p className="text-xs" style={{ color: "#70CFDC" }}>
                وظيفته
              </p>
            </div>
          </div>
        </div>

        <nav className="flex-1 p-4">
          <ul className="space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon
              const isActive = activeTab === item.id
              return (
                <li key={item.id}>
                  <button
                    onClick={() => setActiveTab(item.id)}
                    className={cn(
                      "w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors",
                      isActive
                        ? "bg-[#70CFDC] text-white"
                        : "text-[#70CFDC] hover:bg-[#70CFDC] hover:text-white"
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

        <div className="p-4 border-t border-border">
          <button className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors">
            <HelpCircle className="h-4 w-4" />
            Help
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col">
        {activeTab === "home" ? (
          <HomeDashboard />
        ) : activeTab === "chat" ? (
          <>
            <header className="border-b border-border bg-card px-6 py-4">
              <h2 className="text-lg font-semibold text-foreground">AI Assistant</h2>
            </header>

            {/* Chat Area */}
            <ScrollArea className="flex-1 p-6">
              <div className="max-w-4xl mx-auto space-y-4">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={cn(
                      "flex items-start gap-3",
                      message.sender === "user" ? "justify-end" : "justify-start"
                    )}
                  >
                    {/* 🧠 Avatar للسستم */}
                    {message.sender === "ai" && (
                      <img
                        src="/charachter_icon.png"
                        alt="AI Assistant"
                        className="w-10 h-10 rounded-full border border-gray-200"
                      />
                    )}

                    {/* 💬 فقاعة الرسالة */}
                    <div
                      className={cn(
                        "max-w-[70%] rounded-2xl px-4 py-3",
                        message.sender === "ai"
                          ? "bg-[#F0F4F9] text-foreground"
                          : "bg-[#E0E7FF] text-foreground"
                      )}
                    >
                      <p className="text-sm leading-relaxed">{message.content}</p>

                      {message.actions && message.actions.length > 0 && (
                        <div className="mt-3 flex flex-wrap gap-2">
                          {message.actions.map((action, idx) => (
                            <Button
                              key={idx}
                              variant="outline"
                              size="sm"
                              className="text-xs bg-white hover:bg-gray-50"
                            >
                              {action.label}
                            </Button>
                          ))}
                        </div>
                      )}
                    </div>

                    {/* 👤 Avatar لليوزر */}
                    {message.sender === "user" && (
                      <img
                        src="/person_icon.png"
                        alt="User Avatar"
                        className="w-10 h-10 rounded-full border border-gray-200"
                      />
                    )}
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
        ) : (
          <DocumentsTab />
        )}
      </main>
    </div>
  )
}
