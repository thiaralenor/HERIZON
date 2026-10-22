import { useEffect, useRef, useState } from 'react'
import {
  Dispatch,
  DispatchPosition,
  cancelDispatch,
  createDispatch,
  fetchPositions,
  tickDispatch,
} from './api'

type Props = {
  compact?: boolean
  onClose?: () => void
}

const TERMINAL = new Set(['arrived', 'cancelled', 'failed'])

export function DispatchTracker({ compact, onClose }: Props) {
  const [dispatch, setDispatch] = useState<Dispatch | null>(null)
  const [positions, setPositions] = useState<DispatchPosition[]>([])
  const [creating, setCreating] = useState(false)
  const [err, setErr] = useState<string | null>(null)
  const tickRef = useRef<number | null>(null)

  async function start() {
    setErr(null)
    setCreating(true)
    try {
      navigator.geolocation.getCurrentPosition(
        async (pos) => {
          try {
            const d = await createDispatch(pos.coords.latitude, pos.coords.longitude)
            setDispatch(d)
          } catch (e: any) {
            setErr(e.message ?? 'Could not create dispatch')
          } finally {
            setCreating(false)
          }
        },
        async () => {
          // Location denied — still create with null coords? Backend requires lat/lng.
          setErr('Location permission is required to request an ambulance.')
          setCreating(false)
        },
        { enableHighAccuracy: true, timeout: 10_000 },
      )
    } catch (e: any) {
      setErr(e.message ?? 'Could not get location')
      setCreating(false)
    }
  }

  // Poll /tick and /positions while dispatch is active
  useEffect(() => {
    if (!dispatch) return
    if (TERMINAL.has(dispatch.status)) {
      if (tickRef.current) window.clearInterval(tickRef.current)
      return
    }

    tickRef.current = window.setInterval(async () => {
      try {
        const next = await tickDispatch(dispatch.id)
        setDispatch(next)
        const p = await fetchPositions(dispatch.id)
        setPositions(p)
      } catch (e: any) {
        setErr(e.message ?? 'Lost connection to dispatch')
      }
    }, 2000)

    return () => {
      if (tickRef.current) window.clearInterval(tickRef.current)
    }
  }, [dispatch?.id, dispatch?.status])

  async function cancel() {
    if (!dispatch) return
    try {
      const next = await cancelDispatch(dispatch.id)
      setDispatch(next)
    } catch (e: any) {
      setErr(e.message ?? 'Could not cancel')
    }
  }

  const last = positions[positions.length - 1]

  return (
    <div className={compact ? '' : 'bg-white rounded-xl border p-6 space-y-3'}>
      {!dispatch && (
        <>
          <p className="text-sm text-stone-600">
            Requests a simulated ambulance, then shows it moving toward your
            location. <strong>No real vehicle is dispatched.</strong>
          </p>
          <button
            onClick={start}
            disabled={creating}
            className="w-full rounded-lg bg-blue-600 text-white py-2 disabled:opacity-50"
          >
            {creating ? 'Requesting…' : 'Start demo dispatch'}
          </button>
        </>
      )}

      {dispatch && (
        <div className="space-y-2">
          <div className="text-sm">
            Status: <span className="font-semibold">{dispatch.status}</span>
          </div>
          <div className="text-xs text-stone-600">
            Ambulance: {dispatch.ambulance_call_sign ?? '—'}
            {dispatch.hospital_name && ` · ${dispatch.hospital_name}`}
          </div>
          {last ? (
            <div className="text-xs text-stone-600">
              Last position: {last.lat.toFixed(5)}, {last.lng.toFixed(5)}
            </div>
          ) : (
            <div className="text-xs text-stone-500">Awaiting first position…</div>
          )}

          {!TERMINAL.has(dispatch.status) && (
            <button
              onClick={cancel}
              className="text-xs text-red-600 underline"
            >
              Cancel dispatch
            </button>
          )}

          {TERMINAL.has(dispatch.status) && onClose && (
            <button
              onClick={onClose}
              className="text-xs text-stone-500 underline"
            >
              Close
            </button>
          )}
        </div>
      )}

      {err && <div className="text-xs text-red-600">{err}</div>}
    </div>
  )
}