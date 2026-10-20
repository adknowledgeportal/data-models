import sys
from pathlib import Path

# the scripts folder isn't a package, so make its modules importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
