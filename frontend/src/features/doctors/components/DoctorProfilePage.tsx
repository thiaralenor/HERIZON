import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { getDoctorBySlug, Doctor } from './api'
import { BookingForm } from '@/features/bookings/BookingForm'

export function DoctorProfilePage() {
  const { slug } = useParams<{ slug: string }>()
  const [doctor, setDoctor] = useState<Doctor | null>(null)
  const [err, setErr] = useState<string | null>(null)

  useEffect(() => {
    if (!slug) return
    getDoctorBySlug(slug).then(setDoctor).catch((e) => setErr(e.message))
  }, [slug])

  if (err) return <div className="p-8 text-red-600">{err}</div>
  if (!doctor) return <div className="p-8 text-stone-500">Loading…</div>

  return (
    <div className="max-w-3xl mx-auto px-4 py-8 space-y-6">
      <div className="bg-white rounded-xl border border-stone-200 p-6">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-2xl font-bold">Dr. {doctor.full_name ?? 'Unnamed'}</h1>
            <p className="text-stone-600">{doctor.specialty}</p>
            {doctor.doctor_type === 'freelance' ? (
              <span className="inline-block mt-2 text-xs bg-amber-100 text-amber-800 px-2 py-1 rounded">
                Freelance specialist
              </span>
            ) : (
              <span className="inline-block mt-2 text-xs bg-emerald-100 text-emerald-800 px-2 py-1 rounded">
                {doctor.hospital_name ?? 'Hospital'}
              </span>
            )}
          </div>
          {doctor.consultation_fee != null && (
            <div className="text-right">
              <div className="text-xs text-stone-500">Consultation</div>
              <div className="text-xl font-semibold">{doctor.consultation_fee} XAF</div>
            </div>
          )}
        </div>

        {doctor.bio && (
          <p className="mt-4 text-stone-700 whitespace-pre-line">{doctor.bio}</p>
        )}

        {doctor.serves_neighborhoods?.length > 0 && (
          <div className="mt-4">
            <div className="text-sm font-medium mb-1">Serves neighborhoods:</div>
            <div className="flex flex-wrap gap-2">
              {doctor.serves_neighborhoods.map((n) => (
                <span key={n} className="text-xs bg-stone-100 text-stone-700 px-2 py-1 rounded">
                  {n}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      <div className="bg-white rounded-xl border border-stone-200 p-6">
        <h2 className="text-lg font-semibold mb-4">Book an appointment</h2>
        <BookingForm doctorId={doctor.id} />
      </div>

      <div className="text-center text-sm">
        <Link to="/" className="text-kam-teal hover:underline">
          ← Back to all specialists
        </Link>
      </div>
    </div>
  )
}