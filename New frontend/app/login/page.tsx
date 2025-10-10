import { LoginForm } from "@/components/login-form"

export default function LoginPage() {
  return (
    <div className="relative flex min-h-screen items-center justify-center overflow-hidden bg-gray-50">
      {/* Decorative background shape */}
      <div className="absolute right-0 top-0 h-full w-1/2 overflow-hidden">
        <div className="absolute -right-32 top-0 h-full w-[600px] rounded-l-[200px] bg-gradient-to-br from-[#8B92FF] to-[#3E4DF9] opacity-90" />
      </div>

      <LoginForm />
    </div>
  )
}
