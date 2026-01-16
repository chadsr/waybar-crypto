__VERSION__ = "0.0.0+unknown"

# Re-export top-level API for convenient imports
from .waybar_crypto import WaybarCrypto, WAYBAR_CLASS_NAME

__all__ = [
    "WaybarCrypto",
    "WAYBAR_CLASS_NAME",
    "__VERSION__",
]
