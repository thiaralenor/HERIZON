import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { listDoctors, Doctor, NEIGHBORHOODS, SPECIALTIES } from './api'

export function DoctorList() {
  const [doctors, setDoctors] = useState<Doctor[]>([])
  const [loading, setLoading] = useState(true)
  const [neighborhood, setNeighborhood] = useState<string>('')
  const [specialty, setSpecialty] = useState<string>('')

  useEffect(() => {
    listDoctors().then(setDoctors).finally(() => setLoading(false))
  }, [])

  const filtered = useMemo(() => {
  return doctors.filter((d) => {
    const neighMatch = !neighborhood || d.serves_neighborhoods?.includes(neighborhood)
    const specMatch = !specialty || d.specialty === specialty
    return neighMatch && specMatch
  })
}, [doctors, neighborhood, specialty])

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <div className="bg-white rounded-xl border border-stone-200 p-6 mb-6">
        <h1 className="text-3xl font-bold mb-1">Find a specialist in Buea</h1>
        <p className="text-stone-600 mb-6">
          Search by neighborhood and specialty. Freelance and hospital-affiliated
          doctors alike.
        </p>

        <div className="grid md:grid-cols-2 gap-3">
          <select
            value={neighborhood}
            onChange={(e) => setNeighborhood(e.target.value)}
            className="border rounded p-2"
          >
            <option value="">All neighborhoods</option>
            {NEIGHBORHOODS.map((n) => (
              <option key={n} value={n}>{n}</option>
            ))}
          </select>

          <select
            value={specialty}
            onChange={(e) => setSpecialty(e.target.value)}
            className="border rounded p-2"
          >
            <option value="">All specialties</option>
            {SPECIALTIES.map((s) => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
        </div>
      </div>

      {loading ? (
        <div className="text-center py-16 text-stone-500">Loading doctors…</div>
      ) : filtered.length === 0 ? (
        <div className="bg-white rounded-xl border border-stone-200 p-10 text-center">
          <h2 className="text-xl font-semibold mb-2">
            No specialists listed here yet
          </h2>
          <p className="text-stone-600 mb-4">
            Are you a specialist in Buea? Register to fill this gap — freelance and
            hospital-affiliated doctors are welcome.
          </p>
          <Link
            to="/signup"
            className="inline-block bg-kam-teal text-white rounded px-4 py-2"
          >
            Register as a doctor
          </Link>
        </div>
      ) : (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered.map((d) => (
            <DoctorCard key={d.id} doctor={d} />
          ))}
        </div>
      )}
    </div>
  )
}

function DoctorCard({ doctor }: { doctor: Doctor }) {
  return (
    <Link
      to={`/doctors/${doctor.slug}`}
      className="block bg-white rounded-xl border border-stone-200 p-5 hover:border-kam-teal transition"
    >
      <div className="flex items-start justify-between mb-2">
        <div>
          <div className="font-semibold text-lg">
            Dr. {doctor.full_name ?? 'Unnamed'}
          </div>
          <div className="text-sm text-stone-600">{doctor.specialty}</div>
        </div>
        {doctor.doctor_type === 'freelance' ? (
          <span className="text-xs bg-amber-100 text-amber-800 px-2 py-1 rounded">
            Freelance
          </span>
        ) : (
          <span className="text-xs bg-emerald-100 text-emerald-800 px-2 py-1 rounded">
            {doctor.hospital_name ?? 'Hospital'}
          </span>
        )}
      </div>
      {doctor.bio && (
        <p className="text-sm text-stone-600 line-clamp-2">{doctor.bio}</p>
      )}
      {doctor.consultation_fee != null && (
        <div className="text-sm mt-3 text-kam-ink">
          Consultation: <strong>{doctor.consultation_fee} XAF</strong>
        </div>
      )}
    </Link>
  )
}