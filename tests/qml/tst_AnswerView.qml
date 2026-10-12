import QtQuick
import QtQuick.Layouts
import QtTest
import "../../ui"

TestCase {
    id: testCase
    name: "AnswerViewGeometry"
    when: windowShown
    // TestCase is invisible by default; layouts skip invisible children.
    visible: true
    width: 760
    height: 650
    property bool accountControlsVisible: false

    ColumnLayout {
        anchors.fill: parent
        spacing: 12
        Item { Layout.fillWidth: true; Layout.preferredHeight: 230 }
        Item {
            visible: testCase.accountControlsVisible
            Layout.fillWidth: true
            Layout.preferredHeight: 160
        }
        AnswerView {
            id: view
            Layout.fillWidth: true
            Layout.fillHeight: true
        }
        Item { Layout.fillWidth: true; Layout.preferredHeight: 40 }
    }

    function test_answer_survives_clear_and_account_controls() {
        view.answer = "MODEL_SEARCH_OK"
        tryVerify(() => view.contentHeight > 0)
        const localHeight = view.height
        view.answer = ""
        tryCompare(view, "contentHeight", 0)
        accountControlsVisible = true
        tryVerify(() => view.height < localHeight)
        view.answer = "MODEL_SEARCH_OK"
        // A nonempty response must occupy visible space after a provider switch.
        tryVerify(() => view.contentHeight > 0 && view.contentChildren[0].width > 0)
        verify(view.contentChildren[0].height > 0)
        verify(view.height > 0)
    }

    function test_long_answer_remains_scrollable_after_resize() {
        testCase.width = 480
        accountControlsVisible = true
        view.answer = "Line of synthetic answer text.\n".repeat(200)
        tryVerify(() => view.contentHeight > view.availableHeight)
        verify(view.contentWidth <= view.availableWidth)
        verify(view.contentChildren[0].width > 0)
    }
}
