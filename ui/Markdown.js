.pragma library
// Adapted from omaSearch AskModel.js, MIT; see THIRD_PARTY_NOTICES.md.
var MAX_FIELD = 1048576
function clipText(value, limit) {
  // Bound an answer like clip(), but keep line breaks and indentation so
  // paragraphs, lists and code survive.
  return String(value || "")
    .replace(/\r\n?/g, "\n")
    .replace(/\t/g, "    ")
    .replace(/[\x00-\x09\x0b-\x1f\x7f-\x9f\ue000\ue001]/g, "")
    .slice(0, limit || MAX_FIELD)
}

function escapeHtml(text) {
  return String(text).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;")
}

function inlineHtml(text, codeColor, dimColor) {
  // Markdown inline spans → StyledText. The text is escaped first, so only the
  // tags built here reach the Text item. Code spans and links are set aside as
  // placeholders so their contents are not formatted.
  var held = []
  function hold(html) {
    held.push(html)
    return "\ue000" + (held.length - 1) + "\ue001"
  }
  var s = String(text)
    .replace(/`([^`\n]+)`/g, function(m, code) {
      return hold("<font color=\"" + codeColor + "\">" + escapeHtml(code) + "</font>")
    })
    .replace(/\[([^\]\n]+)\]\((https?:\/\/[^\s)]+)\)/g, function(m, label, url) {
      return hold(link(url, label, codeColor))
    })
    .replace(/https?:\/\/[^\s<>"'`\]]+/g, function(url) {
      // Bare URL; trailing punctuation stays outside the link.
      var tail = /[.,;:!?)]+$/.exec(url)
      var bare = tail ? url.slice(0, url.length - tail[0].length) : url
      return hold(link(bare, bare, codeColor)) + (tail ? tail[0] : "")
    })
  s = escapeHtml(s)
    .replace(/\*\*(?=\S)([\s\S]*?\S)\*\*/g, "<b>$1</b>")
    .replace(/(^|[^\w])__(?=\S)([\s\S]*?\S)__(?!\w)/g, "$1<b>$2</b>")
    .replace(/(^|[^*\w])\*(?=[^\s*])([^*\n]*?[^\s*])\*(?![*\w])/g, "$1<i>$2</i>")
    .replace(/(^|[^\w])_(?=[^\s_])([^_\n]*?[^\s_])_(?!\w)/g, "$1<i>$2</i>")
    .replace(/~~(?=\S)([\s\S]*?\S)~~/g, "<s>$1</s>")
    .replace(/\n/g, "<br>")
  return s.replace(/\ue000(\d+)\ue001/g, function(m, i) { return held[Number(i)] })
}

function link(url, label, color) {
  // A clickable link (the overlay opens http(s) links in the default browser).
  return '<a href="' + escapeHtml(url) + '" style="color:' + color + '; text-decoration:underline;">'
    + escapeHtml(label) + "</a>"
}

function tableText(rows) {
  // A pipe table as aligned monospace text (the overlay font is monospace).
  var raw = rows.join("\n")
  if (rows.length > 200) return raw
  var cells = []
  var widths = []
  for (var r = 0; r < rows.length; r++) {
    var line = rows[r].replace(/^\s*\|/, "").replace(/\|\s*$/, "")
    if (/^\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*$/.test(line)) continue
    var row = line.split("|").map(function(c) {
      return c.replace(/\*\*|__|`/g, "").replace(/^\s+|\s+$/g, "")
    })
    if (row.length > 20 || row.some(function(cell) { return cell.length > 120 })) return raw
    for (var c = 0; c < row.length; c++) widths[c] = Math.max(widths[c] || 0, row[c].length)
    cells.push(row)
  }
  // Compute the expansion before allocating any padding.
  var rowWidth = widths.reduce(function(total, width) { return total + width + 2 }, 1)
  if (rowWidth * (cells.length + 1) > Math.min(MAX_FIELD, raw.length * 4)) return raw
  var out = []
  for (var i = 0; i < cells.length; i++) {
    var padded = []
    for (var j = 0; j < cells[i].length; j++)
      padded.push(j === cells[i].length - 1 ? cells[i][j] : cells[i][j] + " ".repeat(widths[j] - cells[i][j].length))
    out.push(padded.join("  "))
    if (i === 0 && cells.length > 1) {
      var rule = []
      for (var k = 0; k < widths.length; k++) rule.push("─".repeat(widths[k]))
      out.push(rule.join("  "))
    }
  }
  return out.join("\n")
}

function parseMarkdown(text, codeColor, dimColor) {
  // Split an answer into blocks the overlay lays out one by one:
  //   p / h / li / quote → { html }   code / table → { text }   hr
  // `gap` is the space above a block, mirroring the answer's own spacing:
  // 0 first block, 1 a plain line break, 2 a blank line before it.
  // An unclosed ``` fence (still streaming) runs to the end as code.
  var plain = clipText(text, MAX_FIELD)
  var lines = plain.split("\n")
  // Keep object creation bounded in the shared desktop shell.
  if (lines.length > 512) return [{ kind: "code", text: plain }]
  var blocks = []
  var open = null   // p / li / quote collecting lines, or a table
  var fence = null
  var bullets = ["•", "◦", "▪", "◦"]
  var indents = []  // indent of each open list level, for nesting depth
  var sawBlank = false

  function takeBlank() {
    var blank = sawBlank
    sawBlank = false
    return blank
  }
  function add(block, blank) {
    block.gap = !blocks.length ? 0 : blank ? 2 : 1
    blocks.push(block)
  }
  function flush() {
    if (!open) return
    if (open.kind === "table") add({ kind: "table", text: tableText(open.lines) }, open.blank)
    else add({ kind: open.kind, level: open.level || 0, depth: open.depth || 0, marker: open.marker || "",
               ordered: !!open.ordered, html: inlineHtml(open.lines.join("\n"), codeColor, dimColor) }, open.blank)
    open = null
  }

  for (var i = 0; i < lines.length; i++) {
    var line = lines[i]
    var m

    if (fence) {
      m = /^\s*(`{3,}|~{3,})\s*$/.exec(line)
      if (m && m[1].charAt(0) === fence.marker.charAt(0) && m[1].length >= fence.marker.length) {
        add({ kind: "code", text: fence.lines.join("\n"), lang: fence.lang }, fence.blank)
        fence = null
      } else {
        var lead = /^ */.exec(line)[0].length
        fence.lines.push(line.slice(Math.min(lead, fence.indent)))
      }
      continue
    }
    if ((m = /^(\s*)(`{3,}|~{3,})\s*([\w+#.-]*)\s*$/.exec(line))) {
      flush()
      fence = { indent: m[1].length, marker: m[2], lang: m[3].toLowerCase(), lines: [], blank: takeBlank() }
      indents = []
      continue
    }
    if (!/\S/.test(line)) {
      flush()
      sawBlank = true
      continue
    }
    if (/^\s*\|.*\|\s*$/.test(line)) {
      if (!open || open.kind !== "table") {
        flush()
        open = { kind: "table", lines: [], blank: takeBlank() }
        indents = []
      }
      open.lines.push(line)
      continue
    }
    if ((m = /^\s{0,3}(#{1,6})\s+(.*?)(?:\s+#+)?\s*$/.exec(line))) {
      flush()
      indents = []
      add({ kind: "h", level: m[1].length, depth: 0, marker: "", ordered: false,
            html: inlineHtml(m[2], codeColor, dimColor) }, takeBlank())
      continue
    }
    if (/^\s{0,3}([-*_])(\s*\1){2,}\s*$/.test(line)) {
      flush()
      indents = []
      add({ kind: "hr" }, takeBlank())
      continue
    }
    if ((m = /^(\s*)([-*+]|\d{1,3}[.)])\s+(?:\[([ xX])\]\s+)?(.*)$/.exec(line))) {
      flush()
      while (indents.length && indents[indents.length - 1] > m[1].length) indents.pop()
      if (!indents.length || indents[indents.length - 1] < m[1].length) indents.push(m[1].length)
      var depth = Math.min(3, indents.length - 1)
      var ordered = /\d/.test(m[2])
      var marker = m[3] !== undefined ? (m[3] === " " ? "☐" : "☑")
        : ordered ? m[2].replace(")", ".") : bullets[depth]
      open = { kind: "li", depth: depth, marker: marker, ordered: ordered, lines: [m[4]], blank: takeBlank() }
      continue
    }
    if ((m = /^\s*>\s?(.*)$/.exec(line))) {
      if (!open || open.kind !== "quote") {
        flush()
        open = { kind: "quote", lines: [], blank: takeBlank() }
        indents = []
      }
      open.lines.push(m[1])
      continue
    }
    // Plain text continues the open paragraph / list item / quote, keeping
    // its line breaks; otherwise it starts a paragraph.
    if (open && open.kind !== "table") {
      open.lines.push(line.replace(/^\s+/, ""))
    } else {
      flush()
      open = { kind: "p", lines: [line.replace(/^\s+/, "")], blank: takeBlank() }
      indents = []
    }
  }
  flush()
  if (fence) add({ kind: "code", text: fence.lines.join("\n"), lang: fence.lang }, fence.blank)

  // Numbered markers in one list share a width so the text lines up.
  // `slot` is that width in characters, including the space after it.
  for (var b = 0; b < blocks.length; b++) {
    if (blocks[b].kind !== "li") continue
    var end = b
    var widest = {}
    while (end < blocks.length && blocks[end].kind === "li") {
      var key = blocks[end].depth + (blocks[end].ordered ? "#" : "")
      widest[key] = Math.max(widest[key] || 0, blocks[end].marker.length)
      end++
    }
    // `lead` is where the marker starts: under the parent item's text.
    var textAt = []
    for (var k = b; k < end; k++) {
      var item = blocks[k]
      item.slot = widest[item.depth + (item.ordered ? "#" : "")] + 1
      item.lead = item.depth > 0 ? (textAt[item.depth - 1] || 0) : 0
      textAt[item.depth] = item.lead + item.slot
    }
    b = end - 1
  }
  return blocks
}

