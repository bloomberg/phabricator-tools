import os
import sys


# Updates sys.path to parent directory for file.
# Allows for imports relative to parent directory.
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
