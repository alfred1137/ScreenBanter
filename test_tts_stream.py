import requests
import sys

def test_tts_stream():
    url = 'http://127.0.0.1:8000/v1/audio/stream'
    payload = {'text': 'Hello, this is a test of the VibeVoice integration. The dedicated GPU should be working now.'}
    
    print(f"Sending request to {url}...")
    try:
        r = requests.post(url, json=payload, stream=True, timeout=30)
        print(f"Status Code: {r.status_code}")
        print(f"Headers: {r.headers}")
        
        if r.status_code != 200:
            print(f"Error: {r.text}")
            return

        print("Receiving audio stream...")
        chunk_count = 0
        total_bytes = 0
        for chunk in r.iter_content(chunk_size=4096):
            if chunk:
                chunk_count += 1
                total_bytes += len(chunk)
                if chunk_count % 10 == 0:
                    print(f"Received {chunk_count} chunks, total {total_bytes} bytes...")
                if chunk_count >= 50:
                    print("Received enough chunks for verification.")
                    break
        
        print(f"Successfully received {chunk_count} chunks ({total_bytes} bytes).")
        print("TTS Stream verification SUCCESSFUL.")
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    test_tts_stream()
