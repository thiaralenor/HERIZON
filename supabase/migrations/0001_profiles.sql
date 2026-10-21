create type public.user_role as enum ('patient', 'doctor', 'freelancer', 'hospital_admin');

create table public.profiles (
    id          uuid primary key references auth.users(id) on delete cascade,
    role        public.user_role not null default 'patient',
    full_name   text not null,
    phone       text,
    created_at  timestamptz not null default now(),
    updated_at  timestamptz not null default now()
);

-- Auto-create profile when a user signs up
create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer set search_path = public
as $$
begin
    insert into public.profiles (id, full_name, role)
    values (
        new.id,
        coalesce(new.raw_user_meta_data->>'full_name', ''),
        coalesce((new.raw_user_meta_data->>'role')::public.user_role, 'patient')
    );
    return new;
end;
$$;

create trigger on_auth_user_created
after insert on auth.users
for each row execute function public.handle_new_user();