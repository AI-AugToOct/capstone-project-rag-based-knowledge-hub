/**
 * ChatInput Component
 *
 * Text input + Send button for user to ask questions.
 * Handles Enter key and displays loading state.
 */

"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Send, Paperclip } from "lucide-react"

interface ChatInputProps {
  onSend: (message: string) => void
  disabled?: boolean
  placeholder?: string
}

/**
 * ChatInput Component
 *
 * Props:
 *   onSend: Callback function called when user sends a message
 *     Example: (message) => console.log("User sent:", message)
 *
 *   disabled: Whether input is disabled (e.g., while loading)
 *     Example: disabled={isLoading}
 *
 *   placeholder: Placeholder text in input
 *     Example: placeholder="Ask a question..."
 *
 * Example Usage:
 *   <ChatInput
 *     onSend={(message) => handleSearch(message)}
 *     disabled={isLoading}
 *     placeholder="How do I deploy Atlas?"
 *   />
 *
 * What This Does:
 *   - Displays text input with Send button
 *   - Handles Enter key (send message)
 *   - Handles Shift+Enter (new line)
 *   - Clears input after sending
 *   - Shows loading state (disabled input)
 *
 * User Experience:
 *   1. User types question
 *   2. Presses Enter or clicks Send
 *   3. Input is cleared
 *   4. Input is disabled while loading
 *   5. When done, input is re-enabled
 */
export function ChatInput({ onSend, disabled = false, placeholder = "Ask a question..." }: ChatInputProps) {
  const [inputValue, setInputValue] = useState("")

  const handleSend = () => {
    if (!inputValue.trim() || disabled) return

    onSend(inputValue.trim())
    setInputValue("")
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    // Enter key → send message (unless Shift is held)
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="border-t border-border bg-card p-4">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center gap-2 bg-background border border-border rounded-xl p-2">
          {/* Optional: Attach file button (future feature) */}
          <Button
            variant="ghost"
            size="icon"
            className="shrink-0 text-muted-foreground hover:text-foreground"
            disabled={disabled}
          >
            <Paperclip className="h-5 w-5" />
          </Button>

          {/* Text input */}
          <Input
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            disabled={disabled}
            className="flex-1 border-0 bg-transparent focus-visible:ring-0 focus-visible:ring-offset-0"
          />

          {/* Send button */}
          <Button
            onClick={handleSend}
            size="icon"
            className="shrink-0 rounded-lg"
            disabled={disabled || !inputValue.trim()}
          >
            <Send className="h-4 w-4" />
          </Button>
        </div>

        {/* Optional: Character count or hints */}
        {inputValue.length > 0 && (
          <p className="text-xs text-muted-foreground mt-2">
            Press Enter to send, Shift+Enter for new line
          </p>
        )}
      </div>
    </div>
  )
}

// Example Integration with Search:
//
// export function SearchPage() {
//   const [isLoading, setIsLoading] = useState(false)
//   const [messages, setMessages] = useState<Message[]>([])
//
//   async function handleSend(query: string) {
//     // Add user message
//     const userMessage: Message = {
//       id: Date.now(),
//       role: 'user',
//       content: query,
//       timestamp: new Date()
//     }
//     setMessages([...messages, userMessage])
//
//     // Call backend
//     setIsLoading(true)
//     try {
//       const result = await searchKnowledge(query)
//
//       // Add assistant message with answer + citations
//       const assistantMessage: Message = {
//         id: Date.now() + 1,
//         role: 'assistant',
//         content: result.answer,
//         chunks: result.chunks,
//         timestamp: new Date()
//       }
//       setMessages([...messages, userMessage, assistantMessage])
//     } catch (error) {
//       console.error('Search failed:', error)
//       // Show error message
//     } finally {
//       setIsLoading(false)
//     }
//   }
//
//   return (
//     <div>
//       <MessageList messages={messages} />
//       <ChatInput onSend={handleSend} disabled={isLoading} />
//     </div>
//   )
// }