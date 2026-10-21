begin;
select plan(3);

insert into auth.users (id, email, raw_user_meta_data) values
  ('00000000-0000-0000-0000-0000000000a1', 'pa@x.com', '{"role":"patient","full_name":"PA"}'),
  ('00000000-0000-0000-0000-0000000000a2', 'pb@x.com', '{"role":"patient","full_name":"PB"}'),
  ('00000000-0000-0000-0000-0000000000d1', 'dd@x.com', '{"role":"doctor","full_name":"DD"}');

insert into public.doctors (id, profile_id, specialty, serves_neighborhoods, contact_method)
values ('20000000-0000-0000-0000-000000000001',
        '00000000-0000-0000-0000-0000000000d1', 'GP', '{Molyko}', 'phone');

insert into public.bookings (id, doctor_id, patient_id, starts_at, ends_at, status)
values ('30000000-0000-0000-0000-000000000001',
        '20000000-0000-0000-0000-000000000001',
        '00000000-0000-0000-0000-0000000000a1',
        now() + interval '1 day', now() + interval '1 day 30 minutes', 'confirmed');

-- patient A sees own booking
set local role authenticated;
set local request.jwt.claim.sub = '00000000-0000-0000-0000-0000000000a1';
select is(
  (select count(*)::int from public.bookings),
  1,
  'patient A sees own booking'
);

-- patient B sees nothing
set local request.jwt.claim.sub = '00000000-0000-0000-0000-0000000000a2';
select is(
  (select count(*)::int from public.bookings),
  0,
  'patient B cannot see patient A booking'
);

-- doctor sees the booking
set local request.jwt.claim.sub = '00000000-0000-0000-0000-0000000000d1';
select is(
  (select count(*)::int from public.bookings),
  1,
  'doctor sees booking addressed to them'
);

select * from finish();
rollback;