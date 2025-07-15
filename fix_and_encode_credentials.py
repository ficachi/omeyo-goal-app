import json
import base64

# Load the original JSON file
with open('gen-lang-client-0204395031-dff004ed95b8.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Fix the typo in the private key
if 'private_key' in data:
    data['private_key'] = data['private_key'].replace('-----END PRIVAVE KEY-----', '-----END PRIVATE KEY-----')

# Save the fixed JSON to a string
fixed_json_str = json.dumps(data, indent=2)

# Encode to base64
encoded = base64.b64encode(fixed_json_str.encode('utf-8')).decode('utf-8')

print('✅ Fixed and base64-encoded credentials:')
print(encoded) 