from importlib.metadata import PackageNotFoundError, version as _pkg_version

try:
    # Read the installed distribution metadata
    __version__ = _pkg_version("waybar-crypto")
except PackageNotFoundError:
    # Fallback when not installed as a distribution
    __version__ = "0.0.0+unknown"

# Re-export top-level API for convenient imports
from .waybar_crypto import WaybarCrypto, WAYBAR_CLASS_NAME

__all__ = [
    "WaybarCrypto",
    "WAYBAR_CLASS_NAME",
    "__version__",
]
