import os
import sys
import datetime
import typing
from pathlib import Path

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER 

import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

from scanner.config import Config

class Reporter:
