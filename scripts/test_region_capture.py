import os
import sys
import numpy as np

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.capture import ScreenCapturer
from app.settings import settings_manager

def test_region_capture():
    print("--- Testing Region Capture Logic ---")
    
    # 1. Setup Settings (Mocking user action)
    test_region = [0, 0, 100, 100] # Left, Top, Right, Bottom
    print(f"Setting test region: {test_region}")
    
    # We don't want to permanently overwrite user settings, so we'll just test the capturer directly first
    # then test the settings integration logic if possible, or just revert settings.
    
    capturer = ScreenCapturer()
    
    # Test direct capture
    print("Attempting capture(region=test_region)...")
    frame = capturer.capture(region=tuple(test_region))
    
    if frame is None:
        print("FAIL: Capture returned None. (Is a monitor attached?)")
        return

    print(f"Frame shape: {frame.shape}")
    
    # Expected shape: (Height, Width, Channels) -> (100, 100, 3)
    expected_shape = (100, 100, 3)
    if frame.shape == expected_shape:
        print("SUCCESS: Frame shape matches region dimensions.")
    else:
        print(f"FAIL: Frame shape {frame.shape} does not match expected {expected_shape}")

if __name__ == "__main__":
    test_region_capture()
