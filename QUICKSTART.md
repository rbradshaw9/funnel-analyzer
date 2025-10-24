# Funnel Analyzer Pro - Quick Start Guide

Get the application running in under 5 minutes!

## Prerequisites

- **Python 3.10+** installed
- **Node.js 18+** installed  
- **OpenAI API Key** (optional - app works without it using placeholder data)

## Step 1: Clone & Setup Environment

```bash
# Clone the repository
git clone https://github.com/rbradshaw9/funnel-analyzer.git
cd funnel-analyzer

# Create Python virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install Python dependencies
cd backend
pip install -r requirements.txt
cd ..
```

## Step 2: Configure Environment (Optional)

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add secrets (as available):
# OPENAI_API_KEY=sk-your-key-here
# AWS_S3_BUCKET=your-screenshot-bucket (optional but recommended)
# AWS_S3_REGION=us-east-1
# AWS_S3_ACCESS_KEY_ID=...
# AWS_S3_SECRET_ACCESS_KEY=...
# AWS_S3_BASE_URL=https://cdn.yourdomain.com  # optional CDN/front door URL
# SENDGRID_API_KEY=...
# EMAIL_DEFAULT_FROM="Funnel Analyzer Pro <reports@funnelanalyzerpro.com>"
# EMAIL_DEFAULT_REPLY_TO=support@funnelanalyzerpro.com
```

**Note:** The app works without an OpenAI key using intelligent placeholder analysis!

## Step 3: Start Backend Server

```bash
# From project root with venv activated
uvicorn backend.main:app --host 0.0.0.0 --port 3000

# Or run in background:
# nohup uvicorn backend.main:app --host 0.0.0.0 --port 3000 > backend.log 2>&1 &
```

Backend runs on: **http://localhost:3000**  
API docs: **http://localhost:3000/docs**

## Step 4: Start Frontend (New Terminal)

```bash
# Open new terminal, navigate to project
cd funnel-analyzer/frontend

# Install dependencies (first time only)
npm install

# Start development server
npm run dev
```

Frontend runs on: **http://localhost:3001**

## Step 5: Test the Application

1. Open browser: **http://localhost:3001**
2. Click **"Get Started"**
3. Enter funnel URLs (try `https://example.com`)
4. Click **"Analyze Funnel"**
5. View AI-generated analysis results!

## ✅ What's Working

- ✅ Real web scraping (extracts content from URLs)
- ✅ OpenAI GPT-4o analysis (when API key configured)
- ✅ Database persistence (SQLite auto-created)
- ✅ Complete frontend UI with results display
- ✅ Analysis history and report retrieval

## 🔧 Troubleshooting

**Backend won't start:**
```bash
# Check Python version
python3 --version  # Should be 3.10+

# Reinstall dependencies
pip install -r backend/requirements.txt
```

**Frontend won't start:**
```bash
# Check Node version
node --version  # Should be 18+

# Clear cache and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**Database errors:**
```bash
# Delete existing database and restart
rm funnel_analyzer.db
# Restart backend - database will auto-recreate
```

**CORS errors:**
- Ensure backend is running on port 3000
- Ensure frontend is running on port 3001
- Check browser console for specific error

## 🚀 Production Deployment

### Backend → Railway

1. Push code to GitHub
2. Create Railway project: https://railway.app
3. Connect GitHub repo
4. Add environment variables:
   - `OPENAI_API_KEY`
   - `DATABASE_URL` (Railway will provide PostgreSQL)
   - `JWT_SECRET`
   - `FRONTEND_URL`

### Frontend → Vercel

1. Push code to GitHub
2. Import project in Vercel
3. Set `NEXT_PUBLIC_API_URL` to your Railway URL
4. Deploy!

## 📚 Next Steps

- Add your OpenAI API key for real AI analysis
- Customize scoring criteria in `backend/services/openai_service.py`
- Update frontend styling in `frontend/app/globals.css`
- Enable screenshot uploads to S3 for persistent visuals
- Plug in SendGrid to deliver magic links or report summaries
- Set up WordPress JWT integration

## 🆘 Getting Help

- Check API logs: `http://localhost:3000/docs`
- View database: SQLite browser on `funnel_analyzer.db`
- Frontend logs: Browser console (F12)
- Backend logs: Terminal output

---

**🎉 You're ready to analyze funnels!**
