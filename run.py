#!/usr/bin/env python
# Entry point to run the enhanced METAR desktop application
import sys
import os

# Add the project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.main import METARViewer

if __name__ == "__main__":
    app = METARViewer()
    app.mainloop()
