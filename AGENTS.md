# AGENTS.md

## Purpose
This document is the authoritative implementation guide for AI coding agents working on the Secured Email Replying Agent project. It translates the product intent from `intial.MD` into concrete engineering direction so future agents can implement the system without re-deciding the core architecture.

## Current Repo Reality
- The repository is currently at an early setup stage with minimal project files.
- The initial product intent lives in `intial.MD`.
- The initial knowledge corpus lives in `towardsai_mixed_courses.csv`.
- There is not yet an established frontend or backend codebase, so agents should build the foundation described here rather than infer an existing architecture.

## Product Mission
Build a secure Gmail reply assistant for the Gmail owner. The system must:
- Read email from the Gmail Primary inbox.
- Generate reply drafts using Gemini.
- Ground relevant replies with knowledge retrieved from Supabase vector storage.
- Let the user review and edit every draft before sending.
- Send email only after explicit human approval.
- Store the AI draft, the final sent reply, and user feedback so the product can improve over time.

## Non-Negotiable Rules
- Never send email automatically.
- Every draft must be editable before send.
- In v1, only the configured Gmail owner may access the app.
- All reply generation for course and program questions must use retrieved knowledge when relevant.
- Store both the original AI-generated draft and the final user-approved reply.
- Store a 1 to 5 star rating and textual feedback for each completed reply.
- Secrets must never be hardcoded in source files.
- Security constraints must not be relaxed without explicit user approval.

## Locked Technical Direction
### Deployment split
- Frontend: lightweight web dashboard deployed on Vercel.
- Backend: Python API deployed on Railway.

### Core integrations
- Gmail API for inbox retrieval and reply sending.
- Gemini API for draft generation.
- Supabase Postgres for application data.
- Supabase `pgvector` for vector storage and retrieval.
- Google OAuth for authentication.

### Access model
- Authenticate with Google login.
- Restrict access to a single owner account defined by `APP_OWNER_EMAIL`.
- Any authenticated Google account other than the owner must be denied access.

### Knowledge source
- Use `towardsai_mixed_courses.csv` as the initial seed corpus.
- Convert the CSV records into retrievable knowledge documents stored in Supabase.
- Use retrieval-augmented generation for relevant replies.

## System Architecture
### Frontend responsibilities
- Provide Google sign-in.
- Display synced Primary inbox threads.
- Show thread details and message history.
- Let the owner trigger draft generation.
- Show retrieved supporting knowledge used for the draft.
- Allow full draft editing before send.
- Require an explicit send action.
- Collect star rating and textual feedback after a reply is sent.

### Backend responsibilities
- Enforce owner-only authentication and session validation.
- Sync Gmail messages from the Primary inbox only.
- Normalize Gmail threads and messages for frontend consumption.
- Generate grounded drafts with Gemini using retrieved context from Supabase.
- Persist draft history, sent replies, and feedback.
- Send approved replies through the Gmail API.
- Ingest knowledge data and manage embeddings plus retrieval.

### Supabase responsibilities
- Store application tables for threads, drafts, sent replies, feedback, and knowledge metadata.
- Store embeddings for knowledge retrieval.
- Preserve source references so generated responses can cite the relevant program information.

## Core Workflows
### 1. Authentication
1. User signs in with Google.
2. Backend validates the identity.
3. Access is granted only if the email matches `APP_OWNER_EMAIL`.
4. Non-owner accounts are rejected and cannot use the system.

### 2. Inbox sync
1. Backend fetches messages from the Gmail Primary inbox.
2. Messages are normalized into thread and message records.
3. Frontend displays the inbox for review.
4. Non-Primary categories are excluded from the workflow unless the user later changes this requirement.

### 3. Draft generation
1. User opens an email thread.
2. Backend analyzes the thread content.
3. Backend retrieves relevant course or program knowledge from Supabase vector storage.
4. Backend generates a reply draft with Gemini using:
   - the email thread context
   - retrieved knowledge snippets
   - the source references tied to those snippets
5. The system stores the initial AI draft and the retrieval context used to create it.

### 4. Review and send
1. Frontend presents the draft to the user.
2. User may edit any part of the draft.
3. Send is available only through an explicit approval action.
4. Backend sends the approved reply via Gmail API.
5. Backend stores the final sent version and related metadata.

### 5. Feedback and learning
1. After send, the user provides a 1 to 5 star rating.
2. The user may also provide textual feedback.
3. Backend stores the feedback linked to the sent reply.
4. Future personalization may use historical drafts, edits, and feedback, but only after the first two phases are complete.

## Canonical Data Model Expectations
Agents must preserve these logical records even if table names evolve.

### UserSession
- Google account email
- owner authorization result
- login timestamp
- session expiration data

### EmailThread
- internal thread id
- Gmail thread id
- message ids
- sender information
- recipients
- subject
- normalized body content
- received timestamps
- Gmail labels and category metadata
- sync timestamps

### KnowledgeDocument
- internal knowledge id
- source type
- source file name
- source row or record identifier
- title or course name
- content chunk
- structured metadata
- embedding vector
- source reference for citation
- ingestion timestamp

### DraftReply
- internal draft id
- linked thread id
- raw AI-generated draft text
- prompt or generation metadata
- retrieval context ids
- retrieval snippets or references
- model name
- created timestamp

### SentReply
- internal sent reply id
- linked draft id
- linked thread id
- final approved reply text
- Gmail sent message id
- sent timestamp
- editor identity

### ReplyFeedback
- internal feedback id
- linked sent reply id
- numeric rating from 1 to 5
- textual feedback
- created timestamp

## Environment and Secret Contract
The implementation must use environment variables for all credentials and deployment-specific settings.

Required variables:
- `APP_OWNER_EMAIL`
- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- `GOOGLE_REDIRECT_URI`
- `GMAIL_SCOPES`
- `GEMINI_API_KEY`
- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `SUPABASE_SERVICE_ROLE_KEY`
- `SUPABASE_DB_SCHEMA`

Rules:
- Do not hardcode secrets.
- Do not commit populated `.env` files.
- Use the service role key only on trusted backend paths.
- Keep the frontend limited to public-safe configuration only.

## Phased Execution Plan
### Phase 1: Secure draft review flow
Deliver the first usable version of the product with:
- Google sign-in
- owner-only access enforcement
- Gmail Primary inbox sync
- thread view
- Gemini draft generation
- editable draft review
- explicit manual send
- persistence of AI draft and final sent reply

Phase 1 success criteria:
- Owner can log in and review inbox threads.
- A draft can be generated for a thread.
- The draft can be edited before send.
- No send happens without explicit approval.
- The system stores both original and final reply text.

### Phase 2: Knowledge ingestion and RAG
Extend the system with:
- ingestion of `towardsai_mixed_courses.csv`
- chunking and embedding pipeline
- vector storage in Supabase
- retrieval for course and program-related replies
- grounded prompting with source references

Phase 2 success criteria:
- CSV records are ingestible into Supabase.
- Relevant email questions retrieve matching program information.
- Drafts use retrieved context rather than unsupported guesses.

### Phase 3: Feedback and preference learning
Add:
- post-send star rating
- textual feedback capture
- storage of reply history for later preference learning
- a personalization strategy based on historical approved replies and feedback

Phase 3 success criteria:
- Each sent reply can collect rating and text feedback.
- Feedback is stored and linked to the sent reply.
- Historical edits and ratings are available for future personalization work.

### Phase 4: Production hardening
Prepare for stable deployment with:
- environment validation
- error handling and retry strategy
- audit-friendly logging
- deployment configuration for Vercel and Railway
- performance checks for Gmail sync, retrieval, and draft generation

Phase 4 success criteria:
- Frontend can be deployed on Vercel.
- Backend can be deployed on Railway.
- Secrets remain isolated.
- Operational failures are visible and diagnosable.

## Acceptance Criteria for the Product Spec
This document should remain detailed enough that another agent can start implementation without choosing the core architecture. Any implementation must satisfy the following:
- The system is owner-only in v1.
- The inbox workflow is based on Gmail Primary messages.
- Drafts are generated with Gemini.
- Knowledge retrieval uses Supabase vector storage.
- Users can always edit drafts before send.
- Sending requires explicit approval.
- AI draft and final reply are both stored.
- Ratings and textual feedback are stored for each sent reply.
- The repo evolves in phases rather than as an unstructured full build.

## Agent Working Rules
- Implement incrementally by phase.
- Do not skip Phase 1 to build the entire platform at once.
- Ask for user confirmation before changing the locked stack, access model, or send-approval requirement.
- Prefer secure defaults and least-privilege access.
- Prefer grounded responses over unsupported model improvisation.
- Keep implementation decisions consistent with this file unless the user explicitly changes requirements.
- When requirements conflict, prioritize this file plus the latest user instruction over older assumptions.

## Future Enhancements
These are valid later additions, but not required for the first implementation pass:
- richer inbox triage and search
- smarter personalization from historical edits
- analytics on response quality
- broader team workflows beyond owner-only access
- expanded knowledge sources beyond the CSV seed corpus
