import { useEffect, useState } from 'react'
import { Dispatch, fetchPositions, tickDispatch } from './api'

export function useDispatchSimulation(dispatch: Dispatch | null) {
  const [positions, setPositions] = useState<{ lat: number; lng: number }[]>([])
  const [status, setStatus] = useState(dispatch?.status ?? 'pending')

  useEffect(() => {
    if (!dispatch) return
    if (['arrived', 'cancelled', 'failed'].includes(status)) return

    const interval = setInterval(async () => {
      const next = await tickDispatch(dispatch.id)
      setStatus(next.status)
      const pos = await fetchPositions(dispatch.id)
      setPositions(pos)
    }, 2000)

    return () => clearInterval(interval)
  }, [dispatch?.id, status])

  return { positions, status }
}