create table public.symptom_logs (
    id          uuid primary key default gen_random_uuid(),
    patient_id  uuid not null references public.profiles(id) on delete cascade,
    symptoms    text not null,
    severity    smallint check (severity between 1 and 10),
    logged_at   timestamptz not null default now()
);

create index symptom_logs_patient_idx on public.symptom_logs (patient_id, logged_at desc);