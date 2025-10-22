# Funnel Analyzer Pro

**AI-Powered Marketing Funnel Analysis SaaS MVP**

A production-ready full-stack application that analyzes marketing funnels using GPT-4o. Users can input multiple funnel URLs (sales pages, order forms, upsells, thank-you pages) and receive comprehensive AI-powered analysis with scores for clarity, value, proof, design, and flow.

## 🎯 Overview

**Backend**: FastAPI (Python 3.11) on Railway  
**Frontend**: Next.js 14 (App Router) on Vercel  
**Database**: PostgreSQL (Neon) with SQLAlchemy  
**AI**: OpenAI GPT-4o for analysis  
**Auth**: JWT tokens from WordPress membership site

### Key Features

- 🎨 Clean, Apple-like UI with Tailwind CSS + Framer Motion
- 🤖 AI-powered analysis of funnel pages
- 📊 Comprehensive scoring: Clarity, Value, Proof, Design, Flow
- 📱 Responsive dashboard with iframe embedding support
- 🔐 JWT authentication for WordPress integration
- 📄 PDF export capability (coming soon)
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
│   │   ├── analyzer.py       # Funnel analysis service (currently mock)
│   │   ├── auth.py           # JWT validation
│   │   └── reports.py        # Report retrieval
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
DATABASE_URL=sqlite:///./funnel_analyzer.db  # SQLite for local dev
JWT_SECRET=your-secret-minimum-32-characters
ENVIRONMENT=development
FRONTEND_URL=http://localhost:3001

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
| POST | `/api/auth/validate` | Validate JWT token |
| GET | `/api/reports/{user_id}` | Get user's past reports |
| GET | `/api/reports/detail/{analysis_id}` | Get detailed report |

### Frontend Routes

| Route | Description |
|-------|-------------|
| `/` | Marketing landing page |
| `/dashboard` | Main analysis interface |
| `/embed` | Minimal UI for iframe embedding |

### Real Analysis

The application now includes:
- ✅ **Web scraping** with BeautifulSoup + requests
- ✅ **OpenAI GPT-4o integration** for AI analysis  
- ✅ **Database persistence** with SQLite (local) or PostgreSQL (production)

**Analysis flow:**
1. Scrapes URLs to extract titles, headings, content, CTAs
2. Sends content to GPT-4o for analysis
3. Generates scores (clarity, value, proof, design, flow)
4. Creates actionable feedback and executive summary
5. Stores results in database

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

1. **Implement Real Analysis:**
   - Add Playwright for web scraping
   - Integrate OpenAI GPT-4o API
   - Parse and structure AI responses

2. **Enable Database:**
   - Set up Neon PostgreSQL
   - Run database migrations
   - Update services to use real database

3. **Add Authentication:**
   - Integrate WordPress JWT validation
   - Add user session management
   - Implement report history

4. **PDF Export:**
   - Integrate jsPDF + html2canvas
   - Style report templates
   - Add download functionality

5. **Advanced Features:**
   - Screenshot capture with Playwright
   - Comparison reports
   - Historical trend analysis
   - Team collaboration

## 🤝 Contributing

This is a private MVP. For questions or issues, contact the development team.

## 📄 License

Proprietary - Smart Tool Club © 2025
