import torch
import os

print("CUDA available: " + str(torch.cuda.is_available()))
print("Device count: " + str(torch.cuda.device_count()))
if torch.cuda.is_available():
    print("Device name: " + torch.cuda.get_device_name(0))
else:
    print("Device name: N/A")

# Also check if NVIDIA_VISIBLE_DEVICES is set
print("NVIDIA_VISIBLE_DEVICES: " + os.getenv("NVIDIA_VISIBLE_DEVICES", "Not Set"))
