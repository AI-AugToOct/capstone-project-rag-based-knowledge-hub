/**
 * TypeScript Type Definitions
 *
 * These types define the shape of data in the frontend.
 * They match the backend's Pydantic models.
 */

/**
 * A single chunk/citation from search results
 */
export interface Chunk {
  doc_id: number
  title: string
  snippet: string
  uri: string
  score: number
}

/**
 * Response from POST /api/search
 */
export interface SearchResponse {
  answer: string
  chunks: Chunk[]
  used_doc_ids: number[]
}

/**
 * Request body for POST /api/search
 */
export interface SearchRequest {
  query: string
  top_k?: number
}

/**
 * Document metadata from GET /api/docs/:doc_id
 */
export interface DocMetadata {
  doc_id: number
  title: string
  project_id?: string | null
  visibility: 'Public' | 'Private'
  uri: string
  updated_at: string
  language?: string | null
}

/**
 * User's Supabase profile
 */
export interface UserProfile {
  id: string
  email?: string
  display_name?: string
}

/**
 * Message in chat interface
 */
export interface Message {
  id: number
  role: 'user' | 'assistant'
  content: string
  chunks?: Chunk[]      // Citations (only for assistant messages)
  timestamp: Date
}

// Example usage:
//
// const response: SearchResponse = await searchKnowledge("How do I deploy?")
// const chunks: Chunk[] = response.chunks
// const answer: string = response.answer