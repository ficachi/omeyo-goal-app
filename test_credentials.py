import os
import base64
import json
from google.oauth2 import service_account
from google.auth.transport.requests import Request

def test_credentials():
    """Test the Google Cloud credentials decoding and authentication"""
    
    # Use the correct credentials from the original JSON file
    encoded_credentials = 'ewogICJ0eXBlIjogInNlcnZpY2VfYWNjb3VudCIsCiAgInByb2plY3RfaWQiOiAiZ2VuLWxhbmctY2xpZW50LTAyMDQzOTUwMzEiLAogICJwcml2YXRlX2tleV9pZCI6ICJkZmYwMDRlZDk1Yjg1YjE2NzA1MWU5NDk1NWFhY2UzOTQ0YThmNTRhIiwKICAicHJpdmF0ZV9rZXkiOiAiLS0tLS1CRUdJTiBQUklWQVRFIEtFWS0tLS0tXG5NSUlFdlFJQkFEQU5CZ2txaGtpRzl3MEJBUUVGQUFTQ0JLY3dnZ1NqQWdFQUFvSUJBUUMxYjdTb1BHTjhzWXIxXG5NQ0E1ZUlyQ1hublg2V081QXFQNW1ENE85V1pVNFFrSUZNTkV5SitzWGxBQnV1N1o0cW56ckNwNUlNbUpOOStwXG5JTnJjREZpOE81VFpMOTdnbEZhbnZpRFlzYk5ZUml5YytzRmk0ZkVnU0hHTXJTMGF6bFFwR1NxNGV2aXYrL0JzXG53TGlZNVQ4R0xJRjZBK2h1UDJIRmx2UXZmalh2VTdYOWZpYzhRa0xVUVpBRkxlakJIQ0VPQUdKMnh0eUF2Z3Y1XG5ERmYvWmNZeXpGQ2c4enFyV2N0Smk5cGROaUtaNmxpQWxzZmVidWtYNFlrdmJ4RHUvbEFxd090cHh0VGhxQ09qXG5FTERVeGhwSlNSd2llaTFyTnZwckxmREQ3TGdDVENzQlpYRHVCTmk1Sng5VmxXTG9yNXltcTkxOFRzdDZ1TlB4XG5ReENwb2R1TEFnTUJBQUVDZ2dFQU0wTWE2MWVZa2xBRlgwNFlKTFM2bTcwZXR0S3h3c0dNdThYNGJyaUdENkEvXG5NWUhRUS94ZEpOSEcwQjVWUXNsb1ZEa0dEUkFtOFBhUTRsT3VrbktJbGJKTjFXbFJrdWxHYklGcS9WNkR1Z0tsXG5zenFqN2dEQlpHb2pidWcwOExod0RlYVc2K1dPb3daUFFTTFlaUmFNVG4yL25VNUNXdmZjYzN1NWhUdW5HSFYyXG5SQmFFYXV6clVDWlZJb3VVUDJjdTFTNnhDWDRRdGdOMVJHUHNrYWJmSXZjYzFPNUFkVnBCeGhldnFSeDh4Y2paXG5OdWRzUFNtZ2FKbU95eWs4QzVEQ1RsTndZZ2pXNTcwbE9yWHVuajA4Lys5SFEyanZEcnNadFA2bFlibHdnT01QXG4rbDlhTHNadmpQamhHb0o3MEhPbERXUkp3Vk5lamVKa1Zqb25ubGJUM1FLQmdRRC8rZ3pzNW5JWmhJZ0xEOXZ2XG5BT3NueUpZVWkwV1FMTko1Nis1WS9rdlJIa3NWR3kyaWFXYXdpTzN6QmdXck9qTlllSmRaTnpaM2JEalZPSFNDXG5Gc2xtMW1pQzhubHUrNlhGRCtrMjMxQTN0QVp0angyTmoyRnBSOVRhQ3Z6UjdjVmFYRmJjUnFpWThXY0NzWHlWXG5XSzlpZ0RUUDBwNE8yNGxqZGlZRmRaWkdyd0tCZ1FDMWMrdzJiR0t4MHRLeTF3VEczY0JPY0NuVGVveWNqSm81XG5hVDJrcko4WHpodmFWZVplb2FkYVVUZmxSUUc1VDVYeGYwUytrOGlmVWJsN1VaSHFzbk94NFpBR2MxRklxZEczXG55VEJnSDUzUFVseW1nWDhjMVFYalVNbWR3OHlzMU1hN2NibW1Xd1Zyb3RTVVdjYlR1c1ZKK1JsT3Q1cWhxSmdrXG56L0NocHcydjVRS0JnUUNBM1lCZVR4RkgrV21Ic0I4M3JrMjBSSTRSbjUrUW1wQUhZeGdsNHplRittc3dIL09VXG5YTjJlcUFDcXBQQjdxQndyUU9Kb3Zwd0QrUTZQZ1JGZVlGeGFFanloRjdLOGhhR0ptSjMreXVPV2QySDVDK0NEXG40SmZZcVpubGZ6eVI3dEs0ejkzR25TZkpmMVl0aSs2OVBOMW1pRWFPRFdrVzc3eTF2c2diWFh3ZTd3S0JnQ1ZhXG4vQ0lvSmhsZHdhcTN3Vy8vYnZ1Mjg2VnA4VkM1VVhiSVI3eURIUzJWYlA2QitLODZzRzFUa3lKTUZwTEQ0NmFZXG5BTnNMS1o1REFPQjJab2ZldlJxOXlSeksyTTBReVBBQkowaGl1ZVpZbW1KYy9vSTlDTDFIZ0hwT09QREx6UzRCXG50NnFieW4zaVE4bFd3aXdNbzFrYlF5NkZkZndaN1ZpR3hvOUJDUHhSQW9HQUhsKy9iODhETXJ4N3ZOTWthOWF0XG5LcWIxUXp3a1NkclhlaGxMWDhYSkhnTFdMdzF6R1BJczJrVFAzNGhnMDd1K0hUei9rNU9kMlM2eFh4OGNlQjFxXG5PeENMaXFZVzZrVkhZOXZZa3BsaHF1TWpTMjJvbXloYnhQR01IZmRXemFkUXQ2bWluaTdocFpZNk01SjExb29EXG5MQ1dsb01KUFVwNEpiZFNZOExmVmdaTT1cbi0tLS0tRU5EIFBSSVZBVEUgS0VZLS0tLS1cbiIsCiAgImNsaWVudF9lbWFpbCI6ICJvbWV5by1iYWNrZW5kQGdlbi1sYW5nLWNsaWVudC0wMjA0Mzk1MDMxLmlhbS5nc2VydmljZWFjY291bnQuY29tIiwKICAiY2xpZW50X2lkIjogIjEwNjUzNTIyNTgyNDg3MDEyMDM2NyIsCiAgImF1dGhfdXJpIjogImh0dHBzOi8vYWNjb3VudHMuZ29vZ2xlLmNvbS9vL29hdXRoMi9hdXRoIiwKICAidG9rZW5fdXJpIjogImh0dHBzOi8vb2F1dGgyLmdvb2dsZWFwaXMuY29tL3Rva2VuIiwKICAiYXV0aF9wcm92aWRlcl94NTA5X2NlcnRfdXJsIjogImh0dHBzOi8vd3d3Lmdvb2dsZWFwaXMuY29tL29hdXRoMi92MS9jZXJ0cyIsCiAgImNsaWVudF94NTA5X2NlcnRfdXJsIjogImh0dHBzOi8vd3d3Lmdvb2dsZWFwaXMuY29tL3JvYm90L3YxL21ldGFkYXRhL3g1MDkvb21leW8tYmFja2VuZCU0MGdlbi1sYW5nLWNsaWVudC0wMjA0Mzk1MDMxLmlhbS5nc2VydmljZWFjY291bnQuY29tIiwKICAidW5pdmVyc2VfZG9tYWluIjogImdvb2dsZWFwaXMuY29tIgp9'
    
    try:
        print("🔍 Testing Google Cloud credentials decoding...")
        
        # Decode the base64 string
        decoded_credentials = base64.b64decode(encoded_credentials).decode('utf-8')
        print("✅ Base64 decoding successful")
        
        # Parse the JSON
        credentials_dict = json.loads(decoded_credentials)
        print("✅ JSON parsing successful")
        print(f"📋 Service account type: {credentials_dict.get('type')}")
        print(f"📋 Project ID: {credentials_dict.get('project_id')}")
        print(f"📋 Client email: {credentials_dict.get('client_email')}")
        
        # Create a temporary file for the credentials
        import tempfile
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.json', delete=False) as temp_file:
            temp_file.write(decoded_credentials.encode('utf-8'))
            temp_file_path = temp_file.name
        
        # Debug: print the contents of the temp file
        with open(temp_file_path, 'r', encoding='utf-8') as f:
            print("\n=== TEMP FILE CONTENTS ===")
            print(f.read())
            print("=== END TEMP FILE CONTENTS ===\n")
        
        # Create credentials from file
        credentials = service_account.Credentials.from_service_account_file(
            temp_file_path,
            scopes=['https://www.googleapis.com/auth/cloud-platform']
        )
        credentials.refresh(Request())
        access_token = credentials.token
        print("✅ Access token obtained successfully")
        print(f"🔑 Token preview: {access_token[:20]}...")
        
        print("\n🎉 All tests passed! The credentials are working correctly.")
        
        # Clean up the temporary file
        import os
        os.unlink(temp_file_path)
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_credentials() 