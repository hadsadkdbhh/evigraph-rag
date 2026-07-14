from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.check_submission_pipeline import RequiredArtifact, check_latex_logs, check_required_artifacts


class SubmissionPipelineCheckTest(unittest.TestCase):
    def test_required_artifacts_accepts_existing_nonempty_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            path = root / "paper" / "main.tex"
            path.parent.mkdir()
            path.write_text("content\n", encoding="utf-8")

            results = check_required_artifacts(root, (RequiredArtifact("main", "paper/main.tex"),))

        self.assertEqual(len(results), 1)
        self.assertTrue(results[0].passed)

    def test_required_artifacts_rejects_missing_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            results = check_required_artifacts(root, (RequiredArtifact("main", "paper/main.tex"),))

        self.assertFalse(results[0].passed)
        self.assertIn("missing", results[0].detail)

    def test_latex_log_rejects_undefined_reference_warnings(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            log = root / "build" / "main.log"
            log.parent.mkdir()
            log.write_text("LaTeX Warning: Reference `tab:x' on page 1 undefined on input line 42.\n", encoding="utf-8")

            results = check_latex_logs(root, ("build/main.log",))

        self.assertFalse(results[0].passed)
        self.assertIn("undefined", results[0].detail)

    def test_latex_log_accepts_clean_log(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            log = root / "build" / "main.log"
            log.parent.mkdir()
            log.write_text("Output written on main.pdf.\n", encoding="utf-8")

            results = check_latex_logs(root, ("build/main.log",))

        self.assertTrue(results[0].passed)


if __name__ == "__main__":
    unittest.main()
