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
        self.model_name = 'models/gemini-flash-lite-latest'

    def extract_text(self, frame_or_frames):
        """
        Sends the screen frame(s) to Gemini for OCR.
        Args:
            frame_or_frames: A numpy array (single frame) or a list of numpy arrays.
        """
        if isinstance(frame_or_frames, list):
            images = [Image.fromarray(f) for f in frame_or_frames]
            prompt = """Extract all text from these images in the order they are presented. 
Join fragmented lines into cohesive passages and remove any duplicated content. Maintain paragraph breaks as they appear visually. 
Output should be plain text only. 
If no text is visible in an image, return exactly `no text identified`."""
        else:
            images = [Image.fromarray(frame_or_frames)]
            prompt = """Extract all text from this image precisely. 
Join fragmented lines into cohesive passages and maintain paragraph breaks as they appear visually. 
Output should be plain text only. 
If no text is visible, return exactly `no text identified`."""
        
        try:
            # Prepare contents: prompt followed by images
            contents = [prompt] + images
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=contents
            )
            return response.text.strip()
        except Exception as e:
            print(f"Gemini API error: {e}")
            return ""
