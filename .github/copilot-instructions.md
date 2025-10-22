# Copilot Instructions for Funnel Analyzer

## Project Architecture

This is a two-part funnel analytics application with a **Node.js backend** (Railway) and **Next.js frontend** (Vercel). The backend handles data ingestion, storage, and OpenAI embedding generation while the frontend provides analytics dashboards.

### Key Components
- **Backend**: API service for funnel data ingestion and analysis (port 3000)
- **Frontend**: Next.js dashboard with static export (`out` directory)
- **Database**: PostgreSQL with vector extension for embeddings
- **AI Integration**: OpenAI Embeddings API for semantic analysis

## Development Workflow

### Environment Setup
```bash
# Always start here - copy and configure environment
cp .env.example .env
# Fill in: OPENAI_API_KEY, DATABASE_URL, JWT_SECRET
```

### Local Development Commands
```bash
# Backend development
cd backend && npm run dev

# Frontend development  
cd frontend && npm run dev

# Docker backend (matches Railway environment)
docker build -t funnel-analyzer-backend ./backend
docker run --rm -p 3000:3000 --env-file .env funnel-analyzer-backend
```

### Testing & Deployment
- CI runs `npm run lint` and `npm run test` in both directories
- Pushes to `main` trigger automatic deployment
- Backend deploys to Railway using Docker build
- Frontend deploys to Vercel with static export

## Critical Patterns

### Environment Variables
All three services (backend, frontend, CI) need these variables:
- `OPENAI_API_KEY`: Required for embedding generation
- `DATABASE_URL`: PostgreSQL connection with vector support
- `JWT_SECRET`: Authentication token signing

### Embedding Workflow
When implementing data ingestion, use this pattern:
```ts
import OpenAI from "openai";
const client = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

export async function embedEventDescription(description: string) {
  const response = await client.embeddings.create({
    input: description,
    model: "text-embedding-3-small"
  });
  return response.data[0]?.embedding ?? [];
}
```

### Deployment Configuration
- **Backend**: Update `backend/Dockerfile` and `railway.json` together
- **Frontend**: Sync `frontend/vercel.json` with build requirements
- **CI Secrets**: Requires `RAILWAY_TOKEN`, `VERCEL_TOKEN`, `VERCEL_ORG_ID`, `VERCEL_PROJECT_ID`

## File Structure Conventions

```
backend/           # Express/Fastify API service
├── package.json   # Must include "start" script for Railway
└── Dockerfile     # Production build (Node 18 Alpine)

frontend/          # Next.js application
├── package.json   # Must include "build" script
└── vercel.json    # Static export configuration
```

## Development Guidelines

- Use Node.js 18.x LTS consistently across all environments
- Backend framework choice is flexible (Express, Fastify, etc.)
- Frontend requires API proxy configuration via `NEXT_PUBLIC_API_URL`
- Store embeddings alongside funnel entities in PostgreSQL
- Implement similarity search for related events/sessions
- Vector database support is essential for embedding functionality

## Integration Points

- **Frontend ↔ Backend**: Configure API proxy for local development
- **Backend ↔ Database**: Use connection pooling for PostgreSQL
- **Backend ↔ OpenAI**: Implement rate limiting and error handling
- **CI ↔ Deployments**: Conditional deployment based on secret availability