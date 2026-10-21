alter table public.profiles         enable row level security;
alter table public.hospitals        enable row level security;
alter table public.doctors          enable row level security;
alter table public.bookings         enable row level security;
alter table public.symptom_logs     enable row level security;
alter table public.notifications    enable row level security;
alter table public.doctor_availability enable row level security;
alter table public.doctor_time_off  enable row level security;
alter table public.sos_logs         enable row level security;

-- Profiles: users read own; public read limited fields via a view (optional)
create policy "profiles_select_own" on public.profiles
    for select using (auth.uid() = id);
create policy "profiles_update_own" on public.profiles
    for update using (auth.uid() = id);

-- Hospitals & doctors: public read
create policy "hospitals_public_read" on public.hospitals for select using (true);
create policy "doctors_public_read"   on public.doctors   for select using (true);

-- Bookings: patient sees own; doctor sees own bookings
create policy "bookings_patient_read" on public.bookings
    for select using (auth.uid() = patient_id);
create policy "bookings_doctor_read" on public.bookings
    for select using (
        exists (
            select 1 from public.doctors d
            where d.id = bookings.doctor_id and d.profile_id = auth.uid()
        )
    );

-- Symptom logs: owner only
create policy "symptoms_owner_all" on public.symptom_logs
    for all using (auth.uid() = patient_id) with check (auth.uid() = patient_id);

-- Notifications: owner only
create policy "notifications_owner_read" on public.notifications
    for select using (auth.uid() = user_id);
create policy "notifications_owner_update" on public.notifications
    for update using (auth.uid() = user_id);

-- SOS records: users may access only their own records.
create policy "sos_logs_owner_all" on public.sos_logs
    for all using (auth.uid() = user_id) with check (auth.uid() = user_id);