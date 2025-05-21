import os
import sys
import psutil
from pathlib import Path

from scanner.cli.terminal import parse_args

def run_application(args=None):
    if args is None:
        try:
            args = parse_args()
        except SystemExit:
            return

    base_path: Path = args.path
    report_dir: Path = args.report_dir
    num_threads: int = args.threads
    lock_timeout: float = args.lock_timeout
    detailed_logging: bool = args.detailed
    age_for_cleanup_days: int = args.age_days
    report_chart_type: str = args.chart_type

    if detailed_logging:
        print(f"[Handler] Mode: {args.mode}, Path: {base_path}, Threads: {num_threads}")
        print(f"[Handler] Report Dir: {report_dir}, Chart Type for PDF: {report_chart_type}") # Uses correct variable now
        print(f"[Handler] Detailed Logging: {detailed_logging}, Age for Cleanup: {age_for_cleanup_days} days")
        print("")

    print("reporter")

    if args.mode == "scan":
        if detailed_logging: print("[Handler] Initiating 'scan' mode.")

        if not base_path.is_dir():
            print(f"\n[Handler] Info: Target path '{base_path}' is not a directory")
        else:
            "dirscanner"
            "analyzer"
            if 1: 
                "scan successful"
                scan_successful = True
            "summary and process memory info"
            if detailed_logging:
                "detailed logging"
                print(f"[Handler] Scan mode memory usage: "
                      f"(Change during scan:")

        print() 
        console_summary_text = "summary text"
        print(console_summary_text)
        
        if (scan_successful):
            print("sum report")
        
        print(f"Scan mode complete.")
        # Conditionally print PDF generation message
        if report_chart_type in ["bar", "pie"] and \
           (scan_successful):
            print(f"PDF report (if generated) is in '{report_dir.resolve()}'.")
        print("")


    elif args.mode == "monitor":
        if detailed_logging: print(" detailed 'monitor' mode.")
        if not base_path.is_dir():
            print(f"\nError: Monitor mode cannot start. Path '{base_path}' is not a directory")
            print("")
            return

        "monitoring"

        final_summary_monitor = None # Initialize
        if detailed_logging: print("\nMonitor mode ended. Generating final summary and report (if applicable).")
            
        print()
        print("sum text")
            
        if final_summary_monitor and final_summary_monitor.get('total_files', 0) > 0:
            print("sum report")

        print(f"[Handler] Monitor mode complete.")
        if report_chart_type in ["bar", "pie"] and \
            (final_summary_monitor and final_summary_monitor.get('total_files', 0) > 0):
            print(f"PDF report (if generated) is in '{report_dir.resolve()}'.")
        print("")


    elif args.mode == "interactive":
        print("")
        
        print("Interactive mode session ended.")
        print("")

    else:
        print(f"Error: Unknown operation mode '{args.mode}'.", file=sys.stderr)
        sys.exit(1)