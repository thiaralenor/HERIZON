-- Ambulances: seeded + admin-manageable. Represents a vehicle that CAN be dispatched.
create table public.ambulances (
    id             uuid primary key default gen_random_uuid(),
    hospital_id    uuid references public.hospitals(id) on delete cascade,
    call_sign      text not null,                  -- e.g. "BRH-AMB-01"
    status         text not null default 'available'
                   check (status in ('available', 'en_route', 'on_scene', 'offline')),
    current_lat    double precision,
    current_lng    double precision,
    updated_at     timestamptz not null default now(),
    created_at     timestamptz not null default now()
);

create index ambulances_status_idx on public.ambulances (status);
create index ambulances_hospital_idx on public.ambulances (hospital_id);

-- Dispatch requests: the operational record created when a patient presses SOS.
create type public.dispatch_status as enum (
    'pending',        -- created, no ambulance assigned yet
    'assigned',       -- ambulance selected, simulating movement
    'en_route',       -- ambulance "moving" toward patient
    'arrived',        -- simulated arrival
    'cancelled',
    'failed'          -- no ambulance available within radius
);

create table public.dispatch_requests (
    id              uuid primary key default gen_random_uuid(),
    patient_id      uuid not null references public.profiles(id) on delete cascade,
    hospital_id     uuid references public.hospitals(id) on delete set null,
    ambulance_id    uuid references public.ambulances(id) on delete set null,
    status          public.dispatch_status not null default 'pending',
    patient_lat     double precision,
    patient_lng     double precision,
    note            text,
    created_at      timestamptz not null default now(),
    updated_at      timestamptz not null default now()
);

create index dispatch_requests_patient_idx on public.dispatch_requests (patient_id, created_at desc);
create index dispatch_requests_status_idx on public.dispatch_requests (status);

-- Real-time "position trail" for the simulated ambulance.
-- For Path B this same table would receive real GPS from the driver app.
create table public.dispatch_positions (
    id                   uuid primary key default gen_random_uuid(),
    dispatch_request_id  uuid not null references public.dispatch_requests(id) on delete cascade,
    lat                  double precision not null,
    lng                  double precision not null,
    recorded_at          timestamptz not null default now()
);

create index dispatch_positions_request_idx
    on public.dispatch_positions (dispatch_request_id, recorded_at desc);

-- Path A simulation: a small function that walks an ambulance toward the patient
-- over N ticks. This is what makes the map animate. In Path B this is replaced
-- by real GPS updates from the driver app — the schema does not change.
create or replace function public.simulate_dispatch_step(p_dispatch_id uuid)
returns void
language plpgsql
as $$
declare
    v_start_lat  double precision;
    v_start_lng  double precision;
    v_pat_lat    double precision;
    v_pat_lng    double precision;
    v_step       integer;
    v_new_lat    double precision;
    v_new_lng    double precision;
    v_total_steps constant integer := 20;
begin
    select a.current_lat, a.current_lng, dr.patient_lat, dr.patient_lng, dr.id
      into v_start_lat, v_start_lng, v_pat_lat, v_pat_lng, v_step
    from public.dispatch_requests dr
    join public.ambulances a on a.id = dr.ambulance_id
    where dr.id = p_dispatch_id;

    if v_start_lat is null or v_pat_lat is null then
        return;
    end if;

    -- count existing simulated positions as the "step" counter
    select count(*) into v_step
    from public.dispatch_positions
    where dispatch_request_id = p_dispatch_id;

    if v_step >= v_total_steps then
        update public.dispatch_requests
           set status = 'arrived', updated_at = now()
         where id = p_dispatch_id;
        return;
    end if;

    -- linear interpolation from start to patient
    v_new_lat := v_start_lat + ((v_pat_lat - v_start_lat) * (v_step + 1) / v_total_steps);
    v_new_lng := v_start_lng + ((v_pat_lng - v_start_lng) * (v_step + 1) / v_total_steps);

    insert into public.dispatch_positions (dispatch_request_id, lat, lng)
    values (p_dispatch_id, v_new_lat, v_new_lng);

    update public.ambulances
       set current_lat = v_new_lat,
           current_lng = v_new_lng,
           updated_at  = now()
     where id = (select ambulance_id from public.dispatch_requests where id = p_dispatch_id);

    update public.dispatch_requests
       set status = 'en_route', updated_at = now()
     where id = p_dispatch_id and status = 'assigned';
end;
$$;

-- RLS
alter table public.ambulances        enable row level security;
alter table public.dispatch_requests enable row level security;
alter table public.dispatch_positions enable row level security;

-- Public can read ambulances (for the demo map); only service role writes.
create policy "ambulances_public_read" on public.ambulances
    for select using (true);

-- Patient sees own dispatches; hospital admin sees dispatches assigned to their hospital.
create policy "dispatch_requests_owner_read" on public.dispatch_requests
    for select using (
        auth.uid() = patient_id
        or auth.uid() = (
            select created_by from public.hospitals where id = hospital_id
        )
    );

create policy "dispatch_requests_patient_insert" on public.dispatch_requests
    for insert with check (auth.uid() = patient_id);

create policy "dispatch_requests_owner_update" on public.dispatch_requests
    for update using (
        auth.uid() = patient_id
        or auth.uid() = (
            select created_by from public.hospitals where id = hospital_id
        )
    ) with check (
        auth.uid() = patient_id
        or auth.uid() = (
            select created_by from public.hospitals where id = hospital_id
        )
    );

-- Position trail is readable only by the patient or the hospital admin for that dispatch.
create policy "dispatch_positions_party_read" on public.dispatch_positions
    for select using (
        auth.uid() = (
            select patient_id from public.dispatch_requests where id = dispatch_request_id
        )
        or auth.uid() = (
            select h.created_by
            from public.dispatch_requests dr
            join public.hospitals h on h.id = dr.hospital_id
            where dr.id = dispatch_request_id
        )
    );