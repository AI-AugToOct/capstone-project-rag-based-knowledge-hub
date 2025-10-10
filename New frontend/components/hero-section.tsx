import { Button } from "@/components/ui/button"
import { ArrowRight, Play } from "lucide-react"

export function HeroSection() {
  return (
    <section className="relative overflow-hidden py-20 md:py-32">
      <div className="absolute inset-0 -z-10 bg-[linear-gradient(to_right,#8080800a_1px,transparent_1px),linear-gradient(to_bottom,#8080800a_1px,transparent_1px)] bg-[size:14px_24px]" />
      <div className="absolute inset-0 -z-10 bg-gradient-to-b from-[#636ef9]/5 via-transparent to-transparent" />

      <div className="container">
        <div className="mx-auto max-w-4xl text-center">
          <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-border bg-muted/50 px-4 py-1.5 text-sm">
            <span className="relative flex h-2 w-2">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-primary opacity-75"></span>
              <span className="relative inline-flex h-2 w-2 rounded-full bg-primary"></span>
            </span>
            <span className="text-muted-foreground">Now available for teams</span>
          </div>

          <h1 className="mb-6 font-sans text-5xl font-bold leading-tight tracking-tight text-balance md:text-6xl lg:text-7xl">
            Streamline your workflow,{" "}
            <span className="bg-gradient-to-r from-[#636ef9] to-[#3e4df9] bg-clip-text text-transparent">
              amplify your results
            </span>
          </h1>

          <p className="mb-10 text-lg text-muted-foreground text-balance md:text-xl">
            The all-in-one platform that helps teams collaborate, automate, and scale their operations. Built for modern
            businesses that move fast.
          </p>

          <div className="flex flex-col items-center justify-center gap-4 sm:flex-row">
            <Button size="lg" className="gap-2 text-base">
              Start Free Trial
              <ArrowRight className="h-4 w-4" />
            </Button>
            <Button size="lg" variant="outline" className="gap-2 text-base bg-transparent">
              <Play className="h-4 w-4" />
              Watch Demo
            </Button>
          </div>

          <p className="mt-6 text-sm text-muted-foreground">
            No credit card required • 14-day free trial • Cancel anytime
          </p>
        </div>
      </div>
    </section>
  )
}
