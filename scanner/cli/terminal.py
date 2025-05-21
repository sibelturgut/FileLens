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

def add_args(parser_obj: argparse.ArgumentParser):
    # helper function to define the cli args for the script.
    # 
    parser_obj.add_argument(
        "-d", "--directory",
        type=Path,
        help="Directory to scan or monitor. Default is the current directory.",
        default=Path.cwd()
    )
    parser_obj.add_argument(
        "-o", "--output",
        type=Path,
        help="Output file to save results. Default is 'results.txt'.",
        default=Path("results.txt")
    )
    parser_obj.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output."
    )
    parser_obj.add_argument(
        "--path", "-P",
        type=Path,
        default=Path.cwd(),
        help="Target Directory. (Default: current directory)"
    )
    parser_obj.add_argument(
        "--threads", "-t",
        type=int,
        default=1,
        help="Number of threads for operations. (Default: 1)"
    )
    parser_obj.add_argument(
        "--age-days", "-a",
        type=int,
        default=30,
        help="Age of the files in days for cleanup in interactive mode. (Default: 30)"
    )
    parser_obj.add_argument(
        "--chart-type", "-C",
        choices=["bar", "pie", "none"],
        default="none",
        help="Chart type for PDF report ('bar','pie','none'). (Default: none)"
    )
    parser_obj.add_argument(
        "--report-dir", "-O",
        type=Path,
        default=Path.cwd() / "filelens_reports",
        help="Directory to save PDF reports. (Default: ./filelens_reports)"
    )
    parser_obj.add_argument(
        "--detailed", "-d",
        action="store_true",
        help="Enable detailed logging output."
    )
    parser_obj.add_argument(
        "--lock-timeout", "-l",
        type=float,
        default=5.0,
        help="Timeout for lock acquisition. (Default: 5.0)"
    )
