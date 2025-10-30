# Feedback System Implementation - Future Sprint

## Overview
User feedback collection system to continuously improve AI analysis quality over time. This is a **future enhancement** - parking here for later implementation.

---

## Phase 1: Basic Feedback Collection (2-3 days)

### 1.1 Database Schema
```sql
-- Overall report feedback
CREATE TABLE report_feedback (
    id SERIAL PRIMARY KEY,
    analysis_id INTEGER REFERENCES analyses(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id),
    overall_rating INTEGER CHECK (overall_rating BETWEEN 1 AND 5),
    thumbs_up BOOLEAN,
    feedback_text TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Per-recommendation feedback
CREATE TABLE recommendation_feedback (
    id SERIAL PRIMARY KEY,
    analysis_id INTEGER REFERENCES analyses(id) ON DELETE CASCADE,
    recommendation_type VARCHAR(50), -- 'headline', 'cta', 'design', etc.
    recommendation_text TEXT,
    helpful BOOLEAN, -- thumbs up/down
    implemented BOOLEAN DEFAULT FALSE,
    implemented_date TIMESTAMP,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes
CREATE INDEX idx_report_feedback_analysis ON report_feedback(analysis_id);
CREATE INDEX idx_recommendation_feedback_analysis ON recommendation_feedback(analysis_id);
CREATE INDEX idx_report_feedback_rating ON report_feedback(overall_rating);
```

### 1.2 Backend API Endpoints
```python
# backend/routers/feedback.py

@router.post("/analyses/{analysis_id}/feedback")
async def submit_report_feedback(
    analysis_id: int,
    rating: int,
    thumbs_up: bool,
    feedback_text: Optional[str] = None,
    user_id: int = Depends(get_current_user)
):
    """Submit overall report feedback."""
    pass

@router.post("/analyses/{analysis_id}/recommendations/{type}/feedback")
async def submit_recommendation_feedback(
    analysis_id: int,
    type: str,
    helpful: bool,
    implemented: bool = False,
    notes: Optional[str] = None
):
    """Submit feedback on specific recommendation."""
    pass

@router.get("/admin/feedback/summary")
async def get_feedback_summary():
    """Admin dashboard - feedback analytics."""
    return {
        "avg_rating": 4.2,
        "total_feedback": 156,
        "thumbs_up_percent": 78,
        "most_helpful_recommendations": [...],
        "common_complaints": [...]
    }
```

### 1.3 Frontend Components
```tsx
// frontend/components/ReportFeedback.tsx
export function ReportFeedback({ analysisId }: { analysisId: number }) {
  return (
    <div className="border-t pt-6 mt-8">
      <h3 className="text-lg font-semibold mb-4">How was this report?</h3>
      
      {/* Star rating */}
      <div className="flex gap-2 mb-4">
        {[1,2,3,4,5].map(star => (
          <StarIcon key={star} onClick={() => setRating(star)} />
        ))}
      </div>
      
      {/* Thumbs up/down */}
      <div className="flex gap-4 mb-4">
        <button>👍 Helpful</button>
        <button>👎 Not Helpful</button>
      </div>
      
      {/* Optional comment */}
      <textarea 
        placeholder="Any specific feedback? (optional)"
        className="w-full p-3 border rounded"
      />
      
      <button>Submit Feedback</button>
    </div>
  );
}

// frontend/components/RecommendationFeedback.tsx
export function RecommendationFeedback({ 
  recommendation, 
  analysisId 
}: Props) {
  return (
    <div className="flex items-center gap-3 mt-2">
      <button 
        onClick={() => markAsHelpful(true)}
        className="text-sm text-gray-600 hover:text-green-600"
      >
        👍 Helpful
      </button>
      
      <button 
        onClick={() => markAsHelpful(false)}
        className="text-sm text-gray-600 hover:text-red-600"
      >
        👎 Not Helpful
      </button>
      
      <label className="flex items-center gap-2 text-sm">
        <input 
          type="checkbox" 
          onChange={(e) => markAsImplemented(e.target.checked)}
        />
        I implemented this
      </label>
    </div>
  );
}
```

---

## Phase 2: Analytics & Insights (1-2 days)

### 2.1 Admin Dashboard
```tsx
// frontend/app/admin/feedback/page.tsx
export default function FeedbackDashboard() {
  return (
    <div>
      <h1>Feedback Analytics</h1>
      
      {/* Key metrics */}
      <div className="grid grid-cols-4 gap-4">
        <MetricCard title="Avg Rating" value="4.2/5" />
        <MetricCard title="Response Rate" value="68%" />
        <MetricCard title="Implementation Rate" value="23%" />
        <MetricCard title="Satisfaction Trend" value="+12%" />
      </div>
      
      {/* Charts */}
      <div className="mt-8">
        <h2>Rating Distribution</h2>
        <BarChart data={ratingDistribution} />
      </div>
      
      <div className="mt-8">
        <h2>Most Helpful Recommendation Types</h2>
        <Table data={recommendationStats} />
      </div>
      
      <div className="mt-8">
        <h2>Recent Feedback Comments</h2>
        <FeedbackList items={recentFeedback} />
      </div>
    </div>
  );
}
```

### 2.2 Quality Metrics Tracking
```python
# backend/services/quality_metrics.py

def calculate_quality_metrics(analysis: Dict) -> Dict:
    """Post-analysis quality checks."""
    
    metrics = {
        # Specificity: Are recommendations concrete?
        "specificity_score": check_specificity(analysis),
        
        # Consistency: Do scores match feedback?
        "consistency_score": check_score_alignment(analysis),
        
        # Completeness: All sections filled?
        "completeness_score": check_completeness(analysis),
        
        # Hallucination: Mentions non-existent elements?
        "hallucination_count": detect_hallucinations(analysis),
        
        # Actionability: Clear next steps?
        "actionability_score": check_actionability(analysis)
    }
    
    # Flag low-quality reports
    if metrics["specificity_score"] < 0.6:
        flag_for_manual_review(analysis.id, "Low specificity")
    
    return metrics

def check_specificity(analysis: Dict) -> float:
    """Check if recommendations are specific vs generic."""
    
    generic_phrases = [
        "improve the",
        "make it better",
        "optimize this",
        "consider changing",
        "you should"
    ]
    
    recommendations = get_all_recommendations(analysis)
    generic_count = 0
    
    for rec in recommendations:
        if any(phrase in rec.lower() for phrase in generic_phrases):
            generic_count += 1
    
    return 1 - (generic_count / len(recommendations))
```

---

## Phase 3: AI Learning Loop (Ongoing)

### 3.1 Prompt Versioning
```python
# backend/services/prompt_versions.py

PROMPT_VERSIONS = {
    "v1.0.0": {
        "date": "2025-10-01",
        "description": "Original prompt",
        "file": "prompts/v1.0.0.txt"
    },
    "v1.1.0": {
        "date": "2025-10-15",
        "description": "Improved specificity based on feedback",
        "file": "prompts/v1.1.0.txt",
        "changes": [
            "Added requirement for specific numbers in recommendations",
            "Included few-shot examples of good vs bad recommendations"
        ]
    },
    "v1.2.0": {
        "date": "2025-10-30",
        "description": "Context-aware single vs multi-page",
        "file": "prompts/v1.2.0.txt"
    }
}

CURRENT_VERSION = "v1.2.0"

# Track version used for each analysis
analysis.prompt_version = CURRENT_VERSION
```

### 3.2 A/B Testing Framework
```python
# backend/services/ab_testing.py

async def get_prompt_for_analysis(analysis_id: int) -> str:
    """A/B test different prompts."""
    
    # 50/50 split between versions
    variant = "A" if analysis_id % 2 == 0 else "B"
    
    prompts = {
        "A": load_prompt("v1.2.0"),
        "B": load_prompt("v1.3.0-beta")  # Testing new version
    }
    
    # Track which variant was used
    await db.execute(
        "UPDATE analyses SET ab_variant = $1 WHERE id = $2",
        variant, analysis_id
    )
    
    return prompts[variant]

async def analyze_ab_results():
    """Compare feedback between variants."""
    
    results = await db.fetch("""
        SELECT 
            ab_variant,
            AVG(overall_rating) as avg_rating,
            AVG(CASE WHEN thumbs_up THEN 1 ELSE 0 END) as thumbs_up_rate
        FROM analyses a
        JOIN report_feedback f ON a.id = f.analysis_id
        WHERE ab_variant IS NOT NULL
        GROUP BY ab_variant
    """)
    
    # Determine winner
    if results["A"]["avg_rating"] > results["B"]["avg_rating"]:
        promote_to_production("v1.2.0")
    else:
        promote_to_production("v1.3.0-beta")
```

### 3.3 Few-Shot Learning
```python
# backend/prompts/few_shot_examples.py

EXCELLENT_EXAMPLES = {
    "headline": {
        "good": """
        CHANGE: Replace "Welcome to Our Service" with "Cut Your Email List Churn by 40% in 60 Days"
        WHY: Current headline is generic and doesn't communicate value. New headline is specific, includes a metric (40%), and a timeframe (60 days).
        IMPACT: Expected 15-20% increase in engagement based on headline specificity studies.
        """,
        "bad": """
        The headline could be better. Consider making it more compelling and specific to your audience.
        """
    },
    "cta": {
        "good": """
        CHANGE: Replace "Submit" button with "Start My Free 14-Day Trial"
        LOCATION: Above the fold, centered in hero section
        DESIGN: Increase button size by 30%, use contrasting orange color (#FF6B35)
        WHY: "Submit" is generic and creates friction. New copy removes risk with "free" and creates urgency with trial period.
        IMPACT: Expected 25-35% increase in click-through rate.
        """,
        "bad": """
        Your CTA button could be improved. Make it more action-oriented.
        """
    }
}

# Inject into prompt
def build_prompt_with_examples(page_type: str) -> str:
    prompt = base_prompt
    
    if page_type in EXCELLENT_EXAMPLES:
        prompt += f"""
        
EXAMPLE OF EXCELLENT ANALYSIS:
{EXCELLENT_EXAMPLES[page_type]}

Your recommendations should be this specific and actionable.
        """
    
    return prompt
```

---

## Phase 4: Advanced Features (Future)

### 4.1 Fine-Tuning Dataset
- Collect 10,000+ high-quality analyses
- Manual review and curation
- Create training dataset
- Fine-tune gpt-4o-mini for speed/cost

### 4.2 Outcome Tracking
- Google Analytics integration
- Track conversion rate before/after
- Correlate recommendations with actual business results
- Build case studies from successful implementations

### 4.3 Self-Healing Prompts
- Automated quality monitoring
- AI suggests prompt improvements when metrics drop
- Weekly feedback analysis reports
- Continuous improvement loops

---

## Implementation Priority

**Must Have (Phase 1):**
- [ ] Database tables for feedback
- [ ] Basic feedback UI (thumbs up/down)
- [ ] Star rating system
- [ ] Backend endpoints

**Should Have (Phase 2):**
- [ ] Admin analytics dashboard
- [ ] Quality metrics tracking
- [ ] Prompt versioning
- [ ] A/B testing framework

**Nice to Have (Phase 3+):**
- [ ] Few-shot learning examples
- [ ] Outcome tracking
- [ ] Fine-tuning custom models
- [ ] Self-healing prompts

---

## Success Metrics

- **Response Rate**: 50%+ of users submit feedback
- **Average Rating**: 4.0+ stars
- **Implementation Rate**: 20%+ of recommendations implemented
- **Specificity Score**: 0.8+ (80% of recommendations are specific)
- **Hallucination Rate**: <5% of analyses mention non-existent elements

---

## Notes for Future Implementation

1. **Start Simple**: Just thumbs up/down is enough to start learning
2. **Make It Easy**: One-click feedback, no required fields
3. **Close the Loop**: Show users how their feedback improved the AI
4. **Privacy**: Let users opt-in to sharing their funnels as examples
5. **Incentives**: Offer credits/discounts for detailed feedback

This system will compound over time - the more feedback collected, the better the AI becomes, creating a virtuous cycle of improvement.
