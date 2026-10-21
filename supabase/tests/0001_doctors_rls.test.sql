begin;
select plan(4);

-- Setup: create two users, two doctors
insert into auth.users (id, email, raw_user_meta_data)
values
  ('00000000-0000-0000-0000-000000000001', 'd1@x.com', '{"role":"doctor","full_name":"D1"}'),
  ('00000000-0000-0000-0000-000000000002', 'd2@x.com', '{"role":"doctor","full_name":"D2"}');

insert into public.doctors (id, profile_id, specialty, serves_neighborhoods, contact_method)
values
  ('10000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000001',
   'Cardio', '{Bokova}', 'phone'),
  ('10000000-0000-0000-0000-000000000002', '00000000-0000-0000-0000-000000000002',
   'Derma', '{Molyko}', 'phone');

-- As doctor 1
set local role authenticated;
set local request.jwt.claim.sub = '00000000-0000-0000-0000-000000000001';

select is(
  (select count(*)::int from public.doctors where profile_id = auth.uid()),
  1,
  'doctor 1 sees own row'
);

-- attempt to update doctor 2 (RLS should filter the row → 0 updated)
update public.doctors set bio = 'hijacked'
 where id = '10000000-0000-0000-0000-000000000002';

select is(
  (select bio from public.doctors where id = '10000000-0000-0000-0000-000000000002'),
  null,
  'doctor 1 cannot update doctor 2 row'
);

-- try to insert row with someone else's profile_id (should fail with check violation)
select throws_ok(
  $$ insert into public.doctors (profile_id, specialty, serves_neighborhoods, contact_method)
     values ('00000000-0000-0000-0000-000000000002', 'X', '{Y}', 'phone') $$,
  '42501',
  null,
  'doctor 1 cannot insert a doctor row for doctor 2'
);

-- public read: anon sees all doctors
set local role anon;
set local request.jwt.claim.sub = '';
select is(
  (select count(*)::int from public.doctors),
  2,
  'anonymous can read all doctors'
);

select * from finish();
rollback;