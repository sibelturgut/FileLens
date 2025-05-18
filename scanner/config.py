import argparse
import os
import sys
import pathlib


class Config:
    def __init__(self):
        parser = argparse.ArgumentParser(
            description="File analyzer and system scanner for Windows and Linux, by Sibel & Orkun.",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )

        parser.add_argument(
            "mode",
            choices=["scan", "monitor", "interactive"],
            help="Operation mode: 'scan' for one time analysis, "
                 "'monitor' for real time monitoring, "
                 "'interactive' for a cli session."
        )
        parser.add_argument(
            "--path", "-P",
            type=pathlib.Path,
            default=pathlib.Path.cwd(),
            help="Target directory path."
        )
        parser.add_argument(
            "--age-days", "-a",
            type=int,
            default=30,
            help="Identifying old files by age (days)."
        )
        parser.add_argument(
            "--export-pdf", "-E",
            action="store_true",
            help="Export the scan report as a PDF document."
        )
        parser.add_argument(
            "--chart-type", "-C",
            choices=["bar", "pie", "none"],
            default="bar",
            help="Type of chart for file type distribution shown in PDF."
        )
        parser.add_argument(
            "--report-output-dir", "-O",
            type=pathlib.Path,
            default=pathlib.Path.cwd() / "reports",
            help="Directory where reports (text, PDF, charts) will be saved."
        )
        parser.add_argument(
            "--threads", "-t",
            type=int,
            default=max(1, os.cpu_count() or 4),
            help="Number of threads for scanning."
        )
        parser.add_argument(
            "--lock-timeout", "-l",
            type=float,
            default=5.0,
            help="Timeout for acquiring locks (seconds)."
        )
        parser.add_argument(
            "--detailed", "-d",
            action="store_true",
            help="Enable detailed output during operation."
        )

        args = parser.parse_args()

        self.mode: str = args.mode
        self.path: pathlib.Path = args.path.resolve()
        self.age_days: int = args.age_days
        self.export_pdf: bool = args.export_pdf
        self.chart_type: str = args.chart_type
        self.num_threads: int = max(1, args.threads)
        self.lock_timeout: float = args.lock_timeout
        self.report_output_dir: pathlib.Path = args.report_output_dir.resolve()
        self.detailed: bool = args.detailed

        if not self.path.exists():
            parser.error(f"Target path does not exist: {self.path}")
        if not self.path.is_dir():
            parser.error(f"Target path is not a directory: {self.path}")

try:
    config = Config()
except SystemExit:
    raise
except Exception:
    print(f",Failed to initialize configuration: {Exception}", file=sys.stderr)
    sys.exit(1)