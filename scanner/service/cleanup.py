import time
import sys
from pathlib import Path
from typing import List, Dict, Any

from send2trash import send2trash, TrashPermissionError

class CleanupManager:
    def __init__(self, age_days: int, detailed: bool):
        self.age_days = age_days
        self.detailed = detailed # detailed is still used for other operational messages

    def find_old_files(self, all_files: List[Dict[str, Any]]) -> List[Path]:
        crit_time = time.time() - (self.age_days * 86400) #cutoff timestamp is the current time minus the age in days
        old_files: List[Path] = []

        for file in all_files:
            path_str = file.get('path')
            mtime = file.get('mtime') # modification time
            if not path_str or not isinstance(mtime, (int, float)):
                if self.detailed:
                    print(f"Invalid file for age check, {file}", file=sys.stderr) # i use sys.stderr for error messages
                continue

            p = Path(path_str).resolve()
            if mtime < crit_time:
                old_files.append(p)

        if self.detailed and old_files:
            print(f"Found {len(old_files)} files older than {self.age_days} days.")
        elif self.detailed:
             print(f"No files found older than {self.age_days} days.")

        return old_files

    def execute_send_to_trash(self, paths_to_trash: List[Path]):        
        if not paths_to_trash:
            if self.detailed:
                print("No files specified to trash.")
            return

        success_count = 0
        failure_count = 0
        print(f"Moving {len(paths_to_trash)} files to trash.")

        for path in paths_to_trash:
            if not isinstance(path, Path):
                if self.detailed:
                    print(f"Invalid path provided for {path}", file=sys.stderr)
                failure_count += 1
                continue

            if not path.exists():
                if self.detailed:
                    print(f"File no longer exists - {path}", file=sys.stderr)
                failure_count += 1
                continue

            try:
                send2trash(str(path)) # send2trash expects a string path
                success_count += 1

                if self.detailed:
                    print(f"[Cleanup] Successfully trashed: {path}")

            except Exception as e: #fixed error handlings
                print(f"Error trashing {path}: {e}", file=sys.stderr)
                failure_count += 1

        print(f"{success_count} files successfully cleaned, {failure_count} files failed to be cleaned.")