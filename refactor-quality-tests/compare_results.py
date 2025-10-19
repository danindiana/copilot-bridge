#!/usr/bin/env python3
"""
Compare refactoring quality results between local and cloud models.

Analyzes saved test results and generates comparison report.
"""
import json
import statistics
from pathlib import Path
from datetime import datetime
from collections import defaultdict

RESULTS_DIR = Path(__file__).parent / "results"

def load_results():
    """Load all test results from JSON files."""
    results = []
    for filepath in RESULTS_DIR.glob("test_*.json"):
        with open(filepath) as f:
            results.append(json.load(f))
    return results

def analyze_by_model(results):
    """Group results by model type."""
    by_model = defaultdict(list)
    for r in results:
        model_type = r["result"]["model_type"]
        by_model[model_type].append(r)
    return by_model

def calculate_stats(results):
    """Calculate statistics for a set of results."""
    if not results:
        return None
    
    correctness = [r["scores"]["correctness"] for r in results]
    readability = [r["scores"]["readability"] for r in results]
    pythonic = [r["scores"]["pythonic"] for r in results]
    completeness = [r["scores"]["completeness"] for r in results]
    overall = [r["scores"]["overall"] for r in results]
    
    return {
        "count": len(results),
        "correctness": {
            "mean": statistics.mean(correctness),
            "median": statistics.median(correctness),
            "stdev": statistics.stdev(correctness) if len(correctness) > 1 else 0
        },
        "readability": {
            "mean": statistics.mean(readability),
            "median": statistics.median(readability),
        },
        "pythonic": {
            "mean": statistics.mean(pythonic),
            "median": statistics.median(pythonic),
        },
        "completeness": {
            "mean": statistics.mean(completeness),
            "median": statistics.median(completeness),
        },
        "overall": {
            "mean": statistics.mean(overall),
            "median": statistics.median(overall),
            "min": min(overall),
            "max": max(overall)
        },
        "avg_time": statistics.mean([r["test_metadata"]["elapsed_seconds"] for r in results])
    }

def generate_report(results, output_file="comparison_report.md"):
    """Generate markdown comparison report."""
    by_model = analyze_by_model(results)
    
    report = []
    report.append("# Refactoring Quality Comparison: Local vs Cloud")
    report.append("")
    report.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"**Total Tests**: {len(results)}")
    report.append("")
    report.append("---")
    report.append("")
    
    # Overall comparison
    report.append("## Overall Results")
    report.append("")
    report.append("| Metric | Local Model | Cloud Model | Winner |")
    report.append("|--------|-------------|-------------|--------|")
    
    local_stats = calculate_stats(by_model.get("local", []))
    cloud_stats = calculate_stats(by_model.get("cloud", []))
    
    if local_stats and cloud_stats:
        metrics = ["correctness", "readability", "pythonic", "completeness", "overall"]
        for metric in metrics:
            local_val = local_stats[metric]["mean"]
            cloud_val = cloud_stats[metric]["mean"]
            winner = "🏆 Local" if local_val > cloud_val else "🏆 Cloud" if cloud_val > local_val else "🤝 Tie"
            report.append(f"| {metric.title()} | {local_val:.1f} | {cloud_val:.1f} | {winner} |")
        
        # Add timing
        local_time = local_stats["avg_time"]
        cloud_time = cloud_stats["avg_time"]
        time_winner = "⚡ Local" if local_time < cloud_time else "⚡ Cloud"
        report.append(f"| Avg Time | {local_time:.1f}s | {cloud_time:.1f}s | {time_winner} |")
    
    report.append("")
    report.append("---")
    report.append("")
    
    # Detailed breakdowns
    if local_stats:
        report.append("## Local Model Performance")
        report.append("")
        report.append(f"**Model**: {by_model['local'][0]['result']['model']}")
        report.append(f"**Tests Run**: {local_stats['count']}")
        report.append("")
        report.append("| Dimension | Mean | Median | Min-Max |")
        report.append("|-----------|------|--------|---------|")
        report.append(f"| Correctness | {local_stats['correctness']['mean']:.1f} | {local_stats['correctness']['median']:.1f} | - |")
        report.append(f"| Readability | {local_stats['readability']['mean']:.1f} | {local_stats['readability']['median']:.1f} | - |")
        report.append(f"| Pythonic | {local_stats['pythonic']['mean']:.1f} | {local_stats['pythonic']['median']:.1f} | - |")
        report.append(f"| Completeness | {local_stats['completeness']['mean']:.1f} | {local_stats['completeness']['median']:.1f} | - |")
        report.append(f"| **Overall** | **{local_stats['overall']['mean']:.1f}** | **{local_stats['overall']['median']:.1f}** | {local_stats['overall']['min']:.1f}-{local_stats['overall']['max']:.1f} |")
        report.append("")
    
    if cloud_stats:
        report.append("## Cloud Model Performance")
        report.append("")
        report.append(f"**Model**: {by_model['cloud'][0]['result']['model']}")
        report.append(f"**Tests Run**: {cloud_stats['count']}")
        report.append("")
        report.append("| Dimension | Mean | Median | Min-Max |")
        report.append("|-----------|------|--------|---------|")
        report.append(f"| Correctness | {cloud_stats['correctness']['mean']:.1f} | {cloud_stats['correctness']['median']:.1f} | - |")
        report.append(f"| Readability | {cloud_stats['readability']['mean']:.1f} | {cloud_stats['readability']['median']:.1f} | - |")
        report.append(f"| Pythonic | {cloud_stats['pythonic']['mean']:.1f} | {cloud_stats['pythonic']['median']:.1f} | - |")
        report.append(f"| Completeness | {cloud_stats['completeness']['mean']:.1f} | {cloud_stats['completeness']['median']:.1f} | - |")
        report.append(f"| **Overall** | **{cloud_stats['overall']['mean']:.1f}** | **{cloud_stats['overall']['median']:.1f}** | {cloud_stats['overall']['min']:.1f}-{cloud_stats['overall']['max']:.1f} |")
        report.append("")
    
    # Individual test details
    report.append("---")
    report.append("")
    report.append("## Individual Test Results")
    report.append("")
    
    for result in sorted(results, key=lambda r: r["sample"]["name"]):
        sample_name = result["sample"]["name"]
        model_type = result["result"]["model_type"]
        scores = result["scores"]
        
        report.append(f"### {sample_name} ({model_type})")
        report.append("")
        report.append(f"**Category**: {result['sample']['category']}")
        report.append(f"**Tokens**: {result['sample']['tokens']}")
        report.append(f"**Time**: {result['test_metadata']['elapsed_seconds']:.1f}s")
        report.append("")
        report.append(f"**Scores**:")
        report.append(f"- Correctness: {scores['correctness']}/10")
        report.append(f"- Readability: {scores['readability']}/10")
        report.append(f"- Pythonic: {scores['pythonic']}/10")
        report.append(f"- Completeness: {scores['completeness']}/10")
        report.append(f"- **Overall: {scores['overall']}/10**")
        
        if "notes" in scores:
            report.append("")
            report.append(f"**Notes**: {scores['notes']}")
        
        report.append("")
    
    # Conclusions
    report.append("---")
    report.append("")
    report.append("## Conclusions")
    report.append("")
    
    if local_stats and cloud_stats:
        local_overall = local_stats["overall"]["mean"]
        cloud_overall = cloud_stats["overall"]["mean"]
        diff = abs(local_overall - cloud_overall)
        
        if diff < 0.5:
            conclusion = "**No significant difference** between local and cloud models for refactoring quality."
        elif local_overall > cloud_overall:
            conclusion = f"**Local model outperforms** cloud by {diff:.1f} points on average."
        else:
            conclusion = f"**Cloud model outperforms** local by {diff:.1f} points on average."
        
        report.append(conclusion)
        report.append("")
        
        # Cost analysis
        report.append("### Cost-Quality Tradeoff")
        report.append("")
        report.append(f"- **Local**: {local_overall:.1f}/10 quality, $0.00 cost, {local_time:.1f}s")
        report.append(f"- **Cloud**: {cloud_overall:.1f}/10 quality, ~$0.02/test cost, {cloud_time:.1f}s")
        report.append("")
        
        if local_overall >= 7.0:
            report.append("✅ **Recommendation**: Use local models for refactoring (quality ≥7.0, zero cost)")
        elif local_overall >= cloud_overall - 1.0:
            report.append("⚖️ **Recommendation**: Consider local models (minor quality difference, significant cost savings)")
        else:
            report.append("☁️ **Recommendation**: Use cloud models for critical refactorings (quality gap >1.0)")
    
    # Write report
    output_path = RESULTS_DIR / output_file
    with open(output_path, 'w') as f:
        f.write('\n'.join(report))
    
    print(f"📄 Report generated: {output_path}")
    print()
    print("Summary:")
    if local_stats:
        print(f"  Local:  {local_stats['overall']['mean']:.1f}/10 overall ({local_stats['count']} tests)")
    if cloud_stats:
        print(f"  Cloud:  {cloud_stats['overall']['mean']:.1f}/10 overall ({cloud_stats['count']} tests)")

def main():
    print("╔" + "═"*76 + "╗")
    print("║" + " "*20 + "REFACTORING QUALITY ANALYSIS" + " "*28 + "║")
    print("╚" + "═"*76 + "╝")
    print()
    
    results = load_results()
    
    if not results:
        print("❌ No test results found in results/")
        print("   Run some tests first: python3 run_refactor_test.py")
        return
    
    print(f"📊 Loaded {len(results)} test results")
    print()
    
    generate_report(results)

if __name__ == "__main__":
    main()
