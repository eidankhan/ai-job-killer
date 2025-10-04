# from datetime import datetime
# # app/utils/text_utils.py
# from dateutil import parser
# from typing import Optional, Any

# def normalize_labels(value: str) -> str:
#     """Normalize comma/semicolon separated label strings."""
#     if not value:
#         return ""
#     labels = [v.strip() for v in value.replace(";", ",").split(",") if v.strip()]
#     return ", ".join(sorted(set(labels)))


# def parse_date(value: Any) -> Optional[str]:
#     """
#     Convert a date-like value to ISO date string (YYYY-MM-DD) or return None.
#     Accepts None, empty strings, pandas NaN, or typical ISO/date strings.
#     """
#     if value is None:
#         return None
#     s = str(value).strip()
#     if s == "" or s.lower() in {"nan", "none", "null"}:
#         return None
#     try:
#         dt = parser.parse(s)
#         # return date part as ISO string so SQLAlchemy can map it to Date
#         return dt.date().isoformat()
#     except Exception:
#         return None

