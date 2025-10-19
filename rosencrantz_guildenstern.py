#!/usr/bin/env python3
"""
Rosencrantz & Guildenstern: Meta-Reasoning Module

Two-stage local inference with quality audit:
1. Large model (gpt-oss:20b) generates draft
2. Small model (qwen2.5-coder:7b) audits for:
   - Relevance score
   - Structure quality
   - Counterfactual detection
   - Hallucination risk
   - Actionability score

The audit provides meta-commentary on the draft's strengths/weaknesses.
"""
import httpx
import json
import time
from typing import Dict, Any, List
from dataclasses import dataclass, asdict


@dataclass
class AuditReport:
    """Results from the meta-reasoning audit."""
    relevance_score: float  # 0-10: How relevant to the prompt?
    structure_score: float  # 0-10: How well-organized?
    specificity_score: float  # 0-10: Concrete vs vague?
    actionability_score: float  # 0-10: Can user act on this?
    hallucination_risk: str  # "low", "medium", "high"
    
    strengths: List[str]  # What the draft does well
    weaknesses: List[str]  # What could be improved
    counterfactuals: List[str]  # Alternative approaches/perspectives
    
    overall_quality: float  # 0-10: Weighted average
    recommendation: str  # "ship", "revise", "regenerate"
    
    audit_time: float  # Seconds for audit
    

class RosencrantzGuildenstern:
    """
    Meta-reasoning orchestrator.
    
    Named after Shakespeare's characters who observe and comment
    on the main action without being central to it.
    """
    
    def __init__(
        self,
        large_model: str = "gpt-oss:20b",
        audit_model: str = "qwen2.5-coder:7b-instruct-q8_0",
        ollama_url: str = "http://192.168.1.138:11434"
    ):
        self.large_model = large_model
        self.audit_model = audit_model
        self.ollama_url = ollama_url
        
    def _call_model(self, model: str, prompt: str, num_ctx: int = 4096) -> Dict[str, Any]:
        """Call Ollama model, return response + metadata."""
        start = time.time()
        
        with httpx.Client(timeout=180.0) as client:
            response = client.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"num_ctx": num_ctx}
                }
            )
            result = response.json()
        
        elapsed = time.time() - start
        
        return {
            "text": result.get("response", ""),
            "time": elapsed,
            "model": model,
            "tokens": result.get("eval_count", 0)
        }
    
    def generate_draft(self, prompt: str, context: str = "") -> Dict[str, Any]:
        """
        Stage 1: Large model generates initial draft.
        
        Args:
            prompt: User's request
            context: Additional context (optional)
        
        Returns:
            Draft response with metadata
        """
        full_prompt = f"{context}\n\n{prompt}" if context else prompt
        
        print("🎭 Stage 1: Large Model Generating Draft...")
        print(f"   Model: {self.large_model}")
        print()
        
        draft = self._call_model(
            self.large_model,
            full_prompt,
            num_ctx=32768  # Use large context window
        )
        
        print(f"✅ Draft generated in {draft['time']:.1f}s")
        print(f"   Tokens: {draft['tokens']}")
        print()
        
        return draft
    
    def audit_draft(self, prompt: str, draft_text: str) -> AuditReport:
        """
        Stage 2: Small model audits the draft.
        
        Provides meta-commentary on quality dimensions.
        """
        audit_prompt = f"""You are a critical AI auditor. Analyze this AI-generated response.

ORIGINAL PROMPT:
{prompt}

AI-GENERATED DRAFT:
{draft_text}

Provide a structured audit with scores (0-10) and commentary:

1. RELEVANCE (0-10): How well does it answer the prompt?
2. STRUCTURE (0-10): Is it well-organized and clear?
3. SPECIFICITY (0-10): Concrete details vs vague generalities?
4. ACTIONABILITY (0-10): Can the user act on this information?
5. HALLUCINATION RISK (low/medium/high): Any unsupported claims?

Then provide:
- STRENGTHS: 2-3 things the draft does well
- WEAKNESSES: 2-3 areas for improvement
- COUNTERFACTUALS: 1-2 alternative approaches not considered

Format your response as JSON:
{{
  "relevance_score": 8.5,
  "structure_score": 9.0,
  "specificity_score": 7.0,
  "actionability_score": 8.0,
  "hallucination_risk": "low",
  "strengths": ["Clear structure", "Good examples", "Actionable steps"],
  "weaknesses": ["Could be more specific on X", "Missing edge case Y"],
  "counterfactuals": ["Alternative approach: ...", "Could consider: ..."]
}}

Respond ONLY with valid JSON, no other text."""

        print("🎭 Stage 2: Small Model Auditing Draft...")
        print(f"   Model: {self.audit_model}")
        print()
        
        audit_result = self._call_model(
            self.audit_model,
            audit_prompt,
            num_ctx=8192  # Smaller context for audit
        )
        
        print(f"✅ Audit completed in {audit_result['time']:.1f}s")
        print()
        
        # Parse JSON response
        try:
            # Extract JSON from response (handle potential markdown wrappers)
            text = audit_result['text'].strip()
            if '```json' in text:
                text = text.split('```json')[1].split('```')[0]
            elif '```' in text:
                text = text.split('```')[1].split('```')[0]
            
            audit_data = json.loads(text)
            
            # Calculate overall quality (weighted average)
            overall = (
                audit_data['relevance_score'] * 0.3 +
                audit_data['structure_score'] * 0.2 +
                audit_data['specificity_score'] * 0.2 +
                audit_data['actionability_score'] * 0.3
            )
            
            # Determine recommendation
            if overall >= 8.0 and audit_data['hallucination_risk'] == 'low':
                recommendation = "ship"
            elif overall >= 6.0:
                recommendation = "revise"
            else:
                recommendation = "regenerate"
            
            report = AuditReport(
                relevance_score=audit_data['relevance_score'],
                structure_score=audit_data['structure_score'],
                specificity_score=audit_data['specificity_score'],
                actionability_score=audit_data['actionability_score'],
                hallucination_risk=audit_data['hallucination_risk'],
                strengths=audit_data.get('strengths', []),
                weaknesses=audit_data.get('weaknesses', []),
                counterfactuals=audit_data.get('counterfactuals', []),
                overall_quality=overall,
                recommendation=recommendation,
                audit_time=audit_result['time']
            )
            
            return report
            
        except (json.JSONDecodeError, KeyError) as e:
            print(f"⚠️  Warning: Could not parse audit JSON: {e}")
            print(f"Raw response: {audit_result['text'][:200]}...")
            
            # Return minimal report on parse failure
            return AuditReport(
                relevance_score=5.0,
                structure_score=5.0,
                specificity_score=5.0,
                actionability_score=5.0,
                hallucination_risk="unknown",
                strengths=["Parse error - manual review needed"],
                weaknesses=["Could not analyze"],
                counterfactuals=[],
                overall_quality=5.0,
                recommendation="manual_review",
                audit_time=audit_result['time']
            )
    
    def generate_with_audit(
        self,
        prompt: str,
        context: str = "",
        return_draft: bool = True
    ) -> Dict[str, Any]:
        """
        Full pipeline: generate + audit.
        
        Args:
            prompt: User's request
            context: Additional context
            return_draft: Include draft text in response
        
        Returns:
            Complete result with draft, audit, and recommendation
        """
        # Stage 1: Generate
        draft = self.generate_draft(prompt, context)
        
        # Stage 2: Audit
        audit = self.audit_draft(prompt, draft['text'])
        
        result = {
            "draft": draft if return_draft else {"time": draft['time'], "tokens": draft['tokens']},
            "audit": asdict(audit),
            "total_time": draft['time'] + audit.audit_time,
            "recommendation": audit.recommendation,
            "cost": 0.0  # Local inference
        }
        
        return result
    
    def print_audit_report(self, audit: AuditReport):
        """Pretty-print the audit report."""
        print("╔" + "═"*76 + "╗")
        print("║" + " "*20 + "META-REASONING AUDIT REPORT" + " "*29 + "║")
        print("╚" + "═"*76 + "╝")
        print()
        
        # Scores
        print("📊 QUALITY SCORES:")
        print(f"   • Relevance:      {audit.relevance_score:.1f}/10")
        print(f"   • Structure:      {audit.structure_score:.1f}/10")
        print(f"   • Specificity:    {audit.specificity_score:.1f}/10")
        print(f"   • Actionability:  {audit.actionability_score:.1f}/10")
        print(f"   • Overall:        {audit.overall_quality:.1f}/10")
        print()
        
        # Risk assessment
        risk_emoji = {"low": "✅", "medium": "⚠️", "high": "❌"}.get(audit.hallucination_risk, "❓")
        print(f"🎯 HALLUCINATION RISK: {risk_emoji} {audit.hallucination_risk.upper()}")
        print()
        
        # Strengths
        if audit.strengths:
            print("✅ STRENGTHS:")
            for s in audit.strengths:
                print(f"   • {s}")
            print()
        
        # Weaknesses
        if audit.weaknesses:
            print("⚠️  WEAKNESSES:")
            for w in audit.weaknesses:
                print(f"   • {w}")
            print()
        
        # Counterfactuals
        if audit.counterfactuals:
            print("🔄 COUNTERFACTUALS (Alternative Perspectives):")
            for c in audit.counterfactuals:
                print(f"   • {c}")
            print()
        
        # Recommendation
        rec_emoji = {"ship": "🚀", "revise": "✏️", "regenerate": "🔄", "manual_review": "👁️"}.get(
            audit.recommendation, "❓"
        )
        print(f"💡 RECOMMENDATION: {rec_emoji} {audit.recommendation.upper()}")
        print()
        
        print(f"⏱️  Audit Time: {audit.audit_time:.1f}s")
        print("="*78)


def demo_meta_reasoning():
    """Interactive demonstration of meta-reasoning."""
    print("╔" + "═"*76 + "╗")
    print("║" + " "*15 + "ROSENCRANTZ & GUILDENSTERN DEMO" + " "*30 + "║")
    print("║" + " "*20 + "Two-Stage Meta-Reasoning" + " "*33 + "║")
    print("╚" + "═"*76 + "╝")
    print()
    print("This demo uses two local models:")
    print("  1️⃣  gpt-oss:20b (Large) - Generates draft response")
    print("  2️⃣  qwen2.5-coder:7b (Small) - Audits the draft")
    print()
    print("The small model provides meta-commentary on:")
    print("  • Relevance, structure, specificity, actionability")
    print("  • Strengths, weaknesses, counterfactuals")
    print("  • Recommendation: ship / revise / regenerate")
    print()
    print("="*78)
    print()
    
    # Example prompts
    examples = [
        {
            "name": "Code Explanation",
            "prompt": "Explain how Python's GIL (Global Interpreter Lock) affects multi-threading.",
            "context": ""
        },
        {
            "name": "Architecture Decision",
            "prompt": "Should I use microservices or a monolith for a new e-commerce platform?",
            "context": "Team size: 5 developers, Expected traffic: 10K users/day, Timeline: 3 months"
        },
        {
            "name": "Refactoring Advice",
            "prompt": "How should I refactor this function to be more testable?",
            "context": "def process_order(order_id):\n    db = connect_db()\n    order = db.get(order_id)\n    email = send_email(order.user)\n    log(f'Processed {order_id}')\n    return True"
        }
    ]
    
    print("Select a test case:")
    for i, ex in enumerate(examples, 1):
        print(f"  {i}. {ex['name']}")
    print(f"  {len(examples) + 1}. Custom prompt")
    print()
    
    choice = input("Choice [1]: ").strip() or "1"
    
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(examples):
            prompt = examples[idx]['prompt']
            context = examples[idx]['context']
        else:
            prompt = input("\nEnter your prompt: ").strip()
            context = input("Enter context (optional): ").strip()
    except ValueError:
        print("Invalid choice, using example 1")
        prompt = examples[0]['prompt']
        context = examples[0]['context']
    
    print()
    print("="*78)
    print()
    
    # Run meta-reasoning
    rg = RosencrantzGuildenstern()
    result = rg.generate_with_audit(prompt, context)
    
    # Display results
    print("─"*78)
    print("DRAFT RESPONSE:")
    print("─"*78)
    print(result['draft']['text'][:500] + "..." if len(result['draft']['text']) > 500 else result['draft']['text'])
    print()
    print(f"(Draft: {result['draft']['time']:.1f}s, {result['draft']['tokens']} tokens)")
    print()
    
    # Display audit
    audit = AuditReport(**result['audit'])
    rg.print_audit_report(audit)
    
    print()
    print(f"🎭 Total Time: {result['total_time']:.1f}s (Draft: {result['draft']['time']:.1f}s + Audit: {audit.audit_time:.1f}s)")
    print(f"💰 Total Cost: $0.00 (both models local)")
    print()
    
    # Show recommendation
    if audit.recommendation == "ship":
        print("✅ This response is high quality and ready to use!")
    elif audit.recommendation == "revise":
        print("✏️  Consider revising based on the weaknesses identified above.")
    elif audit.recommendation == "regenerate":
        print("🔄 Quality is below threshold. Consider regenerating with more context.")
    else:
        print("👁️  Manual review recommended due to parsing issues.")


if __name__ == "__main__":
    demo_meta_reasoning()
