pragma ComponentBehavior: Bound
// Shell lifecycle adapted from Omarchy's emoji overlay; MIT notice retained.
import Quickshell
import Quickshell.Io
import Quickshell.Wayland
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import qs.Commons as Commons
import "ui"
import "ui/Presentation.js" as Presentation

Item {
  id: root
  property var shell: null
  property var manifest: null
  property bool opened: false
  property bool aiEnabled: false
  property bool busy: false
  property bool discovering: false
  property string answer: ""
  property string status: "Local search · AI is optional"
  property string queryId: ""
  property string answerId: ""
  property int serial: 0
  property var results: []
  property var providers: []
  property var models: []
  property int selection: 0
  readonly property string sourceDir: decodeURIComponent(Qt.resolvedUrl(".").toString().replace(/^file:\/\//, ""))
  function send(message) { if (bridge.running) bridge.write(JSON.stringify(message) + "\n") }
  function open(payloadJson) {
    root.opened = true
    Qt.callLater(function() { input.forceActiveFocus() })
  }
  function close() { root.opened = false; send({op: "cancel"}) }
  function dismiss() {
    close()
    if (root.shell && root.manifest) root.shell.hide(root.manifest.id)
  }
  function toggle() { if (root.opened) dismiss(); else open("{}") }
  function searchNow() {
    queryId = "s" + (++serial)
    if (input.text.indexOf("ai:") === 0) { results = []; return }
    send({op: "search", request_id: queryId, text: input.text})
  }
  function submit() {
    if (input.inputMethodComposing) return
    if (input.text.indexOf("ai:") !== 0) {
      if (results.length && selection < results.length) send({op: "activate", id: results[selection].id})
      return
    }
    if (!aiEnabled || busy || provider.currentIndex < 0 || modelPicker.currentIndex < 0) {
      status = "Enable AI and explicitly choose an available provider and model"
      return
    }
    answerId = "a" + (++serial)
    answer = ""
    busy = true
    status = "Waiting for selected provider…"
    send({op: "ask", request: {version: 1, request_id: answerId, route_id: providers[provider.currentIndex].route_id,
      model_id: models[modelPicker.currentIndex].id, backend_id: models[modelPicker.currentIndex].backend_id || "", prompt: input.text.slice(3).trim()}})
  }
  Process {
    id: bridge
    command: ["/usr/bin/python", "-B", "-m", "backend.main"]
    workingDirectory: root.sourceDir
    stdinEnabled: true
    running: true
    onStarted: root.send({op: "settings"})
    onExited: { root.discovering = false; root.busy = false; root.status = "Backend stopped; reopen after checking installation" }
    stdout: SplitParser {
      onRead: data => {
        try {
          const event = JSON.parse(data)
          if (event.kind === "settings") root.aiEnabled = event.settings.ai_enabled === true
          else if (event.kind === "results" && event.request_id === root.queryId) { root.results = event.results; root.selection = 0 }
          else if (event.kind === "discovery_error") { root.discovering = false; root.status = event.text }
          else if (event.kind === "providers") { root.discovering = false; root.providers = event.providers; provider.currentIndex = -1; root.models = []; modelPicker.currentIndex = -1; root.status = "Provider availability refreshed" }
          else if (event.kind === "activated") root.dismiss()
          else if (event.kind === "history") { root.answer = ""; root.status = "History cleared" }
          else if (event.request_id === root.answerId || !event.request_id) {
            if (event.kind === "delta") root.answer += event.text
            else if (["done", "error", "cancelled"].indexOf(event.kind) >= 0) { root.busy = false; root.status = event.text || event.kind }
          }
        } catch (_) { root.status = "Invalid backend response" }
      }
    }
  }
  Process {
    id: copyProcess
    command: ["wl-copy"]
    stdinEnabled: true
    onStarted: { copyProcess.write(root.answer); copyProcess.stdinEnabled = false }
  }
  Timer { id: debounce; interval: 100; onTriggered: root.searchNow() }
  PanelWindow {
    id: panel
    visible: root.opened
    anchors { top: true; bottom: true; left: true; right: true }
    color: "transparent"
    WlrLayershell.namespace: "omarchy-model-search"
    WlrLayershell.layer: WlrLayer.Overlay
    WlrLayershell.keyboardFocus: WlrKeyboardFocus.Exclusive
    exclusionMode: ExclusionMode.Ignore
    Rectangle { anchors.fill: parent; color: "#80000000" }
    Rectangle {
      anchors.centerIn: parent
      width: Math.min(760, panel.width - 40)
      height: Math.min(650, panel.height - 60)
      color: Commons.Color.menu.background
      border.color: Commons.Color.menu.border
      border.width: 1
      radius: 16
      ColumnLayout {
        anchors.fill: parent
        anchors.margins: 22
        spacing: 12
        Label { text: "Model Search"; font.pixelSize: 22; color: Commons.Color.menu.text }
        TextField {
          id: input
          Layout.fillWidth: true
          placeholderText: "Search applications · type ai: for a question"
          onTextChanged: debounce.restart()
          onAccepted: root.submit()
          Keys.onEscapePressed: { if (text.length) text = ""; else root.dismiss() }
          Keys.onDownPressed: root.selection = Math.min(root.results.length - 1, root.selection + 1)
          Keys.onUpPressed: root.selection = Math.max(0, root.selection - 1)
        }
        RowLayout {
          Layout.fillWidth: true
          CheckBox { text: "Enable AI"; checked: root.aiEnabled; onClicked: root.send({op: "opt_in", enabled: checked}) }
          Button { text: root.discovering ? "Checking…" : "Refresh providers"; enabled: !root.busy && !root.discovering; onClicked: { root.discovering = true; root.status = "Checking providers…"; root.send({op: "discover"}) } }
          Button { text: "Web search"; enabled: input.text.trim().length > 0; onClicked: Qt.openUrlExternally("https://duckduckgo.com/?q=" + encodeURIComponent(input.text)) }
        }
        RowLayout {
          Layout.fillWidth: true
          ComboBox {
            id: provider
            Layout.fillWidth: true
            model: root.providers
            textRole: "route_id"
            currentIndex: -1
            displayText: currentIndex < 0 ? "Choose provider" : currentText
            enabled: root.aiEnabled && !root.busy
            onActivated: {
              const item = root.providers[currentIndex]
              root.models = item.models
              modelPicker.currentIndex = -1
              root.status = item.available ? "Choose a model · destination: local" : item.reason
            }
          }
          ComboBox {
            id: modelPicker
            Layout.fillWidth: true
            model: root.models
            textRole: "id"
            currentIndex: -1
            displayText: currentIndex < 0 ? "Choose model" : currentText
            enabled: root.aiEnabled && !root.busy
          }
        }
        Label { Layout.fillWidth: true; text: root.status; wrapMode: Text.Wrap; color: Commons.Color.menu.text }
        ListView {
          Layout.fillWidth: true
          Layout.fillHeight: true
          visible: !Presentation.showAnswer(input.text, root.answer)
          clip: true
          model: root.results
          currentIndex: root.selection
          delegate: ItemDelegate {
            required property var modelData
            required property int index
            width: ListView.view.width
            text: modelData.label + "  ·  " + modelData.kind
            highlighted: index === root.selection
            onClicked: root.send({op: "activate", id: modelData.id})
          }
        }
        ScrollView {
          Layout.fillWidth: true
          Layout.fillHeight: true
          visible: Presentation.showAnswer(input.text, root.answer)
          clip: true
          Answer { width: panel.width > 800 ? 700 : panel.width - 100; answer: root.answer; foreground: Commons.Color.menu.text }
        }
        RowLayout {
          Button { text: "Stop"; enabled: root.busy; onClicked: root.send({op: "cancel"}) }
          Button { text: "Copy answer"; enabled: root.answer.length > 0; onClicked: { copyProcess.stdinEnabled = true; copyProcess.running = true } }
          Button { text: "Clear history"; onClicked: root.send({op: "clear_history"}) }
          Item { Layout.fillWidth: true }
          Button { text: "Close · Esc"; onClicked: root.dismiss() }
        }
      }
    }
  }
}
