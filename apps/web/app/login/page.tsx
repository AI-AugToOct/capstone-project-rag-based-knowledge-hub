import { LoginForm } from "@/components/login-form"
import Image from "next/image"

export default function LoginPage() {
  return (
    <div className="relative flex min-h-screen items-center justify-center overflow-hidden bg-gray-50">
      {/* Decorative background shape */}
      <div className="absolute right-0 top-0 h-full w-1/2 overflow-hidden">
        <div className="absolute -right-32 top-0 h-full w-[600px] rounded-l-[200px] bg-gradient-to-br from-[#8B92FF] to-[#3E4DF9] opacity-90" />
      </div>

      {/* Character Image */}
      <div className="absolute right-8 top-1/2 -translate-y-1/2 z-10 hidden lg:block xl:right-16">
        <div className="relative h-[350px] w-[350px] xl:h-[400px] xl:w-[400px]">
          <Image
            src="/GhanamLogin.png"
            alt="Login Character"
            fill
            className="object-contain drop-shadow-2xl"
            priority
          />
        </div>
      </div>

      <LoginForm />
    </div>
  )
}
