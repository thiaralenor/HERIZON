create type public.doctor_type as enum ('hospital', 'freelance');

create table public.doctors (
    id              uuid primary key default gen_random_uuid(),
    profile_id      uuid not null unique references public.profiles(id) on delete cascade,
    doctor_type     public.doctor_type not null,
    hospital_id     uuid references public.hospitals(id) on delete restrict,
    specialty       text not null,
    bio             text,
    consultation_fee numeric(10,2),
    slug            text not null unique,        -- for landing page URL
    is_active       boolean not null default true,
    created_at      timestamptz not null default now(),
    updated_at      timestamptz not null default now(),

    constraint doctor_hospital_consistency check (
        (doctor_type = 'hospital'  and hospital_id is not null) or
        (doctor_type = 'freelance' and hospital_id is null)
    )
);

create index doctors_hospital_idx on public.doctors (hospital_id);
create index doctors_type_idx on public.doctors (doctor_type);
create index doctors_specialty_idx on public.doctors (specialty);