"""
Sprint 5 - Sector Report Generator

This module exposes the sector-report generation functionality
implemented and tested in batch_reports.py.

The existing batch_reports.py contains:
- sector data loading
- latest KPI calculation
- sector median calculation
- company KPI tables
- ReportLab PDF generation
- sector report verification
"""

from batch_reports import (
    generate_sector_reports,
)

if __name__ == "__main__":
    generate_sector_reports()
