import { Navigate, Route, Routes } from 'react-router-dom'
import { AuthProvider, useAuth } from '@/features/auth/AuthProvider'
import { AppShell } from '@/components/layout/AppShell'
import { LoginPage } from '@/features/auth/LoginPage'
import { SignupPage } from '@/features/auth/SignupPage'
import { DoctorList } from '@/features/doctors/DoctorList'
import { DoctorProfilePage } from '@/features/doctors/DoctorProfilePage'
import { MyBookings } from '@/features/bookings/MyBookings'
import { SymptomHistory } from '@/features/patients/SymptomHistory'
import { DoctorDashboard } from '@/features/doctors/DoctorDashboard'
import { HospitalDashboard } from '@/features/dispatch/HospitalDashboard'

function Protected({ children, role }: { children: JSX.Element; role?: string }) {
  const { user, loading } = useAuth()
  if (loading) return <div className="p-8">Loading…</div>
  if (!user) return <Navigate to="/login" replace />
  if (role && user.role !== role) return <Navigate to="/" replace />
  return children
}

export default function App() {
  return (
    <AuthProvider>
      <AppShell>
        <Routes>
          <Route path="/" element={<DoctorList />} />
          <Route path="/doctors/:slug" element={<DoctorProfilePage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/signup" element={<SignupPage />} />

          <Route
            path="/my-bookings"
            element={<Protected role="patient"><MyBookings /></Protected>}
          />
          <Route
            path="/my-symptoms"
            element={<Protected role="patient"><SymptomHistory /></Protected>}
          />
          <Route
            path="/doctor"
            element={<Protected role="doctor"><DoctorDashboard /></Protected>}
          />
          <Route
            path="/hospital"
            element={<Protected role="hospital_admin"><HospitalDashboard /></Protected>}
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AppShell>
    </AuthProvider>
  )
}