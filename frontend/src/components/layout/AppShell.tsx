import { ReactNode } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '@/features/auth/AuthProvider'
import { SOSPanel } from '@/features/emergency/SOSPanel'

export function AppShell({ children }: { children: ReactNode }) {
  const { user, signOut } = useAuth()
  const nav = useNavigate()

  return (
    <div className="min-h-full flex flex-col">
      <header className="bg-white border-b border-stone-200">
        <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
          <Link to="/" className="flex items-baseline gap-1">
            <span className="text-xl font-bold text-kam-teal">Kam</span>
            <span className="text-xl font-bold text-kam-ink">Well</span>
            <span className="text-xs text-stone-500 ml-2">Buea</span>
          </Link>

          <nav className="flex items-center gap-4 text-sm">
            <Link to="/" className="hover:text-kam-teal">Find a specialist</Link>
            {user?.profile.role === 'patient' && (
              <>
                <Link to="/my-bookings" className="hover:text-kam-teal">My bookings</Link>
                <Link to="/my-symptoms" className="hover:text-kam-teal">My symptoms</Link>
              </>
            )}
            {user?.profile.role === 'doctor' && (
              <Link to="/doctor" className="hover:text-kam-teal">Doctor dashboard</Link>
            )}
            {user?.profile.role === 'hospital_admin' && (
              <Link to="/hospital" className="hover:text-kam-teal">Hospital dashboard</Link>
            )}
            {user ? (
              <button onClick={() => signOut().then(() => nav('/'))}
                      className="text-stone-600 hover:text-kam-ink">
                Sign out
              </button>
            ) : (
              <>
                <Link to="/login" className="hover:text-kam-teal">Sign in</Link>
                <Link to="/signup" className="bg-kam-teal text-white px-3 py-1 rounded">
                  Sign up
                </Link>
              </>
            )}
          </nav>
        </div>
      </header>

      <main className="flex-1">{children}</main>

      <footer className="border-t border-stone-200 bg-white text-xs text-stone-500 py-3">
        <div className="max-w-6xl mx-auto px-4">
          Kam Well · Buea, Cameroon · Emergencies: dial <strong>119</strong> or <strong>1510</strong>
        </div>
      </footer>

      <SOSPanel />
    </div>
  )
}