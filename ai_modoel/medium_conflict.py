import requests
import json
import datetime

BASE_URL = "http://localhost:8000/predictor/"

# Medium-level conflict with multiple changes (validation, naming, and output shape)
CONFLICT_TEXT = '''Resolve the following merge conflict in python.

BASE VERSION:
def summarize_orders(orders, min_total=0):
    """
    Summarize a list of order dicts.

    Args:
        orders: list of dicts with keys: id, total, status
        min_total: minimum total to include

    Returns:
        dict with count, total, average
    """
    valid = [o for o in orders if o["total"] >= min_total]
    if not valid:
        return {"count": 0, "total": 0, "average": 0}
    total = sum(o["total"] for o in valid)
    return {
        "count": len(valid),
        "total": round(total, 2),
        "average": round(total / len(valid), 2)
    }

OURS VERSION:
def summarize_orders(orders, min_total=0, include_status=False):
    """
    Summarize a list of order dicts.
    """
    if not isinstance(orders, list):
        raise ValueError("orders must be a list")
    valid = [o for o in orders if o.get("total", 0) >= min_total]
    if not valid:
        return {"count": 0, "total": 0, "average": 0}
    total = sum(o.get("total", 0) for o in valid)
    result = {
        "count": len(valid),
        "total": round(total, 2),
        "average": round(total / len(valid), 2)
    }
    if include_status:
        result["status_breakdown"] = _count_status(valid)
    return result

def _count_status(orders):
    breakdown = {}
    for order in orders:
        status = order.get("status", "unknown")
        breakdown[status] = breakdown.get(status, 0) + 1
    return breakdown

THEIRS VERSION:
from typing import Iterable, Dict, Any

def summarize_orders(items: Iterable[Dict[str, Any]], minimum: float = 10.0) -> Dict[str, Any]:
    """
    Summarize order totals with a has_data flag.
    """
    filtered = [o for o in items if float(o["total"]) > minimum]
    stats = {"count": len(filtered), "total": 0.0, "mean": 0.0, "has_data": False}
    if filtered:
        stats["total"] = round(sum(o["total"] for o in filtered), 2)
        stats["mean"] = round(stats["total"] / stats["count"], 2)
        stats["has_data"] = True
    return stats'''


def test_with_different_parameters():
    """Test with different max_length and temperature parameters"""

    test_cases = [
        {
            "name": "Default settings",
            "max_length": 512,
            "temperature": 0.7
        },
        {
            "name": "More tokens",
            "max_length": 1024,
            "temperature": 0.7
        },
        {
            "name": "Lower temperature (more deterministic)",
            "max_length": 512,
            "temperature": 0.3
        },
        {
            "name": "Higher temperature (more creative)",
            "max_length": 512,
            "temperature": 0.9
        }
    ]

    results = []

    for test_case in test_cases:
        print(f"\n🧪 Testing: {test_case['name']}")
        print(
            f"   max_length: {test_case['max_length']}, temperature: {test_case['temperature']}")

        # Note: You may need to modify your API to accept temperature parameter
        # If not, we'll just use max_length
        payload = {
            "conflict_text": CONFLICT_TEXT,
            "language": "python",
            "max_length": test_case["max_length"]
        }

        try:
            response = requests.post(
                f"{BASE_URL}resolve/",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                resolved = data.get('resolved', '')

                # Basic validation
                is_valid = validate_resolution(resolved)

                results.append({
                    "name": test_case["name"],
                    "status": "success",
                    "length": len(resolved),
                    "valid": is_valid,
                    "preview": resolved[:100] + "..." if len(resolved) > 100 else resolved
                })

                print(
                    f"   ✅ Success, Length: {len(resolved)}, Valid: {is_valid}")

                # Save individual result
                save_individual_result(test_case["name"], resolved, data)

            else:
                print(f"   ❌ Failed: {response.status_code}")
                results.append({
                    "name": test_case["name"],
                    "status": "failed",
                    "error": response.status_code
                })

        except Exception as e:
            print(f"   ❌ Error: {str(e)[:50]}")
            results.append({
                "name": test_case["name"],
                "status": "error",
                "error": str(e)[:50]
            })

    return results


def validate_resolution(code):
    """Validate if the resolved code is syntactically correct"""
    try:
        # Try to compile the code
        compile(code, '<string>', 'exec')

        # Check for obvious issues
        issues = []

        if '<<<<<<<' in code or '=======' in code or '>>>>>>>' in code:
            issues.append("Contains conflict markers")

        if 'data_list' in code and 'numbers' in code:
            issues.append("Mixed parameter references")

        # Check for undefined variables
        if 'data_list' in code and 'threshold' in code:
            # Check if they're used in a way that makes sense
            pass

        return len(issues) == 0

    except SyntaxError as e:
        print(f"   Syntax error: {str(e)[:50]}")
        return False
    except Exception as e:
        print(f"   Validation error: {str(e)[:50]}")
        return False


def save_individual_result(test_name, resolved_code, response_data):
    """Save individual test result"""
    try:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = test_name.lower().replace(" ", "_")
        filename = f"result_{safe_name}_{timestamp}.txt"

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"Test: {test_name}\n")
            f.write(f"Time: {datetime.datetime.now()}\n")
            f.write(f"Status: {response_data.get('status', 'N/A')}\n")
            f.write(
                f"Processing Time: {response_data.get('processing_time', 'N/A')}s\n\n")

            f.write("RESOLVED CODE:\n")
            f.write("="*60 + "\n")
            f.write(resolved_code + "\n")
            f.write("="*60 + "\n\n")

            # Try to execute and test
            f.write("EXECUTION TEST:\n")
            f.write("="*60 + "\n")
            try:
                exec_globals = {}
                exec(resolved_code, exec_globals)

                # Find function
                func = None
                for name in ['calculate_stats', 'calculate_statistics']:
                    if name in exec_globals:
                        func = exec_globals[name]
                        f.write(f"Found function: {name}\n")
                        break

                if func:
                    # Test 1
                    test_data = [5, 15, 25, 35, 45]
                    result = func(test_data)
                    f.write(f"Test with {test_data}:\n")
                    f.write(f"Result: {result}\n")

                    # Test 2 - empty or filtered out
                    # All below 10 if using min_value=10
                    test_data2 = [1, 2, 3, 4, 5]
                    result2 = func(test_data2)
                    f.write(f"\nTest with {test_data2}:\n")
                    f.write(f"Result: {result2}\n")

                    f.write("\n✅ Function executes successfully!\n")
                else:
                    f.write("❌ Could not find function\n")

            except Exception as e:
                f.write(f"❌ Execution failed: {str(e)}\n")

            f.write("="*60 + "\n")

        print(f"   💾 Saved to: {filename}")

    except Exception as e:
        print(f"   ⚠️ Could not save result: {str(e)}")


def main():
    print("🚀 TESTING MEDIUM-LEVEL CONFLICT WITH DIFFERENT PARAMETERS")
    print("="*80)

    # Check if server is running
    try:
        health_response = requests.get(f"{BASE_URL}health/", timeout=5)
        if health_response.status_code != 200:
            print("❌ Server not healthy. Please start Django server first.")
            print("   Run: python manage.py runserver")
            return
    except:
        print("❌ Cannot connect to server. Please start Django server first.")
        print("   Run: python manage.py runserver")
        return

    print("✅ Server is running and healthy")
    print(
        f"⏰ Starting tests at: {datetime.datetime.now().strftime('%H:%M:%S')}")
    print("-"*80)

    # Run tests with different parameters
    results = test_with_different_parameters()

    # Generate summary
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)

    for result in results:
        status_icon = "✅" if result["status"] == "success" else "❌"
        valid_icon = "✅" if result.get("valid", False) else "❌"
        print(f"{status_icon} {result['name']}:")
        print(f"   Status: {result['status']}")
        if result["status"] == "success":
            print(f"   Length: {result['length']} chars")
            print(f"   Valid: {valid_icon}")
            print(f"   Preview: {result['preview']}")
        print()

    print("="*80)
    print("✅ All tests completed!")
    print(f"⏰ Finished at: {datetime.datetime.now().strftime('%H:%M:%S')}")


if __name__ == "__main__":
    main()
