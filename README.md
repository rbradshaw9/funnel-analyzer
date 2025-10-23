# Funnel Analyzer Pro

**AI-Powered Marketing Funnel Analysis SaaS MVP**

A production-ready full-stack application that analyzes marketing funnels using GPT-4o. Users can input multiple funnel URLs (sales pages, order forms, upsells, thank-you pages) and receive comprehensive AI-powered analysis with scores for clarity, value, proof, design, and flow.

## 🎯 Overview

**Backend**: FastAPI (Python 3.11) on Railway  
**Frontend**: Next.js 14 (App Router) on Vercel  
**Database**: PostgreSQL with SQLAlchemy  
**AI**: OpenAI GPT-4o for analysis (pluggable provider registry)  
**Auth**: JWT tokens from WordPress membership site

### Key Features

- 🎨 Clean, Apple-like UI with Tailwind CSS + Framer Motion
- 🤖 AI-powered analysis of funnel pages with CRO-grade recommendations
- 📊 Comprehensive scoring: Clarity, Value, Proof, Design, Flow plus diagnostics
- 📱 Responsive dashboard with iframe embedding support
- 🔐 JWT authentication for WordPress integration
- 📄 PDF export capability (coming soon)
- 🖼️ Automatic Playwright screenshots stored in S3 (optional)
- ✉️ SendGrid-ready transactional email service for magic links and notifications
- ⚡ Real-time analysis with loading animations

## 📁 Project Structure

```
funnel-analyzer/
├── backend/                    # FastAPI Python backend
│   ├── main.py                # Application entry point
│   ├── routes/                # API route handlers
│   │   ├── analysis.py       # POST /api/analyze
│   │   ├── auth.py           # POST /api/auth/validate
│   │   └── reports.py        # GET /api/reports/{user_id}
│   ├── models/               # Database models & Pydantic schemas
│   │   ├── database.py       # SQLAlchemy models (User, Analysis, AnalysisPage)
│   │   └── schemas.py        # Request/response validation
│   ├── services/             # Business logic
│   │   ├── analyzer.py       # Funnel analysis orchestration
│   │   ├── auth.py           # JWT validation
│   │   ├── email.py          # SendGrid transactional helper
│   │   ├── llm_provider.py   # Provider registry (OpenAI by default)
│   │   ├── reports.py        # Report retrieval
│   │   ├── screenshot.py     # Playwright screenshot capture
│   │   ├── scraper.py        # Content extraction
│   │   └── storage.py        # Screenshot upload to S3
│   ├── utils/                # Utilities
│   │   └── config.py         # Settings management
│   ├── requirements.txt      # Python dependencies
│   ├── package.json          # For Railway compatibility
│   └── Dockerfile            # Production Docker build
│
├── frontend/                  # Next.js 14 frontend
│   ├── app/                  # App Router pages
│   │   ├── page.tsx         # Landing page (/)
│   │   ├── dashboard/       # Main app (/dashboard)
│   │   ├── embed/           # iframe version (/embed)
│   │   ├── layout.tsx       # Root layout
│   │   └── globals.css      # Global styles
│   ├── components/          # React components
│   │   ├── URLInputForm.tsx        # Multi-URL input
│   │   ├── LoadingAnimation.tsx    # Analysis progress
│   │   ├── ResultsDashboard.tsx    # Results display
│   │   ├── ScoreCard.tsx          # Individual score cards
│   │   └── PageAnalysisCard.tsx   # Per-page analysis
│   ├── lib/                 # Utilities
│   │   └── api.ts          # API client (Axios)
│   ├── store/              # State management
│   │   └── analysisStore.ts # Zustand store
│   ├── types/              # TypeScript types
│   │   └── index.ts       # Shared interfaces
│   ├── package.json       # Node dependencies
│   ├── next.config.js     # Next.js config (static export)
│   ├── tailwind.config.js # Tailwind setup
│   └── vercel.json        # Vercel deployment config
│
├── .github/
│   ├── workflows/
│   │   └── deploy.yml      # CI/CD pipeline
│   └── copilot-instructions.md  # AI agent guidelines
├── .env.example            # Environment template
├── railway.json            # Railway deployment config
└── README.md              # This file
```

## 🚀 Quick Start

### Prerequisites

- **Node.js 18.x** (LTS)
- **Python 3.11+**
- **OpenAI API Key** (for AI analysis - get from https://platform.openai.com)
- **PostgreSQL database** (optional - SQLite used by default for local dev)

### 1. Clone & Environment Setup

```bash
# Clone the repository
git clone https://github.com/rbradshaw9/funnel-analyzer.git
cd funnel-analyzer

# Copy environment template
cp .env.example .env
```

### 2. Configure Environment Variables

Edit `.env` with your credentials:

```bash
# Backend (.env in project root or backend/.env)
OPENAI_API_KEY=sk-your-actual-openai-key-here
LLM_PROVIDER=openai
DATABASE_URL=sqlite:///./funnel_analyzer.db  # SQLite for local dev
JWT_SECRET=your-secret-minimum-32-characters
ENVIRONMENT=development
FRONTEND_URL=http://localhost:3001
# Optional screenshot storage (S3, R2, Supabase)
AWS_S3_BUCKET=your-screenshot-bucket
AWS_S3_REGION=us-east-1
AWS_S3_ACCESS_KEY_ID=...
AWS_S3_SECRET_ACCESS_KEY=...
AWS_S3_ENDPOINT_URL=https://s3.us-east-1.amazonaws.com  # optional for R2/Supabase
AWS_S3_BASE_URL=https://cdn.yourdomain.com (optional CDN)
# Optional transactional email (SendGrid)
SENDGRID_API_KEY=...
EMAIL_DEFAULT_FROM="Funnel Analyzer <reports@smarttoolclub.com>"
EMAIL_DEFAULT_REPLY_TO=support@smarttoolclub.com
# Automation/webhooks
THRIVECART_WEBHOOK_SECRET=...
MAUTIC_BASE_URL=https://your-mautic-instance
MAUTIC_CLIENT_ID=...
MAUTIC_CLIENT_SECRET=...
MAUTIC_API_USERNAME=...
MAUTIC_API_PASSWORD=...

# Frontend (.env.local in frontend/)
NEXT_PUBLIC_API_URL=http://localhost:3000
NEXT_PUBLIC_ENV=development
```

### 3. Backend Setup & Run

```bash
# From project root, activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies (if not already installed)
cd backend
pip install -r requirements.txt

# Run development server
uvicorn backend.main:app --reload --host 0.0.0.0 --port 3000

# Or run in background
nohup uvicorn backend.main:app --host 0.0.0.0 --port 3000 > /tmp/funnel-backend.log 2>&1 &
```

The backend API will be available at: `http://localhost:3000`

**API Documentation**: `http://localhost:3000/docs` (Swagger UI)

### 4. Frontend Setup & Run

Open a new terminal:

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

The frontend will be available at: `http://localhost:3001`

### 5. Test the Application

1. Open browser to `http://localhost:3001`
2. Click "Get Started" or navigate to `/dashboard`
3. Enter funnel URLs (e.g., `https://example.com/sales`)
4. Click "Analyze Funnel"
5. View AI-generated results with scores and feedback

## 🔧 Development

### Backend API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| GET | `/health` | Detailed system status |
| POST | `/api/analyze` | Analyze funnel URLs (returns scores + feedback) |
| POST | `/api/analyze/{analysis_id}/email` | Trigger email delivery for an existing report |
| POST | `/api/auth/validate` | Validate JWT token |
| POST | `/api/webhooks/thrivecart` | Receive ThriveCart purchase webhooks |
| GET | `/api/reports/{user_id}` | Get user's past reports |
| GET | `/api/reports/detail/{analysis_id}` | Get detailed report |

#### POST `/api/analyze`

Request body:

```json
{
   "urls": ["https://example.com/sales", "https://example.com/checkout"],
   "email": "optional-recipient@example.com"
}
```

- `email` is optional. When supplied, the backend queues a SendGrid notification with the executive summary and page breakdown and stores the recipient so the report can be re-sent later.

#### POST `/api/analyze/{analysis_id}/email`

```json
{
   "email": "recipient@example.com"
}
```

- Allows operations or the frontend to re-send any saved analysis once credentials are configured. Responds with `{"status": "sent"}` when the email service succeeds.

#### POST `/api/webhooks/thrivecart`

- Expects a ThriveCart webhook payload with header `X-Webhook-Signature` containing an HMAC SHA-256 digest of the raw body using `THRIVECART_WEBHOOK_SECRET`.
- Persists the payload to the `webhook_events` table for audit/replay and returns `{ "status": "ok" }` with HTTP 202 when accepted.
- Use Railway/Vercel secrets to configure the shared secret before enabling the webhook in ThriveCart.

### Frontend Routes

| Route | Description |
|-------|-------------|
| `/` | Marketing landing page |
| `/dashboard` | Main analysis interface |
| `/embed` | Minimal UI for iframe embedding |

### Real Analysis

The application now includes:
- ✅ **Web scraping** with BeautifulSoup + requests
- ✅ **OpenAI GPT-4o integration** for AI analysis (extensible provider layer)  
- ✅ **Database persistence** with SQLite (local) or PostgreSQL (production)
- ✅ **Vision analysis** with Playwright screenshots (uploaded to S3 when configured)
- ✅ **Consultant-level recommendations** including CTA tests, alerts, trust gaps, diagnostics

**Analysis flow:**
1. Scrapes URLs to extract titles, headings, content, CTAs
2. Captures above-the-fold screenshots via Playwright (optional upload to S3)
3. Sends content + visual context to the configured LLM for analysis
3. Generates scores (clarity, value, proof, design, flow)
4. Creates actionable feedback, diagnostics, and executive summary
5. Stores results in database and persists screenshot URLs when available

**Without OpenAI API key:** Falls back to intelligent placeholder scores based on scraped content.

### Database Setup

The application automatically creates the database on first run.

**Local Development (SQLite):**
- Database file: `funnel_analyzer.db` in project root
- No setup required - auto-created on startup
- Tables: `users`, `analyses`, `analysis_pages`
- Demo user created automatically: `demo@funnelanalyzer.pro`

**Production (PostgreSQL):**
- Set `DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/dbname`
- Database schema created automatically on deployment
- Use Railway PostgreSQL or Neon for hosting

## 🐳 Docker Development

Test the backend in a production-like environment:

```bash
# Build Docker image
docker build -t funnel-analyzer-backend ./backend

# Run container
docker run --rm -p 3000:3000 --env-file .env funnel-analyzer-backend
```

## 🚢 Deployment

### Backend → Railway

1. Create Railway project: `railway.app`
2. Add environment variables in Railway dashboard:
   - `OPENAI_API_KEY`
   - `DATABASE_URL`
   - `JWT_SECRET`
   - `ENVIRONMENT=production`
   - `FRONTEND_URL=https://your-vercel-app.vercel.app`
   - `AWS_S3_BUCKET=funnel-analyzer-pro`
   - `AWS_S3_REGION=us-east-1`
   - `AWS_S3_ACCESS_KEY_ID=...`
   - `AWS_S3_SECRET_ACCESS_KEY=...`
   - `AWS_S3_BASE_URL` (optional CDN/front-door URL)
   - `SENDGRID_API_KEY=...`
   - `EMAIL_DEFAULT_FROM="Funnel Analyzer <reports@smarttoolclub.com>"`
   - `EMAIL_DEFAULT_REPLY_TO=support@smarttoolclub.com`

3. Railway will automatically:
   - Detect `Dockerfile`
   - Build and deploy
   - Use `railway.json` configuration

**Manual deployment:**
```bash
npm install -g @railway/cli
railway login
railway link  # Link to existing project
railway up
```

### Frontend → Vercel

1. Import project in Vercel dashboard
2. Set environment variables:
   - `NEXT_PUBLIC_API_URL=https://your-railway-app.railway.app`

3. Vercel will automatically:
   - Detect Next.js
   - Build static export
   - Deploy to CDN

**Manual deployment:**
```bash
npm install -g vercel
cd frontend
vercel --prod
```

### Automated CI/CD

GitHub Actions workflow (`.github/workflows/deploy.yml`) automatically:

1. **On push to `main`:**
   - Runs Python linting (flake8) on backend
   - Runs Next.js linting on frontend
   - Deploys backend to Railway (if `RAILWAY_TOKEN` secret exists)
   - Deploys frontend to Vercel (if `VERCEL_TOKEN` secrets exist)

2. **Required GitHub Secrets:**
   - `RAILWAY_TOKEN`
   - `VERCEL_TOKEN`
   - `VERCEL_ORG_ID`
   - `VERCEL_PROJECT_ID`

## 🔌 WordPress Integration

This is a **standalone application**, not a WordPress plugin. It integrates via JWT tokens:

### Setup

1. Install JWT plugin on WordPress (e.g., JWT Authentication for WP REST API)
2. Configure shared `JWT_SECRET` in both WordPress and Funnel Analyzer
3. Pass token to app via URL parameter:
   ```
   https://app.smarttoolclub.com/dashboard?token=abc123
   ```

### Embedding in WordPress

Use iframe:

```html
<iframe 
  src="https://app.smarttoolclub.com/embed?token=USER_JWT_TOKEN"
  width="100%" 
  height="800"
  frameborder="0"
></iframe>
```

## 🎨 Customization

### Styling

- Edit `frontend/tailwind.config.js` for colors/themes
- Primary color: `primary-600` (#4f46e5 indigo)
- Modify `frontend/app/globals.css` for global styles

### Analysis Criteria

Modify scoring criteria in `backend/services/analyzer.py`:
- Clarity: Message understanding
- Value: Value proposition strength
- Proof: Social proof elements
- Design: Visual quality
- Flow: User journey smoothness

## 🧪 Testing

```bash
# Backend
cd backend
pip install pytest pytest-asyncio
pytest

# Frontend
cd frontend
npm test
```

## 📝 Next Steps

### To Complete Production Setup:

1. **Credential wiring:** supply S3 + SendGrid + ThriveCart/Mautic secrets to unlock screenshot hosting, email notifications, and CRM sync.
2. **Auth polish:** finish JWT/magic-link flow and gated dashboard UX.
3. **Reporting:** implement PDF export and scheduled email digests using the email service.
4. **Data sync:** integrate ThriveCart webhooks + Mautic API to push analyses into lifecycle automations.
5. **Insights roadmap:** add historical trend comparisons, experiment tracking, and team collaboration features.

## 🤝 Contributing

This is a private MVP. For questions or issues, contact the development team.

## 📄 License

Proprietary - Smart Tool Club © 2025
