import { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import { supabase } from '@/lib/supabase'
import { api } from '@/lib/api'

type Me = {
  profile: { id: string; role: string; full_name: string; phone: string | null }
  doctor_id: string | null
  hospital_id: string | null
}

type AuthCtx = {
  user: Me | null
  loading: boolean
  signOut: () => Promise<void>
}

const Ctx = createContext<AuthCtx>({ user: null, loading: true, signOut: async () => {} })

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<Me | null>(null)
  const [loading, setLoading] = useState(true)

  async function hydrate() {
    const { data: { session } } = await supabase.auth.getSession()
    if (!session) { setUser(null); setLoading(false); return }
    try {
      const me = await api<Me>('/auth/me')
      setUser(me)
    } catch {
      setUser(null)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    hydrate()
    const { data: sub } = supabase.auth.onAuthStateChange(() => { hydrate() })
    return () => sub.subscription.unsubscribe()
  }, [])

  async function signOut() {
    await supabase.auth.signOut()
    setUser(null)
  }

  return <Ctx.Provider value={{ user, loading, signOut }}>{children}</Ctx.Provider>
}

export const useAuth = () => useContext(Ctx)