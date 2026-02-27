"""Core EZRA engine for perception processing."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

from ezra.errors import EPBValidationError, PluginExecutionError

if TYPE_CHECKING:
    from ezra.plugins.interface import OCRPlugin


class EzraEngine:
    """Main engine for running perception workflows.

    This is a minimal stub. Full implementation will be added in later milestones.
    """

    def __init__(self, plugin: OCRPlugin) -> None:
        """Initialize engine with a plugin.

        Args:
            plugin: OCR plugin instance to use for inference.
        """
        self.plugin = plugin

    def process_image(
        self,
        image: Any,
        *,
        emit_epb: bool = False,
        epb_output_dir: Path | None = None,
    ) -> dict[str, Any]:
        """Process an image through the perception pipeline.

        Args:
            image: Input image (format depends on plugin implementation).
            emit_epb: If True, emit EPB v1.0.0 bundle to epb_output_dir.
            epb_output_dir: Directory path for EPB bundle emission (required if emit_epb=True).

        Returns:
            Dictionary containing detection results from plugin.infer().

        Raises:
            EPBValidationError: If emit_epb=True but epb_output_dir is None.
            PluginExecutionError: If plugin inference fails.
        """
        # Run plugin inference
        result = self.plugin.infer(image)

        # Optionally emit EPB bundle
        if emit_epb:
            if epb_output_dir is None:
                raise EPBValidationError("epb_output_dir must be provided when emit_epb=True")

            # Import here to avoid circular dependencies
            from ezra.epb import build_epb_bundle, write_epb_bundle

            # Get plugin metadata
            capabilities = self.plugin.describe_capabilities()
            plugin_name = type(self.plugin).__name__.replace("Plugin", "").lower()
            plugin_version = capabilities.get("version", "unknown")

            # Extract input metadata (assume image has size attributes if available)
            input_metadata: dict[str, Any] = {
                "width": getattr(image, "width", 0),
                "height": getattr(image, "height", 0),
                "channels": getattr(image, "channels", 3) if hasattr(image, "channels") else 3,
            }

            # Extract detections from result
            detections = result.get("detections", [])

            # Build EPB bundle
            bundle = build_epb_bundle(
                detections=detections,
                plugin_name=plugin_name,
                plugin_version=plugin_version,
                input_metadata=input_metadata,
                state=None,  # No structured state yet (minimal state will be created)
                delta=None,  # No delta yet
            )

            # Write EPB bundle to disk
            write_epb_bundle(bundle, Path(epb_output_dir))

        return result
