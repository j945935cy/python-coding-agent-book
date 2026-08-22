from pathlib import Path

import pytest

from publishing.build_epub import image_dimensions


ROOT = Path(__file__).resolve().parents[1]


def test_image_dimensions_reads_publishing_png_and_jpeg_without_pillow():
    cover_dir = ROOT / "publishing/cover"

    assert image_dimensions((cover_dir / "cover-1600x2400.png").read_bytes()) == (1600, 2400)
    assert image_dimensions((cover_dir / "cover-1600x2400.jpg").read_bytes()) == (1600, 2400)


def test_image_dimensions_rejects_unknown_or_truncated_data():
    with pytest.raises(ValueError, match="Unsupported or invalid image"):
        image_dimensions(b"not-an-image")
