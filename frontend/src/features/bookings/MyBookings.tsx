import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Booking, listMyBookings, cancelBooking } from './api'

export function MyBookings() {
  const [bookings, setBookings] = useState<Booking[]>([])
  const [loading, setLoading] = useState(true)

  async function refresh() {
    setLoading(true)
    try { setBookings(await listMyBookings()) } finally { setLoading(false) }
  }
  useEffect(() => { refresh() }, [])

  async function cancel(id: string) {
    if (!confirm('Cancel this booking?')) return
    await cancelBooking(id)
    await refresh()
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">My bookings</h1>
      {loading ? (
        <div className="text-stone-500">Loading…</div>
      ) : bookings.length === 0 ? (
        <div className="bg-white rounded-xl border p-8 text-center text-stone-600">
          No bookings yet. <Link to="/" className="text-kam-teal underline">Find a specialist</Link>.
        </div>
      ) : (
        <div className="space-y-3">
          {bookings.map((b) => (
            <div key={b.id} className="bg-white rounded-xl border p-4 flex items-start justify-between">
              <div>
                <div className="font-semibold">
                  Dr. {b.doctor_name ?? 'Unknown'}
                </div>
                <div className="text-sm text-stone-600">
                  {new Date(b.starts_at).toLocaleString()}
                </div>
                {b.reason && <div className="text-sm mt-1">Reason: {b.reason}</div>}
              </div>
              <div className="text-right">
                <span className="inline-block text-xs px-2 py-1 rounded bg-stone-100">
                  {b.status}
                </span>
                {b.status === 'confirmed' && (
                  <button
                    onClick={() => cancel(b.id)}
                    className="block text-xs text-red-600 mt-2"
                  >
                    Cancel
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}