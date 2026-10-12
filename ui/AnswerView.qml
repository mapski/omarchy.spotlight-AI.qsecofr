pragma ComponentBehavior: Bound
import QtQuick
import QtQuick.Controls

ScrollView {
  id: root
  property string answer: ""
  property color foreground: "white"
  clip: true
  Answer { width: root.availableWidth; answer: root.answer; foreground: root.foreground }
}
