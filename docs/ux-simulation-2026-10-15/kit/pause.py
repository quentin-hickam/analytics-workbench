#!/usr/bin/env python3
"""pause.py SECONDS: block for up to SECONDS (max 540) so queued agent messages can arrive."""
import sys, time
time.sleep(min(int(sys.argv[1]) if len(sys.argv) > 1 else 30, 540))
print("pause done")
