create extension if not exists vector;

create table if not exists draft_replies (
    id uuid primary key default gen_random_uuid(),
    gmail_thread_id text not null,
    thread_snapshot jsonb not null,
    draft_text text not null,
    model_name text not null,
    retrieval_context jsonb not null default '[]'::jsonb,
    created_at timestamptz not null default timezone('utc', now())
);

create table if not exists sent_replies (
    id uuid primary key default gen_random_uuid(),
    draft_reply_id uuid null,
    gmail_thread_id text not null,
    thread_snapshot jsonb not null,
    final_text text not null,
    gmail_sent_message_id text not null,
    sent_at timestamptz not null default timezone('utc', now())
);

create table if not exists reply_feedback (
    id uuid primary key default gen_random_uuid(),
    sent_reply_id uuid not null references sent_replies(id) on delete cascade,
    rating smallint not null check (rating between 1 and 5),
    feedback_text text null,
    created_at timestamptz not null default timezone('utc', now())
);

create table if not exists knowledge_documents (
    id uuid primary key default gen_random_uuid(),
    source_type text not null,
    source_file text not null,
    source_record_id text not null,
    title text not null,
    content text not null,
    metadata jsonb not null default '{}'::jsonb,
    embedding vector(1536),
    created_at timestamptz not null default timezone('utc', now())
);

create index if not exists idx_draft_replies_gmail_thread_id on draft_replies (gmail_thread_id);
create index if not exists idx_sent_replies_gmail_thread_id on sent_replies (gmail_thread_id);
