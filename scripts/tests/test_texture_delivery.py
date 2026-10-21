"""Regression: missing photo textures cannot block a finished GLB.

Pure Python: no Anthropic API, Blender, image API, or paid build necessary.
"""
import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from texture_delivery import inventory_new_materials, missing_texture_note


class TextureDeliveryTests(unittest.TestCase):
    def test_missing_photos_only_logged(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            green = root / "inbox" / "grand_fond_h07" / "new_paint_green_metal.png"
            green.parent.mkdir(parents=True)
            green.write_bytes(b"test-only-nonempty-file")  # deliberately NOT a real PNG
            available, missing = inventory_new_materials(
                ["plaster_white", "new_paint_green_metal", "new_paint_green_timber",
                 "new_paint_green_timber", "glass"],
                {"new_paint_green_metal": green})
            self.assertEqual(available, [green])
            self.assertEqual(missing, ["new_paint_green_timber"])
            # No image-content or size verification occurs in this workflow.
            note = missing_texture_note(missing, "grand_fond_h07")
            self.assertIn("inbox/grand_fond_h07/new_paint_green_timber.png", note)
            self.assertIn("(FEHLT)", note)
            self.assertNotIn("new_paint_green_metal.png", note)

    def test_no_missing_is_not_an_error(self):
        files, missing = inventory_new_materials(["roof_terracotta", "glass"], {})
        self.assertEqual(files, [])
        self.assertEqual(missing, [])
        self.assertIn("Keine.", missing_texture_note(missing, "finca"))

    def test_nonexistent_and_empty_count_as_missing(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "new_render_old.png"
            path.touch()
            available, missing = inventory_new_materials(
                ["new_render_old", "new_brass_faded"],
                {"new_render_old": path, "new_brass_faded": path.parent / "not_present.png"})
            self.assertEqual(available, [])
            self.assertEqual(missing, ["new_brass_faded", "new_render_old"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
