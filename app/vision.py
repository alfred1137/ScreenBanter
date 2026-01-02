# app/vision.py
import os
from google import genai
from PIL import Image
import numpy as np

class VisionEngine:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("GEMINI_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_KEY not found in environment or provided.")
        
        self.client = genai.Client(api_key=self.api_key)
        self.model_name = 'gemini-2.0-flash-lite'

    def extract_text(self, frame_np):
        """
        Sends the screen frame to Gemini for OCR.
        """
        # Convert numpy array (from DXcam) to PIL Image if needed by genai client
        # or handle the format expected by the SDK.
        # Most genai vision models accept PIL images or byte arrays.
        img = Image.fromarray(frame_np)
        
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=['Extract text precisely. Text only. If no text is visible, return an empty string.', img]
            )
            return response.text.strip()
        except Exception as e:
            print(f"Gemini API error: {e}")
            return ""
