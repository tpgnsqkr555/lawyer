#!/usr/bin/env python3
"""
Quick test script to upload and process test_nexvira_complete.pdf
"""
import requests
import sys

# Upload file
with open('test_nexvira_complete.pdf', 'rb') as f:
    files = {'file': ('test_nexvira_complete.pdf', f, 'application/pdf')}
    data = {'request': 'stakeholders'}

    print("Uploading test_nexvira_complete.pdf...")
    print("=" * 60)

    response = requests.post(
        'http://localhost:8000/api/process',
        files=files,
        data=data,
        stream=True
    )

    # Stream and display the response
    for line in response.iter_lines():
        if line:
            line_str = line.decode('utf-8')
            if line_str.startswith('data: '):
                import json
                try:
                    data = json.loads(line_str[6:])
                    print(f"[{data['type'].upper()}] {data['message']}")
                except:
                    print(line_str)

print("\n" + "=" * 60)
print("Processing complete! Check backend/output/timeline.html")
