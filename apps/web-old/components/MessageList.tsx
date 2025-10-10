/**
 * MessageList Component
 *
 * Displays the conversation history (user questions + AI answers).
 * Renders messages with different styles for user vs assistant.
 */

"use client"

import { ScrollArea } from "@/components/ui/scroll-area"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Message } from "@/types"
import { User, Bot } from "lucide-react"

interface MessageListProps {
  messages: Message[]
}

/**
 * MessageList Component
 *
 * Props:
 *   messages: Array of Message objects
 *     Example: [
 *       { id: 1, role: 'user', content: 'How do I deploy?', timestamp: new Date() },
 *       { id: 2, role: 'assistant', content: 'To deploy...', chunks: [...], timestamp: new Date() }
 *     ]
 *
 * Example Usage:
 *   const messages = [...]
 *   <MessageList messages={messages} />
 *
 * What This Does:
 *   - Displays all messages in chronological order
 *   - User messages appear on the right (blue background)
 *   - Assistant messages appear on the left (gray background)
 *   - Shows avatar for each message
 *   - Auto-scrolls to newest message
 *
 * Message Rendering:
 *   User message:
 *     [User Icon] "How do I deploy Atlas?"
 *
 *   Assistant message:
 *     [Bot Icon] "To deploy Atlas API, follow these steps: 1. ..."
 *                [Citations shown below - see SourcesList component]
 */
export function MessageList({ messages }: MessageListProps) {
  return (
    <ScrollArea className="flex-1 p-6">
      <div className="max-w-4xl mx-auto space-y-4">
        {messages.length === 0 ? (
          // Empty state
          <div className="text-center py-12">
            <Bot className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold text-foreground mb-2">
              Welcome to Knowledge Hub
            </h3>
            <p className="text-muted-foreground">
              Ask a question to get started. I'll search our knowledge base and provide answers with citations.
            </p>
          </div>
        ) : (
          // Messages
          messages.map((message) => (
            <div
              key={message.id}
              className={`flex gap-3 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              {/* Avatar (left side for assistant, right for user) */}
              {message.role === 'assistant' && (
                <Avatar className="shrink-0">
                  <AvatarFallback className="bg-primary/10">
                    <Bot className="h-4 w-4 text-primary" />
                  </AvatarFallback>
                </Avatar>
              )}

              {/* Message bubble */}
              <div
                className={`max-w-[70%] rounded-2xl px-4 py-3 ${
                  message.role === 'user'
                    ? 'bg-primary text-primary-foreground'
                    : 'bg-muted text-foreground'
                }`}
              >
                {/* Message content */}
                <p className="text-sm leading-relaxed whitespace-pre-wrap">
                  {message.content}
                </p>

                {/* Timestamp (optional) */}
                <p className="text-xs opacity-70 mt-2">
                  {message.timestamp.toLocaleTimeString()}
                </p>
              </div>

              {/* Avatar (right side for user) */}
              {message.role === 'user' && (
                <Avatar className="shrink-0">
                  <AvatarFallback className="bg-primary">
                    <User className="h-4 w-4 text-primary-foreground" />
                  </AvatarFallback>
                </Avatar>
              )}
            </div>
          ))
        )}
      </div>
    </ScrollArea>
  )
}

// Example with Citations:
//
// If you want to show citations below assistant messages,
// you can modify the component to include SourcesList:
//
// import { SourcesList } from '@/components/SourcesList'
//
// // Inside the assistant message rendering:
// {message.role === 'assistant' && message.chunks && (
//   <div className="mt-3">
//     <SourcesList chunks={message.chunks} />
//   </div>
// )}


// Auto-Scroll to Bottom (optional enhancement):
//
// import { useEffect, useRef } from 'react'
//
// export function MessageList({ messages }: MessageListProps) {
//   const bottomRef = useRef<HTMLDivElement>(null)
//
//   useEffect(() => {
//     bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
//   }, [messages])
//
//   return (
//     <ScrollArea className="flex-1 p-6">
//       {/* ... messages ... */}
//       <div ref={bottomRef} />
//     </ScrollArea>
//   )
// }


// Markdown Rendering (optional enhancement):
//
// If LLM returns Markdown-formatted answers, render with markdown library:
//
// import ReactMarkdown from 'react-markdown'
//
// <ReactMarkdown>{message.content}</ReactMarkdown>
//
// This would render:
//   - **bold** → <strong>bold</strong>
//   - `code` → <code>code</code>
//   - # Heading → <h1>Heading</h1>
//   - Lists, links, etc.