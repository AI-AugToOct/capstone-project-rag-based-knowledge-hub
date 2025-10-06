"use client"

import { motion } from "framer-motion"
import { Button } from "@/components/ui/button"
import { Shield, Sparkles, FileText, RefreshCw } from "lucide-react"
import Image from "next/image"
import Link from "next/link"

export function AiHubLanding() {
  return (
    <div className="min-h-screen bg-white">
      {/* Hero Section */}
      <section className="relative overflow-hidden px-4 py-12 md:py-20">
        <div className="absolute right-0 top-0 h-full w-full md:w-1/2">
          <Image src="/banner-wave.png" alt="" fill className="object-cover object-left" priority />
        </div>

        <div className="relative mx-auto max-w-7xl">
          <div className="grid items-center gap-8 md:grid-cols-2">
            {/* Left content */}
            <motion.div
              initial={{ opacity: 0, x: -50 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6 }}
              className="z-10"
            >
              <h1 className="mb-6 text-4xl font-bold leading-tight text-gray-900 md:text-5xl lg:text-6xl">
                All your company's knowledge, in <span className="text-[#3E4DF9]">one</span>
                <br />
                secure <span className="text-[#3E4DF9]">AI-powered hub</span>
              </h1>
              <p className="mb-8 text-lg text-gray-600">
                No more confusion | one place for every answer, document, and project detail.
              </p>
              <div className="flex flex-wrap gap-4">
                <Link href="/login">
                  <Button size="lg" className="rounded-full bg-[#3E4DF9] px-8 text-white hover:bg-[#3E4DF9]/90">
                    Log In
                  </Button>
                </Link>
                <Button
                  size="lg"
                  variant="outline"
                  className="rounded-full border-2 border-[#3E4DF9] text-[#3E4DF9] hover:bg-[#3E4DF9]/10 bg-transparent"
                >
                  Watch Demo
                </Button>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="relative z-10 flex justify-center md:justify-end"
            >
              <div className="relative h-[300px] w-[300px] md:h-[450px] md:w-[450px]">
                <Image src="/character.png" alt="AI Hub Character" fill className="object-contain" priority />
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="px-4 py-16">
        <div className="mx-auto max-w-7xl">
          <div className="grid gap-8 md:grid-cols-3">
            <motion.div
              initial={{ opacity: 0, y: 50, scale: 0.9 }}
              whileInView={{ opacity: 1, y: 0, scale: 1 }}
              viewport={{ once: true, margin: "-100px" }}
              transition={{ duration: 0.6, ease: "easeOut" }}
              className="text-center"
            >
              <div className="mb-2 text-5xl font-bold text-[#3E4DF9]">85%</div>
              <p className="text-gray-600">faster information retrieval</p>
            </motion.div>
            <motion.div
              initial={{ opacity: 0, y: 50, scale: 0.9 }}
              whileInView={{ opacity: 1, y: 0, scale: 1 }}
              viewport={{ once: true, margin: "-100px" }}
              transition={{ duration: 0.6, delay: 0.15, ease: "easeOut" }}
              className="text-center"
            >
              <div className="mb-2 text-5xl font-bold text-[#3E4DF9]">70%</div>
              <p className="text-gray-600">reduction in onboarding time</p>
            </motion.div>
            <motion.div
              initial={{ opacity: 0, y: 50, scale: 0.9 }}
              whileInView={{ opacity: 1, y: 0, scale: 1 }}
              viewport={{ once: true, margin: "-100px" }}
              transition={{ duration: 0.6, delay: 0.3, ease: "easeOut" }}
              className="text-center"
            >
              <div className="mb-2 text-5xl font-bold text-[#3E4DF9]">95%</div>
              <p className="text-gray-600">improvement in data confidentiality</p>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="px-4 py-16">
        <div className="mx-auto max-w-7xl">
          <motion.h2
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="mb-16 text-center text-4xl font-bold text-gray-900"
          >
            Feature
          </motion.h2>

          <div className="space-y-16">
            {/* Feature 1 - Seamless Handover Support */}
            <motion.div
              initial={{ opacity: 0, y: 60, scale: 0.95 }}
              whileInView={{ opacity: 1, y: 0, scale: 1 }}
              viewport={{ once: true, margin: "-100px" }}
              transition={{ duration: 0.7, ease: "easeOut" }}
              className="grid items-center gap-3 md:grid-cols-2"
            >
              <div className="flex justify-center md:justify-start">
                <div className="flex h-32 w-32 items-center justify-center rounded-2xl bg-[#3E4DF9]/10">
                  <RefreshCw className="h-16 w-16 text-[#3E4DF9]" />
                </div>
              </div>
              <div>
                <h3 className="mb-3 text-2xl font-bold text-[#1e3a8a]">Seamless Handover Support</h3>
                <p className="text-gray-600">
                  When employees transfer roles or leave the organization, all their project insights, documents, and
                  conversations remain stored and searchable, ensuring zero knowledge loss and smooth continuation of
                  work.
                </p>
              </div>
            </motion.div>

            {/* Feature 2 - Authorized Access Protection */}
            <motion.div
              initial={{ opacity: 0, y: 60, scale: 0.95 }}
              whileInView={{ opacity: 1, y: 0, scale: 1 }}
              viewport={{ once: true, margin: "-100px" }}
              transition={{ duration: 0.7, ease: "easeOut" }}
              className="grid items-center gap-3 md:grid-cols-2"
            >
              <div className="order-2 md:order-1">
                <h3 className="mb-3 text-2xl font-bold text-[#1e3a8a]">Authorized Access Protection</h3>
                <p className="text-gray-600">
                  Protects organizational confidentiality by giving each employee access only to their department and
                  assigned projects, reducing risks of unauthorized data exposure.
                </p>
              </div>
              <div className="order-1 flex justify-center md:order-2 md:justify-end">
                <div className="flex h-32 w-32 items-center justify-center rounded-2xl bg-[#3E4DF9]/10">
                  <Shield className="h-16 w-16 text-[#3E4DF9]" />
                </div>
              </div>
            </motion.div>

            {/* Feature 3 - AI Knowledge Chatbot */}
            <motion.div
              initial={{ opacity: 0, y: 60, scale: 0.95 }}
              whileInView={{ opacity: 1, y: 0, scale: 1 }}
              viewport={{ once: true, margin: "-100px" }}
              transition={{ duration: 0.7, ease: "easeOut" }}
              className="grid items-center gap-3 md:grid-cols-2"
            >
              <div className="flex justify-center md:justify-start">
                <div className="flex h-32 w-32 items-center justify-center rounded-2xl bg-[#3E4DF9]/10">
                  <Sparkles className="h-16 w-16 text-[#3E4DF9]" />
                </div>
              </div>
              <div>
                <h3 className="mb-3 text-2xl font-bold text-[#1e3a8a]">AI Knowledge Chatbot</h3>
                <p className="text-gray-600">
                  An intelligent assistant that answers employee questions in seconds and provides verified,
                  source-backed references, making information retrieval effortless and reliable.
                </p>
              </div>
            </motion.div>

            {/* Feature 4 - Easy Information Access */}
            <motion.div
              initial={{ opacity: 0, y: 60, scale: 0.95 }}
              whileInView={{ opacity: 1, y: 0, scale: 1 }}
              viewport={{ once: true, margin: "-100px" }}
              transition={{ duration: 0.7, ease: "easeOut" }}
              className="grid items-center gap-3 md:grid-cols-2"
            >
              <div className="order-2 md:order-1">
                <h3 className="mb-3 text-2xl font-bold text-[#1e3a8a]">Easy Information Access</h3>
                <p className="text-gray-600">
                  All company knowledge policies, project files, and procedures is stored in one organized hub, allowing
                  employees to instantly find what they need without searching across multiple platforms.
                </p>
              </div>
              <div className="order-1 flex justify-center md:order-2 md:justify-end">
                <div className="flex h-32 w-32 items-center justify-center rounded-2xl bg-[#3E4DF9]/10">
                  <FileText className="h-16 w-16 text-[#3E4DF9]" />
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Bottom decorative wave */}
      <div className="relative h-[400px] overflow-hidden">
        <div className="absolute bottom-0 left-0 h-full w-full">
          <svg viewBox="0 0 500 400" className="h-full w-full" preserveAspectRatio="none">
            <path d="M0,200 Q125,100 250,150 T500,200 L500,400 L0,400 Z" fill="url(#gradient1)" />
            <path d="M0,250 Q125,180 250,220 T500,280 L500,400 L0,400 Z" fill="url(#gradient2)" />
            <defs>
              <linearGradient id="gradient1" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#8B92FF" />
                <stop offset="100%" stopColor="#5B62FF" />
              </linearGradient>
              <linearGradient id="gradient2" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#5B62FF" />
                <stop offset="100%" stopColor="#3E4DF9" />
              </linearGradient>
            </defs>
          </svg>
        </div>
      </div>
    </div>
  )
}
