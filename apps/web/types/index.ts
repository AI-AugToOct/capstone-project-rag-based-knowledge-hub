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

/**
 * Handover status enum
 */
export type HandoverStatus = 'pending' | 'acknowledged' | 'completed'

/**
 * Next step item in a handover
 */
export interface NextStep {
  task: string
  done: boolean
}

/**
 * Resource in a handover
 */
export interface Resource {
  type: 'doc' | 'link'
  doc_id?: number
  url?: string
  title: string
}

/**
 * Contact in a handover
 */
export interface Contact {
  name: string
  email: string
  role: string
}

/**
 * Request body for POST /api/handovers
 */
export interface CreateHandoverRequest {
  to_employee_id: string
  title: string
  project_id?: string | null
  context?: string | null
  current_status?: string | null
  next_steps?: NextStep[]
  resources?: Resource[]
  contacts?: Contact[]
  additional_notes?: string | null
  cc_employee_ids?: string[]
}

/**
 * Response from handover endpoints
 */
export interface HandoverResponse {
  handover_id: number
  title: string
  status: HandoverStatus
  from_employee_id: string
  to_employee_id: string
  project_id?: string | null
  context?: string | null
  current_status?: string | null
  next_steps?: NextStep[]
  resources?: Resource[]
  contacts?: Contact[]
  additional_notes?: string | null
  cc_employee_ids?: string[]
  created_at: string
  acknowledged_at?: string | null
  completed_at?: string | null
}

/**
 * Response from GET /api/handovers
 */
export interface HandoversListResponse {
  received: HandoverResponse[]
  sent: HandoverResponse[]
}

/**
 * Request body for PATCH /api/handovers/:id
 */
export interface UpdateHandoverStatusRequest {
  status: HandoverStatus
}

// Example usage:
//
// const response: SearchResponse = await searchKnowledge("How do I deploy?")
// const chunks: Chunk[] = response.chunks
// const answer: string = response.answer