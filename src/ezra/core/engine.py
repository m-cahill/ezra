"""Core EZRA engine for perception processing."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ezra.plugins.interface import OCRPlugin


class EzraEngine:
    """Main engine for running perception workflows.

    This is a minimal stub. Full implementation will be added in later milestones.
    """

    def __init__(self, plugin: "OCRPlugin") -> None:
        """Initialize engine with a plugin.

        Args:
            plugin: OCR plugin instance to use for inference.
        """
        self.plugin = plugin
