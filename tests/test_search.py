import tempfile
import unittest
from pathlib import Path
from backend.search import classify_query, search


class SearchTests(unittest.TestCase):
    def test_modes_require_explicit_intent(self):
        for text, mode, expected in [('hello', 'local', 'local'), ('ai: hello', 'local', 'ai'), ('weather', 'web', 'web'), ('weather', 'ai', 'ai'), ('chair', 'local', 'local')]:
            self.assertEqual(classify_query(text, mode), expected)
        with self.assertRaises(ValueError):
            classify_query('hello', 'guess')

    def test_search_only_configured_roots_and_treats_shell_text_as_data(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'Notes').mkdir()
            (root / 'Notes' / 'café.txt').write_text('synthetic')
            (root / '$(touch marker).txt').write_text('synthetic')
            result = search('CAFÉ', [tmp], app_dirs=[])
            self.assertEqual([r.label for r in result], ['café.txt'])
            self.assertEqual(result[0].kind, 'file')
            self.assertEqual(search('marker', [tmp], app_dirs=[])[0].label, '$(touch marker).txt')
            self.assertFalse((root / 'marker').exists())
            self.assertEqual(search('café', [], app_dirs=[]), [])

    def test_no_following_symlinks_or_hidden_directories(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / '.private').mkdir()
            (root / '.private' / 'secret.txt').touch()
            (root / 'link').symlink_to(root / '.private', target_is_directory=True)
            self.assertEqual(search('secret', [tmp], app_dirs=[]), [])
            self.assertEqual(search('', [tmp], app_dirs=[]), [])
            self.assertEqual(search('x', [str(root / 'missing')], app_dirs=[]), [])

    def test_application_visibility_and_deterministic_ranking(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for filename, content in [('z.desktop', '[Desktop Entry]\nType=Application\nName=Zebra Notes\nExec=z\n'), ('n.desktop', '[Desktop Entry]\nType=Application\nName=Notes\nExec=n\n'), ('h.desktop', '[Desktop Entry]\nType=Application\nName=Notes Hidden\nNoDisplay=true\nExec=h\n')]:
                (root / filename).write_text(content)
            results = search('notes', [], app_dirs=[tmp])
            self.assertEqual([r.label for r in results], ['Notes', 'Zebra Notes'])
            self.assertTrue(all(r.kind == 'application' for r in results))
