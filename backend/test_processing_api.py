"""
Example usage of the Processing API endpoints.
Run this after starting the backend service.
"""
import requests
import time
import json
import base64


BASE_URL = "http://localhost:8080"


def create_sample_pdf_base64():
    """Create a minimal valid PDF content encoded as base64."""
    # Minimal PDF structure
    pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/Resources <<
/Font <<
/F1 <<
/Type /Font
/Subtype /Type1
/BaseFont /Helvetica
>>
>>
>>
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj
4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
100 700 Td
(Sample PDF) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
0000000317 00000 n
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
409
%%EOF
"""
    return base64.b64encode(pdf_content).decode('utf-8')


def submit_processing_job():
    """Submit a new processing job with sample items."""
    print("=" * 60)
    print("Submitting Processing Job")
    print("=" * 60)

    # Create a sample base64-encoded PDF
    pdf_base64 = create_sample_pdf_base64()

    payload = {
        "items": [
            {
                "type": "text",
                "content": "Analyze this customer feedback about our product",
                "wage": 50.00
            },
            {
                "type": "file",
                "content": pdf_base64,
                "wage": 75.50
            },
            {
                "type": "link",
                "content": "https://example.com/market-research",
                "wage": 100.00
            }
        ]
    }

    print(f"\nRequest Payload (file content truncated for display):")
    display_payload = payload.copy()
    display_payload['items'] = [
        item if item['type'] != 'file' else {**item, 'content': item['content'][:50] + '...'}
        for item in payload['items']
    ]
    print(json.dumps(display_payload, indent=2))

    response = requests.post(
        f"{BASE_URL}/api/processing/submit",
        json=payload
    )

    print(f"\nResponse Status: {response.status_code}")
    print(f"Response Body:")
    print(json.dumps(response.json(), indent=2))

    if response.status_code == 201:
        return response.json()
    else:
        print("\nFailed to create job!")
        return None


def check_status(job_uuid):
    """Check the status of a processing job."""
    print("\n" + "=" * 60)
    print(f"Checking Job Status: {job_uuid}")
    print("=" * 60)

    response = requests.get(
        f"{BASE_URL}/api/processing/status/{job_uuid}"
    )

    print(f"\nResponse Status: {response.status_code}")

    if response.status_code == 200:
        status_data = response.json()
        print(f"\nJob Status: {status_data['status']}")
        print(f"Total Items: {status_data['total_items']}")
        print(f"Completed Items: {status_data['completed_items']}")
        print(f"Failed Items: {status_data['failed_items']}")
        print(f"\nCreated At: {status_data['created_at']}")
        print(f"Updated At: {status_data['updated_at']}")

        print(f"\nItems Details:")
        for item in status_data['items']:
            print(f"  - Item #{item['id']}: {item['type']} | Status: {item['status']} | Wage: ${item['wage']}")

        return status_data
    else:
        print(f"Error: {response.json()}")
        return None


def test_invalid_requests():
    """Test various invalid request scenarios."""
    print("\n" + "=" * 60)
    print("Testing Invalid Requests")
    print("=" * 60)

    test_cases = [
        {
            "name": "Empty items list",
            "payload": {"items": []}
        },
        {
            "name": "Missing items field",
            "payload": {}
        },
        {
            "name": "Invalid type",
            "payload": {
                "items": [{"type": "invalid", "content": "test", "wage": 10}]
            }
        },
        {
            "name": "Missing content",
            "payload": {
                "items": [{"type": "text", "wage": 10}]
            }
        },
        {
            "name": "Empty content",
            "payload": {
                "items": [{"type": "text", "content": "", "wage": 10}]
            }
        },
        {
            "name": "Invalid base64 for file type",
            "payload": {
                "items": [{"type": "file", "content": "not-valid-base64!!!", "wage": 10}]
            }
        },
        {
            "name": "Invalid URL for link type",
            "payload": {
                "items": [{"type": "link", "content": "not-a-url", "wage": 10}]
            }
        },
        {
            "name": "Link without http/https",
            "payload": {
                "items": [{"type": "link", "content": "example.com", "wage": 10}]
            }
        }
    ]

    for test_case in test_cases:
        print(f"\nTest: {test_case['name']}")
        response = requests.post(
            f"{BASE_URL}/api/processing/submit",
            json=test_case['payload']
        )
        print(f"  Status: {response.status_code}")
        print(f"  Response: {response.json()}")


def main():
    """Run the complete test workflow."""
    print("\n" + "🚀 Processing API Test Suite" + "\n")

    # Test 1: Submit a valid job
    job_response = submit_processing_job()

    if not job_response:
        print("\n❌ Failed to create job. Exiting...")
        return

    job_uuid = job_response['job_uuid']

    # Test 2: Check status immediately
    time.sleep(1)
    check_status(job_uuid)

    # Test 3: Check status of non-existent job
    print("\n" + "=" * 60)
    print("Testing Non-Existent Job")
    print("=" * 60)
    fake_uuid = "00000000-0000-0000-0000-000000000000"
    response = requests.get(f"{BASE_URL}/api/processing/status/{fake_uuid}")
    print(f"Response Status: {response.status_code}")
    print(f"Response: {response.json()}")

    # Test 4: Invalid requests
    test_invalid_requests()

    print("\n" + "=" * 60)
    print("✅ All Tests Completed!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the backend service.")
        print("Make sure the backend is running on http://localhost:8080")
    except Exception as e:
        print(f"❌ Error: {e}")

