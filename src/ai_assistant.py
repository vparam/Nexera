"""
AI Assistant for answering questions about savings recommendations
Uses Claude API or falls back to rule-based responses
"""

import os
from typing import Optional, Dict, Any, List
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


class AIAssistant:
    """AI-powered Q&A assistant for cost savings"""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize AI assistant"""
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        self.client = None
        self.conversation_history: List[Dict[str, str]] = []
        self.analysis_context = None

        if self.api_key and ANTHROPIC_AVAILABLE:
            self.client = anthropic.Anthropic(api_key=self.api_key)

    def set_analysis_context(self, findings: Dict[str, Any], opportunities: List[Any], summary: Dict[str, Any]):
        """Set dynamic context from analysis results"""

        # Build context from actual analysis data
        context_parts = [
            "You are an AI Savings Advisor helping executives understand cloud cost optimization.",
            "You have just analyzed their infrastructure and found the following:",
            ""
        ]

        # Infrastructure findings
        if findings and 'infrastructure' in findings:
            infra = findings['infrastructure']
            context_parts.append(f"**Infrastructure Analysis:**")
            context_parts.append(f"- Total instances analyzed: {infra.get('total_instances', 'N/A'):,}")
            context_parts.append(f"- Spot-compatible instances: {infra.get('spot_candidates', 'N/A'):,}")
            context_parts.append(f"- Idle instances detected: {infra.get('idle_instances', 'N/A'):,}")
            context_parts.append("")

        # Storage findings
        if findings and 'storage' in findings:
            storage = findings['storage']
            context_parts.append(f"**Storage Analysis:**")
            context_parts.append(f"- Total storage: {storage.get('total_tb', 'N/A'):.1f} TB")
            context_parts.append(f"- Stale data (90+ days): {storage.get('stale_tb', 'N/A'):.1f} TB")
            context_parts.append("")

        # Cross-cloud findings
        if findings and 'cross_cloud' in findings:
            cc = findings['cross_cloud']
            context_parts.append(f"**Cross-Cloud Duplicates:**")
            context_parts.append(f"- Total duplicates: {cc.get('total_duplicates', 'N/A'):,}")
            context_parts.append(f"- Monthly waste: ${cc.get('monthly_waste', 0):,.0f}")
            if cc.get('by_team'):
                teams = [t['team'] for t in cc['by_team'][:4]]
                context_parts.append(f"- Affected teams: {', '.join(teams)}")
            context_parts.append("")

        # ML model findings
        if findings and 'ml_models' in findings:
            ml = findings['ml_models']
            context_parts.append(f"**ML Model Registry:**")
            context_parts.append(f"- Total versions: {ml.get('total_versions', 'N/A'):,}")
            context_parts.append(f"- Prunable versions: {ml.get('prunable_versions', 'N/A'):,}")
            context_parts.append("")

        # Opportunities
        if opportunities:
            context_parts.append("**Prioritized Quick Win Recommendations:**")
            for i, opp in enumerate(opportunities, 1):
                context_parts.append(f"{i}. {opp.name}")
                context_parts.append(f"   - Monthly Savings: ${opp.monthly_savings:,.0f}")
                context_parts.append(f"   - Risk Level: {opp.risk_level}")
                context_parts.append(f"   - Timeline: {opp.implementation_time}")
                context_parts.append(f"   - Confidence: {opp.confidence * 100:.0f}%")
            context_parts.append("")

        # Summary metrics
        if summary:
            context_parts.append("**Financial Summary:**")
            context_parts.append(f"- Total Monthly Savings: ${summary.get('total_monthly_savings', 0):,.0f}")
            context_parts.append(f"- Total Annual Savings: ${summary.get('total_annual_savings', 0):,.0f}")
            context_parts.append(f"- Affected Resources: {summary.get('total_affected_resources', 0):,}")
            context_parts.append("")

        context_parts.append("Be concise, executive-focused, and reference the specific data from the analysis.")
        context_parts.append("When discussing specific recommendations, cite the actual numbers discovered.")

        self.analysis_context = "\n".join(context_parts)

    def get_system_prompt(self) -> str:
        """Get the system prompt with analysis context"""
        if self.analysis_context:
            return self.analysis_context

        # Default context if no analysis has been run
        return """
You are an AI Savings Advisor helping executives understand cloud cost optimization.

No analysis has been run yet. Encourage the user to click "Start Infrastructure Analysis"
to scan their cloud infrastructure and discover savings opportunities.

Be concise and helpful.
"""

    def ask(self, question: str) -> str:
        """Ask a question and get an answer"""

        # Add to conversation history
        self.conversation_history.append({"role": "user", "content": question})

        if self.client:
            try:
                response = self._ask_claude(question)
            except Exception as e:
                print(f"Claude API error: {e}")
                response = self._fallback_response(question)
        else:
            response = self._fallback_response(question)

        # Add response to history
        self.conversation_history.append({"role": "assistant", "content": response})

        return response

    def _ask_claude(self, question: str) -> str:
        """Get response from Claude API with conversation history"""

        message = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            system=self.get_system_prompt(),
            messages=self.conversation_history
        )

        return message.content[0].text

    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []

    def _fallback_response(self, question: str) -> str:
        """Provide rule-based responses when API is unavailable"""

        q_lower = question.lower()

        if 'spot' in q_lower or 'instance' in q_lower:
            return """
**Spot Instance Migration**

This is typically our highest-value, lowest-risk recommendation.

**How it works:**
- Migrate non-critical workloads to spot instances
- 60-70% cost reduction vs on-demand
- Automatic fallback if spot capacity unavailable

**Risk Mitigation:**
- Only non-critical workloads (batch, data processing)
- Auto-scaling groups handle interruptions
- Quick implementation, zero downtime

This approach is proven at scale (Netflix, Lyft use this strategy).

*For exact numbers specific to your infrastructure, check the analysis results above.*
"""

        elif 'roi' in q_lower or 'return' in q_lower or 'payback' in q_lower:
            return """
**ROI Analysis**

The ROI is calculated based on your actual infrastructure analysis:

**Formula:**
- Payback Period = Investment / Monthly Savings
- First Year ROI = (Annual Savings - Investment) / Investment × 100
- NPV = -Investment + Σ(Annual Savings / (1 + 10%)^year)

**Use the ROI Calculator** in the app to model different investment scenarios with interactive sliders.

*Adjust the investment amount to see how it affects payback period and NPV.*
"""

        elif 'risk' in q_lower:
            return """
**Risk Assessment**

**Low Risk (Spot + Dedup):**
- Proven technologies
- Reversible changes
- No SLA impact
- Automatic failover

**No Risk (Storage):**
- Cloud provider native feature
- Transparent to applications
- Easily reversible

**Medium Risk (ML Models):**
- Requires testing
- Mitigation: staged rollout

*Check each recommendation's risk level in the Quick Wins section above.*
"""

        elif 'storage' in q_lower or 'lifecycle' in q_lower:
            return """
**Storage Lifecycle Optimization**

Our safest recommendation with zero risk.

**Strategy:**
- Move infrequently accessed data (90+ days old)
- Use cheaper storage tiers (S3 IA, Glacier)
- Zero application changes required

**Savings Calculation:**
- Standard: ~$0.023/GB/month
- Infrequent Access: ~$0.0125/GB/month
- ~45% savings on eligible data

**Implementation:**
- 1-day setup using native cloud lifecycle policies
- Completely transparent to applications

*See the Storage Pattern Analysis phase for your specific stale data amounts.*
"""

        elif 'duplicate' in q_lower or 'cross-cloud' in q_lower or 'team' in q_lower:
            return """
**Cross-Cloud Duplicate Detection**

We scan for resources duplicated across AWS, GCP, and Azure.

**What we find:**
- Same databases running in multiple clouds
- Duplicate storage buckets
- Redundant compute resources

**Breakdown available by:**
- Team (data-science, backend, ml-ops, etc.)
- Resource type (database, cache, load_balancer)
- Cloud provider

**Savings:** Keep one copy, eliminate waste from duplicates.

*Check the Cross-Cloud phase results for team-by-team breakdown.*
"""

        elif 'model' in q_lower or 'ml' in q_lower or 'registry' in q_lower:
            return """
**ML Model Registry Cleanup**

Old model versions accumulate over time and consume storage.

**What we analyze:**
- Active vs inactive model versions
- Age of each version (90+ days is prunable)
- Storage per framework (PyTorch, TensorFlow, etc.)

**Safe cleanup:**
- Keep active/production versions
- Prune old inactive versions
- Staged rollout with testing

*See the ML Model Registry Audit phase for specific models and version counts.*
"""

        elif 'timeline' in q_lower or 'implementation' in q_lower or 'when' in q_lower:
            return """
**Implementation Timeline**

**Week 1: Quick Wins**
- Hours 1-2: Spot instance migration
- Day 1: Storage lifecycle policies
- Days 2-7: Cross-cloud deduplication

**Weeks 2-3: Model Registry**
- Testing and validation
- Staged rollout
- Monitoring setup

**Success Factors:**
- Dedicated implementation team
- Automated tooling
- Zero-downtime approach
- Continuous monitoring

*Click "Execute Top 3 Quick Wins" to queue implementation.*
"""

        else:
            return """
**I can help you understand:**

- **Spot Instances**: EC2 cost optimization details
- **ROI/Payback**: Financial projections and calculations
- **Risk**: Assessment and mitigation strategies
- **Storage**: Lifecycle policy benefits
- **Cross-Cloud**: Duplicate detection by team
- **ML Models**: Registry cleanup opportunities
- **Timeline**: Implementation schedule

**Try asking:**
- "What's the risk of spot instance migration?"
- "How is the ROI calculated?"
- "Which teams have the most duplicates?"
- "How quickly can we implement this?"

*Run the analysis first to get specific numbers for your infrastructure.*
"""

    def is_available(self) -> bool:
        """Check if Claude API is available"""
        return self.client is not None


if __name__ == '__main__':
    # Test the assistant
    assistant = AIAssistant()

    print("AI Assistant Status:", "Claude API" if assistant.is_available() else "Fallback Mode")
    print("\n" + "=" * 60)

    questions = [
        "What are the risks of spot instance migration?",
        "How does the ROI calculation work?",
        "Tell me about storage optimization",
    ]

    for q in questions:
        print(f"\nQ: {q}")
        print(f"A: {assistant.ask(q)}")
        print("-" * 60)
