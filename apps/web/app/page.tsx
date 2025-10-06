"use client"

import { useState } from "react"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Home, MessageSquare, FileText, HelpCircle, Send, Upload } from "lucide-react"
import { cn } from "@/lib/utils"
import HomeDashboard from "@/components/home-dashboard"
import ManagerInterface from "@/components/manager-interface"
import LoginPage from "@/components/login-page"
import DocumentsTab from "@/components/documentsTab"  // ✅ ربط documentsTab هنا

type TabType = "home" | "chat" | "documents" | "manager"

interface Message {
  id: number
  sender: "ai" | "user"
  content: string
}

export default function KnowledgeHub() {
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [isManager, setIsManager] = useState(false)
  const [activeTab, setActiveTab] = useState<TabType>("home")
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      sender: "ai",
      content: "Welcome to your KnowledgeHub assistant. How can I help you today?",
    },
  ])
  const [inputMessage, setInputMessage] = useState("")

  // 👇 تعديل navItems حسب نوع المستخدم
  const navItems = isManager
    ? [
        { id: "documents" as TabType, label: "Documents", icon: FileText },
      ]
    : [
        { id: "home" as TabType, label: "Home", icon: Home },
        { id: "chat" as TabType, label: "Chat", icon: MessageSquare },
        { id: "documents" as TabType, label: "Documents", icon: FileText },
      ]

  // 👇 التحقق من تسجيل الدخول
  const handleLogin = (email: string, password: string) => {
    if (email === "manager@example.com" && password === "1234") {
      setIsManager(true)
      setActiveTab("manager")
    } else {
      setIsManager(false)
      setActiveTab("home")
    }
    setIsLoggedIn(true)
  }

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
      }
      setMessages((prev) => [...prev, aiResponse])
    }, 1000)
  }

  // 👇 إذا ما سجل دخول → عرض صفحة تسجيل الدخول
  if (!isLoggedIn) {
    return <LoginPage onLogin={handleLogin} />
  }

  // مثال: هنا تمرر توكن المانجر (أو أي علامة)
  const managerToken = isManager ? "MANAGER_FAKE_TOKEN" : ""

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
              <AvatarFallback>U</AvatarFallback>
            </Avatar>
            <div>
              <p className="text-sm font-medium" style={{ color: "#70CFDC" }}>
                {isManager ? "المدير" : "الموظف"}
              </p>
              <p className="text-xs" style={{ color: "#70CFDC" }}>
                {isManager ? "صفحة المدير" : "الموظف"}
              </p>
            </div>
          </div>
        </div>

        {/* Navigation */}
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
            {isManager && (
              <li>
                <button
                  onClick={() => setActiveTab("manager")}
                  className={cn(
                    "w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors",
                    activeTab === "manager"
                      ? "bg-[#70CFDC] text-white"
                      : "text-[#70CFDC] hover:bg-[#70CFDC] hover:text-white"
                  )}
                >
                  <Upload className="h-5 w-5" />
                  Manager
                </button>
              </li>
            )}
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
        {activeTab === "home" && <HomeDashboard />}
        {activeTab === "chat" && (
          <>
            <header className="border-b border-border bg-card px-6 py-4">
              <h2 className="text-lg font-semibold text-foreground">AI Assistant</h2>
            </header>
            <ScrollArea className="flex-1 p-6">
              <div className="max-w-4xl mx-auto space-y-4">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={cn(
                      "flex",
                      message.sender === "user" ? "justify-end" : "justify-start"
                    )}
                  >
                    <div
                      className={cn(
                        "max-w-[70%] rounded-2xl px-4 py-3",
                        message.sender === "ai"
                          ? "bg-[#F0F4F9] text-foreground"
                          : "bg-[#E0E7FF] text-foreground"
                      )}
                    >
                      <p className="text-sm leading-relaxed">{message.content}</p>
                    </div>
                  </div>
                ))}
              </div>
            </ScrollArea>
            <div className="border-t border-border bg-card p-4">
              <div className="max-w-4xl mx-auto">
                <div className="flex items-end gap-2 bg-background border border-border rounded-xl p-2">
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
                    className="flex-1 border-0 bg-transparent focus-visible:ring-0"
                  />
                  <Button
                    onClick={handleSendMessage}
                    size="icon"
                    className="shrink-0 rounded-lg"
                  >
                    <Send className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </div>
          </>
        )}

        {activeTab === "home" && <HomeDashboard />}
        {activeTab === "documents" && (
          <DocumentsTab isManager={isManager} token={managerToken} />
        )}
        {activeTab === "manager" && isManager && <ManagerInterface />}

      </main>
    </div>
  )
}
