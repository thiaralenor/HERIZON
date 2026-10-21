import { useEffect, useState, type FormEvent } from 'react';
import {
  getBookingOptions,
  requestBooking,
  type BookingOptions,
  type BookingReceipt,
  type ProviderType,
} from '../api';

const timeSlots = ['09:00', '10:30', '12:00', '14:00', '15:30'];

function formatDate(value: string) {
  return new Intl.DateTimeFormat('en', {
    weekday: 'long',
    month: 'long',
    day: 'numeric',
    year: 'numeric',
  }).format(new Date(`${value}T12:00:00`));
}

export function PatientBookingPage() {
  const [options, setOptions] = useState<BookingOptions | null>(null);
  const [providerType, setProviderType] = useState<ProviderType>('hospital');
  const [hospitalId, setHospitalId] = useState('');
  const [specialty, setSpecialty] = useState('');
  const [doctorId, setDoctorId] = useState('');
  const [appointmentDate, setAppointmentDate] = useState('');
  const [appointmentTime, setAppointmentTime] = useState('');
  const [patientName, setPatientName] = useState('');
  const [patientEmail, setPatientEmail] = useState('');
  const [reason, setReason] = useState('');
  const [receipt, setReceipt] = useState<BookingReceipt | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    getBookingOptions()
      .then((data) => {
        setOptions(data);
        setHospitalId(data.hospitals[0]?.id ?? '');
        setSpecialty(data.specialties[0] ?? '');
      })
      .catch(() => setError('We could not load providers. Check that the Health Platform API is running.'))
      .finally(() => setLoading(false));
  }, []);

  const providers = options?.providers.filter((provider) => {
    const matchesType = providerType === 'freelance'
      ? provider.hospital_id === null
      : provider.hospital_id === hospitalId;
    return matchesType && (!specialty || provider.specialty === specialty);
  }) ?? [];

  const availableSpecialties = [...new Set(
    (options?.providers ?? [])
      .filter((provider) => providerType === 'freelance'
        ? provider.hospital_id === null
        : provider.hospital_id === hospitalId)
      .map((provider) => provider.specialty),
  )];

  function changeProviderType(type: ProviderType) {
    setProviderType(type);
    setDoctorId('');
    setSpecialty('');
    setError('');
  }

  function changeHospital(id: string) {
    setHospitalId(id);
    setDoctorId('');
    setSpecialty('');
  }

  async function submitBooking(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError('');
    setSubmitting(true);
    try {
      const result = await requestBooking({
        patient_name: patientName,
        patient_email: patientEmail,
        provider_type: providerType,
        hospital_id: providerType === 'hospital' ? hospitalId : null,
        doctor_id: doctorId,
        appointment_date: appointmentDate,
        appointment_time: appointmentTime,
        reason: reason.trim() || null,
      });
      setReceipt(result);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : 'Booking request could not be sent.');
    } finally {
      setSubmitting(false);
    }
  }

  function startAnotherBooking() {
    setReceipt(null);
    setDoctorId('');
    setAppointmentDate('');
    setAppointmentTime('');
    setReason('');
  }

  if (receipt) {
    return (
      <main className="booking-shell confirmation-shell">
        <header className="topbar">
          <a className="brand" href="#home" aria-label="Careway home"><span className="brand-mark">+</span> careway</a>
          <span className="topbar-label">PATIENT SERVICES</span>
        </header>
        <section className="confirmation-panel" aria-live="polite">
          <div className="confirmation-icon" aria-hidden="true">&#10003;</div>
          <p className="eyebrow">REQUEST RECEIVED</p>
          <h1>Your care request is in.</h1>
          <p className="confirmation-copy">This demo has recorded your request. In a live service, the provider or hospital would confirm availability with you.</p>
          <div className="receipt-details">
            <div><span>Provider</span><strong>{receipt.provider_name}</strong></div>
            {receipt.hospital_name && <div><span>Hospital</span><strong>{receipt.hospital_name}</strong></div>}
            <div><span>Date and time</span><strong>{formatDate(receipt.appointment_date)} · {receipt.appointment_time}</strong></div>
            <div><span>Request reference</span><strong>{receipt.id.slice(0, 8).toUpperCase()}</strong></div>
          </div>
          <button className="button button-dark" type="button" onClick={startAnotherBooking}>Request another appointment <span aria-hidden="true">&#8594;</span></button>
        </section>
      </main>
    );
  }

  return (
    <main className="booking-shell">
      <header className="topbar">
        <a className="brand" href="#home" aria-label="Careway home"><span className="brand-mark">+</span> careway</a>
        <span className="topbar-label">PATIENT SERVICES</span>
        <a className="help-link" href="mailto:help@careway.example">Need help? <span aria-hidden="true">&#8599;</span></a>
      </header>

      <section className="booking-intro">
        <div className="intro-copy">
          <p className="eyebrow"><span className="eyebrow-line" /> APPOINTMENTS, MADE SIMPLE</p>
          <h1>Find the right<br /><em>care for you.</em></h1>
          <p className="intro-description">Choose a hospital and its care team, or book directly with an independent doctor.</p>
        </div>
        <div className="intro-art" aria-hidden="true">
          <div className="art-sun" />
          <div className="art-cross">+</div>
          <div className="art-ring art-ring-one" />
          <div className="art-ring art-ring-two" />
          <div className="art-caption">Care that<br />starts with you.</div>
        </div>
      </section>

      <section className="booking-area">
        <div className="form-heading">
          <div><p className="eyebrow">YOUR APPOINTMENT</p><h2>Book a consultation</h2></div>
          <span className="step-count"><b>01</b> / 01</span>
        </div>

        {options?.demo_mode && <div className="demo-note"><span aria-hidden="true">i</span> Demo directory: hospitals and providers shown are sample listings.</div>}
        {error && <div className="form-error" role="alert">{error}</div>}

        <form onSubmit={submitBooking}>
          <fieldset className="provider-choice">
            <legend>Where would you like to receive care?</legend>
            <div className="choice-grid">
              <button className={`choice-option ${providerType === 'hospital' ? 'is-selected' : ''}`} type="button" onClick={() => changeProviderType('hospital')} aria-pressed={providerType === 'hospital'}>
                <span className="choice-icon hospital-icon" aria-hidden="true">&#9633;</span>
                <span><strong>At a hospital</strong><small>Choose a facility and its doctors</small></span>
                <span className="radio-mark" aria-hidden="true" />
              </button>
              <button className={`choice-option ${providerType === 'freelance' ? 'is-selected' : ''}`} type="button" onClick={() => changeProviderType('freelance')} aria-pressed={providerType === 'freelance'}>
                <span className="choice-icon freelance-icon" aria-hidden="true">&#10010;</span>
                <span><strong>Independent doctor</strong><small>Book with a freelance provider</small></span>
                <span className="radio-mark" aria-hidden="true" />
              </button>
            </div>
          </fieldset>

          <div className="form-grid">
            {providerType === 'hospital' && (
              <label className="field field-wide">
                <span className="field-label">Hospital <span className="required-mark">*</span></span>
                <select value={hospitalId} onChange={(event) => changeHospital(event.target.value)} required>
                  <option value="">Select a hospital</option>
                  {options?.hospitals.map((hospital) => <option key={hospital.id} value={hospital.id}>{hospital.name} · {hospital.location}</option>)}
                </select>
              </label>
            )}

            <label className="field">
              <span className="field-label">Specialty <span className="required-mark">*</span></span>
              <select value={specialty} onChange={(event) => { setSpecialty(event.target.value); setDoctorId(''); }} required disabled={loading || availableSpecialties.length === 0}>
                <option value="">Choose a specialty</option>
                {availableSpecialties.map((item) => <option key={item} value={item}>{item}</option>)}
              </select>
            </label>

            <label className="field">
              <span className="field-label">{providerType === 'hospital' ? 'Doctor' : 'Freelance doctor'} <span className="required-mark">*</span></span>
              <select value={doctorId} onChange={(event) => setDoctorId(event.target.value)} required disabled={loading || !specialty || providers.length === 0}>
                <option value="">{loading ? 'Loading providers...' : providers.length ? 'Select a provider' : 'No providers for this selection'}</option>
                {providers.map((provider) => <option key={provider.id} value={provider.id}>{provider.name} · next available {formatDate(provider.next_available)}</option>)}
              </select>
              {providerType === 'hospital' && <small className="field-hint">Only doctors affiliated with your chosen hospital are shown.</small>}
            </label>

            <label className="field">
              <span className="field-label">Preferred date <span className="required-mark">*</span></span>
              <input type="date" value={appointmentDate} min={new Date().toISOString().slice(0, 10)} onChange={(event) => setAppointmentDate(event.target.value)} required />
            </label>

            <fieldset className="field time-field">
              <legend className="field-label">Preferred time <span className="required-mark">*</span></legend>
              <div className="time-slots">
                {timeSlots.map((slot) => (
                  <label key={slot} className={`time-slot ${appointmentTime === slot ? 'is-selected' : ''}`}>
                    <input type="radio" name="appointment-time" value={slot} checked={appointmentTime === slot} onChange={(event) => setAppointmentTime(event.target.value)} required />
                    <span>{slot}</span>
                  </label>
                ))}
              </div>
            </fieldset>

            <label className="field">
              <span className="field-label">Your name <span className="required-mark">*</span></span>
              <input type="text" autoComplete="name" value={patientName} onChange={(event) => setPatientName(event.target.value)} placeholder="Full name" minLength={2} maxLength={120} required />
            </label>

            <label className="field">
              <span className="field-label">Email address <span className="required-mark">*</span></span>
              <input type="email" autoComplete="email" value={patientEmail} onChange={(event) => setPatientEmail(event.target.value)} placeholder="you@example.com" required />
            </label>

            <label className="field field-wide">
              <span className="field-label">What would you like help with? <span className="optional-label">OPTIONAL</span></span>
              <textarea value={reason} onChange={(event) => setReason(event.target.value)} placeholder="Share a short note for the care team" rows={3} maxLength={500} />
            </label>
          </div>

          <div className="form-footer">
            <p><span className="privacy-mark" aria-hidden="true">&#9673;</span> Your details are used only to prepare this appointment request.</p>
            <button className="button button-dark" type="submit" disabled={submitting || loading || !appointmentTime}>
              {submitting ? 'Sending request...' : 'Request appointment'} <span aria-hidden="true">&#8594;</span>
            </button>
          </div>
        </form>
      </section>

      <footer className="site-footer"><span>&copy; 2026 Careway Health</span><span>Thoughtful care, closer to you.</span></footer>
    </main>
  );
}