import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { supabase } from '@/lib/supabase'

export function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [err, setErr] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)
  const nav = useNavigate()

  async function submit(e: React.FormEvent) {
    e.preventDefault()
    setErr(null); setBusy(true)
    const { error } = await supabase.auth.signInWithPassword({ email, password })
    setBusy(false)
    if (error) setErr(error.message)
    else nav('/')
  }

  return (
    <div className="max-w-md mx-auto mt-16 bg-white p-8 rounded-xl shadow">
      <h1 className="text-2xl font-semibold mb-6">Sign in to Kam Well</h1>
      <form onSubmit={submit} className="space-y-4">
        <input className="w-full border rounded p-2" type="email" placeholder="Email"
               value={email} onChange={(e) => setEmail(e.target.value)} required />
        <input className="w-full border rounded p-2" type="password" placeholder="Password"
               value={password} onChange={(e) => setPassword(e.target.value)} required />
        {err && <div className="text-red-600 text-sm">{err}</div>}
        <button disabled={busy} className="w-full bg-kam-teal text-white rounded p-2 disabled:opacity-50">
          {busy ? 'Signing in…' : 'Sign in'}
        </button>
      </form>
      <p className="text-sm mt-4">
        No account? <Link className="text-kam-teal underline" to="/signup">Create one</Link>
      </p>
    </div>
  )
}