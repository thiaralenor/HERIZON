import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { EmergencyContact, fetchEmergencyContacts, logSos } from './api'
import { DispatchTracker } from '@/features/dispatch/DispatchTracker'
import { useAuth } from '@/features/auth/AuthProvider'

type Stage = 'closed' | 'menu' | 'dispatch'

export function SOSPanel() {
  const { user } = useAuth()
  const nav = useNavigate()
  const [stage, setStage] = useState<Stage>('closed')
  const [contacts, setContacts] = useState<EmergencyContact[]>([])
  const [loadingContacts, setLoadingContacts] = useState(false)
  const [err, setErr] = useState<string | null>(null)

  async function openSos() {
    if (!user) {
      nav('/login')
      return
    }
    setErr(null)
    setStage('menu')
    setLoadingContacts(true)
    try {
      const res = await fetchEmergencyContacts()
      setContacts(res.contacts)
    } catch (e: any) {
      setErr(e.message ?? 'Could not load emergency contacts')
    } finally {
      setLoadingContacts(false)
    }
  }

  function callNumber(phone: string) {
    // Log the tap for audit; never block the dialer on the network call
    logSos({}).catch(() => {})
    window.location.href = `tel:${phone}`
  }

  if (!user) return null

  return (
    <div className="fixed bottom-6 right-6 z-40">
      {stage === 'closed' && (
        <button
          onClick={openSos}
          aria-label="Emergency SOS"
          className="h-20 w-20 rounded-full bg-red-600 text-white text-xl font-bold shadow-xl hover:bg-red-700"
        >
          SOS
        </button>
      )}

      {stage === 'menu' && (
        <div className="w-80 rounded-2xl bg-white shadow-2xl border border-stone-200 p-4">
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-semibold text-red-700">Emergency</h3>
            <button
              onClick={() => setStage('closed')}
              className="text-xs text-stone-500"
            >
              close
            </button>
          </div>

          {loadingContacts && <div className="text-sm text-stone-500">Loading contacts…</div>}
          {err && (
            <div className="text-sm text-red-600 mb-2">
              {err}
              <button
                onClick={openSos}
                className="ml-2 underline"
              >
                retry
              </button>
            </div>
          )}

          <div className="space-y-2">
            {contacts.map((c) => (
              <button
                key={c.phone}
                onClick={() => callNumber(c.phone)}
                className="w-full text-left rounded-lg border border-stone-200 p-2 hover:border-red-400"
              >
                <div className="text-sm font-medium">{c.label}</div>
                <div className="text-lg font-bold text-red-700">{c.phone}</div>
              </button>
            ))}
          </div>

          <hr className="my-3" />

          <button
            onClick={() => setStage('dispatch')}
            className="w-full rounded-lg bg-red-600 text-white py-2 text-sm font-medium hover:bg-red-700"
          >
            Request ambulance (demo)
          </button>
          <p className="text-[11px] text-stone-500 mt-1 leading-tight">
            Demo only. No real ambulance is dispatched. Use the phone numbers
            above for a real emergency.
          </p>
        </div>
      )}

      {stage === 'dispatch' && (
        <div className="w-80 rounded-2xl bg-white shadow-2xl border border-stone-200 p-4">
          <div className="flex items-center justify-between mb-2">
            <h3 className="font-semibold">Dispatch (demo)</h3>
            <button
              onClick={() => setStage('menu')}
              className="text-xs text-stone-500"
            >
              back
            </button>
          </div>
          <DispatchTracker compact onClose={() => setStage('closed')} />
        </div>
      )}
    </div>
  )
}