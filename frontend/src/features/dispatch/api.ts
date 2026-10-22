import { api } from '@/lib/api-client'

export type Dispatch = {
  id: string
  patient_id: string
  hospital_id: string | null
  hospital_name: string | null
  ambulance_id: string | null
  ambulance_call_sign: string | null
  status: 'pending' | 'assigned' | 'en_route' | 'arrived' | 'cancelled' | 'failed'
  patient_lat: number | null
  patient_lng: number | null
  note: string | null
  created_at: string
  updated_at: string
}

export type DispatchPosition = {
  lat: number
  lng: number
  recorded_at: string
}

export async function createDispatch(lat: number, lng: number, hospitalId?: string) {
  return api<Dispatch>('/dispatch', {
    method: 'POST',
    body: JSON.stringify({ latitude: lat, longitude: lng, hospital_id: hospitalId }),
  })
}

export async function tickDispatch(id: string) {
  return api<Dispatch>(`/dispatch/${id}/tick`, { method: 'POST' })
}

export async function fetchPositions(id: string) {
  return api<DispatchPosition[]>(`/dispatch/${id}/positions`)
}

export async function cancelDispatch(id: string) {
  return api<Dispatch>(`/dispatch/${id}/cancel`, { method: 'POST' })
}