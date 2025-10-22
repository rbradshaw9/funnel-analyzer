// Score explanation data with tooltips and detailed descriptions

export interface ScoreMetric {
  name: string;
  key: string;
  icon: string;
  color: string;
  description: string;
  goodExample: string;
  badExample: string;
  howToImprove: string[];
}

export const SCORE_METRICS: ScoreMetric[] = [
  {
    name: "Clarity",
    key: "clarity",
    icon: "💬",
    color: "blue",
    description: "How clearly your message communicates what you offer and who it's for. Visitors should immediately understand your value proposition.",
    goodExample: "\"AI-Powered Funnel Analysis in 60 Seconds - Used by 10,000+ Marketers\"",
    badExample: "\"Innovative Solutions for Modern Businesses\"",
    howToImprove: [
      "Use a specific, benefit-focused headline",
      "State who the product is for in the subheadline",
      "Remove jargon and buzzwords",
      "Lead with the transformation, not features",
      "Include a clear unique selling proposition (USP)"
    ]
  },
  {
    name: "Value",
    key: "value",
    icon: "💎",
    color: "purple",
    description: "How compelling your value proposition is and whether visitors understand what they'll gain. Strong value propositions focus on outcomes, not features.",
    goodExample: "\"Save 10 hours/week on funnel optimization\" with specific ROI metrics",
    badExample: "\"Advanced analytics dashboard with real-time data\"",
    howToImprove: [
      "Quantify the benefit (time saved, revenue gained, costs reduced)",
      "Show before/after transformations",
      "Use customer success stories with numbers",
      "Focus on emotional and practical benefits",
      "Address the visitor's pain points directly"
    ]
  },
  {
    name: "Proof",
    key: "proof",
    icon: "⭐",
    color: "yellow",
    description: "Social proof and credibility signals that build trust. This includes testimonials, case studies, logos, ratings, and trust badges.",
    goodExample: "Video testimonials with specific results + logos of 50+ well-known brands",
    badExample: "\"Trusted by thousands\" with no specifics or verification",
    howToImprove: [
      "Add customer testimonials with photos and specific results",
      "Display logos of recognizable clients/partners",
      "Show review ratings from verified platforms",
      "Include case studies with measurable outcomes",
      "Add trust badges (security, certifications, guarantees)",
      "Show real-time social proof (\"127 people signed up today\")"
    ]
  },
  {
    name: "Design",
    key: "design",
    icon: "🎨",
    color: "pink",
    description: "Visual hierarchy, professional aesthetics, mobile responsiveness, and how well the design guides visitors toward conversion.",
    goodExample: "Clear visual flow, strategic use of white space, mobile-optimized, fast loading",
    badExample: "Cluttered layout, poor color contrast, broken on mobile, slow loading",
    howToImprove: [
      "Use consistent branding (colors, fonts, spacing)",
      "Create clear visual hierarchy with size and contrast",
      "Optimize images for fast loading (<3 seconds)",
      "Ensure mobile responsiveness (60%+ mobile traffic)",
      "Use white space to reduce cognitive load",
      "Apply contrast for important elements (CTAs, headlines)"
    ]
  },
  {
    name: "Flow",
    key: "flow",
    icon: "🎯",
    color: "green",
    description: "How smoothly visitors move toward your desired action. Good flow removes friction, provides clear next steps, and maintains momentum.",
    goodExample: "Single clear CTA above fold, progressive disclosure, logical page sections",
    badExample: "Multiple competing CTAs, confusing navigation, unclear next steps",
    howToImprove: [
      "Use one primary CTA per section",
      "Place CTAs above the fold and at natural decision points",
      "Reduce form fields to essential only",
      "Create logical content progression (problem → solution → proof → CTA)",
      "Remove navigation distractions on critical pages",
      "Use directional cues (arrows, animations) to guide eyes"
    ]
  }
];

export const OVERALL_SCORE_RANGES = [
  {
    min: 90,
    max: 100,
    label: "Excellent",
    color: "green",
    icon: "🏆",
    description: "Your page is performing exceptionally well. Focus on testing minor variations to incrementally improve conversion rates.",
    nextSteps: ["Run A/B tests on headline variations", "Test different CTA button colors/text", "Optimize page speed further"]
  },
  {
    min: 70,
    max: 89,
    label: "Good",
    color: "blue",
    icon: "✅",
    description: "Solid foundation with room for optimization. Address the specific areas scoring below 80 to reach excellent performance.",
    nextSteps: ["Strengthen weakest scoring metric", "Add more social proof elements", "Simplify your primary CTA"]
  },
  {
    min: 50,
    max: 69,
    label: "Needs Improvement",
    color: "yellow",
    icon: "⚠️",
    description: "Your page has potential but needs significant optimization. Focus on the fundamentals: clarity, value proposition, and removing friction.",
    nextSteps: ["Rewrite headline to be more specific and benefit-focused", "Add customer testimonials with results", "Simplify the page design and reduce clutter"]
  },
  {
    min: 0,
    max: 49,
    label: "Critical Issues",
    color: "red",
    icon: "🚨",
    description: "Major improvements needed across multiple areas. Consider a comprehensive redesign focusing on core conversion principles.",
    nextSteps: ["Start with a clear value proposition", "Ensure mobile responsiveness", "Add trust signals immediately", "Simplify to one clear CTA"]
  }
];

export function getScoreRange(score: number) {
  return OVERALL_SCORE_RANGES.find(range => score >= range.min && score <= range.max) || OVERALL_SCORE_RANGES[3];
}

export function getScoreColor(score: number): string {
  if (score >= 70) return 'text-green-600';
  if (score >= 40) return 'text-yellow-600';
  return 'text-red-600';
}

export function getScoreBgColor(score: number): string {
  if (score >= 70) return 'bg-green-50 border-green-200';
  if (score >= 40) return 'bg-yellow-50 border-yellow-200';
  return 'bg-red-50 border-red-200';
}

export function getScoreGradient(score: number): string {
  if (score >= 70) return 'from-green-500 to-green-600';
  if (score >= 40) return 'from-yellow-500 to-yellow-600';
  return 'from-red-500 to-red-600';
}

// A/B Testing Recommendations Generator
export interface ABTestRecommendation {
  element: string;
  priority: "high" | "medium" | "low";
  hypothesis: string;
  controlVersion: string;
  testVersion: string;
  expectedImpact: string;
  implementationDifficulty: "easy" | "medium" | "hard";
}

export function generateABTestRecommendations(scores: Record<string, number>, pageContent: any): ABTestRecommendation[] {
  const recommendations: ABTestRecommendation[] = [];

  // Clarity-based tests
  if (scores.clarity < 70) {
    recommendations.push({
      element: "Headline",
      priority: "high",
      hypothesis: "A more specific, benefit-focused headline will improve visitor understanding and engagement",
      controlVersion: "Current headline",
      testVersion: "\"[Specific Outcome] in [Timeframe] - [Social Proof]\" format",
      expectedImpact: "15-25% increase in time on page and scroll depth",
      implementationDifficulty: "easy"
    });
  }

  // Value-based tests
  if (scores.value < 70) {
    recommendations.push({
      element: "Value Proposition",
      priority: "high",
      hypothesis: "Quantified benefits will make the value more tangible and compelling",
      controlVersion: "Current feature-focused description",
      testVersion: "\"Save X hours/week\" or \"Increase revenue by Y%\" with specific numbers",
      expectedImpact: "10-20% increase in conversion rate",
      implementationDifficulty: "medium"
    });
  }

  // Proof-based tests
  if (scores.proof < 60) {
    recommendations.push({
      element: "Social Proof",
      priority: "high",
      hypothesis: "Customer testimonials with specific results will increase trust and credibility",
      controlVersion: "No testimonials or generic testimonials",
      testVersion: "3-5 testimonials with photos, names, and specific outcomes (\"Increased sales by 47%\")",
      expectedImpact: "20-30% increase in conversion rate",
      implementationDifficulty: "medium"
    });
  }

  // Design-based tests
  if (scores.design < 70) {
    recommendations.push({
      element: "Visual Hierarchy",
      priority: "medium",
      hypothesis: "Improved visual hierarchy will guide visitors to the CTA more effectively",
      controlVersion: "Current layout",
      testVersion: "Hero section with larger headline, more white space, and contrasting CTA button",
      expectedImpact: "12-18% increase in CTA click-through rate",
      implementationDifficulty: "medium"
    });
  }

  // Flow-based tests
  if (scores.flow < 70) {
    recommendations.push({
      element: "Call-to-Action Button",
      priority: "high",
      hypothesis: "Action-oriented, first-person CTA copy will increase click-through rate",
      controlVersion: "Current CTA text (e.g., \"Submit\", \"Learn More\")",
      testVersion: "Action-specific, first-person text (e.g., \"Show Me My Results\", \"Start My Free Trial\")",
      expectedImpact: "8-15% increase in button clicks",
      implementationDifficulty: "easy"
    });

    recommendations.push({
      element: "Form Length",
      priority: "medium",
      hypothesis: "Reducing form fields will decrease friction and increase completions",
      controlVersion: "Current form with X fields",
      testVersion: "Simplified form with only essential fields (name + email only)",
      expectedImpact: "25-40% increase in form completion rate",
      implementationDifficulty: "easy"
    });
  }

  // Always recommend CTA color test
  recommendations.push({
    element: "CTA Button Color",
    priority: "low",
    hypothesis: "High-contrast button color will make the CTA more visible and increase clicks",
    controlVersion: "Current button color",
    testVersion: "Test bright color that contrasts with page background (orange, green, or red)",
    expectedImpact: "5-10% increase in button visibility and clicks",
    implementationDifficulty: "easy"
  });

  // Sort by priority
  const priorityOrder = { high: 0, medium: 1, low: 2 };
  return recommendations.sort((a, b) => priorityOrder[a.priority] - priorityOrder[b.priority]);
}
