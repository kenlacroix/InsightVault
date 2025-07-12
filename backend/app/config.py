"""
Configuration module for InsightVault app
"""

import sys
import os

# Add the parent directory to the path so we can import the root config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config

# Re-export the Config class
__all__ = ['Config'] 