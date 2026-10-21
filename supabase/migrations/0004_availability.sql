create table public.doctor_availability (
    id            uuid primary key default gen_random_uuid(),
    doctor_id     uuid not null references public.doctors(id) on delete cascade,
    weekday       smallint not null check (weekday between 0 and 6),   -- 0=Sunday
    start_time    time not null,
    end_time      time not null,
    slot_minutes  smallint not null default 30 check (slot_minutes > 0),
    constraint availability_time_order check (end_time > start_time)
);

create table public.doctor_time_off (
    id          uuid primary key default gen_random_uuid(),
    doctor_id   uuid not null references public.doctors(id) on delete cascade,
    starts_at   timestamptz not null,
    ends_at     timestamptz not null,
    reason      text,
    constraint time_off_order check (ends_at > starts_at)
);