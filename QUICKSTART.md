# Quick Start Guide - Running Locally in VS Code

## Terminal Setup

You'll need **two terminals** running simultaneously:

### Terminal 1: Backend (Python/FastAPI)

```bash
# Navigate to backend
cd backend

# Create virtual environment (first time only)
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate  # Windows

# Install dependencies (first time only)
pip install -r requirements.txt

# Run the server
python main.py
```

**Backend will run on:** `http://localhost:3000`  
**API docs available at:** `http://localhost:3000/docs`

### Terminal 2: Frontend (Next.js)

```bash
# Navigate to frontend
cd frontend

# Install dependencies (first time only)
npm install

# Run the dev server
npm run dev
```

**Frontend will run on:** `http://localhost:3001`

## Environment Variables

Create `.env` in the project root:

```bash
cp .env.example .env
```

Minimum required variables for local development:

```bash
# Backend
OPENAI_API_KEY=sk-test  # Can be dummy for mock mode
DATABASE_URL=postgresql://user:pass@localhost:5432/funnel_analyzer
JWT_SECRET=your-secret-key-here

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:3000
```

## VS Code Tips

1. **Open integrated terminals:** `` Ctrl+` `` (backtick)
2. **Split terminal:** Click the split icon or use Command Palette
3. **Recommended Extensions:**
   - Python
   - Pylance
   - ES7+ React/Redux/React-Native snippets
   - Tailwind CSS IntelliSense

## Testing the App

1. Open browser to `http://localhost:3001`
2. Navigate to `/dashboard`
3. Enter test URLs:
   - `https://example.com/sales`
   - `https://example.com/checkout`
4. Click "Analyze Funnel"
5. See mock results appear!

## Troubleshooting

### Backend Issues

**Port already in use:**
```bash
# Find and kill process on port 3000
lsof -ti:3000 | xargs kill -9
```

**Module not found:**
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

### Frontend Issues

**Next.js build errors:**
```bash
# Clear Next.js cache
rm -rf .next
npm install
npm run dev
```

**TypeScript errors:**
These are expected until `npm install` completes. The packages define the types.

## Development Workflow

1. Make changes to backend Python files → auto-reloads
2. Make changes to frontend React/TS files → auto-reloads
3. API changes? Check Swagger docs at `/docs`
4. UI changes? Hot reload in browser
5. Test with different URLs and see mock responses

## Next Steps

- Implement real OpenAI analysis in `backend/services/analyzer.py`
- Add database connection in `backend/models/database.py`
- Style components in `frontend/components/`
- Deploy to Railway (backend) + Vercel (frontend)
