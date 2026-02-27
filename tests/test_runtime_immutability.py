"""Runtime immutability tests for EZRA data structures.

This module tests that EZRA's runtime data structures are sealed against
post-construction mutation. All structures should raise TypeError or
FrozenInstanceError when mutation is attempted.
"""

from types import MappingProxyType

import pytest

from ezra.epb.builder import build_epb_bundle
from ezra.epb.hasher import assert_structural_hash
from ezra.types import ImageInput, ModelArtifactMetadata, OCRResult
from ezra.zones.schema import BBoxNorm, ZonePersistence, ZoneSchema


class TestImageInputImmutability:
    """Test that ImageInput is immutable."""

    def test_image_input_frozen(self) -> None:
        """Test that ImageInput is frozen and cannot be mutated."""
        img = ImageInput(
            data=b"test",
            width=100,
            height=200,
            channels=3,
            metadata={"key": "value"},
        )

        # Attempt to mutate attributes should raise FrozenInstanceError
        with pytest.raises(Exception) as exc_info:  # noqa: PT011
            img.width = 200  # type: ignore[misc]
        assert "FrozenInstanceError" in str(type(exc_info.value).__name__)

        with pytest.raises(Exception) as exc_info:  # noqa: PT011
            img.metadata = {"new": "dict"}  # type: ignore[misc]
        assert "FrozenInstanceError" in str(type(exc_info.value).__name__)

    def test_image_input_metadata_sealed(self) -> None:
        """Test that ImageInput.metadata is wrapped in MappingProxyType."""
        metadata = {"key": "value", "nested": {"inner": "data"}}
        img = ImageInput(
            data=b"test",
            width=100,
            height=200,
            metadata=metadata,
        )

        # Metadata should be MappingProxyType
        assert isinstance(img.metadata, MappingProxyType)

        # Attempt to mutate metadata dict should raise TypeError
        with pytest.raises(TypeError):
            img.metadata["new_key"] = "new_value"  # type: ignore[index]

        # Original dict should be unchanged (not mutated by MappingProxyType)
        assert "new_key" not in metadata


class TestOCRResultImmutability:
    """Test that OCRResult is immutable."""

    def test_ocr_result_frozen(self) -> None:
        """Test that OCRResult is frozen and cannot be mutated."""
        result = OCRResult(
            text="Hello",
            confidence=0.9,
            bbox=[10.0, 20.0, 50.0, 40.0],
            metadata={"key": "value"},
        )

        # Attempt to mutate attributes should raise FrozenInstanceError
        with pytest.raises(Exception) as exc_info:  # noqa: PT011
            result.text = "World"  # type: ignore[misc]
        assert "FrozenInstanceError" in str(type(exc_info.value).__name__)

        with pytest.raises(Exception) as exc_info:  # noqa: PT011
            result.confidence = 0.8  # type: ignore[misc]
        assert "FrozenInstanceError" in str(type(exc_info.value).__name__)

    def test_ocr_result_bbox_is_tuple(self) -> None:
        """Test that OCRResult.bbox is stored as a tuple."""
        result = OCRResult(
            text="Hello",
            confidence=0.9,
            bbox=[10.0, 20.0, 50.0, 40.0],  # Pass list, should be coerced to tuple
        )

        # Bbox should be a tuple
        assert isinstance(result.bbox, tuple)
        assert result.bbox == (10.0, 20.0, 50.0, 40.0)

        # Attempt to mutate tuple should raise TypeError
        with pytest.raises(TypeError):
            result.bbox[0] = 99.0  # type: ignore[index]

    def test_ocr_result_metadata_sealed(self) -> None:
        """Test that OCRResult.metadata is wrapped in MappingProxyType."""
        metadata = {"key": "value"}
        result = OCRResult(
            text="Hello",
            confidence=0.9,
            bbox=[10.0, 20.0, 50.0, 40.0],
            metadata=metadata,
        )

        # Metadata should be MappingProxyType
        assert isinstance(result.metadata, MappingProxyType)

        # Attempt to mutate metadata dict should raise TypeError
        with pytest.raises(TypeError):
            result.metadata["new_key"] = "new_value"  # type: ignore[index]


class TestModelArtifactMetadataImmutability:
    """Test that ModelArtifactMetadata is immutable."""

    def test_model_artifact_metadata_frozen(self) -> None:
        """Test that ModelArtifactMetadata is frozen and cannot be mutated."""
        metadata = ModelArtifactMetadata(
            artifact_path="/path/to/model",
            version="1.0.0",
            input_size=(224, 224),
            normalization={"mean": 0.5, "std": 0.25},
            preprocessing_config={"resize": True},
            postprocessing_config={"threshold": 0.5},
        )

        # Attempt to mutate attributes should raise FrozenInstanceError
        with pytest.raises(Exception) as exc_info:  # noqa: PT011
            metadata.artifact_path = "/new/path"  # type: ignore[misc]
        assert "FrozenInstanceError" in str(type(exc_info.value).__name__)

    def test_model_artifact_metadata_dict_fields_sealed(self) -> None:
        """Test that dict fields are wrapped in MappingProxyType."""
        normalization = {"mean": 0.5, "std": 0.25}
        metadata = ModelArtifactMetadata(
            artifact_path="/path/to/model",
            version="1.0.0",
            input_size=(224, 224),
            normalization=normalization,
        )

        # Dict fields should be MappingProxyType
        assert isinstance(metadata.normalization, MappingProxyType)

        # Attempt to mutate dict should raise TypeError
        with pytest.raises(TypeError):
            metadata.normalization["new_key"] = "new_value"  # type: ignore[index]


class TestEPBBundleImmutability:
    """Test that EPB bundles are immutable."""

    def test_epb_bundle_sealed(self) -> None:
        """Test that EPB bundle dict is sealed with MappingProxyType."""
        bundle = build_epb_bundle(
            detections=[{"text": "Hello", "confidence": 0.9}],
            plugin_name="test",
            plugin_version="1.0.0",
            input_metadata={"width": 100, "height": 200},
        )

        # Bundle should be MappingProxyType
        assert isinstance(bundle, MappingProxyType)

        # Attempt to mutate bundle dict should raise TypeError
        with pytest.raises(TypeError):
            bundle["new_key"] = "new_value"  # type: ignore[index]

        # Attempt to mutate nested dicts should also raise TypeError
        with pytest.raises(TypeError):
            bundle["manifest"]["new_key"] = "new_value"  # type: ignore[index]

    def test_epb_bundle_nested_dicts_sealed(self) -> None:
        """Test that nested dicts in EPB bundle are also sealed."""
        bundle = build_epb_bundle(
            detections=[{"text": "Hello", "confidence": 0.9}],
            plugin_name="test",
            plugin_version="1.0.0",
            input_metadata={"width": 100, "height": 200},
        )

        # Nested dicts should be MappingProxyType
        assert isinstance(bundle["manifest"], MappingProxyType)
        assert isinstance(bundle["detections"], MappingProxyType)
        assert isinstance(bundle["state"], MappingProxyType)

        # Attempt to mutate nested dicts should raise TypeError
        with pytest.raises(TypeError):
            bundle["manifest"]["new_key"] = "new_value"  # type: ignore[index]


class TestZoneStructuresImmutability:
    """Test that zone structures remain frozen (regression guard)."""

    def test_bbox_norm_frozen(self) -> None:
        """Test that BBoxNorm is frozen and cannot be mutated."""
        bbox = BBoxNorm(x_min=0.0, y_min=0.0, x_max=1.0, y_max=1.0)

        # Attempt to mutate should raise FrozenInstanceError
        with pytest.raises(Exception) as exc_info:  # noqa: PT011
            bbox.x_min = 0.5  # type: ignore[misc]
        assert "FrozenInstanceError" in str(type(exc_info.value).__name__)

    def test_zone_persistence_frozen(self) -> None:
        """Test that ZonePersistence is frozen and cannot be mutated."""
        persistence = ZonePersistence(sticky=True)

        # Attempt to mutate should raise FrozenInstanceError
        with pytest.raises(Exception) as exc_info:  # noqa: PT011
            persistence.sticky = False  # type: ignore[misc]
        assert "FrozenInstanceError" in str(type(exc_info.value).__name__)

    def test_zone_schema_frozen(self) -> None:
        """Test that ZoneSchema is frozen and cannot be mutated."""
        schema = ZoneSchema(
            id="zone1",
            kind="text",
            channel_index=0,
            bbox_norm=BBoxNorm(x_min=0.0, y_min=0.0, x_max=1.0, y_max=1.0),
            persistence=ZonePersistence(sticky=True),
        )

        # Attempt to mutate should raise FrozenInstanceError
        with pytest.raises(Exception) as exc_info:  # noqa: PT011
            schema.id = "zone2"  # type: ignore[misc]
        assert "FrozenInstanceError" in str(type(exc_info.value).__name__)


class TestStructuralHashCrossValidation:
    """Test structural hash cross-validation for immutability verification."""

    def test_epb_bundle_structural_hash_deterministic(self) -> None:
        """Test that EPB bundle structural hash is deterministic across rebuilds."""
        detections = [{"text": "Hello", "confidence": 0.9, "bbox": [10.0, 20.0, 50.0, 40.0]}]
        input_metadata = {"width": 100, "height": 200}

        # Build first bundle
        bundle1 = build_epb_bundle(
            detections=detections,
            plugin_name="test",
            plugin_version="1.0.0",
            input_metadata=input_metadata,
        )

        # Build second bundle with same inputs
        bundle2 = build_epb_bundle(
            detections=detections,
            plugin_name="test",
            plugin_version="1.0.0",
            input_metadata=input_metadata,
        )

        # Compute structural hashes
        hash1 = assert_structural_hash(bundle1)
        hash2 = assert_structural_hash(bundle2)

        # Hashes should be identical (deterministic)
        assert hash1 == hash2
        assert len(hash1) == 64  # SHA256 hex length
        assert len(hash2) == 64

    def test_epb_bundle_structural_hash_different_inputs(self) -> None:
        """Test that different inputs produce different structural hashes."""
        bundle1 = build_epb_bundle(
            detections=[{"text": "Hello", "confidence": 0.9}],
            plugin_name="test",
            plugin_version="1.0.0",
            input_metadata={"width": 100, "height": 200},
        )

        bundle2 = build_epb_bundle(
            detections=[{"text": "World", "confidence": 0.9}],  # Different text
            plugin_name="test",
            plugin_version="1.0.0",
            input_metadata={"width": 100, "height": 200},
        )

        # Structural hashes should be different
        hash1 = assert_structural_hash(bundle1)
        hash2 = assert_structural_hash(bundle2)

        assert hash1 != hash2

