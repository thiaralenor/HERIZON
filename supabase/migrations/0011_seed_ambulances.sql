-- supabase/migrations/0011_seed_ambulances.sql
insert into public.ambulances (hospital_id, call_sign, status, current_lat, current_lng)
select h.id, 'BRH-AMB-01', 'available', 4.1560, 9.2410 from public.hospitals h
where h.name = 'Buea Regional Hospital' limit 1;

insert into public.ambulances (hospital_id, call_sign, status, current_lat, current_lng)
select h.id, 'BRH-AMB-02', 'available', 4.1520, 9.2380 from public.hospitals h
where h.name = 'Buea Regional Hospital' limit 1;