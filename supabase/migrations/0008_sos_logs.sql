create table public.sos_logs (
    id           uuid primary key default gen_random_uuid(),
    user_id      uuid not null references public.profiles(id) on delete cascade,
    hospital_id  uuid references public.hospitals(id),
    latitude     double precision,
    longitude    double precision,
    created_at   timestamptz not null default now()
);