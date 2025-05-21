import argparse
import sys
from pathlib import Path

def print_initial_usage_and_exit():
    # message for the first run, and "python main.py" with no args.
    print(" ")
    print("Welcome to FileLens: Cross‐platform file analyzer and scanner.")
    print(" ")
    print("Please specify an operation mode.")
    print("\nUsage: python main.py <mode> [options]")
    print("\nAvailable modes:")
    print("  scan          Perform a one-time scan of a directory.")
    print("  monitor       Continuously monitor a directory for changes.")
    print("  interactive   Start an interactive shell for more commands.")
    print("\nFor a list of all general options applicable across modes, try:")
    print("  python main.py --help")
    print("\nFor more information about a specific mode and its options, try:")
    print("  python main.py <mode> --help")
    sys.exit(0)
   