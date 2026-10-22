import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { supabase } from '@/lib/supabase'

type Role = 'patient' | 'doctor' | 'hospital_admin'

export function SignupPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [fullName, setFullName] = useState('')
  const [role, setRole] = useState<Role>('patient')
  const [err, setErr] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)
  const nav = useNavigate()

  async function submit(e: React.FormEvent) {
    e.preventDefault()
    setErr(null); setBusy(true)
    const { error } = await supabase.auth.signUp({
      email,
      password,
      options: { data: { full_name: fullName, role } },
    })
    setBusy(false)
    if (error) setErr(error.message)
    else nav('/')
  }

  return (
    <div className="max-w-md mx-auto mt-16 bg-white p-8 rounded-xl shadow">
      <h1 className="text-2xl font-semibold mb-6">Create your Kam Well account</h1>
      <form onSubmit={submit} className="space-y-4">
        <input className="w-full border rounded p-2" placeholder="Full name" value={fullName}
               onChange={(e) => setFullName(e.target.value)} required />
        <input className="w-full border rounded p-2" type="email" placeholder="Email"
               value={email} onChange={(e) => setEmail(e.target.value)} required />
        <input className="w-full border rounded p-2" type="password" placeholder="Password"
               value={password} onChange={(e) => setPassword(e.target.value)} required minLength={8} />
        <select className="w-full border rounded p-2" value={role}
                onChange={(e) => setRole(e.target.value as Role)}>
          <option value="patient">I'm a patient</option>
          <option value="doctor">I'm a doctor</option>
          <option value="hospital_admin">I manage a hospital</option>
        </select>
        {err && <div className="text-red-600 text-sm">{err}</div>}
        <button disabled={busy} className="w-full bg-kam-teal text-white rounded p-2 disabled:opacity-50">
          {busy ? 'Creating…' : 'Create account'}
        </button>
      </form>
      <p className="text-sm mt-4">
        Already have one? <Link className="text-kam-teal underline" to="/login">Sign in</Link>
      </p>
    </div>
  )
}