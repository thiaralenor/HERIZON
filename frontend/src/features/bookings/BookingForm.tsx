import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { createBooking } from './api'
import { useAuth } from '@/features/auth/AuthProvider'

export function BookingForm({ doctorId }: { doctorId: string }) {
  const { user } = useAuth()
  const nav = useNavigate()
  const [when, setWhen] = useState<string>(defaultWhen())
  const [reason, setReason] = useState('')
  const [busy, setBusy] = useState(false)
  const [err, setErr] = useState<string | null>(null)
  const [ok, setOk] = useState(false)

  if (!user) {
    return (
      <div className="text-sm">
        <button
          onClick={() => nav('/login')}
          className="bg-kam-teal text-white rounded px-4 py-2"
        >
          Sign in to book
        </button>
      </div>
    )
  }
  if (user.profile.role !== 'patient') {
    return <div className="text-sm text-stone-600">Only patients can book.</div>
  }

  async function submit(e: React.FormEvent) {
    e.preventDefault()
    setErr(null); setBusy(true)
    try {
      const start = new Date(when)
      const end = new Date(start.getTime() + 30 * 60 * 1000)
      await createBooking({
        doctor_id: doctorId,
        starts_at: start.toISOString(),
        ends_at: end.toISOString(),
        reason: reason || undefined,
      })
      setOk(true)
      setTimeout(() => nav('/my-bookings'), 800)
    } catch (e: any) {
      setErr(e.message ?? 'Booking failed')
    } finally {
      setBusy(false)
    }
  }

  if (ok) {
    return <div className="text-emerald-700 text-sm">Booked! Redirecting to your bookings…</div>
  }

  return (
    <form onSubmit={submit} className="space-y-3">
      <label className="block">
        <span className="text-sm font-medium">Date & time</span>
        <input
          type="datetime-local"
          className="w-full border rounded p-2 mt-1"
          value={when}
          onChange={(e) => setWhen(e.target.value)}
          required
        />
      </label>
      <label className="block">
        <span className="text-sm font-medium">Reason for visit (optional)</span>
        <textarea
          className="w-full border rounded p-2 mt-1"
          rows={3}
          value={reason}
          onChange={(e) => setReason(e.target.value)}
          maxLength={500}
        />
      </label>
      {err && <div className="text-red-600 text-sm">{err}</div>}
      <button
        disabled={busy}
        className="bg-kam-teal text-white rounded px-4 py-2 disabled:opacity-50"
      >
        {busy ? 'Booking…' : 'Confirm booking'}
      </button>
    </form>
  )
}

function defaultWhen() {
  const d = new Date()
  d.setDate(d.getDate() + 1)
  d.setHours(10, 0, 0, 0)
  return d.toISOString().slice(0, 16)
}