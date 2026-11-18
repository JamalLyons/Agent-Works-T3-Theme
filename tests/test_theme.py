"""Build invariants for the Agent Works theme. Run: python3 -m unittest discover -s tests"""
import json, os, re, subprocess, sys, tempfile, unittest
from fractions import Fraction

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import gen  # noqa: E402  (builds in memory, writes nothing)


def durations(css):
    """Animation durations in seconds: the first time value of each `animation:` shorthand
    (and each comma-separated item in it) plus every `animation-duration:`."""
    out = []
    for decl in re.findall(r'animation:([^;}]+)', css):
        decl = re.sub(r'\([^)]*\)', '', decl)   # drop cubic-bezier(...)/steps(...) args before splitting on commas
        for item in decl.split(','):
            m = re.search(r'(\d*\.?\d+)s\b', item)
            if m:
                out.append(m.group(1))
    out += re.findall(r'animation-duration:(\d*\.?\d+)s', css)
    return out


class Build(unittest.TestCase):
    def test_css_fits_t3_limit(self):
        self.assertLessEqual(len(gen.theme_css), 50000)

    def test_css_passes_t3_restrictions(self):
        css = gen.theme_css
        self.assertNotIn('@import', css)
        self.assertNotIn('image-set(', css)
        self.assertNotIn('\\', css)
        # data: URIs are allowed whole, in any quoting
        rest = re.sub(r'url\(\s*(["\'])data:.*?\1\s*\)|url\(\s*data:[^)]*\)', '', css)
        for u in re.findall(r'url\(\s*["\']?([^"\')]*)', rest):
            self.assertTrue(u.startswith('#'), f'url({u}) is not data: or #id')

    def test_overlay_leds_sit_on_scene_leds(self):
        gen.check()
        self.assertEqual(sorted(gen.overlay_leds()), sorted(gen.PRESS_LEDS + gen.PANEL_LEDS))
        # and the scene really draws a 2x2 LED at each anchor
        for x, y in gen.PRESS_LEDS:
            self.assertIn(f'M{x} {y - gen.DY}h2v2', gen.svg_raw)
        for x, y in gen.PANEL_LEDS:
            self.assertIn(f'M{x} {y}h2v2', gen.svg_raw)

    def test_overlay_lamps_match_scene_bulbs(self):
        for lx in gen.ANCHORS['lamps']:
            self.assertIn(f"M{lx - 1} {gen.ANCHORS['bulbY']}h3v1", gen.svg_raw)

    def test_scene_animations_divide_the_loop(self):
        loop = Fraction(gen.ANCHORS['loop'])
        css = re.search(r'<style>(.*?)</style>', gen.svg_raw).group(1)
        ds = durations(css)
        self.assertGreater(len(ds), 30)
        bad = [d for d in ds if (loop / Fraction(d)).denominator != 1]
        self.assertEqual(bad, [], f'periods that do not divide {loop}s make the WebP jump at the loop')

    def test_overlay_animations_divide_the_loop(self):
        loop = Fraction(gen.ANCHORS['loop'])
        css = re.search(r'<style>(.*?)</style>', gen.lights_svg).group(1)
        ds = durations(css)
        self.assertGreaterEqual(len(ds), 3)
        bad = [d for d in ds if (loop / Fraction(d)).denominator != 1]
        self.assertEqual(bad, [], f'periods that do not divide {loop}s make preview.gif jump at the loop')

    def test_anchor_timing_matches_keyframes(self):
        # the anchor time must be the keyframe percentage of the period the scene CSS really uses
        css = re.search(r'<style>(.*?)</style>', gen.svg_raw).group(1)
        for name, an, pct in (('pr', gen.ANCHORS['pressHit'], gen.PRESS_HIT_PCT), ('wo', gen.ANCHORS['weld'], gen.WELD_OFF_PCT)):
            period = float(re.search(rf'\.{name}{{animation:{name} (\d*\.?\d+)s', css).group(1))
            self.assertEqual(an['period'], period, name)
            self.assertAlmostEqual(an['t' if name == 'pr' else 'on'], pct / 100 * period, msg=name)

    def test_weld_anchor_is_on_the_arc(self):
        x, y = gen.ANCHORS['weld']['x'], gen.ANCHORS['weld']['y']
        self.assertIn(f"<g class='wa'><path fill='{gen.G[13]}' d='M{x - 1} {y - 1}h2v2", gen.svg_raw)

    def test_credit_in_scene_and_css(self):
        self.assertTrue(gen.theme_css.startswith('/* Agent Works by Jamal Lyons'))
        self.assertIn('jamallyons.com', gen.theme_css)
        x, y = gen.CREDIT_XY
        cw = gen.text_w(gen.CREDIT)
        self.assertGreaterEqual(x, 347, 'credit plate must stay right of the chat column')
        self.assertLessEqual(x + cw + 3, 446, 'credit plate must clear the crane chain')
        self.assertIn(''.join(gen.R(*r[1:]) for r in gen.text(gen.CREDIT, x, y, '')[:3]), gen.svg_raw)

    def test_durations_parser_handles_timing_functions(self):
        self.assertEqual(durations('.a{animation:x cubic-bezier(.2,.7,.2,1) 4s infinite,y 2s}'), ['4', '2'])


def load(path):
    with open(path) as f:
        return json.load(f)


class Cli(unittest.TestCase):
    def run_gen(self, *args):
        d = tempfile.mkdtemp()
        out = os.path.join(d, 'new', 'out')   # main() must create missing folders
        subprocess.run([sys.executable, os.path.join(ROOT, 'gen.py'), out, *args], check=True, capture_output=True)
        return out

    def test_writes_all_outputs(self):
        out = self.run_gen()
        self.assertEqual(sorted(os.listdir(out)), ['agent-works.json', 'anchors.json', 'factory.svg', 'lights.svg'])
        self.assertEqual(load(f'{out}/agent-works.json')['id'], 'agent-works')
        self.assertEqual(load(f'{out}/anchors.json'), json.loads(json.dumps(gen.ANCHORS)))

    def test_no_id_for_themes_folder(self):
        out = self.run_gen('--no-id')
        self.assertNotIn('id', load(f'{out}/agent-works.json'))

    def test_bad_args_exit_nonzero(self):
        r = subprocess.run([sys.executable, os.path.join(ROOT, 'gen.py')], capture_output=True)
        self.assertNotEqual(r.returncode, 0)


if __name__ == '__main__':
    unittest.main()
