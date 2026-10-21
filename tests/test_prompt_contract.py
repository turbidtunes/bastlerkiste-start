"""Offline tests: parish church and mixed-use building with very different requirements."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from prompt_contract import (  # noqa: E402
    MANDATORY_SECTIONS, compiler_task, contract_context,
    sha256_text, source_brief, validate_compiled_contract,
)

CHURCH = """Katholische Pfarrkirche Grand-Fond Mauritius: 30 x 42 m plot, -Y street,
max three floors, nave, choir, sacristy, bell tower with real stairs, authority furniture;
no go, all doors as leaf meshes, PBR and metrically tiled photo textures."""
BAKERY = """Creole bakery on Mauritius: two-level shop and home, 15x25 m plot.
Shop, oven room, store, WC on ground floor. Living, kitchen, bath, bedroom upstairs.
Corrugated roof, balcony, creole_poor style. Absolutely no tower."""
VALID_CONTRACT = "\n".join("## " + h + "\nDetails: " + "x" * 70
                           for h in MANDATORY_SECTIONS)


class PromptContractTests(unittest.TestCase):
    def test_church_keeps_full_original_and_specifics(self):
        task = compiler_task(CHURCH, ["references/church.png"], "church")
        self.assertIn(CHURCH, task)
        self.assertIn("bell tower", task)
        self.assertIn("references/church.png", task)
        validate_compiled_contract(VALID_CONTRACT)
        self.assertIn(CHURCH, contract_context(CHURCH, VALID_CONTRACT, "briefs/church.md"))

    def test_non_church_does_not_force_tower(self):
        task = compiler_task(BAKERY, ["references/shop.png"], "bakery")
        self.assertIn(BAKERY, task)
        self.assertIn("Keine generischen Kirchtürme", task)
        self.assertIn(sha256_text(BAKERY),
                      contract_context(BAKERY, VALID_CONTRACT, "briefs/bakery.md"))

    def test_file_and_direct_input(self):
        with tempfile.TemporaryDirectory() as td:
            file = Path(td) / "test.md"
            file.write_text(CHURCH, encoding="utf-8")
            self.assertEqual(source_brief(file)[0], CHURCH)
            self.assertEqual(source_brief(file, BAKERY)[0], BAKERY)

    def test_long_prompt_survives_without_truncation(self):
        long_source = CHURCH + "\n" + ("MANDATORY_DETAIL_" + "0123456789" * 70 + "\n") * 100
        self.assertGreater(len(long_source), 50000)
        task = compiler_task(long_source, [], "long_building")
        self.assertIn(long_source, task)
        context = contract_context(long_source, VALID_CONTRACT, "briefs/long.md")
        self.assertIn(long_source, context)
        self.assertIn(sha256_text(long_source), context)

    def test_real_church_brief_survives_verbatim(self):
        actual = Path(__file__).resolve().parents[1] / "briefs" / "grand_fond_parish_church.md"
        self.assertTrue(actual.is_file())
        original = actual.read_text(encoding="utf-8")
        context = contract_context(original, VALID_CONTRACT, str(actual))
        self.assertIn(original, context)
        self.assertIn(sha256_text(original), context)

    def test_compiler_required_sections(self):
        with self.assertRaises(ValueError):
            validate_compiled_contract("## ROOMS_AND_FURNITURE\nNo other details")


if __name__ == "__main__":
    unittest.main()
