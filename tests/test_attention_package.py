"""Documentation/UI release gate run by the existing Python CI matrix."""
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PUBLIC=ROOT/'blueprints/attention-desk/dashboard/engine/public'

class AttentionPackageTests(unittest.TestCase):
    def test_accessible_ui_contract(self):
        html=(PUBLIC/'attention.html').read_text()
        css=(PUBLIC/'attention.css').read_text()
        js=(PUBLIC/'attention-ui.js').read_text()
        for value in ['lang="en"','name="viewport"','role="status"','role="alert"','<audio controls','<summary>','alt=','<label>','id="practice"']:
            self.assertIn(value,html)
        for value in ['prefers-reduced-motion',':focus-visible','min-height:44px','max-width:100%']:
            self.assertIn(value,css)
        for value in ['innerHTML','outerHTML','alert(','confirm(']:
            self.assertNotIn(value,js)
    def test_vark_assets(self):
        self.assertGreater((PUBLIC/'attention-walkthrough.mp3').stat().st_size,10000)
        self.assertIn('<svg',(ROOT/'docs/diagrams/attention-desk.svg').read_text())
        self.assertIn('flowchart',(ROOT/'docs/diagrams/attention-desk.mmd').read_text())
        self.assertTrue((ROOT/'blueprints/attention-desk/walkthrough-transcript.txt').exists())

if __name__=='__main__':
    unittest.main()
