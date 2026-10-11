pragma ComponentBehavior: Bound
import QtQuick
import "Markdown.js" as Markdown
Column {
  id: root
  property string answer: ""
  property color foreground: "white"
  spacing: 8
  Repeater {
    model: Markdown.parseMarkdown(root.answer, "#89b4fa", "#a6adc8")
    delegate: TextEdit {
      required property var modelData
      width: root.width
      readOnly: true
      selectByMouse: true
      wrapMode: TextEdit.Wrap
      color: root.foreground
      font.pixelSize: 15
      font.family: modelData.kind === "code" ? "monospace" : "sans-serif"
      textFormat: modelData.kind === "code" || modelData.kind === "table" ? TextEdit.PlainText : TextEdit.RichText
      text: modelData.text || modelData.html || "────────"
      onLinkActivated: link => { if (/^https?:\/\//.test(link)) Qt.openUrlExternally(link) }
    }
  }
}
