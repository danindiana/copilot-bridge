"""
Test Samples for Refactoring Quality Comparison

Each sample includes:
- Original code (realistic, messy)
- Token count (pre-calculated)
- Refactoring goals (what to improve)
- Expected improvements (quality criteria)
"""

# ═══════════════════════════════════════════════════════════════════════════
# SAMPLE 1: Legacy Login Function
# ═══════════════════════════════════════════════════════════════════════════

LEGACY_LOGIN = {
    "name": "legacy_login.py",
    "tokens": 450,
    "category": "extract_function",
    "description": "Monolithic login function with mixed concerns",
    "code": '''
def login(username, password):
    # Validate inputs
    if not username or not password:
        return {"success": False, "error": "Missing credentials"}
    if len(username) < 3 or len(password) < 8:
        return {"success": False, "error": "Invalid length"}
    
    # Check database
    import sqlite3
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=?", (username,))
    user = cursor.fetchone()
    conn.close()
    
    if not user:
        return {"success": False, "error": "User not found"}
    
    # Verify password
    import hashlib
    hashed = hashlib.sha256(password.encode()).hexdigest()
    if user[2] != hashed:
        return {"success": False, "error": "Wrong password"}
    
    # Generate session
    import uuid
    import time
    session_id = str(uuid.uuid4())
    expires = time.time() + 3600
    
    # Store session
    conn = sqlite3.connect('sessions.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO sessions VALUES (?, ?, ?)", 
                   (session_id, user[0], expires))
    conn.commit()
    conn.close()
    
    return {"success": True, "session_id": session_id, "user_id": user[0]}
''',
    "refactor_goals": [
        "Extract validation logic to separate function",
        "Extract database operations to separate functions",
        "Extract password hashing to separate function",
        "Add type hints",
        "Use context managers for database connections",
        "Add docstrings"
    ],
    "quality_criteria": {
        "correctness": "All functionality preserved, no bugs",
        "readability": "Clear separation of concerns, easy to follow",
        "pythonic": "Type hints, context managers, proper imports",
        "completeness": "All 6 refactoring goals addressed"
    }
}

# ═══════════════════════════════════════════════════════════════════════════
# SAMPLE 2: Data Processor
# ═══════════════════════════════════════════════════════════════════════════

DATA_PROCESSOR = {
    "name": "data_processor.py",
    "tokens": 680,
    "category": "modernize_syntax",
    "description": "Old-style Python 2 code needing modernization",
    "code": '''
import os
import sys

class DataProcessor:
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.results = []
    
    def process(self):
        files = []
        for root, dirs, filenames in os.walk(self.data_dir):
            for filename in filenames:
                if filename.endswith('.txt'):
                    files.append(os.path.join(root, filename))
        
        for filepath in files:
            f = open(filepath, 'r')
            content = f.read()
            f.close()
            
            lines = content.split('\\n')
            valid_lines = []
            for line in lines:
                if line and not line.startswith('#'):
                    valid_lines.append(line.strip())
            
            if len(valid_lines) > 0:
                self.results.append({
                    'file': filepath,
                    'lines': valid_lines,
                    'count': len(valid_lines)
                })
    
    def get_results(self):
        sorted_results = sorted(self.results, key=lambda x: x['count'], reverse=True)
        return sorted_results
    
    def save_report(self, output_file):
        f = open(output_file, 'w')
        f.write("Data Processing Report\\n")
        f.write("=" * 50 + "\\n\\n")
        for result in self.get_results():
            f.write("File: %s\\n" % result['file'])
            f.write("Lines: %d\\n" % result['count'])
            f.write("\\n")
        f.close()
        print "Report saved to", output_file
''',
    "refactor_goals": [
        "Use pathlib instead of os.path",
        "Use context managers for file operations",
        "Use list comprehensions instead of loops",
        "Use f-strings instead of % formatting",
        "Fix Python 2 print statement",
        "Add type hints",
        "Use Path.glob() for file finding"
    ],
    "quality_criteria": {
        "correctness": "Same output, Python 3 compatible",
        "readability": "More concise, modern idioms",
        "pythonic": "pathlib, comprehensions, f-strings, type hints",
        "completeness": "All 7 modernization goals addressed"
    }
}

# ═══════════════════════════════════════════════════════════════════════════
# SAMPLE 3: API Client
# ═══════════════════════════════════════════════════════════════════════════

API_CLIENT = {
    "name": "api_client.py",
    "tokens": 520,
    "category": "improve_naming",
    "description": "Cryptic variable names and poor error handling",
    "code": '''
import requests

class AC:
    def __init__(self, u, k):
        self.u = u
        self.k = k
        self.s = requests.Session()
        self.s.headers.update({"Authorization": "Bearer " + k})
    
    def g(self, ep, p=None):
        r = self.s.get(self.u + ep, params=p)
        if r.status_code == 200:
            return r.json()
        return None
    
    def p(self, ep, d):
        r = self.s.post(self.u + ep, json=d)
        if r.status_code in [200, 201]:
            return r.json()
        return None
    
    def d(self, ep):
        r = self.s.delete(self.u + ep)
        return r.status_code == 204
    
    def gu(self, uid):
        return self.g(f"/users/{uid}")
    
    def cu(self, n, e):
        return self.p("/users", {"name": n, "email": e})
    
    def du(self, uid):
        return self.d(f"/users/{uid}")
''',
    "refactor_goals": [
        "Rename class and variables to descriptive names",
        "Add proper error handling with exceptions",
        "Add input validation",
        "Add type hints",
        "Add docstrings",
        "Extract common response handling logic"
    ],
    "quality_criteria": {
        "correctness": "Same API behavior, better error messages",
        "readability": "Clear names, obvious what each method does",
        "pythonic": "Explicit is better than implicit, proper exceptions",
        "completeness": "All 6 naming and error handling goals met"
    }
}

# ═══════════════════════════════════════════════════════════════════════════
# SAMPLE 4: Report Generator
# ═══════════════════════════════════════════════════════════════════════════

REPORT_GENERATOR = {
    "name": "report_generator.py",
    "tokens": 890,
    "category": "performance",
    "description": "Inefficient loops and repeated calculations",
    "code": '''
def generate_sales_report(sales_data):
    report = {}
    
    # Calculate total sales per product
    report['product_totals'] = {}
    for sale in sales_data:
        product = sale['product']
        amount = sale['amount']
        if product not in report['product_totals']:
            report['product_totals'][product] = 0
        report['product_totals'][product] += amount
    
    # Calculate total sales per region
    report['region_totals'] = {}
    for sale in sales_data:
        region = sale['region']
        amount = sale['amount']
        if region not in report['region_totals']:
            report['region_totals'][region] = 0
        report['region_totals'][region] += amount
    
    # Calculate total sales per month
    report['monthly_totals'] = {}
    for sale in sales_data:
        month = sale['date'].split('-')[1]
        amount = sale['amount']
        if month not in report['monthly_totals']:
            report['monthly_totals'][month] = 0
        report['monthly_totals'][month] += amount
    
    # Find top products
    report['top_products'] = []
    product_list = []
    for product, total in report['product_totals'].items():
        product_list.append((product, total))
    sorted_products = sorted(product_list, key=lambda x: x[1], reverse=True)
    for i in range(min(10, len(sorted_products))):
        report['top_products'].append(sorted_products[i])
    
    # Find top regions
    report['top_regions'] = []
    region_list = []
    for region, total in report['region_totals'].items():
        region_list.append((region, total))
    sorted_regions = sorted(region_list, key=lambda x: x[1], reverse=True)
    for i in range(min(5, len(sorted_regions))):
        report['top_regions'].append(sorted_regions[i])
    
    # Calculate overall total
    report['total_sales'] = 0
    for sale in sales_data:
        report['total_sales'] += sale['amount']
    
    # Calculate average sale
    report['average_sale'] = report['total_sales'] / len(sales_data)
    
    return report
''',
    "refactor_goals": [
        "Use defaultdict or Counter for aggregations",
        "Single pass through data where possible",
        "Use list comprehensions for filtering/mapping",
        "Extract repeated aggregation pattern",
        "Use sum() instead of manual loops",
        "Cache expensive calculations"
    ],
    "quality_criteria": {
        "correctness": "Same results, verifiable correctness",
        "readability": "Clearer intent, less boilerplate",
        "pythonic": "collections module, comprehensions, built-ins",
        "completeness": "All 6 performance improvements applied"
    }
}

# ═══════════════════════════════════════════════════════════════════════════
# SAMPLE 5: Config Manager
# ═══════════════════════════════════════════════════════════════════════════

CONFIG_MANAGER = {
    "name": "config_manager.py",
    "tokens": 340,
    "category": "type_hints",
    "description": "Untyped configuration manager",
    "code": '''
import json
import os

class ConfigManager:
    def __init__(self, config_file):
        self.config_file = config_file
        self.config = {}
        self.load()
    
    def load(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = self.get_defaults()
            self.save()
    
    def get_defaults(self):
        return {
            "api_url": "https://api.example.com",
            "timeout": 30,
            "retries": 3,
            "debug": False
        }
    
    def get(self, key, default=None):
        return self.config.get(key, default)
    
    def set(self, key, value):
        self.config[key] = value
        self.save()
    
    def save(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def reset(self):
        self.config = self.get_defaults()
        self.save()
''',
    "refactor_goals": [
        "Add complete type hints (Python 3.9+ syntax)",
        "Use TypedDict for config structure",
        "Add validation for set() method",
        "Use pathlib for file operations",
        "Add docstrings with types",
        "Make get_defaults() return typed dict"
    ],
    "quality_criteria": {
        "correctness": "Mypy passes with --strict",
        "readability": "Clear types make API obvious",
        "pythonic": "Modern typing module usage",
        "completeness": "All 6 type hint goals met"
    }
}

# ═══════════════════════════════════════════════════════════════════════════
# SAMPLE 6: Test Utils
# ═══════════════════════════════════════════════════════════════════════════

TEST_UTILS = {
    "name": "test_utils.py",
    "tokens": 280,
    "category": "extract_helpers",
    "description": "Duplicated test setup code",
    "code": '''
import unittest
import tempfile
import os

class TestDataProcessor(unittest.TestCase):
    def test_process_single_file(self):
        # Setup
        test_dir = tempfile.mkdtemp()
        test_file = os.path.join(test_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("line1\\nline2\\nline3")
        
        # Test
        processor = DataProcessor(test_dir)
        processor.process()
        results = processor.get_results()
        
        # Assert
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['count'], 3)
        
        # Cleanup
        os.unlink(test_file)
        os.rmdir(test_dir)
    
    def test_process_multiple_files(self):
        # Setup
        test_dir = tempfile.mkdtemp()
        test_file1 = os.path.join(test_dir, "test1.txt")
        test_file2 = os.path.join(test_dir, "test2.txt")
        with open(test_file1, 'w') as f:
            f.write("line1\\nline2")
        with open(test_file2, 'w') as f:
            f.write("line1")
        
        # Test
        processor = DataProcessor(test_dir)
        processor.process()
        results = processor.get_results()
        
        # Assert
        self.assertEqual(len(results), 2)
        
        # Cleanup
        os.unlink(test_file1)
        os.unlink(test_file2)
        os.rmdir(test_dir)
''',
    "refactor_goals": [
        "Extract test data setup to setUp() method",
        "Extract cleanup to tearDown() method",
        "Create helper methods for file creation",
        "Use unittest.mock for file operations",
        "Add fixtures for common test data",
        "Use pytest-style fixtures if possible"
    ],
    "quality_criteria": {
        "correctness": "All tests still pass",
        "readability": "DRY principle, clear test intent",
        "pythonic": "Proper unittest patterns, fixtures",
        "completeness": "All 6 extraction goals achieved"
    }
}

# ═══════════════════════════════════════════════════════════════════════════
# Test Corpus Summary
# ═══════════════════════════════════════════════════════════════════════════

ALL_SAMPLES = [
    LEGACY_LOGIN,
    DATA_PROCESSOR,
    API_CLIENT,
    REPORT_GENERATOR,
    CONFIG_MANAGER,
    TEST_UTILS
]

CORPUS_STATS = {
    "total_samples": len(ALL_SAMPLES),
    "total_tokens": sum(s["tokens"] for s in ALL_SAMPLES),
    "categories": {
        "extract_function": 2,
        "modernize_syntax": 1,
        "improve_naming": 1,
        "performance": 1,
        "type_hints": 1
    },
    "avg_tokens_per_sample": sum(s["tokens"] for s in ALL_SAMPLES) // len(ALL_SAMPLES)
}

def get_sample(name):
    """Get a sample by name."""
    for sample in ALL_SAMPLES:
        if sample["name"] == name:
            return sample
    return None

def get_samples_by_category(category):
    """Get all samples in a category."""
    return [s for s in ALL_SAMPLES if s["category"] == category]

if __name__ == "__main__":
    print("Test Corpus Summary")
    print("=" * 70)
    print(f"Total samples: {CORPUS_STATS['total_samples']}")
    print(f"Total tokens: {CORPUS_STATS['total_tokens']:,}")
    print(f"Average tokens per sample: {CORPUS_STATS['avg_tokens_per_sample']}")
    print()
    print("Samples:")
    for sample in ALL_SAMPLES:
        print(f"  • {sample['name']:25s} {sample['tokens']:4d} tokens  ({sample['category']})")
