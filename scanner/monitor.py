import time
import os 
import sys
import threading
import typing
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileMovedEvent

from scanner.config import Config
from scanner.analyzer import Analyzer
from scanner.scan import Scan
from scanner.resources import LockWrapper

class Monitor(FileSystemEventHandler):
    