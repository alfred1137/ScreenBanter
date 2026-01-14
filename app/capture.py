# app/capture.py
import dxcam
import numpy as np

class ScreenCapturer:
    def __init__(self):
        print("Initializing DXcam...")
        self.camera = dxcam.create()
        
    def capture(self, region=None):
        """
        Captures the current screen frame as a numpy array.
        Args:
            region: Optional tuple (left, top, right, bottom)
        Returns None if capture fails.
        """
        frame = self.camera.grab(region=region)
        if frame is not None:
            # DXcam returns RGB by default
            return frame
        return None

    def __del__(self):
        if hasattr(self, 'camera'):
            self.camera.stop()
