import { AuthLayout } from '../components/layout/AuthLayout'
import LoginCard from '../authentication/components/LoginCard.jsx'

export function LoginPage() {
  return (
    <AuthLayout>
      <LoginCard />
    </AuthLayout>
  )
}
