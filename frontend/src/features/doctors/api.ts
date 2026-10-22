import { api } from '@/lib/api'

export const NEIGHBORHOODS = [
  'Molyko', 'Bokova', 'Mile 16', 'Buea Town', 'Muea',
  'Bomaka', 'Mile 17', 'Great Soppo', 'Federal Quarter', "Clerk's Quarter",
] as const

export const SPECIALTIES = [
  'General Practice', 'Pediatrics', 'Obstetrics & Gynecology', 'Internal Medicine',
  'Surgery', 'Psychiatry', 'Dermatology', 'Dentistry', 'Ophthalmology', 'ENT',
  'Cardiology', 'Orthopedics', 'Neurology', 'Oncology', 'Public Health', 'Physiotherapy',
] as const

export type Doctor = {
  id: string
  profile_id: string
  full_name: string | null
  doctor_type: 'hospital' | 'freelance'
  hospital_id: string | null
  hospital_name: string | null
  specialty: string
  bio: string | null
  consultation_fee: number | null
  slug: string
  is_active: boolean
  serves_neighborhoods: string[]
}

export async function listDoctors(params: {
  hospital_id?: string; specialty?: string; doctor_type?: string; search?: string
} = {}) {
  const q = new URLSearchParams()
  Object.entries(params).forEach(([k, v]) => v && q.append(k, String(v)))
  return api<Doctor[]>(`/doctors?${q.toString()}`)
}

export async function getDoctorBySlug(slug: string) {
  return api<Doctor>(`/doctors/by-slug/${slug}`)
}
