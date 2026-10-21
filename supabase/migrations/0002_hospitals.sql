create table public.hospitals (
    id               uuid primary key default gen_random_uuid(),
    name             text not null,
    address          text,
    city             text,
    phone            text,
    emergency_line   text,                 -- used by SOS
    internship_open  boolean not null default false,
    created_by       uuid references public.profiles(id),
    created_at       timestamptz not null default now(),
    updated_at       timestamptz not null default now()
);

create index hospitals_city_idx on public.hospitals (city);
create index hospitals_internship_idx on public.hospitals (internship_open);