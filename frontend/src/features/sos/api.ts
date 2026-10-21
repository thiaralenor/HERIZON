import { api } from '@/lib/api-client'

export type EmergencyContact = { label: string; phone: string; kind: string }

export async function fetchEmergencyContacts(hospitalId?: string) {
  const params = hospitalId ? `?hospital_id=${hospitalId}` : ''
  return api<{ contacts: EmergencyContact[] }>(`/emergency/contacts${params}`)
}

export async function logSos(payload: {
  hospital_id?: string
  latitude?: number
  longitude?: number
  note?: string
}) {
  return api('/emergency/sos', { method: 'POST', body: JSON.stringify(payload) })
}