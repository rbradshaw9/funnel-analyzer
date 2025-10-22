# Funnel Analyzer

A two-part application for experimenting with conversion funnel analytics. The backend exposes the ingestion, storage, and embedding generation APIs while the frontend provides a dashboard for exploring funnels. This repository now includes deployment-ready configuration for Railway (backend) and Vercel (frontend).

## Project structure

```
.
├── backend/              # Backend application source & Dockerfile
├── frontend/             # Frontend application source & Vercel configuration
├── .github/workflows/    # Continuous integration and deployment workflow
├── .env.example          # Example environment configuration for local use
├── railway.json          # Railway service definition for the backend
└── README.md
```

## Prerequisites

- Node.js 18.x (LTS) and npm
- Docker (for container builds and local parity with Railway)
- Optional CLIs for manual deployments:
  - [Railway CLI](https://docs.railway.app/develop/cli)
  - [Vercel CLI](https://vercel.com/docs/cli)

## Environment setup

1. Copy `.env.example` to `.env` and fill in the values:
   ```bash
   cp .env.example .env
   ```
2. Ensure the following secrets are available:
   - `OPENAI_API_KEY` – required for generating embeddings.
   - `DATABASE_URL` – connection string for the primary application database.
   - `JWT_SECRET` – used to sign and verify access tokens.
   - `VERCEL_TOKEN` – used by CI to authenticate with Vercel.
   - `RAILWAY_TOKEN` – used by CI to authenticate with Railway.
3. When running locally, export the variables into your shell or use a tool such as [`direnv`](https://direnv.net/) or [`dotenv`](https://github.com/motdotla/dotenv).

## Local development

### Backend

```bash
cd backend
npm install
npm run dev
```

The backend defaults to port `3000`. Update `npm run dev` in the backend `package.json` when implementing the service to invoke your preferred framework (Express, Fastify, etc.).

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Configure the frontend to proxy API requests to the backend (e.g., via `NEXT_PUBLIC_API_URL`). The provided `frontend/vercel.json` exposes the same variables for preview and production deployments.

### Using Docker for the backend

The `backend/Dockerfile` mirrors the environment used on Railway. To run locally:

```bash
docker build -t funnel-analyzer-backend ./backend
docker run --rm -p 3000:3000 --env-file .env funnel-analyzer-backend
```

## Testing and linting

Each project should define `lint` and `test` scripts within its respective `package.json`. GitHub Actions will invoke these commands automatically, but you can run them locally:

```bash
npm run lint
npm run test
```

## Continuous integration & deployment

The workflow defined in `.github/workflows/deploy.yml` executes on pushes to the `main` branch and can be triggered manually. It performs the following steps:

1. Installs dependencies for both the backend and frontend, then runs their `lint` and `test` scripts (when present).
2. Deploys the backend to Railway using the provided `RAILWAY_TOKEN` secret.
3. Deploys the frontend to Vercel using the provided `VERCEL_TOKEN`, `VERCEL_ORG_ID`, and `VERCEL_PROJECT_ID` secrets.

Ensure the corresponding GitHub repository secrets are configured before enabling automated deployments. The workflow conditionally skips the deployment steps if the required tokens are absent.

### Manual deployments

You can also deploy manually from your workstation:

```bash
# Backend
railway login --token $RAILWAY_TOKEN
railway up --service funnel-analyzer-backend

# Frontend
cd frontend
vercel pull --environment=production --yes
vercel deploy --prod --yes
```

## Embedding workflow

To generate embeddings for funnel events or other textual data:

1. Ensure `OPENAI_API_KEY` is set in your environment.
2. Choose an embedding model (e.g., `text-embedding-3-small`).
3. Call the OpenAI Embeddings API from the backend when ingesting new data. A minimal Node.js example:
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
4. Store embeddings alongside funnel entities in your database (e.g., PostgreSQL with the `vector` extension, Pinecone, or another vector store).
5. Use similarity search to surface related events, marketing assets, or user sessions within the frontend dashboard.

## Deployment configuration references

- `backend/Dockerfile` – Production Docker build used by Railway.
- `railway.json` – Railway configuration with environment variable bindings and start command.
- `frontend/vercel.json` – Vercel configuration including build commands and required environment variables.

These files should be updated in tandem with any changes to the build or runtime requirements of the respective applications.
