import importlib.metadata as md
import sys
from pathlib import Path

# Resolve project imports when this script is run directly from any directory.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import os
from pathlib import Path
import h5py
import hdf5plugin
import stable_worldmodel as swm

path = Path(os.environ["STABLEWM_HOME"]) / "datasets/pusht_expert_train.h5"
with h5py.File(path, "r") as f:
    for key in f:
        obj = f[key]
        print(key, getattr(obj, "shape", None), getattr(obj, "dtype", None))
    required = {"pixels", "action", "proprio", "state", "ep_len", "ep_offset"}
    assert required.issubset(f.keys())

ds = swm.data.load_dataset(
    str(path), num_steps=4, frameskip=5,
    keys_to_load=["pixels", "action", "proprio", "state"],
  )
print("samples:", len(ds))
print("raw action dimension:", ds.get_dim("action"))
print("sample shapes:", {k: tuple(v.shape) for k, v in ds[0].items()})