# Funnel Analyzer - Development To-Do List

## 🎯 GOAL
Transform the report from "a static readout" → "an interactive improvement dashboard."

---

## 🔥 SPRINT 1: Quick Wins (1-2 weeks)
**Focus:** Immediate value & ROI visibility

### ROI Context & Business Value
- [ ] **Create ROI Calculator Service** (backend)
  - Industry benchmarks database
  - Traffic estimation logic
  - Conversion rate improvement formulas
  - Monthly revenue impact calculator
  
- [ ] **ROI Widget Component** (frontend)
  - Header position (top-right)
  - "Potential Gain: +$X/mo" display
  - "Captured so far: $X/mo" tracking
  - "Next 3 highest-impact fixes" list
  - Responsive design
  
- [ ] **Add Revenue Context to Recommendations**
  - Update `PageAnalysis` schema with `estimated_impact_monthly`
  - Update OpenAI prompt to estimate financial impact
  - Add effort estimation (minutes/hours)
  - Add P1/P2/P3 priority classification
  - Frontend display of 💰 and ⏱ icons

- [ ] **Transform Executive Summary**
  - Replace generic summary with 3-point format:
    1. "What's costing you the most"
    2. "What you've fixed"
    3. "What to do next"
  - Add financial context to each point
  - Link to specific recommendations

### Enhanced Action Plan
- [x] ~~Add "Example Fix" for every recommendation~~ ✅ (Completed - headline_alternatives added)
  
- [ ] **Enhance "Example Fix" Further**
  - Add before/after for CTAs
  - Add before/after for copy sections
  - Add visual examples for design changes
  
- [ ] **Implement What → Why → How Format**
  - Update recommendation cards structure
  - Add collapsible "Why this matters" section
  - Add step-by-step "How to fix" guide
  - ⚙️ _In progress (Oct 30 2025): redesigning actionable card layout and acceptance criteria_
  
- [ ] **Progress Metrics per Category**
  - Track completion by type (Copy, Design, Trust, Flow)
  - Add progress bars to each category
  - Calculate % complete per category
  
- [ ] **Category Tabs/Grouping**
  - Reorganize Action Plan with tabs
  - Copy | Design | Trust | Flow | Other
  - Persist selected tab in localStorage
  
- [ ] **Completion Animation Enhancement**
  - Add confetti library (canvas-confetti)
  - Trigger on checkbox click
  - Subtle check animation (Framer Motion)
  - Sound effect option (optional toggle)

- [ ] **Sort by ROI/Effort Ratio**
  - Calculate impact/effort score
  - Default sort: highest ROI, lowest effort first
  - Add sort dropdown (Impact, Effort, Category, Status)

### Visual Comprehension
- [ ] **Score Comparison Chart Component**
  - Install chart library (recharts or chart.js)
  - Create radar chart for 5 dimensions
  - Fetch previous report data
  - Overlay current vs previous
  - Add to Score Overview section
  
- [ ] **Score Delta Display**
  - Calculate deltas vs previous report
  - "+12 vs last run" inline badges
  - Color coding (green/red)
  - Trend arrows (↑↓→)
  
- [x] ~~Screenshot lightbox~~ ✅ (Completed)
  
- [ ] **Screenshot Annotation System**
  - Canvas overlay on screenshots
  - Heatmap problem areas
  - Clickable annotation pins
  - Tooltip with issue description
  - Integration with recommendations
  - ⚙️ _In progress (Oct 30 2025): adding category-based overlays and CTA highlight helper_

---

## ✅ SPRINT 2: Usability & Navigation (2-3 weeks)
**Focus:** Make reports easy to navigate and digest

### Navigation & Information Architecture
- [ ] **Sticky Section Navigator**
  - Create sidebar component
  - Summary | Pages | Action Plan | History sections
  - Auto-highlight current section on scroll
  - Completion % badges per section
  - Collapse/expand on mobile
  
- [ ] **Collapsible Section Controls**
  - Add expand/collapse to all major sections
  - "Expand All" / "Collapse All" buttons
  - Save state to localStorage
  - Smooth animations (Framer Motion)
  
- [ ] **Floating Quick Jump Menu**
  - Appears after scrolling 300px
  - Anchors to major sections
  - Smooth scroll behavior
  - Hide on scroll up
  - Accessible (keyboard navigation)
  
- [ ] **Breadcrumb & Report Selector**
  - Show current report in breadcrumb
  - Dropdown of previous reports
  - Quick navigation between reports
  - "Compare to Report #39" option

### Filters & Search
- [ ] **Action Plan Filter System**
  - Filter by priority (P1, P2, P3)
  - Filter by category
  - Filter by completion status
  - Filter by effort level
  - Multiple filters (AND logic)
  
- [ ] **Smart Sorting Options**
  - Dropdown: Impact, Effort, Category, Status, Date
  - Default: Impact/Effort ratio
  - Persist sort preference
  - Visual indicator of current sort
  
- [ ] **Search Functionality**
  - Search input in Action Plan header
  - Search within recommendation text
  - Highlight matching terms
  - Clear search button
  - Show result count

---

## ⚙️ SPRINT 3: Engagement & Retention (3-4 weeks)
**Focus:** Long-term value and user retention

### Comparative & Longitudinal Features
- [ ] **Report History View**
  - New `/reports/history` route
  - Line chart component (recharts)
  - Each dimension over time
  - Date range selector
  - Download CSV export
  
- [ ] **Implementation Impact Chart**
  - Track recommendations completed per report
  - Correlate with score changes
  - "After fixing X, score increased by Y"
  - Visual proof of value
  
- [ ] **Benchmark Comparison System**
  - Industry benchmarks database (backend)
  - Aggregate anonymized user data
  - "Your score vs industry average"
  - Percentile ranking
  - Industry selector dropdown

### Engagement Hooks
- [ ] **Re-run CTA Implementation**
  - Add to report header
  - Add to report footer
  - "Last run X days ago" display
  - One-click re-analysis button
  - Show estimated time
  
- [ ] **Achievement Badge System**
  - Badge database schema
  - Achievement unlock logic
  - Badge display component
  - Badges:
    - "100% Checklist Complete! 🎉"
    - "First Re-run Completed! 🔄"
    - "ROI Positive Funnel! 💰"
    - "Perfect Score (90+) 🌟"
    - "5 Reports Analyzed 📊"
    - "Quick Learner (Fixed in <7 days) ⚡"
  
- [ ] **Email Follow-up Triggers**
  - Database triggers for events
  - Email templates
  - SendGrid/Resend integration
  - Campaigns:
    - "You've implemented 3 fixes - re-run now"
    - Weekly progress summary
    - "Report ready - view results"
    - Re-engagement (inactive 14 days)

### Sharing & Collaboration
- [ ] **Share Report Feature**
  - Generate public read-only link
  - Share modal component
  - Copy link button
  - Optional password protection
  - Expiring links (7 days default)
  
- [ ] **PDF Export**
  - PDF generation service (Puppeteer or jsPDF)
  - Branded template
  - Include all sections
  - Download button
  - Email delivery option
  
- [ ] **CSV Data Export**
  - Export recommendations as CSV
  - Export scores over time
  - Export implementation checklist
  - Bulk export option
  
- [ ] **Team Comments (Premium Feature)**
  - Comments database schema
  - Comment threads per recommendation
  - @mention system
  - Real-time updates (WebSocket)
  - Notification system
  
- [ ] **Task Assignment (Premium Feature)**
  - Assign recommendations to team members
  - Status tracking (To Do, In Progress, Done, Blocked)
  - Due dates
  - Team dashboard view

---

## 💬 SPRINT 4: Content & Polish (Ongoing)
**Focus:** Refinement and user experience

### Content Enhancements
- [x] ~~Specific examples in recommendations~~ ✅ (Completed)
  
- [ ] **Visual Context Integration**
  - Inline screenshot crops
  - Highlighted problem areas
  - Side-by-side comparisons
  - Before/after mockups
  
- [ ] **Platform-Specific Implementation Guides**
  - Detect platform from URL (ClickFunnels, Kajabi, etc.)
  - Platform-specific instructions
  - Code snippets with syntax highlighting
  - Video tutorial links
  - Integration guides

### UI/UX Polish
- [ ] **Loading States**
  - Skeleton screens for all sections
  - Progress indicators
  - Optimistic UI updates
  - Error boundaries
  
- [ ] **Animations & Transitions**
  - Page transitions
  - Section reveals
  - Chart animations
  - Micro-interactions
  
- [ ] **Accessibility Audit**
  - WCAG 2.1 AA compliance
  - Keyboard navigation
  - Screen reader support
  - Color contrast checks
  - Focus indicators
  
- [ ] **Mobile Optimization**
  - Responsive design review
  - Touch-friendly targets
  - Mobile navigation
  - Chart responsiveness
  
- [ ] **Dark Mode** (Optional)
  - Theme toggle
  - Dark mode styles
  - Persist preference
  - Chart color adjustments

---

## 🚀 Future Premium Features
**Phase 2+**

### AI-Powered Features
- [ ] **AI Rewrite Button**
  - Real-time headline generation
  - CTA copy suggestions
  - Preview before/after
  - A/B test variant generator
  
- [ ] **Competitor Analysis Mode**
  - Side-by-side comparison
  - Gap analysis
  - Benchmark against competitors
  - Industry leader comparison
  
- [ ] **"Fix All" Simulation**
  - AI-generated mockups
  - Annotated screenshots
  - Visual preview of changes
  - Export mockups

### Advanced Integrations
- [ ] **Direct Edit Mode**
  - ClickFunnels API integration
  - Kajabi integration
  - WordPress page builder plugins
  - One-click apply fixes
  
- [ ] **A/B Testing Tool Connections**
  - Google Optimize integration
  - VWO integration
  - Optimizely integration
  - Auto-create test variants

---

## 📊 Analytics & Tracking

### Implementation Tracking
- [ ] Add event tracking for:
  - Report views
  - Section expansions
  - Filter usage
  - Sort changes
  - Checkbox completions
  - Share link generation
  - Export downloads
  - Re-run clicks
  - Badge unlocks

### Performance Monitoring
- [ ] Core Web Vitals tracking
- [ ] API response time monitoring
- [ ] Error rate tracking
- [ ] User session recordings (optional)

---

## 🐛 Bug Fixes & Technical Debt

### Current Issues
- [x] ~~Backend API 500 errors for recommendations endpoint~~ ✅ (Fixed)
- [x] ~~Screenshot thumbnail showing "/" for homepage URLs~~ ✅ (Fixed)
- [x] ~~Screenshots not expanding on click~~ ✅ (Fixed)
- [ ] Check all TypeScript compile errors
- [ ] Fix any linting warnings
- [ ] Update dependencies
- [ ] Security audit

### Database
- [ ] Add indexes for performance
- [ ] Optimize queries
- [ ] Add database migrations system
- [ ] Backup strategy

### Testing
- [ ] Unit tests for critical functions
- [ ] Integration tests for API endpoints
- [ ] E2E tests for user flows
- [ ] Visual regression tests

---

## 📝 Documentation

### User Documentation
- [ ] Getting started guide
- [ ] Feature documentation
- [ ] FAQ section
- [ ] Video tutorials
- [ ] Troubleshooting guide

### Developer Documentation
- [ ] API documentation
- [ ] Architecture overview
- [ ] Deployment guide
- [ ] Contributing guide
- [ ] Code style guide

---

## Quick Reference: Priority Matrix

| Priority | Feature | Impact | Effort | Sprint |
|----------|---------|--------|--------|--------|
| 🔥🔥🔥 | ROI Widget | High | Medium | 1 |
| 🔥🔥🔥 | Revenue per recommendation | High | Low | 1 |
| 🔥🔥 | Score comparison chart | High | Medium | 1 |
| 🔥🔥 | Progress metrics | Medium | Low | 1 |
| 🔥🔥 | Sticky navigation | Medium | Medium | 2 |
| 🔥 | Collapsible sections | Medium | Low | 2 |
| 🔥 | Report history view | High | High | 3 |
| 🔥 | Achievement badges | Medium | Medium | 3 |
| ✅ | Team comments | Medium | High | 4 |
| ✅ | AI rewrite button | High | Very High | Phase 2 |

---

## Notes
- **Completed items** are marked with ✅
- **In progress** should be moved to the top of each sprint
- **Blocked items** should be documented with reason
- Review and update weekly
