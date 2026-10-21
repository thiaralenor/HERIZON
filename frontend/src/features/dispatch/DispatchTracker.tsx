import { useEffect, useState } from 'react'
import { Dispatch, cancelDispatch, createDispatch } from './api'
import { useDispatchSimulation } from './useDispatchSimulation'

export function DispatchTracker({ hospitalId }: { hospitalId?: string }) {
  const [dispatch, setDispatch] = useState<Dispatch | null>(null)
  const { positions, status } = useDispatchSimulation(dispatch)

  async function start() {
    navigator.geolocation.getCurrentPosition(async (pos) => {
      const d = await createDispatch(
        pos.coords.latitude,
        pos.coords.longitude,
        hospitalId,
      )
      setDispatch(d)
    })
  }

  if (!dispatch) {
    return (
      <button
        onClick={start}
        className="rounded-lg bg-blue-600 px-4 py-2 text-white"
      >
        Request ambulance (demo)
      </button>
    )
  }

  const last = positions[positions.length - 1]

  return (
    <div className="rounded-xl border p-4 space-y-2">
      <div className="text-sm text-gray-600">
        Status: <span className="font-medium">{status}</span>
      </div>
      <div className="text-sm">
        {last
          ? `Position: ${last.lat.toFixed(5)}, ${last.lng.toFixed(5)}`
          : 'Awaiting position…'}
      </div>
      <div className="text-xs text-gray-500">
        Ambulance: {dispatch.ambulance_call_sign ?? '—'} · Hospital:{' '}
        {dispatch.hospital_name ?? '—'}
      </div>
      {!['arrived', 'cancelled', 'failed'].includes(status) && (
        <button
          onClick={async () => setDispatch(await cancelDispatch(dispatch.id))}
          className="text-sm text-red-600"
        >
          Cancel
        </button>
      )}
    </div>
  )
}