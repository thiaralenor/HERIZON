import { api } from '@/lib/api'

export type Booking = {
  id: string
  doctor_id: string
  doctor_name: string | null
  doctor_slug: string | null
  patient_id: string
  patient_name: string | null
  starts_at: string
  ends_at: string
  status: 'pending' | 'confirmed' | 'completed' | 'cancelled' | 'no_show'
  reason: string | null
  created_at: string
}

export async function createBooking(payload: {
  doctor_id: string; starts_at: string; ends_at: string; reason?: string
}) {
  return api<Booking>('/bookings', { method: 'POST', body: JSON.stringify(payload) })
}

export async function listMyBookings() {
  return api<Booking[]>('/bookings/me')
}

export async function cancelBooking(id: string) {
  return api<Booking>(`/bookings/${id}/status`, {
    method: 'PATCH',
    body: JSON.stringify({ status: 'cancelled' }),
  })
}