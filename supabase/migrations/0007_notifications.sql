create table public.notifications (
    id           uuid primary key default gen_random_uuid(),
    user_id      uuid not null references public.profiles(id) on delete cascade,
    type         text not null,               -- e.g. 'internship_open', 'booking_confirmed'
    title        text not null,
    body         text,
    data         jsonb not null default '{}'::jsonb,
    read_at      timestamptz,
    created_at   timestamptz not null default now()
);

create index notifications_user_idx on public.notifications (user_id, created_at desc);
create index notifications_unread_idx on public.notifications (user_id) where read_at is null;

-- Notify hospital admins and affiliated doctors whenever internship status changes.
create or replace function public.notify_internship_toggle()
returns trigger
language plpgsql
security definer set search_path = public
as $$
begin
    if old.internship_open is distinct from new.internship_open then
        insert into public.notifications (user_id, type, title, body, data)
        select recipients.user_id,
            case when new.internship_open
                then 'internship_open'
                else 'internship_closed'
            end,
            new.name || case when new.internship_open
                then ' is now open to interns'
                else ' is no longer open to interns'
            end,
            null,
            jsonb_build_object(
                'hospital_id', new.id,
                'internship_open', new.internship_open
            )
        from (
            select new.created_by as user_id
            where new.created_by is not null
            union
            select d.profile_id as user_id
            from public.doctors d
            where d.hospital_id = new.id
        ) as recipients;
    end if;
    return new;
end;
$$;

create trigger trg_notify_internship_toggle
after update of internship_open on public.hospitals
for each row execute function public.notify_internship_toggle();