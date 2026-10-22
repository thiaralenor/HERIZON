import { useEffect, useState } from 'react'
import { Dispatch } from './api'
import { cancelDispatch, fetchDispatchPositions, fetchHospitalDispatches } from './hospital-api'

const ACTIVE = new Set(['pending', 'assigned', 'en_route'])

export function HospitalDashboard() {
  const [dispatches, setDispatches] = useState<Dispatch[]>([])
  const [loading, setLoading] = useState(true)
  const [err, setErr] = useState<string | null>(null)

  async function refresh() {
    try {
      const data = await fetchHospitalDispatches('me')
      setDispatches(data)
      setErr(null)
    } catch (e: any) {
      setErr(e.message ?? 'Failed to load dispatches')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    refresh()
    const id = window.setInterval(refresh, 5000)
    return () => window.clearInterval(id)
  }, [])

  async function cancel(id: string) {
    if (!confirm('Cancel this dispatch?')) return
    try {
      await cancelDispatch(id)
      refresh()
    } catch (e: any) {
      setErr(e.message ?? 'Failed to cancel')
    }
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8 space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Hospital dashboard</h1>
        <p className="text-sm text-stone-600 mt-1">
          Live list of dispatch requests assigned to your hospital (demo).
        </p>
      </div>

      {loading ? (
        <div className="text-stone-500">Loading…</div>
      ) : err ? (
        <div className="bg-red-50 border border-red-200 text-red-800 rounded-xl p-4 text-sm">
          {err}
          <button onClick={refresh} className="ml-2 underline">retry</button>
        </div>
      ) : dispatches.length === 0 ? (
        <div className="bg-white rounded-xl border p-8 text-center text-stone-600">
          No dispatches assigned to your hospital yet.
        </div>
      ) : (
        <div className="space-y-3">
          {dispatches.map((d) => (
            <DispatchRow key={d.id} dispatch={d} onCancel={cancel} />
          ))}
        </div>
      )}
    </div>
  )
}

function DispatchRow({ dispatch, onCancel }: { dispatch: Dispatch; onCancel: (id: string) => void }) {
  const [last, setLast] = useState<{ lat: number; lng: number } | null>(null)

  useEffect(() => {
    if (!ACTIVE.has(dispatch.status)) return
    let cancelled = false
    async function pull() {
      try {
        const pos = await fetchDispatchPositions(dispatch.id)
        if (!cancelled && pos.length > 0) {
          const p = pos[pos.length - 1]
          setLast({ lat: p.lat, lng: p.lng })
        }
      } catch {
        // silent — position poll failure is not fatal for the row
      }
    }
    pull()
    const id = window.setInterval(pull, 2000)
    return () => { cancelled = true; window.clearInterval(id) }
  }, [dispatch.id, dispatch.status])

  return (
    <div className="bg-white rounded-xl border p-4">
      <div className="flex items-start justify-between">
        <div>
          <div className="font-semibold">
            {dispatch.ambulance_call_sign ?? 'Ambulance TBD'} · {dispatch.status}
          </div>
          <div className="text-sm text-stone-600 mt-1">
            Patient location: {dispatch.patient_lat?.toFixed(5) ?? '—'},{' '}
            {dispatch.patient_lng?.toFixed(5) ?? '—'}
          </div>
          {last && (
            <div className="text-xs text-stone-500 mt-1">
              Ambulance now at {last.lat.toFixed(5)}, {last.lng.toFixed(5)}
            </div>
          )}
          {dispatch.note && (
            <div className="text-xs text-stone-500 mt-1">Note: {dispatch.note}</div>
          )}
        </div>
        {ACTIVE.has(dispatch.status) && (
          <button
            onClick={() => onCancel(dispatch.id)}
            className="text-xs text-red-600 underline"
          >
            Cancel
          </button>
        )}
      </div>
    </div>
  )
}