# Setup for all tests to pull from our app directory
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'app'))
sys.path.insert(0, str(Path(__file__).parent / 'test'))