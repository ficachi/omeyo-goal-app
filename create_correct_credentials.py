import json
import base64

# Read the original JSON file (which has the correct private key)
with open('gen-lang-client-0204395031-dff004ed95b8.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Convert to JSON string
json_str = json.dumps(data, indent=2)

# Encode to base64
encoded = base64.b64encode(json_str.encode('utf-8')).decode('utf-8')

print('✅ Correct base64-encoded credentials:')
print(encoded) 