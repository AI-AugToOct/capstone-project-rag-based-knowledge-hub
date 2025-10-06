import { Card, CardContent } from "@/components/ui/card"
import { Star } from "lucide-react"

const testimonials = [
  {
    name: "Sarah Chen",
    role: "CEO at TechFlow",
    content:
      "StreamLine transformed how our team works. We've seen a 40% increase in productivity since switching. The automation features alone have saved us countless hours.",
    avatar: "/professional-woman-diverse.png",
  },
  {
    name: "Michael Rodriguez",
    role: "Product Manager at InnovateCo",
    content:
      "The best investment we've made this year. The analytics dashboard gives us insights we never had before, and the team collaboration features are second to none.",
    avatar: "/professional-man.jpg",
  },
  {
    name: "Emily Watson",
    role: "CTO at DataSync",
    content:
      "Security was our top concern, and StreamLine exceeded our expectations. The enterprise-grade features at this price point are unmatched in the market.",
    avatar: "/professional-woman-executive.png",
  },
]

export function TestimonialsSection() {
  return (
    <section id="testimonials" className="bg-muted/30 py-20 md:py-32">
      <div className="container">
        <div className="mx-auto mb-16 max-w-2xl text-center">
          <h2 className="mb-4 font-sans text-3xl font-bold tracking-tight text-balance md:text-4xl lg:text-5xl">
            Loved by teams worldwide
          </h2>
          <p className="text-lg text-muted-foreground text-balance">
            Join thousands of companies already using StreamLine to power their operations.
          </p>
        </div>

        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {testimonials.map((testimonial, index) => (
            <Card key={index} className="border-border/50 bg-card">
              <CardContent className="p-6">
                <div className="mb-4 flex gap-1">
                  {[...Array(5)].map((_, i) => (
                    <Star key={i} className="h-4 w-4 fill-[#636ef9] text-[#636ef9]" />
                  ))}
                </div>
                <p className="mb-6 leading-relaxed text-card-foreground">"{testimonial.content}"</p>
                <div className="flex items-center gap-3">
                  <img
                    src={testimonial.avatar || "/placeholder.svg"}
                    alt={testimonial.name}
                    className="h-12 w-12 rounded-full object-cover"
                  />
                  <div>
                    <p className="font-semibold">{testimonial.name}</p>
                    <p className="text-sm text-muted-foreground">{testimonial.role}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  )
}
