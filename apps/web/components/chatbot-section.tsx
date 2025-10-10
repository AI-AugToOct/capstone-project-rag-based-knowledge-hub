"use client"

import { LayoutGrid, Sparkles, FileText, Handshake, Send, Loader2 } from "lucide-react"
import Image from "next/image"
import Link from "next/link"
import { useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { searchKnowledge } from "@/lib/api"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"

interface Message {
  id: string
  type: "user" | "bot"
  content: string
  timestamp: Date
  loading?: boolean
}

export function ChatbotSection() {
  const [activeNav, setActiveNav] = useState("Chatbot")
  const [messages, setMessages] = useState<Message[]>([])
  const [inputValue, setInputValue] = useState("")
  const [isChatActive, setIsChatActive] = useState(false)
  const [isLoading, setIsLoading] = useState(false)

  const navItems = [
    { name: "Home", icon: LayoutGrid, href: "/home" },
    { name: "Chatbot", icon: Sparkles, href: "/chatbot" },
    { name: "Documents", icon: FileText, href: "/documents" },
    { name: "HandOvers", icon: Handshake, href: "/handovers" },
  ]

  const suggestions = ["How do I deploy the Atlas API?", "Find policies related to remote work"]

  const handleSendMessage = async (content: string) => {
    if (!content.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      type: "user",
      content: content.trim(),
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    setInputValue("")
    setIsLoading(true)

    // Add loading message
    const loadingId = (Date.now() + 1).toString()
    setMessages((prev) => [
      ...prev,
      {
        id: loadingId,
        type: "bot",
        content: "Searching knowledge base...",
        timestamp: new Date(),
        loading: true,
      },
    ])

    try {
      // Call real backend API
      const result = await searchKnowledge(content.trim())

      // Remove loading message and add real response
      setMessages((prev) => {
        const filtered = prev.filter((m) => m.id !== loadingId)
        return [
          ...filtered,
          {
            id: Date.now().toString(),
            type: "bot",
            content: result.answer,
            timestamp: new Date(),
          },
        ]
      })
    } catch (error) {
      console.error("[Chatbot] Search failed:", error)

      // Show error message
      setMessages((prev) => {
        const filtered = prev.filter((m) => m.id !== loadingId)
        return [
          ...filtered,
          {
            id: Date.now().toString(),
            type: "bot",
            content: error instanceof Error ? error.message : "Sorry, something went wrong. Please try again.",
            timestamp: new Date(),
          },
        ]
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleStartNewConversation = () => {
    setIsChatActive(true)
    setMessages([])
  }

  const handleSuggestionClick = (suggestion: string) => {
    setIsChatActive(true)
    handleSendMessage(suggestion)
  }

  return (
    <div className="flex min-h-screen bg-gray-50">
      <aside className="relative w-64 bg-gradient-to-b from-[#5B62FF] via-[#4651F9] to-[#3E4DF9] text-white">
        <div className="absolute right-0 top-0 h-full w-12 overflow-hidden">
          <svg
            viewBox="0 0 100 800"
            className="h-full w-full"
            preserveAspectRatio="none"
            style={{ transform: "translateX(50%)" }}
          >
            <path
              d="M0,0 Q30,100 0,200 T0,400 T0,600 T0,800 L100,800 L100,0 Z"
              fill="url(#sidebarGradient)"
              opacity="0.3"
            />
            <defs>
              <linearGradient id="sidebarGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#8B92FF" />
                <stop offset="100%" stopColor="#5B62FF" />
              </linearGradient>
            </defs>
          </svg>
        </div>

        <div className="relative z-10 flex h-full flex-col p-6">
          <div className="mb-12 flex items-center gap-3">
            <div className="relative h-12 w-12 overflow-hidden rounded-full bg-white">
              <Image src="/professional-avatar.png" alt="Omar Saad" fill className="object-cover" />
            </div>
            <div>
              <h2 className="text-lg font-bold">Omar Saad</h2>
              <p className="text-sm text-white/80">AI developer</p>
            </div>
          </div>

          <nav className="space-y-2">
            {navItems.map((item) => {
              const Icon = item.icon
              const isActive = activeNav === item.name

              return (
                <Link
                  key={item.name}
                  href={item.href}
                  onClick={() => setActiveNav(item.name)}
                  className={`flex items-center gap-3 rounded-xl px-4 py-3 transition-all ${
                    isActive ? "bg-white text-[#3E4DF9] shadow-lg" : "text-white hover:bg-white/10"
                  }`}
                >
                  <Icon className="h-5 w-5" />
                  <span className="font-medium">{item.name}</span>
                </Link>
              )
            })}
          </nav>
        </div>
      </aside>

      <main className="flex flex-1 flex-col">
        <div className="flex flex-1 flex-col">
          <div className="relative flex-1 overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-br from-blue-100 via-purple-100 to-blue-200" />

            {!isChatActive ? (
              <div className="relative flex h-full flex-col items-center justify-center p-8">
                <motion.div
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ duration: 0.5 }}
                  className="mb-8"
                >
                  <div className="flex items-center justify-center">
                    <Sparkles className="h-24 w-24 text-gray-900" strokeWidth={1.5} />
                  </div>
                </motion.div>

                <motion.h1
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: 0.2 }}
                  className="mb-4 text-3xl font-bold text-gray-900"
                >
                  Ask our AI anything
                </motion.h1>

                <motion.p
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: 0.3 }}
                  className="mb-8 text-gray-600"
                >
                  Suggestions on what to ask Our AI
                </motion.p>

                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: 0.4 }}
                  className="mb-12 flex flex-wrap justify-center gap-4"
                >
                  {suggestions.map((suggestion, index) => (
                    <button
                      key={index}
                      onClick={() => handleSuggestionClick(suggestion)}
                      className="rounded-xl bg-white/80 px-6 py-3 text-sm text-gray-700 shadow-sm transition-all hover:bg-white hover:shadow-md"
                    >
                      {suggestion}
                    </button>
                  ))}
                </motion.div>

                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: 0.5 }}
                >
                  <Button
                    onClick={handleStartNewConversation}
                    size="lg"
                    className="rounded-full bg-[#3E4DF9] px-8 py-6 text-lg text-white shadow-lg hover:bg-[#3E4DF9]/90"
                  >
                    Start New conversation
                  </Button>
                </motion.div>
              </div>
            ) : (
              <div className="relative flex h-full flex-col">
                <div className="flex-1 overflow-y-auto p-8">
                  <div className="mx-auto max-w-4xl space-y-6">
                    <AnimatePresence>
                      {messages.map((message) => (
                        <motion.div
                          key={message.id}
                          initial={{ opacity: 0, y: 20 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ duration: 0.4 }}
                          className={`flex ${message.type === "user" ? "justify-end" : "justify-start"}`}
                        >
                          <div className="flex max-w-[80%] items-start gap-3">
                            {message.type === "bot" && (
                              <div className="relative h-10 w-10 flex-shrink-0 overflow-hidden rounded-full border-2 border-white bg-white shadow-md">
                                <Image src="/character.png" alt="AI Assistant" fill className="object-cover" />
                              </div>
                            )}

                            <div
                              className={`rounded-2xl px-6 py-4 shadow-sm ${
                                message.type === "user" ? "bg-white/90 text-gray-900" : "bg-white/80 text-gray-900"
                              }`}
                            >
                              {message.type === "bot" ? (
                                <div className="prose prose-sm max-w-none text-[15px] leading-relaxed prose-headings:font-bold prose-headings:text-gray-900 prose-p:text-gray-900 prose-strong:text-gray-900 prose-code:bg-gray-100 prose-code:px-1.5 prose-code:py-0.5 prose-code:rounded prose-code:text-sm prose-code:font-mono prose-code:text-gray-800 prose-pre:bg-gray-100 prose-pre:text-gray-800 prose-ul:text-gray-900 prose-ol:text-gray-900 prose-li:text-gray-900">
                                  <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.content}</ReactMarkdown>
                                </div>
                              ) : (
                                <p className="text-[15px] leading-relaxed">{message.content}</p>
                              )}
                            </div>

                            {message.type === "user" && (
                              <div className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-full bg-[#3E4DF9] text-white shadow-md">
                                <span className="text-lg font-semibold">O</span>
                              </div>
                            )}
                          </div>
                        </motion.div>
                      ))}
                    </AnimatePresence>
                  </div>
                </div>
              </div>
            )}
          </div>

          {isChatActive && (
            <div className="border-t bg-white p-6">
              <div className="mx-auto max-w-4xl">
                <form
                  onSubmit={(e) => {
                    e.preventDefault()
                    handleSendMessage(inputValue)
                  }}
                  className="flex items-center gap-3"
                >
                  <Input
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    placeholder="What can I ask you to do?"
                    className="flex-1 rounded-xl border-gray-200 px-6 py-6 text-base focus-visible:ring-[#3E4DF9]"
                  />
                  <Button type="submit" size="icon" className="h-12 w-12 rounded-xl bg-[#3E4DF9] hover:bg-[#3E4DF9]/90">
                    <Send className="h-5 w-5" />
                  </Button>
                </form>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}
