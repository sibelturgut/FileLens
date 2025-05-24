import argparse
import sys
import os
from pathlib import Path
from scanner import handler

def print_initial_usage_and_exit():
    # message for the first run, and "python main.py" with no args.
    print(" ")
    print("Welcome to FileLens: Cross‐platform file analyzer and scanner.")
    print(" ")
    print("\nFor a list of all general options applicable across modes, try:")
    print("  python main.py --help")
    print("\nFor more information about a specific mode and its options, try:")
    print("  python main.py <mode> --help")

def add_args(parser_obj: argparse.ArgumentParser):
    # helper function to define the cli args for the script.
    # 
    subparsers = parser_obj.add_subparsers(dest="command")
    scan_parser = subparsers.add_parser("scan", help="Run scan operation")
    subparsers.add_parser("interactive", help="Start interactive mode")
    report_parser = subparsers.add_parser("report", help="Create report for scan results")
    findold_parser = subparsers.add_parser("interactive", help="Start interactive mode")

    scan_parser.add_argument(
        "sdirectory",  # Positional argument (no -d flag needed)
        type=Path,
        help="Directory to scan or monitor. Default is the root",
        nargs="?",  # Makes it optional
        default=os.path.abspath(os.sep)
    )

    scan_parser.add_argument(
        "-m", "--monitor",
        help="Scan with monitoring",
        action="store_true"
    )
    scan_parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output."
    )
    scan_parser.add_argument(
        "--threads", "-t",
        type=int,
        default=1,
        help="Number of threads for operations. (Default: 1)"
    )
    scan_parser.add_argument(
        "--charttype", "-C",
        choices=["bar", "pie", "none"],
        default="none",
        help="Chart type for PDF report ('bar','pie','none'). (Default: none)"
    )
    scan_parser.add_argument(
        "--reportdir", "-O",
        type=Path,
        default=Path.cwd() / "filelens_reports",
        help="Directory to save PDF reports. (Default: ./filelens_reports)"
    )

    report_parser.add_argument(
        "rdirectory",  # Positional argument (no -d flag needed)
        type=Path,
        help="Directory to scan or monitor. Default is the root",
        nargs="?",  # Makes it optional
        default=os.path.abspath(os.sep)
    )

    report_parser.add_argument(
        "--charttype", "-C",
        choices=["bar", "pie", "none"],
        default="none",
        help="Chart type for PDF report ('bar','pie','none'). (Default: none)"
    )

    findold_parser.add_argument(
        "-d", "--day",
        help="Determine the days passed since last accessed",
        type=int
    )

def run_cli():
    parser = argparse.ArgumentParser(description='Welcome to FileLens')
    add_args(parser)
    args = parser.parse_args()

    if args.command == "scan":
        handler.scan(args.sdirectory, args.monitor, args.verbose, args.threads, args.charttype, args.reportdir)
    if args.command == "interactive":
        print_initial_usage_and_exit()
        while True:
            enter = input("FileLens >> ")

            if enter == "exit" or enter == "quit" or enter == "q":
                break

            try:
                args = parser.parse_args(enter.split())  # Parse user input
            except SystemExit:
                print("Invalid command. Type 'help' for command list.")

            if args.command == "scan":
                handler.scan(args.sdirectory, args.monitor, args.verbose, args.threads, args.charttype, args.reportdir)
            elif args.command == "report":
                handler.report(args.rdirectory, args.charttype)
            elif args.command == "findold":
                handler.findold(args.day)
            elif args.command == "cleanup":
                handler.cleanup()
            elif args.command == "config":
                handler.config()
            elif args.command == "help":
                return