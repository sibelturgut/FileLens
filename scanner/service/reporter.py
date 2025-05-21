
import sys
import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER


class Reporter:
    def __init__(self, output_dir: Path, chart_type: str, detailed: bool):
        self.output_dir = output_dir
        self.chart_type = chart_type
        self.detailed = detailed
        self._temp_chart_path: Path = self.output_dir / "_chart_temp_filelens.png"

        if self.chart_type in ["bar", "pie"]:
            try:
                self.output_dir.mkdir(parents=True, exist_ok=True) # creates the directory if it doesn't exist
                if self.detailed:
                    print(f"PDF reports will be saved to: {self.output_dir.resolve()}") # resolve() -> absolute path
            except Exception as e:
                print(f"Error creating report directory {self.output_dir}: {e}", file=sys.stderr)
                self.output_dir = Path.cwd()
                print(f"Creating report directory in: {self.output_dir.resolve()}", file=sys.stderr)
        
    def convert_size(self, size_bytes: int) -> str:
        if size_bytes < 0: size_bytes = 0
        units = ["Bytes", "KB", "MB", "GB", "TB", "PB"]
        num = float(size_bytes)
        unit = 0
        while num >= 1024 and unit < len(units) - 1:
            num /= 1024
            unit += 1
        return (f"{num:.2f} {units[unit]}") # format size with 2 decimal places
    
    def format_summary_text(self, summary_data: Dict[str, Any], scan_path_for_report: Optional[Path] = None) -> str:
        lines = [" "
            "    FileLens Scan Summary",
            f"Path Scanned: {str(scan_path_for_report.resolve()) if scan_path_for_report else 'N/A'}", # resolve() -> absolute path
            f"Report Time: {datetime.datetime.now():%Y-%m-%d %H:%M:%S}", # fix formatted datetime syntax
            f"Total Files: {summary_data.get('total_files', 0)}",
            f"Total Size : {self.convert_size(summary_data.get('total_size', 0))}",
            ""]
        
        stats = summary_data.get('by_type', {})
        if stats:
            lines.append("Top file types by count:")
            top_types = sorted(stats.items(), key=lambda item: (item[1]['count'], item[1]['size']), reverse=True)[:15]
            for type_name, data in top_types:
                count_str = f"{data['count']}"
                size_str = self.convert_size(data['size'])
                lines.append(f" {type_name:<40} : {count_str:>7} files, {size_str:>10}")

            lines.append("Top file types by size:")
            top_types = sorted(stats.items(), key=lambda item: (item[1]['size'], item[1]['count']), reverse=True)[:15]
            for type_name, data in top_types:
                count_str = f"{data['count']}"
                size_str = self.convert_size(data['size'])
                lines.append(f" {type_name:<40} : {count_str:>7} files, {size_str:>10}")
        else:
            lines.append(" No specific file type data found.")
        
        lines.append("     End of Summary")
        output = "\n".join(lines)
        return output
    
    
    def _generate_chart_image(self, summary_data: Dict[str, Any]) -> bool:
        type_stats = summary_data.get('by_type', {}) # a dictionary with file types as keys and their stats as values
        if not type_stats or self.chart_type == "none":
            return False

        types_counts_sorted = sorted(
            ((type_name, data['count'])
            for type_name, data in type_stats.items()),
            key = lambda x: x[1], reverse=True)
        # sorting the file types by their count descending
        
        top_types_data = types_counts_sorted[:10]
        
        if not top_types_data:
            if self.detailed: print("No data suitable for chart generation.")
            return False
            
        labels, counts = zip(*top_types_data) # unzipping the sorted data into labels and counts

        figure, ax = plt.subplots(figsize=(10, 7)) # matplotlib.pyplot.subplots creates a figure and a set of axes.

        if self.chart_type == "bar":
            bars = ax.bar(labels, counts, color='skyblue') # matplotlib bar chart

            ax.set_ylabel("Number of Files")
            ax.set_xlabel("File Type")
            ax.set_title("Top File Types by Count", fontsize=14)

            plt.xticks(rotation=45, ha='right', fontsize=9) # sets x-axis tick properties.
            plt.yticks(fontsize=9) # sets y-axis tick properties.


            ax.yaxis.set_major_locator(MaxNLocator(integer=True))
            ax.grid(axis='y', linestyle='--', alpha=0.7)
            for bar_widget in bars:
                height = bar_widget.get_height()
                if height > 0:
                    ax.text(bar_widget.get_x() + bar_widget.get_width() / 2., height + 0.01 * max(counts, default=1),
                            f'{int(height)}', ha='center', va='bottom', fontsize=8)
        
        elif self.chart_type == "pie":
            explode_values = [0.05 if i < 3 else 0 for i in range(len(counts))]
            ax.pie(counts, labels=labels, autopct='%1.1f%%', startangle=140, explode=explode_values if len(counts) > 1 else None,
                   wedgeprops={'edgecolor': 'black'}, textprops={'fontsize': 9})
            ax.axis('equal')
            ax.set_title("Top 10 File Types Distribution by Count", fontsize=14)


        figure.savefig(str(self._temp_chart_path), bbox_inches='tight', dpi=150) # saving the figure
        if self.detailed:
            print(f"Chart image saved temporarily to: {self._temp_chart_path}")
        plt.close(figure) # closes a figure window.
        return True


    def _create_pdf_report(self, summary_data: Dict[str, Any], chart_image_exists_and_valid: bool, scan_path_for_report: Optional[Path] = None):
        pdf_file_path = self.output_dir / f"FileLens_Report_{datetime.datetime.now():%Y%m%d_%H%M%S}.pdf" # datetime formatting
        doc = SimpleDocTemplate(str(pdf_file_path), pagesize=LETTER) # reportlab.platypus.SimpleDocTemplate -> basic pdf document structure.
        styles = getSampleStyleSheet() # pre-defined text styles.
        story: list = [] 

        story.append(Paragraph("FileLens Scan Report", styles['h1'])) # for text.
        story.append(Spacer(1, 0.1 * inch)) # for adding space.
        story.append(Paragraph(f"Report Generated: {datetime.datetime.now():%Y-%m-%d %H:%M:%S}", styles['Normal']))
        story.append(Paragraph(f"Target Path Scanned: {str(scan_path_for_report.resolve()) if scan_path_for_report else 'N/A'}", styles['Normal']))
        story.append(Paragraph(f"Total Files: {summary_data.get('total_files', 0)}", styles['Normal']))
        story.append(Paragraph(f"Total Size: {self.convert_size(summary_data.get('total_size', 0))}", styles['Normal']))
        story.append(Spacer(1, 0.2 * inch))

        if chart_image_exists_and_valid and self._temp_chart_path.exists():
            img = Image(str(self._temp_chart_path), width=7 * inch, height=5 * inch) # flowable for images.
            img.hAlign = 'CENTER'
            story.append(img)
            story.append(Spacer(1, 0.2 * inch))
        
        by_type_stats = summary_data.get('by_type', {})
        if by_type_stats:
            story.append(Paragraph("Top 15 File Types (by count, then size):", styles['h2']))
            story.append(Spacer(1, 0.1 * inch))
            table_content_data_types = [
                [Paragraph("<b>File Type</b>", styles['Normal']), 
                 Paragraph("<b>Count</b>", styles['Normal']), 
                 Paragraph("<b>Total Size</b>", styles['Normal']),
                 Paragraph("<b>Avg. Size</b>", styles['Normal'])]
            ]
            sorted_types_for_table = sorted(
                by_type_stats.items(),
                key=lambda item: (item[1]['count'], item[1]['size']),
                reverse=True
            )[:15]
            
            for type_name, data_for_type in sorted_types_for_table:
                avg_size = data_for_type['size'] / data_for_type['count'] if data_for_type['count'] > 0 else 0
                table_content_data_types.append([
                     Paragraph(type_name if len(type_name) < 40 else type_name[:37]+"...", styles['Normal']),
                     str(data_for_type['count']),
                     self.convert_size(data_for_type['size']),
                     self.convert_size(int(avg_size))
                 ])
            
            if len(table_content_data_types) > 1:
                pdf_table_types = Table(table_content_data_types, colWidths=[2.5*inch, 1.2*inch, 1.8*inch, 1.5*inch]) # flowable for tabular data.
                pdf_table_types.setStyle(TableStyle([ # reportlab.platypus.TableStyle defines table appearance.
                    ('BACKGROUND', (0,0), (-1,0), colors.darkslategray), 
                    ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),
                    ('ALIGN',(0,0),(-1,-1),'LEFT'),
                    ('ALIGN',(1,0),(-1,-1),'RIGHT'),
                    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0,0), (-1,0), 10),
                    ('BACKGROUND',(0,1),(-1,-1),colors.ghostwhite),
                    ('GRID',(0,0),(-1,-1),0.5,colors.darkgrey),
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                    ('LEFTPADDING', (0,0), (-1,-1), 5),
                    ('RIGHTPADDING', (0,0), (-1,-1), 5),
                ]))
                story.append(pdf_table_types)
                story.append(Spacer(1, 0.2*inch))

        all_files_details: Optional[List[Dict[str, Any]]] = summary_data.get('all_files_details')
        if all_files_details:
            story.append(Paragraph("All Scanned Files (Sorted by Size - Largest First):", styles['h2']))
            story.append(Spacer(1, 0.1 * inch))

            sorted_all_files = sorted(all_files_details, key=lambda x: x.get('size', 0), reverse=True)
            
            table_content_all_files = [
                [Paragraph("<b>File Path</b>", styles['Normal']), Paragraph("<b>Size</b>", styles['Normal'])]
            ]
            for file_detail in sorted_all_files:
                path_str = str(file_detail.get('path', 'N/A'))
                display_path = path_str if len(path_str) < 70 else "..." + path_str[-67:]
                table_content_all_files.append([
                    Paragraph(display_path, styles['Normal']),
                    self.convert_size(file_detail.get('size', 0))
                ])
            
            if len(table_content_all_files) > 1:
                pdf_table_all_files = Table(table_content_all_files, colWidths=[5.5*inch, 2.0*inch])
                pdf_table_all_files.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), colors.darkblue),
                    ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),
                    ('ALIGN',(0,0),(-1,-1),'LEFT'),
                    ('ALIGN',(1,0),(-1,-1),'RIGHT'),
                    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0,0), (-1,0), 10),
                    ('BACKGROUND',(0,1),(-1,-1),colors.lightgrey),
                    ('GRID',(0,0),(-1,-1),0.5,colors.grey),
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                    ('LEFTPADDING', (0,0), (-1,-1), 5),
                    ('RIGHTPADDING', (0,0), (-1,-1), 5),
                ]))
                story.append(pdf_table_all_files)
                story.append(Spacer(1, 0.2*inch))
        else:
            if self.detailed:
                story.append(Paragraph("Detailed list of all files not available in summary data.", styles['Normal']))
                story.append(Spacer(1, 0.2*inch))

        doc.build(story) # compiles the story into a PDF.
        print(f"[Reporter] PDF report successfully generated: {pdf_file_path.resolve()}")


    def write_summary_report(self, summary_data: Dict[str, Any], scan_path_for_report: Optional[Path] = None):
        if not summary_data or not summary_data.get('total_files', 0):
            if self.detailed:
                print("[Reporter] No summary data or no files found. Skipping PDF report generation.")
            return

        generate_pdf_report = self.chart_type in ["bar", "pie", "none"]
        should_generate_chart = self.chart_type in ["bar", "pie"]

        if not generate_pdf_report:
            if self.detailed:
                print(f"[Reporter] Chart type is '{self.chart_type}'. PDF report generation is skipped as type is not bar, pie, or none.")
            if self._temp_chart_path.exists():
                self._temp_chart_path.unlink()
                if self.detailed:
                    print(f"[Reporter] Temporary chart file '{self._temp_chart_path}' deleted (PDF generation skipped).")
            return

        self.output_dir.mkdir(parents=True, exist_ok=True)

        chart_generated_successfully = False
        if should_generate_chart:
            if self.detailed:
                print(f"[Reporter] Chart type is '{self.chart_type}'. Attempting chart generation.")
            chart_generated_successfully = self._generate_chart_image(summary_data)
        elif self.detailed:
            print(f"[Reporter] Chart type is '{self.chart_type}'. Chart generation skipped; proceeding with PDF.")
        
        if self.detailed:
            print(f"[Reporter] Attempting PDF report generation for chart_type '{self.chart_type}'.")
        
        self._create_pdf_report(summary_data, chart_generated_successfully, scan_path_for_report)
        
        if self._temp_chart_path.exists():
            self._temp_chart_path.unlink()
            if self.detailed:
                print(f"[Reporter] Temporary chart file '{self._temp_chart_path}' deleted.")
