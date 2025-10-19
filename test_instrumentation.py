#!/usr/bin/env python3
"""
Quick test of instrumented bridge and exporter.

Sends sample requests through the instrumented bridge,
verifies JSON logs are emitted, and checks Prometheus metrics.
"""
import subprocess
import time
import requests
import json
import sys

def test_bridge_logging():
    """Test that bridge emits proper JSON logs"""
    print("═"*78)
    print("TEST 1: Bridge Logging")
    print("═"*78)
    
    # Run instrumented bridge with sample prompt
    prompt = "Write a docstring for a function that sorts a list"
    cmd = ["python3", "proxy_instrumented.py", "--prompt", prompt, "--task", "docstring"]
    
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Check stdout (response)
    print(f"\n✓ Response received ({len(result.stdout)} chars)")
    print(f"  Preview: {result.stdout[:100]}...")
    
    # Check stderr (JSON log)
    if result.stderr:
        print(f"\n✓ JSON log emitted:")
        try:
            log_data = json.loads(result.stderr.strip())
            print(f"  Route: {log_data.get('route')}")
            print(f"  Tokens: {log_data.get('tokens_in')} in, {log_data.get('tokens_out')} out")
            print(f"  Cost saved: ${log_data.get('cost_saved_usd'):.4f}")
            print(f"  Latency: {log_data.get('latency_ms')}ms")
            return True
        except json.JSONDecodeError:
            print(f"✗ Invalid JSON in stderr: {result.stderr}")
            return False
    else:
        print("✗ No JSON log in stderr")
        return False

def test_exporter_metrics():
    """Test that exporter exposes Prometheus metrics"""
    print("\n" + "═"*78)
    print("TEST 2: Exporter Metrics")
    print("═"*78)
    
    # Check if exporter is running
    try:
        response = requests.get("http://localhost:8000/metrics", timeout=2)
        if response.status_code == 200:
            print("✓ Exporter is running on :8000")
            
            # Look for our custom metrics
            metrics_text = response.text
            expected_metrics = [
                "copilot_bridge_tokens_saved_total",
                "copilot_bridge_cost_saved_usd",
                "copilot_bridge_requests_by_route",
            ]
            
            found = []
            for metric in expected_metrics:
                if metric in metrics_text:
                    found.append(metric)
                    print(f"  ✓ Found metric: {metric}")
            
            if len(found) == len(expected_metrics):
                print(f"\n✓ All {len(expected_metrics)} expected metrics present")
                return True
            else:
                print(f"\n✗ Missing {len(expected_metrics) - len(found)} metrics")
                return False
        else:
            print(f"✗ Exporter returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ Exporter not running (connection refused)")
        print("  Start it with: python3 exporter.py &")
        return False

def test_end_to_end():
    """Test full pipeline: bridge → log → exporter → metrics"""
    print("\n" + "═"*78)
    print("TEST 3: End-to-End Pipeline")
    print("═"*78)
    
    # Check if exporter is ready
    try:
        requests.get("http://localhost:8000/metrics", timeout=2)
    except requests.exceptions.ConnectionError:
        print("✗ Exporter must be running first")
        print("  Run in another terminal: python3 exporter.py")
        return False
    
    # Get baseline metrics
    response = requests.get("http://localhost:8000/metrics")
    baseline = response.text
    
    # Extract current token count
    baseline_tokens = 0
    for line in baseline.split('\n'):
        if line.startswith('copilot_bridge_tokens_saved_total'):
            baseline_tokens = float(line.split()[1])
            break
    
    print(f"Baseline tokens saved: {baseline_tokens}")
    
    # Send a request through bridge
    prompt = "Explain binary search algorithm"
    print(f"\nSending request: {prompt}")
    
    result = subprocess.run(
        ["python3", "proxy_instrumented.py", "--prompt", prompt, "--task", "explain"],
        capture_output=True,
        text=True
    )
    
    if result.stderr:
        # Parse log and send to exporter
        log_line = result.stderr.strip()
        print(f"Log line: {log_line[:80]}...")
        
        try:
            # Send log to exporter
            response = requests.post(
                "http://localhost:8080",
                data=log_line,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 204:
                print("✓ Log sent to exporter")
                
                # Wait a moment for metrics to update
                time.sleep(0.5)
                
                # Check updated metrics
                response = requests.get("http://localhost:8000/metrics")
                updated = response.text
                
                updated_tokens = 0
                for line in updated.split('\n'):
                    if line.startswith('copilot_bridge_tokens_saved_total'):
                        updated_tokens = float(line.split()[1])
                        break
                
                print(f"Updated tokens saved: {updated_tokens}")
                
                if updated_tokens > baseline_tokens:
                    delta = updated_tokens - baseline_tokens
                    print(f"✓ Metrics incremented by {delta} tokens")
                    return True
                else:
                    print("✗ Metrics did not increment")
                    return False
            else:
                print(f"✗ Exporter returned {response.status_code}")
                return False
                
        except Exception as e:
            print(f"✗ Error: {e}")
            return False
    else:
        print("✗ No log output from bridge")
        return False

if __name__ == "__main__":
    print("╔" + "═"*76 + "╗")
    print("║" + " "*22 + "INSTRUMENTATION TEST SUITE" + " "*28 + "║")
    print("╚" + "═"*76 + "╝")
    print()
    
    results = []
    
    # Test 1: Bridge logging
    results.append(("Bridge Logging", test_bridge_logging()))
    
    # Test 2: Exporter metrics
    results.append(("Exporter Metrics", test_exporter_metrics()))
    
    # Test 3: End-to-end
    if results[1][1]:  # Only if exporter is running
        results.append(("End-to-End", test_end_to_end()))
    
    # Summary
    print("\n" + "═"*78)
    print("SUMMARY")
    print("═"*78)
    
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {name}")
    
    passed_count = sum(1 for _, p in results if p)
    total_count = len(results)
    
    print()
    print(f"Results: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("\n🎉 All tests passed! System is ready.")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed. Check output above.")
        sys.exit(1)
