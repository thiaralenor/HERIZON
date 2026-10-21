create extension if not exists btree_gist;

create type public.booking_status as enum ('pending', 'confirmed', 'completed', 'cancelled', 'no_show');

create table public.bookings (
    id            uuid primary key default gen_random_uuid(),
    doctor_id     uuid not null references public.doctors(id) on delete cascade,
    patient_id    uuid not null references public.profiles(id) on delete cascade,
    starts_at     timestamptz not null,
    ends_at       timestamptz not null,
    status        public.booking_status not null default 'pending',
    reason        text,
    created_at    timestamptz not null default now(),
    updated_at    timestamptz not null default now(),

    constraint booking_time_order check (ends_at > starts_at)
);

-- Reject overlapping active bookings for the same doctor atomically.
-- Cancelled / no_show bookings release the slot.
alter table public.bookings
    add constraint no_overlapping_bookings
    exclude using gist (
        doctor_id with =,
        tstzrange(starts_at, ends_at) with &&
    ) where (status in ('pending', 'confirmed'));

create index bookings_patient_idx on public.bookings (patient_id, starts_at desc);
create index bookings_doctor_idx  on public.bookings (doctor_id, starts_at desc);