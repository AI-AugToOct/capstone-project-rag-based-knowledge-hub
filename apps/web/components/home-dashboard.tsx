"use client"

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Checkbox } from "@/components/ui/checkbox"
import { Send, FileText, Calendar } from "lucide-react"
import { motion } from "framer-motion"
import { useState } from "react"

export function HomeDashboard() {
  const [checkedTasks, setCheckedTasks] = useState<number[]>([])

  const previousFiles = [
    { name: "UX Research", icon: "figma" },
    { name: "Product Analytics and Statistics", icon: "miro" },
    { name: "R2 Strategic Goals & Objectives.pdf", icon: "pdf" },
  ]

  const tasks = [
    {
      title: "Design Meeting",
      hasJoinLink: true,
      status: "urgent",
      statusIcon: "red",
      dueDate: "by today",
      dueDateIcon: "red",
    },
    {
      title: "Refine UI components based on user feedback",
      status: "in progress",
      statusIcon: "yellow",
      dueDate: "by today",
      dueDateIcon: "red",
    },
    {
      title: "Review and approve marketing materials",
      status: "urgent",
      statusIcon: "red",
      dueDate: "by today",
      dueDateIcon: "red",
    },
    {
      title: "Prepare presentation for stakeholder meeting",
      status: "to do",
      statusIcon: "gray",
      dueDate: "by tomorrow",
      dueDateIcon: "green",
    },
    {
      title: "Update project documentation",
      status: "in progress",
      statusIcon: "yellow",
      dueDate: "by tomorrow",
      dueDateIcon: "green",
    },
  ]

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
      },
    },
  }

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.4,
        ease: "easeOut",
      },
    },
  }

  const taskVariants = {
    hidden: { opacity: 0, x: -20 },
    visible: {
      opacity: 1,
      x: 0,
      transition: {
        duration: 0.3,
        ease: "easeOut",
      },
    },
  }

  return (
    <div className="flex-1 flex flex-col bg-[#FAFBFC]">
      {/* Main Content */}
      <div className="flex-1 overflow-auto p-8">
        <motion.div
          className="max-w-6xl mx-auto space-y-8"
          variants={containerVariants}
          initial="hidden"
          animate="visible"
        >
          {/* Welcome Header with Highlighter Effect */}
          <motion.div className="space-y-2" variants={itemVariants}>
            <div className="relative inline-block">
              <motion.div
                className="absolute inset-0 bg-blue-200/40 -skew-y-1 rounded-sm"
                style={{
                  left: "-8px",
                  right: "-8px",
                  top: "8px",
                  bottom: "4px",
                }}
                initial={{ scaleX: 0 }}
                animate={{ scaleX: 1 }}
                transition={{ duration: 0.6, ease: "easeOut", delay: 0.2 }}
              />
              <h1 className="relative text-4xl font-bold text-gray-900">Welcome, Jane Doe! 👋</h1>
            </div>
            <p className="text-lg text-gray-500 font-light">How can I help you today?</p>
          </motion.div>

          {/* Summary Cards Section */}
          <motion.div className="grid md:grid-cols-2 gap-6" variants={itemVariants}>
            <motion.div
              whileHover={{
                scale: 1.02,
                rotate: 1,
                y: -4,
                transition: { duration: 0.2 },
              }}
              whileTap={{ scale: 0.98 }}
            >
              <Card
                className="shadow-md border-gray-200 transition-all duration-200 cursor-pointer"
                style={{ backgroundColor: "#FFFBEB" }}
              >
                <CardHeader>
                  <CardTitle className="text-base font-semibold text-gray-900">Previously viewed files</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  {previousFiles.map((file, idx) => (
                    <motion.div
                      key={idx}
                      className="flex items-center gap-3 p-2 rounded-lg hover:bg-yellow-100/50 transition-colors"
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.4 + idx * 0.1 }}
                      whileHover={{ x: 4 }}
                    >
                      <div className="w-8 h-8 rounded flex items-center justify-center">
                        {file.icon === "figma" && (
                          <svg className="w-6 h-6" viewBox="0 0 24 24" fill="none">
                            <path d="M8 24c2.208 0 4-1.792 4-4v-4H8c-2.208 0-4 1.792-4 4s1.792 4 4 4z" fill="#0ACF83" />
                            <path d="M4 12c0-2.208 1.792-4 4-4h4v8H8c-2.208 0-4-1.792-4-4z" fill="#A259FF" />
                            <path d="M4 4c0-2.208 1.792-4 4-4h4v8H8C5.792 8 4 6.208 4 4z" fill="#F24E1E" />
                            <path d="M12 0h4c2.208 0 4 1.792 4 4s-1.792 4-4 4h-4V0z" fill="#FF7262" />
                            <path d="M20 12c0 2.208-1.792 4-4 4s-4-1.792-4-4 1.792-4 4-4 4 1.792 4 4z" fill="#1ABCFE" />
                          </svg>
                        )}
                        {file.icon === "miro" && (
                          <svg className="w-6 h-6" viewBox="0 0 24 24" fill="none">
                            <path
                              d="M17.392 0H13.9L17 10.444 10.444 0H6.949l3.102 10.444L3.494 0H0l5.05 17.639L2.172 24h3.494l2.878-6.361L11.422 24h3.494l-2.878-6.361L17.088 24h3.494l-2.878-6.361L23.753 0h-3.494l-6.507 10.444z"
                              fill="#FFD02F"
                            />
                          </svg>
                        )}
                        {file.icon === "pdf" && <FileText className="w-6 h-6 text-red-600" />}
                      </div>
                      <span className="text-sm text-gray-700 font-medium">{file.name}</span>
                    </motion.div>
                  ))}
                </CardContent>
              </Card>
            </motion.div>

            {/* Summarize Last Meeting */}
            <motion.div whileHover={{ scale: 1.02 }} transition={{ duration: 0.2 }}>
              <Card className="shadow-sm border-gray-200 bg-white">
                <CardHeader>
                  <CardTitle className="text-base font-semibold text-gray-900">Summarize your last meeting</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-start gap-4 p-3 rounded-lg bg-gray-50">
                    <Avatar className="w-12 h-12">
                      <AvatarImage src="/professional-woman-diverse.png" />
                      <AvatarFallback>UX</AvatarFallback>
                    </Avatar>
                    <div className="flex-1 space-y-1">
                      <h4 className="text-sm font-semibold text-gray-900">UX Strategy Meet up</h4>
                      <div className="flex items-center gap-2 text-xs text-gray-500">
                        <Calendar className="w-3 h-3" />
                        <span>1 Apr 2025, 14:00 PM</span>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          </motion.div>

          {/* Suggested Tasks Section */}
          <motion.div className="space-y-4" variants={itemVariants}>
            <h2 className="text-xl font-semibold text-gray-900">Suggested Task</h2>
            <div className="grid md:grid-cols-2 gap-4">
              <motion.button
                className="p-6 bg-white border border-gray-200 rounded-xl shadow-sm hover:shadow-md hover:border-blue-300 transition-all text-left"
                whileHover={{ scale: 1.03, y: -2 }}
                whileTap={{ scale: 0.98 }}
              >
                <span className="text-base font-medium text-gray-900">Conduct UX Research</span>
              </motion.button>
              <motion.button
                className="p-6 bg-white border border-gray-200 rounded-xl shadow-sm hover:shadow-md hover:border-blue-300 transition-all text-left"
                whileHover={{ scale: 1.03, y: -2 }}
                whileTap={{ scale: 0.98 }}
              >
                <span className="text-base font-medium text-gray-900">Write a prospect email</span>
              </motion.button>
            </div>
          </motion.div>

          {/* My Tasks Section */}
          <motion.div className="space-y-4" variants={itemVariants}>
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-semibold text-gray-900">
                My Tasks <span className="text-gray-400 font-normal">(13)</span>
              </h2>
              <div className="flex items-center gap-3">
                <div className="relative">
                  <div className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 flex items-center justify-center">
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" className="text-gray-400">
                      <circle cx="7" cy="7" r="5.5" stroke="currentColor" strokeWidth="1.5" />
                      <path d="M11 11L14 14" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
                      <text x="7" y="9.5" fontSize="7" fontWeight="600" fill="currentColor" textAnchor="middle">
                        Q
                      </text>
                    </svg>
                  </div>
                  <Input placeholder="Search for name..." className="pl-9 w-64 bg-white border-gray-200" />
                </div>
                <motion.button
                  className="px-4 py-2 bg-white border-2 rounded-lg font-medium text-sm text-gray-900 hover:bg-purple-50 transition-colors"
                  style={{
                    borderColor: "#C4B5FD",
                    borderRadius: "8px",
                    boxShadow: "2px 2px 0px rgba(196, 181, 253, 0.3)",
                  }}
                  whileHover={{
                    rotate: [0, -2, 2, -2, 0],
                    transition: { duration: 0.4 },
                  }}
                  whileTap={{ scale: 0.95 }}
                >
                  Prioritize Tasks
                </motion.button>
              </div>
            </div>

            {/* Tasks List */}
            <Card className="shadow-sm border-gray-200">
              <CardContent className="p-0">
                <motion.div
                  className="divide-y divide-gray-100"
                  variants={containerVariants}
                  initial="hidden"
                  animate="visible"
                >
                  {tasks.map((task, idx) => (
                    <motion.div
                      key={idx}
                      className="flex items-center gap-4 p-4 hover:bg-gray-50 transition-colors"
                      variants={taskVariants}
                      whileHover={{ x: 4, backgroundColor: "#F9FAFB" }}
                    >
                      <motion.div
                        whileTap={{ scale: 0.9 }}
                        animate={
                          checkedTasks.includes(idx)
                            ? {
                                scale: [1, 1.2, 1],
                                transition: { duration: 0.3 },
                              }
                            : {}
                        }
                      >
                        <Checkbox
                          className="border-gray-300"
                          checked={checkedTasks.includes(idx)}
                          onCheckedChange={(checked) => {
                            if (checked) {
                              setCheckedTasks([...checkedTasks, idx])
                            } else {
                              setCheckedTasks(checkedTasks.filter((i) => i !== idx))
                            }
                          }}
                        />
                      </motion.div>
                      <div className="flex-1 flex items-center gap-2">
                        <motion.p
                          className="text-sm font-medium text-gray-900"
                          animate={
                            checkedTasks.includes(idx)
                              ? {
                                  opacity: 0.5,
                                  textDecoration: "line-through",
                                }
                              : {
                                  opacity: 1,
                                  textDecoration: "none",
                                }
                          }
                        >
                          {task.title}
                        </motion.p>
                        {task.hasJoinLink && (
                          <motion.a
                            href="#"
                            className="text-sm font-medium text-blue-600 hover:text-blue-700 hover:underline"
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                          >
                            Join now
                          </motion.a>
                        )}
                      </div>
                      <div className="flex items-center gap-2">
                        <motion.span
                          className="px-3 py-1 rounded-full text-xs font-medium bg-gray-50 text-gray-700 flex items-center gap-1.5"
                          initial={{ scale: 0 }}
                          animate={{ scale: 1 }}
                          transition={{ delay: 0.6 + idx * 0.05, type: "spring", stiffness: 200 }}
                        >
                          <motion.span
                            className="w-2 h-2 rounded-full"
                            style={{
                              backgroundColor:
                                task.statusIcon === "red"
                                  ? "#EF4444"
                                  : task.statusIcon === "yellow"
                                    ? "#F59E0B"
                                    : "#9CA3AF",
                            }}
                            animate={{
                              scale: [1, 1.2, 1],
                            }}
                            transition={{
                              duration: 2,
                              repeat: Number.POSITIVE_INFINITY,
                              repeatDelay: 1,
                            }}
                          />
                          {task.status}
                        </motion.span>
                        <motion.span
                          className="px-3 py-1 rounded-full text-xs font-medium bg-gray-50 text-gray-700 flex items-center gap-1.5"
                          initial={{ scale: 0 }}
                          animate={{ scale: 1 }}
                          transition={{ delay: 0.65 + idx * 0.05, type: "spring", stiffness: 200 }}
                        >
                          <motion.span
                            className="w-2 h-2 rounded-full"
                            style={{
                              backgroundColor: task.dueDateIcon === "green" ? "#10B981" : "#EF4444",
                            }}
                            animate={{
                              scale: [1, 1.2, 1],
                            }}
                            transition={{
                              duration: 2,
                              repeat: Number.POSITIVE_INFINITY,
                              repeatDelay: 1,
                            }}
                          />
                          {task.dueDate}
                        </motion.span>
                      </div>
                    </motion.div>
                  ))}
                </motion.div>
              </CardContent>
            </Card>
          </motion.div>
        </motion.div>
      </div>

      {/* Quick Chat Input Bar */}
      <motion.div
        className="border-t border-gray-200 bg-white p-4"
        initial={{ y: 100, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.8, duration: 0.4 }}
      >
        <div className="max-w-6xl mx-auto">
          <motion.div
            className="flex items-center gap-2 bg-gray-50 border border-gray-200 rounded-xl px-4 py-3"
            whileFocus={{ borderColor: "#3B82F6", boxShadow: "0 0 0 3px rgba(59, 130, 246, 0.1)" }}
          >
            <Input
              placeholder="💡 Ask or search for anything. Use @ to tag a file or collection."
              className="flex-1 border-0 bg-transparent focus-visible:ring-0 focus-visible:ring-offset-0 text-sm"
            />
            <motion.div whileHover={{ scale: 1.1 }} whileTap={{ scale: 0.9 }}>
              <Button size="icon" variant="ghost" className="shrink-0 text-gray-400 hover:text-gray-600">
                <Send className="h-4 w-4" />
              </Button>
            </motion.div>
          </motion.div>
        </div>
      </motion.div>
    </div>
  )
}
