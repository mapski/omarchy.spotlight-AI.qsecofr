import shutil
import subprocess
import unittest
from pathlib import Path


@unittest.skipUnless(shutil.which('node'), 'Node required for pure presentation JavaScript tests')
class PresentationTests(unittest.TestCase):
    def run_js(self, file, expression):
        runner = 'const fs=require("fs"),vm=require("vm");const s={};vm.createContext(s);vm.runInContext(fs.readFileSync(process.argv[1],"utf8").replace(/^\\.pragma library\\n/,""),s);process.stdout.write(JSON.stringify(vm.runInContext(process.argv[2],s)));'
        return subprocess.check_output(['node', '-e', runner, str(file), expression], text=True, timeout=5)

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

    def test_malformed_inline_delimiters_fall_back_without_losing_text(self):
        expression = r'''(() => {
          for (const token of ["[", "**a ", "__a ", "~~a ", "``` ", "# "]) {
            for (const size of [8192, 1048576]) {
              const text = (token.repeat(Math.ceil(size / token.length))).slice(0, size - 4) + "TAIL";
              const blocks = parseMarkdown(text, "blue", "gray");
              if (blocks.length !== 1 || blocks[0].kind !== "code" || blocks[0].text !== text) return false;
            }
          }
          return true;
        })()'''
        self.assertEqual(self.run_js(Path('ui/Markdown.js'), expression), 'true')

    def test_normal_markdown_still_formats_and_escapes(self):
        expression = r'''(() => {
          const blocks = parseMarkdown("# Heading\n\n**bold** and [site](https://example.com) <script>", "blue", "gray");
          return blocks[0].kind === "h" && blocks[1].html.includes("<b>bold</b>")
            && blocks[1].html.includes('href="https://example.com"')
            && blocks[1].html.includes("&lt;script&gt;");
        })()'''
        self.assertEqual(self.run_js(Path('ui/Markdown.js'), expression), 'true')


    def test_unicode_heading_separators_do_not_backtrack(self):
        expression = r'''(() => {
          for (const separator of ["\u2028", "\u2029"]) {
            const text = "# " + " ".repeat(2000) + "x" + " ".repeat(2000) + separator + "y";
            const blocks = parseMarkdown(text, "blue", "gray");
            if (blocks.length !== 1 || blocks[0].kind !== "h" || !blocks[0].html.includes("y")) return false;
          }
          const normal = parseMarkdown("## Heading ##", "blue", "gray");
          return normal[0].kind === "h" && normal[0].html === "Heading";
        })()'''
        self.assertEqual(self.run_js(Path('ui/Markdown.js'), expression), 'true')
