import requests
import time

def test_stream():
    url = "http://localhost:8000/v1/audio/stream"
    payload = {"text": "This is a test of the Screen Banter text to speech system. It should stream audio in real time."}
    
    print(f"Sending request to {url}...")
    start_time = time.time()
    
    try:
        with requests.post(url, json=payload, stream=True) as r:
            r.raise_for_status()
            print("Connected to stream. Receiving data...")
            
            chunk_count = 0
            total_bytes = 0
            first_chunk_time = None
            
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    if first_chunk_time is None:
                        first_chunk_time = time.time()
                        print(f"First chunk received in {first_chunk_time - start_time:.2f} seconds.")
                    
                    chunk_count += 1
                    total_bytes += len(chunk)
                    
            print(f"Stream finished. Received {chunk_count} chunks, {total_bytes} bytes total.")
            print(f"Total time: {time.time() - start_time:.2f} seconds.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_stream()
