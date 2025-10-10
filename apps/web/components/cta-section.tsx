import { Button } from "@/components/ui/button"
import { ArrowRight } from "lucide-react"

export function CtaSection() {
  return (
    <section className="py-20 md:py-32">
      <div className="container">
        <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-[#636ef9] to-[#3e4df9] px-8 py-16 md:px-16 md:py-24">
          <div className="absolute inset-0 bg-[linear-gradient(to_right,#ffffff0a_1px,transparent_1px),linear-gradient(to_bottom,#ffffff0a_1px,transparent_1px)] bg-[size:14px_24px]" />

          <div className="relative mx-auto max-w-3xl text-center">
            <h2 className="mb-6 font-sans text-3xl font-bold tracking-tight text-white text-balance md:text-4xl lg:text-5xl">
              Ready to transform your workflow?
            </h2>
            <p className="mb-8 text-lg text-white/90 text-balance md:text-xl">
              Join thousands of teams already using StreamLine. Start your free trial today—no credit card required.
            </p>
            <div className="flex flex-col items-center justify-center gap-4 sm:flex-row">
              <Button size="lg" variant="secondary" className="gap-2 bg-white text-[#636ef9] hover:bg-white/90">
                Get Started Free
                <ArrowRight className="h-4 w-4" />
              </Button>
              <Button
                size="lg"
                variant="outline"
                className="gap-2 border-white/20 bg-white/10 text-white hover:bg-white/20"
              >
                Schedule a Demo
              </Button>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
