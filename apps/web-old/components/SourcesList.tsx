/**
 * SourcesList Component
 *
 * Displays citations (chunks) that were used to generate the answer.
 * Each citation is clickable and links to the source document in Notion.
 */

"use client"

import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { ExternalLink } from "lucide-react"
import { Chunk } from "@/types"

interface SourcesListProps {
  chunks: Chunk[]
  title?: string
}

/**
 * SourcesList Component
 *
 * Props:
 *   chunks: Array of Chunk objects (citations)
 *     Example: [
 *       {
 *         doc_id: 123,
 *         title: "Atlas Deploy Guide",
 *         snippet: "To deploy Atlas API...",
 *         uri: "https://notion.so/abc123",
 *         score: 0.87
 *       }
 *     ]
 *
 *   title: Optional title for the sources section
 *     Example: "Sources" or "Referenced Documents"
 *
 * Example Usage:
 *   <SourcesList chunks={result.chunks} title="Sources" />
 *
 * What This Does:
 *   - Displays each citation as a card
 *   - Shows document title, snippet, and relevance score
 *   - Links to original document (opens in new tab)
 *   - Highlights which documents were used
 *
 * Why We Need This:
 *   - Users need to verify AI answers
 *   - Citations provide transparency
 *   - Links allow users to read full context
 *   - Scores show relevance
 */
export function SourcesList({ chunks, title = "Sources" }: SourcesListProps) {
  if (!chunks || chunks.length === 0) {
    return null
  }

  return (
    <div className="space-y-3">
      {/* Title */}
      <h3 className="text-sm font-semibold text-foreground">
        {title} ({chunks.length})
      </h3>

      {/* Citations */}
      <div className="space-y-2">
        {chunks.map((chunk, index) => (
          <Card key={chunk.doc_id + index} className="hover:bg-accent/50 transition-colors">
            <CardHeader className="pb-3">
              <div className="flex items-start justify-between gap-2">
                <CardTitle className="text-sm font-medium text-foreground line-clamp-1">
                  {chunk.title}
                </CardTitle>

                {/* Relevance score badge */}
                <Badge variant="secondary" className="shrink-0">
                  {Math.round(chunk.score * 100)}%
                </Badge>
              </div>
            </CardHeader>

            <CardContent>
              {/* Snippet */}
              <p className="text-xs text-muted-foreground line-clamp-3 mb-3">
                {chunk.snippet}
              </p>

              {/* Link to source */}
              <a
                href={chunk.uri}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1 text-xs text-primary hover:underline"
              >
                View in Notion
                <ExternalLink className="h-3 w-3" />
              </a>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}

// Example Integration with MessageList:
//
// You can show sources directly below assistant messages:
//
// {message.role === 'assistant' && message.chunks && (
//   <div className="mt-4 border-t border-border pt-4">
//     <SourcesList chunks={message.chunks} />
//   </div>
// )}


// Alternative: Side Panel Layout:
//
// For a side-by-side layout (chat on left, sources on right):
//
// <div className="flex h-screen">
//   {/* Left: Chat */}
//   <div className="flex-1 flex flex-col">
//     <MessageList messages={messages} />
//     <ChatInput onSend={handleSend} />
//   </div>
//
//   {/* Right: Sources */}
//   <div className="w-96 border-l p-4 overflow-y-auto">
//     {currentSources && <SourcesList chunks={currentSources} />}
//   </div>
// </div>


// Enhanced Features (optional):
//
// 1. Expand/Collapse:
//    - Show only first 3 sources by default
//    - "Show more" button to reveal rest
//
// 2. Filtering:
//    - Filter by project
//    - Filter by score (>80%, >60%, etc.)
//
// 3. Grouping:
//    - Group by document (multiple chunks from same doc)
//    - Show document title once, list chunks below
//
// 4. Preview:
//    - Click to open modal with full chunk text
//    - Show full heading_path
//
// 5. Actions:
//    - Copy snippet
//    - Share link
//    - Bookmark document