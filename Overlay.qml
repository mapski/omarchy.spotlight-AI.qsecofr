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
  property bool checkingAuth: false
  readonly property string authRoute: provider.currentIndex >= 0 ? providers[provider.currentIndex].route_id : ""
  property string answer: ""
  property string status: "Local search · AI is optional"
  property string queryId: ""
  property string answerId: ""
  property int serial: 0
  property string conversationId: ""
  property var savedSelection: ({})
  property var searchRoots: []
  property var history: ({})
  property var recentChats: []
  property bool temporaryChat: false
  property bool settingsLoaded: false
  readonly property string destination: provider.currentIndex >= 0 && modelPicker.currentIndex >= 0
    ? providers[provider.currentIndex].route_id + " / " + models[modelPicker.currentIndex].id + " · " + models[modelPicker.currentIndex].locality
    : savedSelection.model_id ? savedSelection.route_id + " / " + savedSelection.model_id + " · unavailable until verified" : "No model selected"
  function newChat() { conversationId = ""; answer = ""; input.text = "ai: "; input.forceActiveFocus() }
  function saveSelection() {
    if (provider.currentIndex < 0 || modelPicker.currentIndex < 0) return
    const m = models[modelPicker.currentIndex]
    savedSelection = {route_id: providers[provider.currentIndex].route_id, model_id: m.id, backend_id: m.backend_id || ""}
    send({op: "configure", selection: savedSelection})
  }
  function restoreSelection() {
    provider.currentIndex = -1; modelPicker.currentIndex = -1; models = []
    for (let i = 0; i < providers.length; i++) {
      if (providers[i].route_id !== savedSelection.route_id) continue
      provider.currentIndex = i
      models = providers[i].available ? providers[i].models : []
      for (let j = 0; j < models.length; j++) {
        if (models[j].id === savedSelection.model_id && (models[j].backend_id || "") === (savedSelection.backend_id || "")) modelPicker.currentIndex = j
      }
    }
  }
  function showConversation(id) {
    const turns = history[id] || []
    if (!turns.length) return
    conversationId = id; temporaryChat = false
    savedSelection = {route_id: turns[0].route_id || "", model_id: turns[0].model_id || "", backend_id: turns[0].backend_id || ""}
    restoreSelection()
    if (savedSelection.route_id && savedSelection.model_id) send({op: "configure", selection: savedSelection})
    answer = turns.map(t => (t.role === "user" ? "## You\n" : "## Answer\n") + t.text).join("\n\n")
    input.text = "ai: "
    status = "Saved conversation · follow-up stays with its original destination"
    historyPopup.close(); input.forceActiveFocus()
  }
  function handleEscape() {
    if (settingsPopup.opened) { settingsPopup.close(); return }
    if (historyPopup.opened) { historyPopup.close(); return }
    if (busy) { send({op: "cancel"}); return }
    if (input.text.length) input.text = ""
    else dismiss()
  }
  property var results: []
  property var providers: []
  property var models: []
  property int selection: 0
  readonly property string sourceDir: decodeURIComponent(Qt.resolvedUrl(".").toString().replace(/^file:\/\//, ""))
  function send(message) { if (bridge.running) bridge.write(JSON.stringify(message) + "\n") }
  function open(payloadJson) {
    root.opened = true
    if (!bridge.running) bridge.running = true
    send({op: "history"})
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
    status = "Waiting · " + destination
    send({op: "ask", request: {version: 1, request_id: answerId, route_id: providers[provider.currentIndex].route_id,
      model_id: models[modelPicker.currentIndex].id, backend_id: models[modelPicker.currentIndex].backend_id || "", prompt: input.text.slice(3).trim(), conversation_id: conversationId, temporary: temporaryChat}})
  }
  Process {
    id: bridge
    command: ["/usr/bin/python", "-B", "-m", "backend.main"]
    workingDirectory: root.sourceDir
    stdinEnabled: true
    running: true
    onStarted: { root.send({op: "settings"}); root.send({op: "history"}) }
    onExited: { root.discovering = false; root.checkingAuth = false; root.busy = false; root.status = "Backend stopped; reopen after checking installation" }
    stdout: SplitParser {
      onRead: data => {
        try {
          const event = JSON.parse(data)
          if (event.kind === "settings") {
            root.aiEnabled = event.settings.ai_enabled === true
            root.searchRoots = event.settings.roots || []
            root.savedSelection = event.settings.selection || {}
            root.restoreSelection()
            if (!root.settingsLoaded) {
              root.settingsLoaded = true
              root.discovering = true
              root.send({op: "discover"})
            }
          }
          else if (event.kind === "results" && event.request_id === root.queryId) { root.results = event.results; root.selection = 0 }
          else if (event.kind === "auth_opened") { root.status = event.text; root.dismiss() }
          else if (event.kind === "auth_status") { root.checkingAuth = false; root.status = event.route_id + ": " + event.text }
          else if (event.kind === "discovery_error") { root.discovering = false; root.status = event.text }
          else if (event.kind === "providers") { root.discovering = false; root.providers = event.providers; root.restoreSelection(); root.status = "Provider availability refreshed" }
          else if (event.kind === "activated") root.dismiss()
          else if (event.kind === "history") {
            root.history = event.history
            root.recentChats = Object.keys(event.history).reverse().map(id => ({id: id, title: (event.history[id][0] || {}).text || "Conversation"}))
            if (event.cleared) { root.answer = ""; root.conversationId = ""; root.status = "History cleared" }
          }
          else if (event.request_id === root.answerId || !event.request_id) {
            if (event.kind === "delta") root.answer += event.text
            else if (["done", "error", "cancelled"].indexOf(event.kind) >= 0) { root.busy = false; root.status = event.text || event.kind
              if (event.kind === "done") { root.conversationId = event.conversation_id || ""; root.send({op: "history"}) }
            }
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
      height: Math.min(input.text.indexOf("ai:") === 0 ? 650 : 410, panel.height - 40)
      color: Commons.Color.menu.background
      border.color: Commons.Color.menu.border
      border.width: 1
      radius: 16
      Pane {
        id: palettePane
        anchors.fill: parent
        padding: 18
        background: null
        palette.window: Commons.Color.menu.background
        palette.base: Commons.Color.menu.background
        palette.button: Commons.Color.menu.background
        palette.text: Commons.Color.menu.text
        palette.buttonText: Commons.Color.menu.text
        palette.windowText: Commons.Color.menu.text
        palette.highlight: "#365680"
        palette.highlightedText: "white"
        palette.disabled.buttonText: "#777777"
        palette.disabled.text: "#777777"
      ColumnLayout {
        anchors.fill: parent
        spacing: 12
        RowLayout {
          Layout.fillWidth: true
          Label { text: "Model Search"; font.pixelSize: 22; Layout.fillWidth: true }
          Button { text: "Recent"; enabled: !root.busy; onClicked: { root.send({op: "history"}); historyPopup.open() } }
          Button { text: "Settings"; enabled: !root.busy; onClicked: { rootsEditor.text = root.searchRoots.join("\n"); settingsPopup.open() } }
        }
        TextField {
          id: input
          Layout.fillWidth: true
          placeholderText: "Search applications · type ai: for a question"
          onTextChanged: debounce.restart()
          onAccepted: root.submit()
          Keys.onEscapePressed: root.handleEscape()
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
          visible: input.text.indexOf("ai:") === 0 || root.aiEnabled
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
              root.conversationId = ""; root.answer = ""
              root.models = item.available ? item.models : []
              modelPicker.currentIndex = -1
              root.status = item.available ? "Choose a model explicitly" : item.reason
            }
          }
          ComboBox {
            id: modelPicker
            Layout.fillWidth: true
            model: root.models
            textRole: "id"
            currentIndex: -1
            displayText: currentIndex < 0 ? "Choose model" : currentText
            onActivated: { root.conversationId = ""; root.answer = ""; root.saveSelection() }
            enabled: root.aiEnabled && !root.busy
          }
        }
        Label { Layout.fillWidth: true; visible: input.text.indexOf("ai:") === 0; text: root.destination; elide: Text.ElideMiddle }
        RowLayout {
          visible: (input.text.indexOf("ai:") === 0 || root.aiEnabled) && (root.authRoute === "claude" || root.authRoute === "codex")
          Button { text: "Sign in"; visible: root.authRoute === "claude" || root.authRoute === "codex"; enabled: !root.busy && !root.checkingAuth
            onClicked: root.send({op: "auth_login", route_id: root.authRoute}) }
          Button { text: root.checkingAuth ? "Checking…" : "Check again"; visible: root.authRoute === "claude" || root.authRoute === "codex"; enabled: !root.busy && !root.checkingAuth
            onClicked: { root.checkingAuth = true; root.send({op: "auth_check", route_id: root.authRoute}) } }
        }
        RowLayout {
          visible: input.text.indexOf("ai:") === 0
          Button { text: "New chat"; enabled: !root.busy; onClicked: root.newChat() }
          CheckBox { text: "Temporary question"; checked: root.temporaryChat; enabled: !root.busy; onClicked: { root.temporaryChat = checked; root.newChat() } }
          Label { text: root.conversationId ? "Follow-up" : "New conversation" }
        }
        Label { Layout.fillWidth: true; text: root.status; wrapMode: Text.Wrap; color: Commons.Color.menu.text }
        Label {
          visible: !root.results.length && input.text.indexOf("ai:") !== 0
          text: input.text.length ? "No local matches. Adjust folders in Settings." : "Type to search applications and your configured folders."
          wrapMode: Text.Wrap
          Layout.fillWidth: true
        }
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
          Answer { width: parent.width; answer: root.answer; foreground: Commons.Color.menu.text }
        }
        RowLayout {
          Button { visible: input.text.indexOf("ai:") === 0; text: "Stop"; enabled: root.busy; onClicked: root.send({op: "cancel"}) }
          Button { visible: input.text.indexOf("ai:") === 0; text: "Copy answer"; enabled: root.answer.length > 0; onClicked: { copyProcess.stdinEnabled = true; copyProcess.running = true } }
          Button { visible: input.text.indexOf("ai:") === 0; text: "Clear history"; onClicked: root.send({op: "clear_history"}) }
          Label { text: "↑↓ select · Enter open · Esc clear / close"; font.pixelSize: 11; Layout.fillWidth: true; elide: Text.ElideRight }
          Button { text: "Close · Esc"; onClicked: root.dismiss() }
        }
      }
      Shortcut { sequence: "Escape"; enabled: root.opened; onActivated: root.handleEscape() }
      Popup {
        id: settingsPopup
        onOpened: { rootsError.text = ""; rootsEditor.forceActiveFocus() }
        palette: palettePane.palette
        anchors.centerIn: parent
        width: Math.min(500, parent.width - 20)
        height: Math.min(380, panel.height - 80)
        modal: true
        focus: true
        ColumnLayout {
          anchors.fill: parent
          Label { text: "Local search folders"; font.pixelSize: 20 }
          Label { text: "One absolute path per line. Empty means applications only."; wrapMode: Text.Wrap; Layout.fillWidth: true }
          ScrollView {
            Layout.fillWidth: true; Layout.fillHeight: true
            TextArea { id: rootsEditor; Keys.onTabPressed: saveFolders.forceActiveFocus(); placeholderText: "/home/mp/Documents"; wrapMode: TextEdit.Wrap }
          }
          Label { text: "AI opt-in and model selection are saved locally. No credentials are stored."; wrapMode: Text.Wrap; Layout.fillWidth: true }
          Label { id: rootsError; text: ""; wrapMode: Text.Wrap; Layout.fillWidth: true }
          RowLayout {
            Button { id: saveFolders; text: "Save"; onClicked: {
              const folders = rootsEditor.text.split("\n").map(p => p.trim()).filter(p => p.length)
              if (folders.length > 32 || folders.some(p => p.charAt(0) !== "/")) { rootsError.text = "Use at most 32 absolute folder paths."; return }
              root.send({op: "configure", roots: folders})
              settingsPopup.close()
            } }
            Button { text: "Cancel"; onClicked: settingsPopup.close() }
          }
        }
      }
      Popup {
        id: historyPopup
        onOpened: { recentList.currentIndex = 0; recentList.forceActiveFocus() }
        palette: palettePane.palette
        anchors.centerIn: parent
        width: Math.min(520, parent.width - 20)
        height: Math.min(400, panel.height - 80)
        modal: true
        focus: true
        ColumnLayout {
          anchors.fill: parent
          Label { text: "Recent conversations"; font.pixelSize: 20 }
          Label { visible: !root.recentChats.length; text: "No saved conversations yet." }
          ListView {
            id: recentList
            Layout.fillWidth: true; Layout.fillHeight: true; clip: true
            model: root.recentChats
            keyNavigationEnabled: true
            Keys.onReturnPressed: { if (currentIndex >= 0 && currentIndex < root.recentChats.length) root.showConversation(root.recentChats[currentIndex].id) }
            Keys.onEnterPressed: { if (currentIndex >= 0 && currentIndex < root.recentChats.length) root.showConversation(root.recentChats[currentIndex].id) }
            delegate: ItemDelegate {
              required property var modelData
              width: ListView.view.width
              required property int index
              highlighted: index === recentList.currentIndex
              text: modelData.title.slice(0, 100)
              onClicked: root.showConversation(modelData.id)
            }
          }
          Button { text: "Close"; onClicked: historyPopup.close() }
        }
      }
      }
    }
  }
}
