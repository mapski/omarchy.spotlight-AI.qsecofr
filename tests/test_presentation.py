import shutil
import subprocess
import unittest
from pathlib import Path


@unittest.skipUnless(shutil.which('node'), 'Node required for pure presentation JavaScript tests')
class PresentationTests(unittest.TestCase):
    def run_js(self, file, expression):
        runner = 'const fs=require("fs"),vm=require("vm");const s={};vm.createContext(s);vm.runInContext(fs.readFileSync(process.argv[1],"utf8").replace(/^\\.pragma library\\n/,""),s);process.stdout.write(JSON.stringify(vm.runInContext(process.argv[2],s)));'
        return subprocess.check_output(['node', '-e', runner, str(file), expression], text=True)

    def test_old_answer_cannot_hide_local_results(self):
        self.assertEqual(self.run_js(Path('ui/Presentation.js'), 'showAnswer("Firefox", "old answer")'), 'false')
        self.assertEqual(self.run_js(Path('ui/Presentation.js'), 'showAnswer("ai: hello", "")'), 'true')

    def test_markdown_preserves_long_answer_tail(self):
        self.assertEqual(self.run_js(Path('ui/Markdown.js'), 'JSON.stringify(parseMarkdown("x".repeat(20001)+"FINAL-MARKER", "blue", "gray")).includes("FINAL-MARKER")'), 'true')

    def test_table_rendering_cannot_amplify_bounded_input(self):
        self.assertEqual(self.run_js(Path('ui/Markdown.js'),
            '(() => { const rows = ["|"+"x".repeat(10000)+"|last|", ...Array(100).fill("|x|y|")]; return tableText(rows).length <= rows.join("\\n").length * 4; })()'), 'true')

    def test_many_blocks_fall_back_to_plain_text_without_losing_tail(self):
        self.assertEqual(self.run_js(Path('ui/Markdown.js'),
            '(() => { const blocks=parseMarkdown("# item\\n".repeat(1000)+"FINAL", "blue", "gray"); return blocks.length <= 512 && JSON.stringify(blocks).includes("FINAL"); })()'), 'true')
