# Funnel Analyzer - Product Roadmap

## Vision
Transform from internal tool → Lead generation freemium SaaS → Premium member feature

---

## PHASE 1: Lead Generation Tool (4-6 weeks) 🎯

### Week 1-2: Free Teaser Analysis
**Goal:** Capture leads with valuable free tool

- [ ] Public landing page (`/free-analysis`)
  - Single URL input
  - No authentication required
  - Marketing copy emphasizing value
  
- [ ] Teaser Analysis Mode
  - Show overall score (full visibility)
  - Show 5 metric scores (full visibility)
  - Blur/hide detailed feedback text
  - Blur/hide page-by-page breakdown
  - Show screenshot (builds trust)
  
- [ ] Lead Capture Modal
  - Trigger: "Unlock Full Report" button
  - Email capture form
  - Privacy policy link
  - "Join Smart Tool Club" CTA
  
- [ ] Email Integration
  - Send full report to email
  - Follow-up sequence (3 emails)
  - Drip campaign to membership

### Week 3: Screenshot Implementation
- [ ] Enable Playwright in Dockerfile
- [ ] Screenshot capture service
- [ ] Image optimization & storage
- [ ] Display in teaser mode

### Week 4: Landing Page Optimization
- [ ] SEO optimization
- [ ] Social proof elements
- [ ] Trust badges
- [ ] Testimonials section
- [ ] Live demo video

---

## PHASE 2: Member Dashboard (6-8 weeks)

### Authentication & Access Control
- [ ] Magic-link login with SendGrid
- [ ] Subscription status sync (ThriveCart webhooks + grace periods)
- [ ] Customer portal messaging for past-due/canceled accounts
- [ ] WordPress JWT integration (wishlist)
- [ ] Session management
- [ ] Member vs non-member routing
- [ ] Rate limiting (free vs paid)

### Full Analysis Features
- [ ] Multi-page funnel analysis
- [ ] Complete feedback visibility
- [ ] Analysis history dashboard
- [ ] Saved reports library
- [ ] Export to PDF

### Advanced Analytics
- [ ] Competitor comparison tool
- [ ] Historical trend tracking
- [ ] Custom scoring weights
- [ ] White-label reports

---

## PHASE 3: Scale & Monetization (Ongoing)

### Tiered Access Model
- **Free Tier:**
  - 1 analysis per day
  - Teaser mode only
  - Email delivery
  
- **Smart Tool Club Member:**
  - Unlimited analyses
  - Full reports
  - Multi-page funnels
  - PDF export
  - Analysis history
  
- **Premium/Agency:**
  - Team collaboration
  - API access
  - White-label reports
  - Priority support
  - Custom training

### Growth Features
- [ ] Affiliate program
- [ ] Public report gallery (social proof)
- [ ] Integration marketplace
  - ClickFunnels
  - Kajabi
  - WordPress plugins
- [ ] Chrome extension (quick analysis)

### Technical Optimization
- [ ] Caching layer (Redis)
- [ ] Queue system for analysis jobs
- [ ] CDN for screenshots
- [ ] Advanced error tracking
- [ ] Performance monitoring

---

## Success Metrics

### Phase 1 KPIs
- **Lead Generation:** 100 emails/month
- **Conversion Rate:** 15% teaser → email capture
- **Member Conversion:** 5% email → membership
- **Page Speed:** <2s load time
- **Analysis Time:** <10s average

### Phase 2 KPIs
- **Member Engagement:** 50% monthly active
- **Analyses/Member:** 10/month average
- **Retention:** 80% monthly retention
- **NPS Score:** >50

### Phase 3 KPIs
- **Revenue:** $10k MRR
- **API Usage:** 1000 calls/day
- **Team Accounts:** 20+ organizations

---

## Current Status

### ✅ Completed
- Backend API (FastAPI + PostgreSQL)
- Frontend dashboard (Next.js)
- OpenAI GPT-4o integration
- Web scraping (BeautifulSoup)
- Production deployment (Railway + Vercel)
- Custom domain (api.smarttoolclub.com)
- Database persistence
- Health monitoring

### 🚧 In Progress
- Screenshot functionality (ready to enable)
- Lead capture system (next sprint)

### 📋 Next Up
- Public landing page
- Teaser analysis mode
- Email integration

---

## Technical Architecture

### Current Stack
- **Backend:** FastAPI (Python 3.11), Railway
- **Frontend:** Next.js 14, Vercel
- **Database:** PostgreSQL (Railway)
- **AI:** OpenAI GPT-4o
- **Scraping:** BeautifulSoup + lxml
- **Screenshots:** Playwright (disabled, ready to enable)

### Phase 1 Additions
- **Email:** SendGrid or Resend
- **Analytics:** Plausible or PostHog
- **Forms:** React Hook Form + Zod

### Phase 2 Additions
- **Auth:** WordPress REST API + JWT
- **PDF:** jsPDF + Puppeteer
- **Storage:** AWS S3 or Cloudinary

### Phase 3 Additions
- **Cache:** Redis (Upstash)
- **Queue:** BullMQ or Celery
- **Monitoring:** Sentry + LogRocket
