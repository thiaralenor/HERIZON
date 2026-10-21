import { useState } from 'react'
import { fetchEmergencyContacts, logSos } from './api'

export function SOSPanel({ hospitalId }: { hospitalId?: string }) {
  const [contacts, setContacts] = useState<{ label: string; phone: string }[]>([])
  const [expanded, setExpanded] = useState(false)

  async function open() {
    setExpanded(true)
    const { contacts } = await fetchEmergencyContacts(hospitalId)
    setContacts(contacts)
    // Ask the browser for location; ignore denial.
    navigator.geolocation?.getCurrentPosition(
      (pos) =>
        logSos({
          hospital_id: hospitalId,
          latitude: pos.coords.latitude,
          longitude: pos.coords.longitude,
        }),
      () => logSos({ hospital_id: hospitalId }),
    )
  }

  return (
    <div className="fixed bottom-6 right-6">
      {!expanded ? (
        <button
          onClick={open}
          className="h-20 w-20 rounded-full bg-red-600 text-white text-xl font-bold shadow-lg"
        >
          SOS
        </button>
      ) : (
        <div className="w-72 rounded-xl bg-white p-4 shadow-xl">
          {contacts.map((c) => (
            <a
              key={c.phone}
              href={`tel:${c.phone}`}
              className="block rounded-lg border p-2 mb-2 text-sm"
            >
              {c.label} — {c.phone}
            </a>
          ))}
          <button className="text-xs text-gray-500" onClick={() => setExpanded(false)}>
            close
          </button>
        </div>
      )}
    </div>
  )
}