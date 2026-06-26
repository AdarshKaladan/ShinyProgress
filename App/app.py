import os, sys, glob
from pathlib import Path
data_path = Path(__file__).resolve().parent.parent / "Data"
sys.path.append(str(data_path))
from tracker import ProgressTracker

pathlist = [os.path.basename(i).split(".")[0] for i in glob.glob(str(data_path / "*.npy"))]
for i in pathlist:print(i)
