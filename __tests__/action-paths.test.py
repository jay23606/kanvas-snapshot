from pathlib import Path
import re
import unittest


class ActionPathTest(unittest.TestCase):
    def test_action_references_resolve_inside_the_action(self):
        root = Path(__file__).resolve().parents[1]
        text = (root / "action.yml").read_text(encoding="utf-8")

        scripts = (
            "playground-ping.sh",
            "manifest-merger.sh",
            "uploadApplicationFile.sh",
            "uploadApplicationUrl.sh",
            "sendSnapshotEmail.sh",
        )
        for script in scripts:
            with self.subTest(script=script):
                self.assertIn(
                    "${{ github.action_path }}/" + script,
                    text,
                    f"{script} is not referenced from github.action_path",
                )
                self.assertTrue((root / script).is_file(), f"missing action script: {script}")

        directories = (
            "cypress-action",
            "node-file-upload",
        )
        for directory in directories:
            with self.subTest(directory=directory):
                self.assertRegex(
                    text,
                    re.compile(r"working-directory:\s*\$\{\{ github\.action_path \}\}/" + directory),
                    f"working directory for {directory} is not action-relative",
                )
                self.assertTrue((root / directory).is_dir(), f"missing action directory: {directory}")

        artifact_paths = (
            "log.txt",
            "cypress-action/cypress/videos",
            "cypress-action/cypress/screenshots",
        )
        for path in artifact_paths:
            with self.subTest(artifact=path):
                self.assertIn(
                    "path: ${{ github.action_path }}/" + path,
                    text,
                    f"artifact path {path} is not action-relative",
                )
                # Cypress output folders and log.txt are created during action execution.
                target = root / path
                ancestor = target.parent
                while not ancestor.exists() and ancestor != root:
                    ancestor = ancestor.parent
                self.assertEqual(ancestor, root if path == "log.txt" else root / "cypress-action" / "cypress")


if __name__ == "__main__":
    unittest.main()
