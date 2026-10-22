import importlib.metadata as md
import sys
from pathlib import Path

# Resolve project imports when this script is run directly from any directory.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import torch
import stable_worldmodel as swm
import stable_pretraining as spt
import train
import eval

for name in ("torch", "torchvision", "stable-worldmodel",
               "stable-pretraining", "lightning", "hydra-core"):
    print(name, md.version(name))

print("CUDA runtime:", torch.version.cuda)
print("CUDA available:", torch.cuda.is_available())
assert hasattr(swm.data, "HDF5Dataset")
assert hasattr(swm.wm.utils, "save_pretrained")
assert hasattr(swm.wm.utils, "load_pretrained")

if torch.cuda.is_available():
    print("GPU:", torch.cuda.get_device_name(0))
    print("BF16:", torch.cuda.is_bf16_supported())
    print("CUDA operation:", torch.ones(1, device="cuda") + 1)
