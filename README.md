# Secured Email Replying AI Agent

Phase 1 is now scaffolded as a split application:

- `backend/`: FastAPI API for Google auth, Gmail inbox sync, Gemini draft generation, and reply sending.
- `frontend/`: Next.js dashboard for login, thread review, draft editing, and explicit send approval.
- `backend/supabase/schema.sql`: starter Supabase schema for drafts, sent replies, feedback, and future knowledge storage.

## Phase 1 Scope
- Google login with owner-only access enforcement
- Gmail Primary inbox listing
- Thread review UI
- Gemini-powered reply draft generation
- Manual draft editing before send
- Explicit send action only
- Draft and sent reply persistence contracts

## Local Development

Backend:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e .[dev]
uvicorn backend.app.main:app --reload
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

## Required Configuration

Backend env:
- `APP_OWNER_EMAIL`
- `FRONTEND_URL`
- `SESSION_SECRET`
- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- `GOOGLE_REDIRECT_URI`
- `GMAIL_SCOPES`
- `GEMINI_API_KEY`
- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`

Frontend env:
- `NEXT_PUBLIC_API_BASE_URL`

See `backend/.env.example` and `frontend/.env.example` for the full template.

## Local Google Auth Setup

To experience Phase 1 locally, complete the OAuth setup below and then fill the generated values into `backend/.env`.

### 1. Create the Google OAuth app
- Create or reuse a Google Cloud project.
- Enable the Gmail API.
- Configure the OAuth consent screen as `External`.
- Keep the app in testing mode for local development.
- Add the Gmail owner account as a test user.
- Create an OAuth client of type `Web application`.

### 2. Add the localhost redirect URI
Use this exact authorized redirect URI in Google Cloud:

```text
http://localhost:8000/api/auth/callback
```

### 3. Fill the local env files
Update `backend/.env` with:
- `APP_OWNER_EMAIL`
- `SESSION_SECRET`
- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- `GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/callback`
- `GMAIL_SCOPES=openid email profile https://www.googleapis.com/auth/gmail.modify https://www.googleapis.com/auth/gmail.send`
- `GEMINI_API_KEY`
- `FRONTEND_URL=http://localhost:3000`
- `ALLOWED_ORIGINS=http://localhost:3000`

Update `frontend/.env.local` with:
- `NEXT_PUBLIC_API_BASE_URL=http://localhost:8000`

### 4. Run the app locally
Start the backend:

```bash
uvicorn backend.app.main:app --reload
```

Start the frontend:

```bash
cd frontend
npm install
npm run dev
```

Then open `http://localhost:3000`.

### 5. Validate the auth flow
- Visit `http://localhost:8000/api/health` and confirm `gmail_configured` becomes `true`.
- Sign in with the exact Gmail address in `APP_OWNER_EMAIL`.
- Confirm the app redirects back to `/auth/callback` and then `/dashboard`.
- Confirm non-owner Google accounts are rejected.
