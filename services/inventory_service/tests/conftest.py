import sys
import os

# Add services root to path
services_root = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.insert(0, os.path.abspath(services_root))