import re
import logging
from typing import Optional


logging.basicConfig(level=logging.INFO, format='%(levelname)s:\t  %(message)s')

class FeatureSanitizer:
    @staticmethod
    def log_warning(message: str):
        """Emits a warning log to the console for auditing."""
        logging.warning(f"[FeatureSanitizer] {message}")

    @staticmethod
    def parse_float(value: Optional[str], default: float) -> float:
        """
        Defensively parses a string to a float using regex.
        Supports both point and comma decimal separators (e.g., '1.5' or '1,5').
        """
        if value is None:
            return default
            
        if not isinstance(value, str):
            try:
                return float(value)
            except (ValueError, TypeError):
                return default
                
        
        value = value.replace(',', '.')
        
        
        match = re.search(r'-?\d*\.?\d+', value)
        if match:
            try:
                return float(match.group(0))
            except ValueError:
                pass
                
        return default

    @staticmethod
    def sanitize_width(value: Optional[str]) -> float:
        """
        Applies a defensive logic of 0.5m for width when OSM data is null.
        Also parses numeric strings stripping metric units.
        """
        if value is None or value == "":
            FeatureSanitizer.log_warning("Width data missing. Applying defensive default of 0.5m.")
            return 0.5
        
        parsed_width = FeatureSanitizer.parse_float(value, default=0.5)
        
        if parsed_width <= 0:
            FeatureSanitizer.log_warning(f"Invalid width parsed ({parsed_width}m) from raw '{value}'. Applying defensive default of 0.5m.")
            return 0.5
            
        return parsed_width

    @staticmethod
    def normalize_surface(raw_surface: Optional[str]) -> str:
        """Normalizes surface values"""
        if not raw_surface:
            return "unknown"
        return raw_surface.strip().lower()
