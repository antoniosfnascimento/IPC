import logging
import re
from typing import Optional

log = logging.getLogger(__name__)


class FeatureSanitizer:
    @staticmethod
    def log_warning(message: str):
        log.warning(message)

    @staticmethod
    def parse_float(value, default: float) -> float:
        """Parse a value into a float, accepting both '1.5' and '1,5'."""
        if value is None:
            return default
        if not isinstance(value, str):
            try:
                return float(value)
            except (ValueError, TypeError):
                return default

        value = value.replace(",", ".")
        match = re.search(r"-?\d*\.?\d+", value)
        if match:
            try:
                return float(match.group(0))
            except ValueError:
                pass
        return default

    @staticmethod
    def sanitize_width(value) -> float:
        """Apply a defensive fallback (0.5 m) when OSM width data is missing."""
        if value is None or value == "":
            return 0.5

        parsed_width = FeatureSanitizer.parse_float(value, default=0.5)
        if parsed_width <= 0:
            return 0.5
        return parsed_width

    @staticmethod
    def normalize_surface(raw_surface: Optional[str]) -> str:
        if not raw_surface:
            return "unknown"
        return raw_surface.strip().lower()
