import { apiRequest } from '../../lib/api-client';

export type ProviderType = 'hospital' | 'freelance';

export interface HospitalOption {
	id: string;
	name: string;
	location: string;
}

export interface ProviderOption {
	id: string;
	name: string;
	specialty: string;
	hospital_id: string | null;
	next_available: string;
}

export interface BookingOptions {
	demo_mode: boolean;
	hospitals: HospitalOption[];
	providers: ProviderOption[];
	specialties: string[];
}

export interface BookingInput {
	patient_name: string;
	patient_email: string;
	provider_type: ProviderType;
	hospital_id: string | null;
	doctor_id: string;
	appointment_date: string;
	appointment_time: string;
	reason: string | null;
}

export interface BookingReceipt {
	id: string;
	status: 'requested';
	provider_name: string;
	provider_type: ProviderType;
	hospital_name: string | null;
	appointment_date: string;
	appointment_time: string;
}

export function getBookingOptions(): Promise<BookingOptions> {
	return apiRequest<BookingOptions>('/api/v1/patients/booking-options');
}

export function requestBooking(input: BookingInput): Promise<BookingReceipt> {
	return apiRequest<BookingReceipt>('/api/v1/patients/bookings', {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify(input),
	});
}
