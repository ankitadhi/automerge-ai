# test_api.py - Updated for AutoMerge AI CodeT5 Model
import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000/predictor/"


def print_section(title):
    """Helper function to print formatted sections"""
    print("\n" + "="*60)
    print(title)
    print("="*60)


def test_health_check():
    """Test if the API is running and model is loaded"""
    print_section("1. Testing Health Check Endpoint")

    try:
        response = requests.get(f"{BASE_URL}health/", timeout=10)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {data.get('status', 'N/A')}")
            print(f"📦 Model: {data.get('model_name', 'N/A')}")
            print(f"⚙️ Framework: {data.get('framework', 'N/A')}")
            print(
                f"🌐 Language Support: {', '.join(data.get('language_support', []))}")

            if 'test_resolution' in data:
                print(f"\n📝 Test Resolution Preview:")
                print("-"*40)
                print(data['test_resolution'])
                print("-"*40)
        elif response.status_code == 503:
            print(
                f"❌ Service Unhealthy: {response.json().get('error', 'Unknown error')}")
        else:
            print(f"❌ Error: {response.text[:200]}...")

    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Could not connect to server. Is the Django server running?")
        print("   Run this command first: python manage.py runserver")
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")


def test_single_merge_resolution(language="python"):
    """Test resolving a single merge conflict"""
    print_section(f"2. Testing Single Merge Resolution ({language.upper()})")

    # Test cases for different languages
    test_cases = {
        "python": {
            "conflict_text": """<<<<<<< HEAD
def calculate_sum(a, b):
    return a + b
=======
def calculate_sum(x, y):
    # Add two numbers
    result = x + y
    return result
>>>>>>> feature-branch""",
            "description": "Python function with variable renaming and comments"
        },
        "javascript": {
            "conflict_text": """<<<<<<< HEAD
function multiply(x, y) {
    return x * y;
}
=======
function multiply(a, b) {
    // Calculate product
    return a * b;
}
>>>>>>> feature-branch""",
            "description": "JavaScript function with variable renaming and comments"
        },
        "java": {
            "conflict_text": """<<<<<<< HEAD
public class Calculator {
    public int add(int x, int y) {
        return x + y;
    }
}
=======
public class Calculator {
    public int add(int a, int b) {
        // Add two integers
        return a + b;
    }
}
>>>>>>> feature-branch""",
            "description": "Java class with method and comments"
        }
    }

    if language not in test_cases:
        print(f"❌ No test case for language: {language}")
        return

    test_case = test_cases[language]
    conflict_text = test_case["conflict_text"]

    payload = {
        "conflict_text": conflict_text,
        "language": language,
        "max_length": 256
    }

    print(f"📄 Test Description: {test_case['description']}")
    print(f"\n📤 Sending conflict ({len(conflict_text)} chars)...")

    try:
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}resolve/",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        elapsed = time.time() - start_time

        print(f"⏱️ Response Time: {elapsed:.2f} seconds")
        print(f"📊 Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Success! Status: {data.get('status', 'N/A')}")
            print(f"🌐 Language: {data.get('language', 'N/A')}")
            print(f"⏰ Processing Time: {data.get('processing_time', 'N/A')}s")

            print(f"\n📥 Original Conflict Preview:")
            print("-"*40)
            print(
                conflict_text[:200] + "..." if len(conflict_text) > 200 else conflict_text)
            print("-"*40)

            print(f"\n📤 Resolved Code:")
            print("-"*40)
            resolved = data.get('resolved', 'No output')
            print(resolved)
            print("-"*40)

            # Basic validation
            if resolved:
                print(f"📏 Resolution Length: {len(resolved)} characters")
                if "<<<<<<<" not in resolved and "=======" not in resolved and ">>>>>>>" not in resolved:
                    print("✅ Validation: No conflict markers in resolved code")
                else:
                    print("⚠️ Warning: Conflict markers still present in resolved code")

        elif response.status_code == 400:
            print(f"\n❌ Validation Error:")
            print(json.dumps(response.json(), indent=2))
        elif response.status_code == 500:
            print(f"\n❌ Server Error:")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"\n❌ Unexpected Status: {response.status_code}")
            print(f"Response: {response.text[:200]}...")

    except Exception as e:
        print(f"❌ ERROR: {str(e)}")


def test_batch_resolution():
    """Test batch processing of multiple conflicts"""
    print_section("3. Testing Batch Resolution")

    conflicts = [
        # Python conflict
        """<<<<<<< HEAD
print('Hello from main branch')
=======
print('Hello from feature branch')
>>>>>>> feature""",
        # JavaScript conflict
        """<<<<<<< HEAD
function oldMethod() {
    return true;
}
=======
function newMethod() {
    console.log('Updated');
    return false;
}
>>>>>>> update""",
        # Python with TODO
        """<<<<<<< HEAD
# TODO: Implement this
pass
=======
def implemented():
    return "Done"
>>>>>>> implementation""",
        # Simple variable conflict
        """<<<<<<< HEAD
x = 10
=======
y = 20
>>>>>>> branch"""
    ]

    payload = {
        "conflicts": conflicts,
        "language": "python",  # Can specify language for all
        "max_length": 200
    }

    print(
        f"📦 Sending {len(conflicts)} merge conflicts for batch processing...")

    try:
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}resolve/batch/",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        elapsed = time.time() - start_time

        print(f"⏱️ Batch Response Time: {elapsed:.2f} seconds")
        print(f"📊 Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Batch processed successfully!")
            print(f"📊 Statistics:")
            print(f"   • Total conflicts: {data.get('total', 0)}")
            print(f"   • Successful: {data.get('successful', 0)}")
            print(f"   • Failed: {data.get('failed', 0)}")
            print(f"   • Language: {data.get('language', 'N/A')}")
            print(f"   • Total time: {data.get('total_time', 0):.2f}s")

            # Show first result details
            if data.get('results') and len(data['results']) > 0:
                first_result = data['results'][0]
                print(f"\n📝 First result preview:")
                print(f"   • Status: {first_result.get('status')}")
                if first_result.get('status') == 'success':
                    resolved = first_result.get('resolved', '')
                    print(f"   • Resolution length: {len(resolved)} chars")
                    if len(resolved) > 100:
                        print(f"   • Preview: {resolved[:100]}...")
                    else:
                        print(f"   • Resolution: {resolved}")

        elif response.status_code == 400:
            print(f"\n❌ Validation Error:")
            print(json.dumps(response.json(), indent=2))
        else:
            print(
                f"\n❌ Batch request failed with status {response.status_code}")
            print("Response:", json.dumps(response.json(), indent=2))

    except Exception as e:
        print(f"❌ ERROR: {str(e)}")


def test_invalid_input():
    """Test error handling with invalid input"""
    print_section("4. Testing Error Handling")

    test_cases = [
        {
            "name": "Empty conflict text",
            "payload": {
                "conflict_text": "",
                "language": "python",
                "max_length": 100
            }
        },
        {
            "name": "Missing conflict markers",
            "payload": {
                "conflict_text": "This is not a git conflict",
                "language": "python",
                "max_length": 100
            }
        },
        {
            "name": "Invalid language",
            "payload": {
                "conflict_text": "<<<<<<<\ntest\n=======\ntest\n>>>>>>>",
                "language": "invalid_lang",
                "max_length": 100
            }
        },
        {
            "name": "Very large max_length",
            "payload": {
                "conflict_text": "<<<<<<<\ntest\n=======\ntest\n>>>>>>>",
                "language": "python",
                "max_length": 10000  # Too large
            }
        }
    ]

    for test_case in test_cases:
        print(f"\n🔄 Testing: {test_case['name']}")
        print(f"   Payload: {json.dumps(test_case['payload'], indent=4)}")

        try:
            response = requests.post(
                f"{BASE_URL}resolve/",
                json=test_case['payload'],
                timeout=10
            )
            print(f"   Status Code: {response.status_code}")

            if response.status_code == 400:
                print(f"   ✅ Expected validation error")
                errors = response.json().get('details', {})
                if errors:
                    print(f"   Error details: {json.dumps(errors, indent=4)}")
            elif response.status_code == 500:
                print(
                    f"   ⚠️ Server error: {response.json().get('message', 'Unknown')}")
            else:
                print(f"   ❓ Unexpected success: {response.status_code}")

        except Exception as e:
            print(f"   ❌ Request failed: {str(e)}")


def test_language_support():
    """Test the model with different programming languages"""
    print_section("5. Testing Multiple Language Support")

    languages = ["python", "javascript", "java"]

    for lang in languages:
        print(f"\n🔤 Testing {lang.upper()}...")
        test_single_merge_resolution(lang)
        time.sleep(1)  # Brief pause between requests


def test_performance():
    """Test API performance with multiple requests"""
    print_section("6. Performance Test")

    test_conflict = "<<<<<<<\nx = 1\n=======\nx = 2\n>>>>>>>"

    num_requests = 5
    print(f"📊 Running {num_requests} consecutive requests...")

    times = []

    for i in range(num_requests):
        payload = {
            "conflict_text": test_conflict,
            "language": "python",
            "max_length": 100
        }

        try:
            start = time.time()
            response = requests.post(
                f"{BASE_URL}resolve/",
                json=payload,
                timeout=30
            )
            elapsed = time.time() - start

            times.append(elapsed)

            status = "✅" if response.status_code == 200 else "❌"
            print(f"   Request {i+1}: {status} {elapsed:.2f}s")

            if response.status_code != 200:
                print(f"      Error: {response.text[:100]}...")

        except Exception as e:
            print(f"   Request {i+1}: ❌ Failed - {str(e)}")

    if times:
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)

        print(f"\n📈 Performance Summary:")
        print(f"   • Average: {avg_time:.2f}s")
        print(f"   • Minimum: {min_time:.2f}s")
        print(f"   • Maximum: {max_time:.2f}s")
        print(f"   • Total: {sum(times):.2f}s for {len(times)} requests")


def run_comprehensive_test():
    """Run all tests in sequence"""
    print("\n" + "🚀"*20)
    print("STARTING COMPREHENSIVE API TESTS")
    print("FOR AutoMerge AI CodeT5 Model")
    print("🚀"*20 + "\n")

    # Wait for server to be ready
    print("⏳ Waiting 3 seconds for server stability...")
    time.sleep(3)

    try:
        # Test 1: Health check
        test_health_check()

        # Quick check if health passed
        health_response = requests.get(f"{BASE_URL}health/", timeout=5)
        if health_response.status_code != 200:
            print("\n⚠️ Skipping further tests - server not healthy")
            return

        # Test 2: Single resolution (default Python)
        test_single_merge_resolution("python")

        # Test 3: Language support
        test_language_support()

        # Test 4: Batch resolution
        test_batch_resolution()

        # Test 5: Invalid input handling
        test_invalid_input()

        # Test 6: Performance
        test_performance()

        print("\n" + "="*60)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY")
        print("="*60)

    except Exception as e:
        print(f"\n❌ Test suite interrupted: {str(e)}")


def run_quick_test():
    """Run a quick smoke test"""
    print("\n⚡ QUICK SMOKE TEST ⚡")
    test_health_check()

    # Test a simple conflict
    print("\n" + "="*60)
    print("Quick Resolution Test")
    print("="*60)

    payload = {
        "conflict_text": "<<<<<<<\nprint('hello')\n=======\nprint('world')\n>>>>>>>",
        "language": "python",
        "max_length": 50
    }

    try:
        response = requests.post(
            f"{BASE_URL}resolve/", json=payload, timeout=15)
        if response.status_code == 200:
            print(f"✅ Quick test passed!")
            data = response.json()
            print(f"   Resolved: {data.get('resolved', 'N/A')}")
        else:
            print(f"❌ Quick test failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Quick test error: {str(e)}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Test AutoMerge AI API')
    parser.add_argument('--quick', action='store_true',
                        help='Run quick smoke test only')
    parser.add_argument('--url', default=BASE_URL,
                        help='Base URL for API (default: http://localhost:8000/predictor/)')

    args = parser.parse_args()

    # Update base URL if provided
    if args.url != BASE_URL:
        BASE_URL = args.url.rstrip('/') + '/'

    if args.quick:
        run_quick_test()
    else:
        run_comprehensive_test()
