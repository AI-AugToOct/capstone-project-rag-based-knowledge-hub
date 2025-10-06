import { Card, CardContent } from "@/components/ui/card"
import { Zap, Users, BarChart3, Shield } from "lucide-react"

const features = [
  {
    icon: Zap,
    title: "Lightning Fast",
    description: "Experience blazing-fast performance with our optimized infrastructure. Deploy in seconds, not hours.",
  },
  {
    icon: Users,
    title: "Team Collaboration",
    description:
      "Work seamlessly with your team. Real-time updates, comments, and shared workspaces keep everyone aligned.",
  },
  {
    icon: BarChart3,
    title: "Advanced Analytics",
    description: "Make data-driven decisions with comprehensive analytics and insights. Track what matters most.",
  },
  {
    icon: Shield,
    title: "Enterprise Security",
    description:
      "Bank-level encryption and compliance certifications. Your data is protected with industry-leading security.",
  },
]

export function FeaturesSection() {
  return (
    <section id="features" className="py-20 md:py-32">
      <div className="container">
        <div className="mx-auto mb-16 max-w-2xl text-center">
          <h2 className="mb-4 font-sans text-3xl font-bold tracking-tight text-balance md:text-4xl lg:text-5xl">
            Everything you need to succeed
          </h2>
          <p className="text-lg text-muted-foreground text-balance">
            Powerful features designed to help your team work smarter, not harder.
          </p>
        </div>

        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          {features.map((feature, index) => (
            <Card
              key={index}
              className="border-border/50 bg-card transition-all hover:border-primary/50 hover:shadow-lg"
            >
              <CardContent className="p-6">
                <div className="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
                  <feature.icon className="h-6 w-6 text-primary" />
                </div>
                <h3 className="mb-2 font-sans text-xl font-semibold">{feature.title}</h3>
                <p className="text-sm leading-relaxed text-muted-foreground">{feature.description}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  )
}
