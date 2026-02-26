import re
import unittest
from pathlib import Path


class FaviconRegressionTest(unittest.TestCase):
    def test_base_template_declares_favicon_link(self):
        base_html = Path("templates/base.html").read_text(encoding="utf-8")
        has_icon_rel = re.search(r'rel=["\'](?:shortcut\s+)?icon["\']', base_html, flags=re.IGNORECASE)
        self.assertIsNotNone(has_icon_rel, "base.html must include a favicon link")

    def test_favicon_asset_exists(self):
        self.assertTrue(Path("static/favicon.png").exists(), "static/favicon.png should exist")


if __name__ == "__main__":
    unittest.main()
