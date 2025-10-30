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

### Future Premium Upgrade Ideas ✨
- [ ] **AI Rewrite Button**
  - Auto-generate headline variations
  - CTA copy suggestions
  - Real-time rewrite preview
  
- [ ] **Competitor Mode**
  - "Analyze competitor.com side-by-side"
  - Gap analysis
  - Benchmark against top performers
  
- [ ] **"Fix All Critical Issues" Simulation**
  - Run AI mock-edits
  - Annotated before/after screenshots
  - Visual preview of changes
  
- [ ] **Collaborator Mode (Team Plan)**
  - Assign recommendations to teammates
  - Comment threads
  - Task management
  - Progress tracking per team member
  
- [ ] **Advanced Integrations**
  - Direct edit mode (for supported platforms)
  - Auto-apply fixes to ClickFunnels
  - WordPress page builder integration
  - A/B testing tool connections

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
- Custom domain (api.funnelanalyzerpro.com)
- Database persistence
- Health monitoring
- **Recommendation completion tracking with checkboxes**
- **Screenshot thumbnails in recommendations**
- **Click-to-enlarge screenshot lightbox**
- **Enhanced LLM prompts for specific examples**
- **Headline alternatives (3-5 options per page)**

### 🚧 In Progress
- Screenshot functionality (ready to enable)
- Lead capture system (next sprint)
- **Interactive dashboard improvements (Phase 1.5)**

---

## Report Structure Template 🧱

### Consistent Pattern for User Clarity

| Section | Purpose | User Value |
|---------|---------|------------|
| **Header** | Scores, timestamps, ROI widget, action buttons | At-a-glance performance |
| **Executive Summary** | 3-point business recap (costs/fixed/next) | Quick comprehension |
| **Score Overview** | Visual charts + trends + deltas | Pattern recognition |
| **Page Analysis** | Details per funnel step | Specific fixes |
| **Action Plan** | Checklist with ROI, effort, examples | Implementation guide |
| **History / Comparison** | Trend over time, benchmarks | Retention & proof of value |

### Information Hierarchy
1. **Scannable** - ROI numbers, completion %, key scores
2. **Actionable** - Specific recommendations with examples
3. **Educational** - Why it matters, how to fix
4. **Inspirational** - Progress tracking, achievements

---

### 📋 Next Up
- Public landing page
- Teaser analysis mode
- Email integration
- **Interactive report dashboard improvements (see Phase 1.5 below)**

---

## PHASE 1.5: Interactive Report Dashboard 🎨
**Goal:** Transform reports from "static readout" → "interactive improvement dashboard"

### Priority 🔥: Quick Wins (1-2 weeks)

#### 1. ROI Context & Business Value
- [ ] **ROI Widget (Header)**
  - Display "Potential Gain: +$X/mo"
  - Show "Captured so far: $X/mo"
  - Highlight "Next 3 highest-impact fixes"
  - Calculate based on industry benchmarks + traffic

- [ ] **Revenue Context per Recommendation**
  - Add 💰 Estimated Impact: "+$420/mo"
  - Add ⏱ Effort estimate: "~30 minutes"
  - Add Priority labels: P1 (Critical) → P3 (Nice-to-have)
  - Sort by ROI/Effort ratio (default view)

- [ ] **3-Point Business Recap (Replace Executive Summary)**
  - "What's costing you the most"
  - "What you've fixed"
  - "What to do next"

#### 2. Enhanced Action Plan
- [ ] **"Example Fix" for Every Recommendation**
  - Concrete before/after examples
  - "Instead of 'Submit', use 'Get My Free Strategy Plan'"
  - Visual context with screenshot highlights

- [ ] **Clarify the Why**
  - What → Why → How format
  - Problem statement
  - Impact explanation
  - Step-by-step fix

- [ ] **Progress Metrics**
  - Progress bar per category (Copy 3/5, Design 2/7)
  - "Show only incomplete" filter
  - Overall completion percentage

- [ ] **Group by Type with Tabs**
  - Copy | Design | Trust | Flow
  - Team-oriented task division

- [ ] **Mark Complete Animation**
  - Subtle check animation
  - Confetti emoji celebration
  - Dopamine reward moment

#### 3. Visual Comprehension
- [ ] **Score Comparison Chart**
  - Radar or bar chart for 5 dimensions
  - Show previous report as faded background
  - Visual improvement tracking

- [ ] **Score Deltas**
  - "+12 vs last run" inline
  - Green (gains) / Red (drops) color coding
  - Trend arrows (↑↓)

- [ ] **Screenshot Annotations** ✅ (Partial - lightbox added)
  - Heatmap overlays on problem areas
  - Annotation pins with tooltips
  - "CTA lacks benefit statement" markers

### Priority ✅: Usability Improvements (2-3 weeks)

#### 4. Navigation & Information Architecture
- [ ] **Sticky Section Navigator**
  - Sidebar or top tabs
  - Summary | Page Breakdown | Action Plan | History
  - Completion % badges (✅ 60% complete)
  - Auto-highlight current section on scroll

- [ ] **Collapsible Sections**
  - Collapse/expand all major sections
  - Remember state in localStorage
  - "Expand All" / "Collapse All" buttons

- [ ] **Quick Jump Floating Menu**
  - Appears on scroll
  - "Go to: Summary | Page 1 | Page 2 | Action Plan"
  - Smooth scroll animations

- [ ] **Breadcrumb Context**
  - Show previous analyses dropdown
  - "Compare to Report #39"
  - Quick navigation between reports

#### 5. Filters & Sorting
- [ ] **Action Plan Filters**
  - By priority (P1, P2, P3)
  - By category (Copy, Design, Trust, Flow)
  - By completion status
  - By effort level

- [ ] **Smart Sorting Options**
  - 💰 High Impact → ⏱ Low Effort (default)
  - By category
  - By completion status
  - By date added

- [ ] **Search Functionality**
  - Search within recommendations
  - Filter by keyword
  - Highlight matches

### Priority ⚙️: Engagement & Retention (3-4 weeks)

#### 6. Comparative & Longitudinal Value
- [ ] **Report History View**
  - Line chart: each dimension over time
  - #37 → #38 → #39 → #40 progression
  - Download trend data (CSV)
  - Date range selector

- [ ] **Implementation Impact Chart**
  - Correlation between completed recs and score improvements
  - "After fixing X, score increased by Y"
  - Proof of value

- [ ] **Benchmark Comparison**
  - "Your Design Score (80) vs SaaS average (72)"
  - Industry-specific benchmarks
  - Anonymized aggregate data
  - Percentile ranking

#### 7. Engagement Hooks
- [ ] **Re-run CTA (Top + Bottom)**
  - "Re-run Analysis → See New Score"
  - "Last run 12 days ago" reminder
  - One-click re-analysis

- [ ] **Achievement Badges**
  - "100% Checklist Complete! 🎉"
  - "First Re-run Completed! 🔄"
  - "ROI Positive Funnel! 💰"
  - "Perfect Score (90+) 🌟"

- [ ] **Email Follow-up Triggers**
  - "You've implemented 3 fixes — let's see what changed"
  - Weekly progress summary
  - Re-engagement campaigns

#### 8. Sharing & Collaboration
- [ ] **Share with Team Button**
  - Generate public read-only link
  - Export PDF for Slack/Email
  - Password-protected sharing
  - Expiring links (7 days)

- [ ] **Team Comments (Premium)**
  - Comment threads per recommendation
  - @mention teammates
  - Task assignment
  - Status updates

- [ ] **Export Options**
  - PDF with branding
  - CSV data export
  - JSON API export
  - Print-optimized view

### Priority 💬: Language & Specificity (Ongoing)

#### 9. Content Enhancements
- [x] **Specific Examples in Recommendations** ✅ (Completed)
  - Headline alternatives (3-5 options)
  - Before/after copy examples
  - Exact CTA button text with styling

- [ ] **Visual Context Integration**
  - "See highlighted area on screenshot"
  - Inline screenshot crops
  - Side-by-side comparisons

- [ ] **Implementation Guides**
  - Platform-specific instructions
  - "How to implement in ClickFunnels"
  - "WordPress plugin setup"
  - Code snippets when applicable

---

## PHASE 1.5 Success Metrics

### User Engagement
- **Time on Report:** >5 minutes average
- **Checklist Completion:** 40% of users complete ≥1 item
- **Re-run Rate:** 30% within 14 days
- **Share Rate:** 15% generate share link

### Business Impact
- **ROI Perception:** 80% understand value proposition
- **Implementation Rate:** 50% attempt ≥1 recommendation
- **Retention Lift:** +20% monthly retention
- **Upgrade Intent:** 25% from improved reports

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
