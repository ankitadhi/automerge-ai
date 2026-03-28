import requests
import time
import json
import sys
import os
from datetime import datetime


class Tee:
    """Class to write to both console and file simultaneously"""

    def __init__(self, *files):
        self.files = files

    def write(self, obj):
        for f in self.files:
            f.write(obj)
            f.flush()

    def flush(self):
        for f in self.files:
            f.flush()


BASE_URL = "http://localhost:8000/predictor/"


def print_section(title):
    print("\n" + "="*60)
    print(title)
    print("="*60)


# -------------------------------
# ✅ HEALTH CHECK
# -------------------------------
def test_health_check():
    print_section("1. Health Check")

    try:
        response = requests.get(f"{BASE_URL}health/", timeout=10)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {data.get('status')}")
            print(f"📦 Model: {data.get('model_name')}")
        else:
            print(f"❌ Error: {response.text}")

    except Exception as e:
        print(f"❌ ERROR: {str(e)}")


# -------------------------------
# ✅ SINGLE TEST (UPDATED LANGS)
# -------------------------------
def test_single_merge_resolution(language="javascript"):
    print_section(f"2. Single Merge Test ({language.upper()})")

    test_cases = {
        "javascript": {
            "conflict_text": """<<<<<<< ours
function authenticateUser(user) {
    if (!user || !user.email) {
        throw new Error("Invalid user");
    }

    const token = generateToken(user);
    console.log("User authenticated:", user.id);

    return { token, status: "success" };
}
||||||| base
function authenticateUser(user) {
    const token = generateToken(user);
    return { token };
}
=======
async function authenticateUser(user) {
    const token = await authService.login(user.email, user.password);

    return {
        token,
        status: "authenticated",
        timestamp: Date.now()
    };
}
>>>>>>> theirs"""
        },

        "java": {
            "conflict_text": """<<<<<<< ours
            public OrderResponse processOrder(Order order) {
                if (order == null | | order.getItems().isEmpty()) {
                    throw new IllegalArgumentException("Invalid order");
                }

                double total = order.getItems()
                .stream()
                .mapToDouble(item -> item.getPrice())
                .sum();

                double discount = order.isPremium() ? total * 0.1: 0;

                logger.info("Processing order: {}", order.getId());

                return new OrderResponse(order.getId(), total - discount, "PROCESSED");
            }
            ||||||| base
            public OrderResponse processOrder(Order order) {
                double total = order.getItems()
                .stream()
                .mapToDouble(item -> item.getPrice())
                .sum();

                return new OrderResponse(order.getId(), total, "PROCESSED");
            }
            =======
            public CompletableFuture < OrderResponse > processOrder(Order order) {
                double total = order.getItems()
                .stream()
                .mapToDouble(item -> item.getPrice() * item.getQuantity())
                .sum();

                return orderRepository.save(order)
                .thenCompose(saved -> notificationService.notify(order.getUserId()))
                .thenApply(v -> new OrderResponse(
                    order.getId(),
                    total,
                    "COMPLETED",
                    System.currentTimeMillis()
                ));
            }
            >>>>>>> theirs
            """
        },

        "csharp": {
            "conflict_text": """<<<<<<< /mnt/batch/tasks/workitems/adfv2-General_1/job-1/cff1c5af-5406-4892-ad0b-2806059265ab/wd/.temp/athenacommon/3460b304-87ba-4618-93e8-71a5befea33f.cs
||||||| /mnt/batch/tasks/workitems/adfv2-General_1/job-1/cff1c5af-5406-4892-ad0b-2806059265ab/wd/.temp/athenacommon/c4d8146b-9287-4206-b4da-5a505b50fe76.cs
            // txtBoundaries
            // 
            this.txtBoundaries.Location = new System.Drawing.Point(85, 90);
            this.txtBoundaries.MaxVal = 2147483647;
            this.txtBoundaries.Name = "txtBoundaries";
            this.txtBoundaries.Separator = ';';
            this.txtBoundaries.Size = new System.Drawing.Size(156, 20);
            this.txtBoundaries.SpacesAroundSeparator = true;
            this.txtBoundaries.TabIndex = 4;
            this.txtBoundaries.Text = "0 ; 0";
            this.txtBoundaries.X = 0;
            this.txtBoundaries.Y = 0;
            // 
=======
            // txtBoundaries
            // 
            this.txtBoundaries.Location = new System.Drawing.Point(85, 90);
            this.txtBoundaries.MaxVal = 2147483647;
            this.txtBoundaries.Name = "txtBoundaries";
            this.txtBoundaries.Separator = ';';
            this.txtBoundaries.Size = new System.Drawing.Size(156, 20);
            this.txtBoundaries.SpacesAroundSeparator = true;
            this.txtBoundaries.TabIndex = 3;
            this.txtBoundaries.Text = "0 ; 0";
            this.txtBoundaries.X = 0;
            this.txtBoundaries.Y = 0;
>>>>>>> /mnt/batch/tasks/workitems/adfv2-General_1/job-1/cff1c5af-5406-4892-ad0b-2806059265ab/wd/.temp/athenacommon/3460b304-87ba-4618-93e8-71a5befea33f.cs
"""
        }
    }

    payload = {
        "conflict_text": test_cases[language]["conflict_text"],
        "language": language,
        "max_length": 256
    }

    try:
        response = requests.post(
            f"{BASE_URL}resolve/", json=payload, timeout=30)

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("\n✅ RESOLVED:")
            print("-"*40)
            print(data.get("resolved"))
            print("-"*40)
        else:
            print(f"❌ Error: {response.text}")

    except Exception as e:
        print(f"❌ ERROR: {str(e)}")


# -------------------------------
# ✅ BATCH TEST
# -------------------------------
def test_batch_resolution():
    print_section("3. Batch Test")

    conflicts = [
        # JS
        """<<<<<<< HEAD
const x = 10;
=======
const y = 20;
>>>>>>> branch""",

        # Java
        """<<<<<<< HEAD
return true;
=======
return false;
>>>>>>> feature""",

        # C#
        """<<<<<<< HEAD
int a = 5;
=======
int b = 10;
>>>>>>> update"""
    ]

    payload = {
        "conflicts": conflicts,
        "language": "javascript",
        "max_length": 200
    }

    try:
        response = requests.post(
            f"{BASE_URL}resolve/batch/",
            json=payload,
            timeout=60
        )

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success: {data.get('successful')} / {data.get('total')}")
        else:
            print(f"❌ Error: {response.text}")

    except Exception as e:
        print(f"❌ ERROR: {str(e)}")


# -------------------------------
# ✅ LANGUAGE SUPPORT TEST
# -------------------------------
def test_language_support():
    print_section("4. Language Support")

    for lang in ["javascript", "java", "csharp"]:
        print(f"\n🔤 Testing {lang.upper()}")
        test_single_merge_resolution(lang)
        time.sleep(1)


# -------------------------------
# ✅ PERFORMANCE TEST
# -------------------------------
def test_performance():
    print_section("5. Performance Test")

    conflict = "<<<<<<<\nint x = 1;\n=======\nint x = 2;\n>>>>>>>"

    for i in range(5):
        payload = {
            "conflict_text": conflict,
            "language": "csharp",
            "max_length": 100
        }

        start = time.time()
        response = requests.post(f"{BASE_URL}resolve/", json=payload)
        elapsed = time.time() - start

        print(f"Request {i+1}: {elapsed:.2f}s")


# -------------------------------
# ✅ MAIN RUNNER
# -------------------------------
def run_tests():
    print("\n🚀 AutoMerge AI Test Suite\n")

    test_health_check()

    if requests.get(f"{BASE_URL}health/").status_code != 200:
        print("❌ Server not ready")
        return

    test_single_merge_resolution("javascript")
    test_language_support()
    test_batch_resolution()
    test_performance()

    print("\n✅ ALL TESTS DONE")


# -------------------------------
# ✅ ENTRY POINT
# -------------------------------
if __name__ == "__main__":
    run_tests()
