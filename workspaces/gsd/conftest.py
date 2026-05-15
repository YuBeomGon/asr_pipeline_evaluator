"""Root conftest — make src importable without installing the package."""
import sys
from pathlib import Path

# Add workspace root to sys.path so `from src.xxx import yyy` works
sys.path.insert(0, str(Path(__file__).parent))
