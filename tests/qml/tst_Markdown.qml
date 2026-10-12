import QtQuick
import QtTest
import "../../ui/Markdown.js" as Markdown

TestCase {
    name: "MarkdownWorkBudget"
    function test_delimiters() {
        const start = Date.now()
        for (const token of ["[", "**a ", "__a ", "~~a ", "``` ", "# "]) {
            for (const size of [4097, 8192, 1048576]) {
                const text = token.repeat(Math.ceil(size / token.length)).slice(0, size - 4) + "TAIL"
                const blocks = Markdown.parseMarkdown(text, "blue", "gray")
                compare(blocks.length, 1)
                compare(blocks[0].kind, "code")
                compare(blocks[0].text, text)
            }
        }
        // Also cover normalization expansion and block-parser whitespace paths.
        for (const text of ["\t".repeat(1100), "```" + " ".repeat(8192) + "!", "# " + " ".repeat(8192) + "x", "https://x/" + ".".repeat(8192) + "a"]) {
            const blocks = Markdown.parseMarkdown(text, "blue", "gray")
            compare(blocks[0].kind, "code")
            compare(blocks[0].text, Markdown.clipText(text, Markdown.MAX_FIELD))
        }
        console.log("Large input cases ms:", Date.now() - start)
    }
    function test_at_budget() {
        const start = Date.now()
        for (const token of ["[", "**a ", "__a ", "~~a "]) {
            for (const size of [4095, 4096]) {
                const text = token.repeat(4096).slice(0, size)
                const blocks = Markdown.parseMarkdown(text, "blue", "gray")
                compare(blocks.length, 1)
                compare(blocks[0].kind, "p")
            }
        }
        for (const text of ["```" + " ".repeat(4092) + "!", "# " + " ".repeat(4093) + "x", "https://x/" + ".".repeat(4086) + "a"]) {
            verify(Markdown.parseMarkdown(text, "blue", "gray").length > 0)
        }
        console.log("At-budget cases ms:", Date.now() - start)
    }
    function test_unicode_line_separators() {
        for (const separator of ["\u2028", "\u2029"]) {
            const text = "# " + " ".repeat(2000) + "x" + " ".repeat(2000) + separator + "y"
            const blocks = Markdown.parseMarkdown(text, "blue", "gray")
            compare(blocks.length, 1)
            compare(blocks[0].kind, "h")
            verify(blocks[0].html.indexOf("y") >= 0)
        }
    }
    function test_normal_formatting() {
        const blocks = Markdown.parseMarkdown("# Heading\n\n**bold** and [site](https://example.com) <script>", "blue", "gray")
        compare(blocks[0].kind, "h")
        verify(blocks[1].html.indexOf("<b>bold</b>") >= 0)
        verify(blocks[1].html.indexOf('href="https://example.com"') >= 0)
        verify(blocks[1].html.indexOf("&lt;script&gt;") >= 0)
        const code = Markdown.parseMarkdown("```\n<script>\n```", "blue", "gray")
        compare(code[0].kind, "code")
        compare(code[0].text, "<script>")
    }
}
