"use client"

import Image from "next/image"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Message } from "@/types"
import { Bot, User } from "lucide-react"

interface MessageListProps {
  messages: Message[]
}

export function MessageList({ messages }: MessageListProps) {
  return (
    <ScrollArea className="flex-1 p-6">
      <div className="max-w-4xl mx-auto space-y-4">
        {messages.length === 0 ? (
          <div className="text-center py-12">
            <Bot className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold text-foreground mb-2">
              Welcome to Knowledge Hub
            </h3>
            <p className="text-muted-foreground">
              Ask a question to get started. I’ll search our knowledge base and provide answers with citations.
            </p>
          </div>
        ) : (
          messages.map((message) => (
            <div
              key={message.id}
              className={`flex gap-3 ${
                message.role === "user" ? "justify-end" : "justify-start"
              }`}
            >
              {message.role === "assistant" && (
  <div className="w-10 h-10 shrink-0 overflow-hidden rounded-full border border-gray-200 relative">
    <Image
      src="/charachter_icon.png"
      alt="Abu Nasser"
      width={40}
      height={40}
      className="object-cover"
    />
  </div>
)}


              {/* 💬 فقاعة الرسالة */}
              <div
                className={`max-w-[70%] rounded-2xl px-4 py-3 shadow-sm ${
                  message.role === "user"
                    ? "bg-primary text-primary-foreground rounded-br-none"
                    : "bg-muted text-foreground rounded-bl-none"
                }`}
              >
                <p className="text-sm leading-relaxed whitespace-pre-wrap">
                  {message.content}
                </p>

                <p className="text-xs opacity-70 mt-2">
                  {message.timestamp.toLocaleTimeString([], {
                    hour: "2-digit",
                    minute: "2-digit",
                  })}
                </p>
              </div>

             {message.role === "user" && (
  <div className="w-10 h-10 shrink-0 overflow-hidden rounded-full border border-gray-200 relative">
    <Image
      src="/person_icon.png"
      alt="User Avatar"
      width={40}
      height={40}
      className="object-cover"
    />
  </div>
)}
            </div>
          ))
        )}
      </div>
    </ScrollArea>
  )
}
