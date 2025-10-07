"use client"

import { LayoutGrid, Sparkles, FileText, Handshake, Search, Filter, ArrowUpRight, FileIcon, Loader2 } from "lucide-react"
import Image from "next/image"
import Link from "next/link"
import { useState, useEffect } from "react"
import { motion } from "framer-motion"
import { getHandovers, createHandover, searchEmployees } from "@/lib/api"
import type { HandoverResponse } from "@/types"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"

interface Handover {
  id: string
  projectName: string
  personName: string
  personRole: string
  personAvatar: string
  date: string
  status: "pending" | "acknowledged" | "completed"
  files: { name: string; icon: string }[]
  rawData: HandoverResponse
}

export function HandoversSection() {
  const [activeNav, setActiveNav] = useState("HandOvers")
  const [searchQuery, setSearchQuery] = useState("")
  const [receivedHandovers, setReceivedHandovers] = useState<Handover[]>([])
  const [sentHandovers, setSentHandovers] = useState<Handover[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedHandover, setSelectedHandover] = useState<Handover | null>(null)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false)
  const [employeeSearch, setEmployeeSearch] = useState("")
  const [employeeResults, setEmployeeResults] = useState<Array<{employee_id: string, email: string, display_name: string}>>([])
  const [selectedEmployee, setSelectedEmployee] = useState<{employee_id: string, email: string, display_name: string} | null>(null)
  const [showResults, setShowResults] = useState(false)

  const navItems = [
    { name: "Home", icon: LayoutGrid, href: "/home" },
    { name: "Chatbot", icon: Sparkles, href: "/chatbot" },
    { name: "Documents", icon: FileText, href: "/documents" },
    { name: "HandOvers", icon: Handshake, href: "/handovers" },
  ]

  useEffect(() => {
    loadHandovers()
  }, [])

  const loadHandovers = async () => {
    try {
      setIsLoading(true)
      setError(null)
      const data = await getHandovers()

      // Transform backend data to UI format
      const transformHandover = (h: HandoverResponse, isReceived: boolean): Handover => ({
        id: h.handover_id.toString(),
        projectName: h.title,
        personName: isReceived ? "From Employee" : "To Employee", // TODO: Get real names
        personRole: h.project_id || "General",
        personAvatar: "/professional-avatar.png",
        date: new Date(h.created_at).toLocaleDateString(),
        status: h.status,
        files: h.resources?.map(r => ({
          name: r.title,
          icon: r.type === 'doc' ? 'doc' : 'link'
        })) || [],
        rawData: h
      })

      setReceivedHandovers(data.received.map(h => transformHandover(h, true)))
      setSentHandovers(data.sent.map(h => transformHandover(h, false)))
    } catch (err) {
      console.error("[Handovers] Load failed:", err)
      setError(err instanceof Error ? err.message : "Failed to load handovers")
    } finally {
      setIsLoading(false)
    }
  }

  const cardVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: (i: number) => ({
      opacity: 1,
      y: 0,
      transition: {
        delay: i * 0.1,
        duration: 0.5,
        ease: "easeOut",
      },
    }),
  }

  const HandoverCard = ({ handover, index }: { handover: Handover; index: number }) => (
    <motion.div
      custom={index}
      initial="hidden"
      animate="visible"
      variants={cardVariants}
      whileHover={{ y: -4, transition: { duration: 0.2 } }}
      onClick={() => {
        setSelectedHandover(handover)
        setIsModalOpen(true)
      }}
      className="group cursor-pointer rounded-2xl bg-white p-6 shadow-sm transition-shadow hover:shadow-lg"
    >
      {/* Header with person info */}
      <div className="mb-4 flex items-start justify-between">
        <div className="flex items-center gap-3">
          <div className="relative h-12 w-12 overflow-hidden rounded-full bg-gray-200">
            <Image
              src={handover.personAvatar || "/placeholder.svg"}
              alt={handover.personName}
              fill
              className="object-cover"
            />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900">{handover.personName}</h3>
            <p className="text-sm text-gray-500">{handover.personRole}</p>
          </div>
        </div>
        <ArrowUpRight className="h-5 w-5 text-[#3E4DF9] opacity-0 transition-opacity group-hover:opacity-100" />
      </div>

      {/* Project name */}
      <h4 className="mb-2 text-xl font-bold text-gray-900">{handover.projectName}</h4>

      {/* Date and status */}
      <div className="mb-4 flex items-center gap-3">
        <span className="text-sm text-gray-500">{handover.date}</span>
        <span
          className={`rounded-full px-3 py-1 text-xs font-medium ${
            handover.status === "Completed" ? "bg-green-100 text-green-700" : "bg-yellow-100 text-yellow-700"
          }`}
        >
          {handover.status}
        </span>
      </div>

      {/* Files */}
      <div className="space-y-2">
        {handover.files.map((file, idx) => (
          <div
            key={idx}
            className="flex items-center gap-2 rounded-lg bg-[#3E4DF9]/5 p-3 transition-colors hover:bg-[#3E4DF9]/10"
          >
            <FileIcon className="h-5 w-5 text-[#3E4DF9]" />
            <span className="flex-1 text-sm text-gray-700">{file.name}</span>
            <ArrowUpRight className="h-4 w-4 text-[#3E4DF9]" />
          </div>
        ))}
      </div>
    </motion.div>
  )

  return (
    <div className="flex min-h-screen bg-gray-50">
      {/* Sidebar */}
      <aside className="relative w-64 bg-gradient-to-b from-[#5B62FF] via-[#4651F9] to-[#3E4DF9] text-white">
        {/* Decorative wave on the right edge */}
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
          {/* Profile Section */}
          <div className="mb-12 flex items-center gap-3">
            <div className="relative h-12 w-12 overflow-hidden rounded-full bg-white">
              <Image src="/professional-avatar.png" alt="Omar Saad" fill className="object-cover" />
            </div>
            <div>
              <h2 className="text-lg font-bold">Omar Saad</h2>
              <p className="text-sm text-white/80">AI developer</p>
            </div>
          </div>

          {/* Navigation */}
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

      {/* Main Content */}
      <main className="flex-1 p-8">
        <div className="mx-auto max-w-7xl">
          {/* Header with search and filter */}
          <div className="mb-8 flex items-center justify-between">
            <div className="flex flex-1 items-center gap-4">
              <div className="relative flex-1 max-w-xl">
                <Search className="absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search handovers..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full rounded-xl border border-gray-200 py-3 pl-12 pr-4 text-gray-900 placeholder-gray-400 focus:border-[#3E4DF9] focus:outline-none focus:ring-2 focus:ring-[#3E4DF9]/20"
                />
              </div>
              <button className="rounded-xl border border-gray-200 bg-white p-3 text-gray-600 transition-colors hover:bg-gray-50">
                <Filter className="h-5 w-5" />
              </button>
            </div>
            <div className="ml-4 flex items-center gap-3">
              <div className="relative h-10 w-10 overflow-hidden rounded-full bg-gray-200">
                <Image src="/professional-avatar.png" alt="User" fill className="object-cover" />
              </div>
            </div>
          </div>

          {/* Page title with filter/sort options */}
          <div className="mb-6 flex items-center justify-between">
            <h1 className="text-4xl font-bold text-gray-900">Handover</h1>
            <div className="flex items-center gap-4">
              <button
                onClick={() => setIsCreateModalOpen(true)}
                className="rounded-full bg-[#3E4DF9] px-6 py-3 text-sm font-medium text-white transition-all hover:bg-[#3240D9] hover:shadow-lg"
              >
                + Create Handover
              </button>
              <div className="flex items-center gap-4 text-sm text-gray-600">
                <button className="font-medium hover:text-[#3E4DF9]">Filter</button>
                <button className="font-medium hover:text-[#3E4DF9]">Sort</button>
                <button className="rounded-lg border border-gray-200 p-2 hover:bg-gray-50">
                  <LayoutGrid className="h-4 w-4" />
                </button>
              </div>
            </div>
          </div>

          {/* Loading State */}
          {isLoading && (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-[#3E4DF9]" />
              <span className="ml-3 text-gray-600">Loading handovers...</span>
            </div>
          )}

          {/* Error State */}
          {error && (
            <div className="rounded-lg bg-red-50 p-4 text-red-600">
              {error}
            </div>
          )}

          {/* Two-column layout for Received and Sent */}
          {!isLoading && !error && (
            <div className="grid gap-8 md:grid-cols-2">
              {/* Received Handovers */}
              <div>
                <h2 className="mb-4 text-2xl font-bold text-gray-900">Received</h2>
                <div className="space-y-4">
                  {receivedHandovers.length > 0 ? (
                    receivedHandovers.map((handover, index) => (
                      <HandoverCard key={handover.id} handover={handover} index={index} />
                    ))
                  ) : (
                    <p className="text-gray-500">No received handovers</p>
                  )}
                </div>
              </div>

              {/* Sent Handovers */}
              <div>
                <h2 className="mb-4 text-2xl font-bold text-gray-900">Sent</h2>
                <div className="space-y-4">
                  {sentHandovers.length > 0 ? (
                    sentHandovers.map((handover, index) => (
                      <HandoverCard key={handover.id} handover={handover} index={index + receivedHandovers.length} />
                    ))
                  ) : (
                    <p className="text-gray-500">No sent handovers</p>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      </main>

      {/* Handover Detail Modal */}
      {isModalOpen && selectedHandover && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4" onClick={() => setIsModalOpen(false)}>
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="relative max-h-[90vh] w-full max-w-3xl overflow-y-auto rounded-2xl bg-white p-8 shadow-2xl"
            onClick={(e) => e.stopPropagation()}
          >
            <button
              onClick={() => setIsModalOpen(false)}
              className="absolute right-6 top-6 rounded-full p-2 text-gray-400 hover:bg-gray-100 hover:text-gray-600"
            >
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>

            <h2 className="mb-6 pr-10 text-3xl font-bold text-gray-900">{selectedHandover.projectName}</h2>

            <div className="space-y-6">
              {/* Context */}
              {selectedHandover.rawData.context && (
                <div>
                  <h3 className="mb-2 font-semibold text-gray-700">Context</h3>
                  <p className="text-gray-600">{selectedHandover.rawData.context}</p>
                </div>
              )}

              {/* Current Status */}
              {selectedHandover.rawData.current_status && (
                <div>
                  <h3 className="mb-2 font-semibold text-gray-700">Current Status</h3>
                  <p className="text-gray-600">{selectedHandover.rawData.current_status}</p>
                </div>
              )}

              {/* Next Steps */}
              {selectedHandover.rawData.next_steps && selectedHandover.rawData.next_steps.length > 0 && (
                <div>
                  <h3 className="mb-2 font-semibold text-gray-700">Next Steps</h3>
                  <ul className="space-y-2">
                    {selectedHandover.rawData.next_steps.map((step, idx) => (
                      <li key={idx} className="flex items-center gap-2">
                        <input
                          type="checkbox"
                          checked={step.done}
                          onChange={async () => {
                            // Optimistic update - change UI immediately
                            const updatedSteps = [...selectedHandover.rawData.next_steps!]
                            updatedSteps[idx] = { ...step, done: !step.done }

                            setSelectedHandover({
                              ...selectedHandover,
                              rawData: {
                                ...selectedHandover.rawData,
                                next_steps: updatedSteps
                              }
                            })

                            // TODO: Save to backend
                            // For now, just update local state
                            // Later: call updateHandover API with new next_steps
                          }}
                          className="h-4 w-4 cursor-pointer rounded border-gray-300 text-[#3E4DF9] focus:ring-[#3E4DF9]"
                        />
                        <span className={step.done ? "text-gray-400 line-through" : "text-gray-600"}>{step.task}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Resources */}
              {selectedHandover.rawData.resources && selectedHandover.rawData.resources.length > 0 && (
                <div>
                  <h3 className="mb-2 font-semibold text-gray-700">Resources</h3>
                  <div className="space-y-2">
                    {selectedHandover.rawData.resources.map((resource, idx) => (
                      <a
                        key={idx}
                        href={resource.url || '#'}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-2 rounded-lg bg-blue-50 p-3 text-blue-600 transition-colors hover:bg-blue-100"
                      >
                        <FileIcon className="h-5 w-5" />
                        <span className="flex-1">{resource.title}</span>
                        <ArrowUpRight className="h-4 w-4" />
                      </a>
                    ))}
                  </div>
                </div>
              )}

              {/* Contacts */}
              {selectedHandover.rawData.contacts && selectedHandover.rawData.contacts.length > 0 && (
                <div>
                  <h3 className="mb-2 font-semibold text-gray-700">Contacts</h3>
                  <div className="space-y-2">
                    {selectedHandover.rawData.contacts.map((contact, idx) => (
                      <div key={idx} className="rounded-lg bg-gray-50 p-3">
                        <p className="font-medium text-gray-900">{contact.name}</p>
                        <p className="text-sm text-gray-600">{contact.role}</p>
                        <p className="text-sm text-blue-600">{contact.email}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Additional Notes */}
              {selectedHandover.rawData.additional_notes && (
                <div>
                  <h3 className="mb-2 font-semibold text-gray-700">Additional Notes</h3>
                  <p className="rounded-lg bg-gray-50 p-3 text-gray-600">{selectedHandover.rawData.additional_notes}</p>
                </div>
              )}

              {/* Status Badge */}
              <div className="flex items-center gap-3 border-t pt-4">
                <span className="text-sm text-gray-500">Status:</span>
                <span
                  className={`rounded-full px-4 py-1 text-sm font-medium ${
                    selectedHandover.status === "completed"
                      ? "bg-green-100 text-green-700"
                      : selectedHandover.status === "acknowledged"
                      ? "bg-blue-100 text-blue-700"
                      : "bg-yellow-100 text-yellow-700"
                  }`}
                >
                  {selectedHandover.status}
                </span>
              </div>
            </div>
          </motion.div>
        </div>
      )}

      {/* Create Handover Modal */}
      {isCreateModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4" onClick={() => setIsCreateModalOpen(false)}>
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="relative max-h-[90vh] w-full max-w-2xl overflow-y-auto rounded-2xl bg-white p-8 shadow-2xl"
            onClick={(e) => e.stopPropagation()}
          >
            <button
              onClick={() => setIsCreateModalOpen(false)}
              className="absolute right-6 top-6 rounded-full p-2 text-gray-400 hover:bg-gray-100 hover:text-gray-600"
            >
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>

            <h2 className="mb-6 pr-10 text-3xl font-bold text-gray-900">Create New Handover</h2>

            <form onSubmit={async (e) => {
              e.preventDefault()
              const formData = new FormData(e.currentTarget)

              try {
                await createHandover({
                  to_employee_id: formData.get('recipient') as string,
                  title: formData.get('title') as string,
                  project_id: formData.get('project') as string || null,
                  context: formData.get('context') as string || null,
                  current_status: formData.get('currentStatus') as string || null,
                  additional_notes: formData.get('notes') as string || null,
                })

                setIsCreateModalOpen(false)
                loadHandovers() // Refresh list
              } catch (err) {
                console.error('Failed to create handover:', err)
                alert('Failed to create handover: ' + (err instanceof Error ? err.message : 'Unknown error'))
              }
            }} className="space-y-6">
              {/* Title */}
              <div>
                <label className="mb-2 block text-sm font-medium text-gray-700">Title *</label>
                <Input
                  name="title"
                  placeholder="e.g., Project Alpha Handover"
                  required
                  className="w-full"
                />
              </div>

              {/* Recipient Autocomplete */}
              <div className="relative">
                <label className="mb-2 block text-sm font-medium text-gray-700">Send to *</label>
                <Input
                  type="text"
                  value={selectedEmployee ? `${selectedEmployee.display_name} (${selectedEmployee.email})` : employeeSearch}
                  onChange={async (e) => {
                    const value = e.target.value
                    setEmployeeSearch(value)
                    setSelectedEmployee(null)

                    if (value.length >= 2) {
                      try {
                        const results = await searchEmployees(value)
                        setEmployeeResults(results)
                        setShowResults(true)
                      } catch (err) {
                        console.error('Search failed:', err)
                      }
                    } else {
                      setEmployeeResults([])
                      setShowResults(false)
                    }
                  }}
                  onFocus={() => {
                    if (employeeResults.length > 0) setShowResults(true)
                  }}
                  onBlur={() => {
                    setTimeout(() => setShowResults(false), 200)
                  }}
                  placeholder="Type name or email..."
                  className="w-full"
                />
                <input type="hidden" name="recipient" value={selectedEmployee?.employee_id || ''} required />

                {/* Results dropdown */}
                {showResults && employeeResults.length > 0 && (
                  <div className="absolute z-10 mt-1 w-full rounded-lg border border-gray-200 bg-white shadow-lg">
                    {employeeResults.map((emp) => (
                      <div
                        key={emp.employee_id}
                        onClick={() => {
                          setSelectedEmployee(emp)
                          setShowResults(false)
                        }}
                        className="cursor-pointer px-4 py-3 hover:bg-gray-50"
                      >
                        <p className="font-medium text-gray-900">{emp.display_name}</p>
                        <p className="text-sm text-gray-500">{emp.email}</p>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Project */}
              <div>
                <label className="mb-2 block text-sm font-medium text-gray-700">Project</label>
                <select
                  name="project"
                  className="w-full rounded-xl border border-gray-200 px-4 py-3 text-gray-900 focus:border-[#3E4DF9] focus:outline-none focus:ring-2 focus:ring-[#3E4DF9]/20"
                >
                  <option value="">Select project...</option>
                  <option value="demo-project">Demo Project</option>
                  <option value="atlas-api">Atlas API</option>
                  <option value="phoenix-ui">Phoenix UI</option>
                  <option value="internal-tools">Internal Tools</option>
                </select>
              </div>

              {/* Context */}
              <div>
                <label className="mb-2 block text-sm font-medium text-gray-700">Context</label>
                <textarea
                  name="context"
                  placeholder="Why is this handover happening?"
                  rows={3}
                  className="w-full rounded-xl border border-gray-200 px-4 py-3 text-gray-900 focus:border-[#3E4DF9] focus:outline-none focus:ring-2 focus:ring-[#3E4DF9]/20"
                />
              </div>

              {/* Current Status */}
              <div>
                <label className="mb-2 block text-sm font-medium text-gray-700">Current Status</label>
                <textarea
                  name="currentStatus"
                  placeholder="What's the current state of the project?"
                  rows={2}
                  className="w-full rounded-xl border border-gray-200 px-4 py-3 text-gray-900 focus:border-[#3E4DF9] focus:outline-none focus:ring-2 focus:ring-[#3E4DF9]/20"
                />
              </div>

              {/* Additional Notes */}
              <div>
                <label className="mb-2 block text-sm font-medium text-gray-700">Additional Notes</label>
                <textarea
                  name="notes"
                  placeholder="Any other important information..."
                  rows={2}
                  className="w-full rounded-xl border border-gray-200 px-4 py-3 text-gray-900 focus:border-[#3E4DF9] focus:outline-none focus:ring-2 focus:ring-[#3E4DF9]/20"
                />
              </div>

              {/* Buttons */}
              <div className="flex gap-3 border-t pt-6">
                <Button
                  type="button"
                  onClick={() => setIsCreateModalOpen(false)}
                  variant="outline"
                  className="flex-1"
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  className="flex-1 bg-[#3E4DF9] hover:bg-[#3240D9]"
                >
                  Create Handover
                </Button>
              </div>
            </form>
          </motion.div>
        </div>
      )}
    </div>
  )
}
