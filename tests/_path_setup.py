from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"

src_root_text = str(SRC_ROOT)
if src_root_text not in sys.path:
    sys.path.insert(0, src_root_text)
