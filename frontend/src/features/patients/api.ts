import { api } from '@/lib/api'

export type SymptomLog = {
  id: string
  patient_id: string
  symptoms: string
  severity: number | null
  logged_at: string
}

export async function listSymptoms() {
  return api<SymptomLog[]>('/patients/me/symptoms')
}

export async function addSymptom(symptoms: string, severity?: number) {
  return api<SymptomLog>('/patients/me/symptoms', {
    method: 'POST',
    body: JSON.stringify({ symptoms, severity }),
  })
}

export async function deleteSymptom(id: string) {
  return api<void>(`/patients/me/symptoms/${id}`, { method: 'DELETE' })
}