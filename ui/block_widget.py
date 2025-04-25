from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit,
    QCheckBox, QMenu, QAction, QSizePolicy
)
from PyQt5.QtCore import pyqtSignal, Qt


class BlockWidget(QWidget):
    request_new_block = pyqtSignal(QWidget, str)
    block_type_changed = pyqtSignal()

    def __init__(self, block_type="text", content="", checked=False):
        super().__init__()
        self.block_type = block_type
        self.content = content
        self.checked = checked

        # 👇 главный layout блока
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.setLayout(self.layout)

        # 👇 самое важное: блок не тянется!
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)

        self.init_ui()

    def init_ui(self):
        self.clear_layout()

        if self.block_type == "text":
            editor = QTextEdit()
            editor.setPlainText(self.content)
            editor.setPlaceholderText("Введите текст...")
            editor.setStyleSheet("""
                QTextEdit {
                    border: none;
                    background: transparent;
                    font-size: 14px;
                    padding: 0px;
                    margin: 0px;
                }
            """)
            editor.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
            editor.setFixedHeight(self.estimate_height(editor))
            editor.textChanged.connect(lambda: self.update_block_height(editor))
            editor.keyPressEvent = self._handle_key_event(editor, next_type="text")
            self.layout.addWidget(editor)
            self.editor = editor

        elif self.block_type == "heading":
            editor = QTextEdit()
            editor.setPlainText(self.content)
            editor.setPlaceholderText("Заголовок...")
            editor.setStyleSheet("""
                QTextEdit {
                    border: none;
                    background: transparent;
                    font-size: 18px;
                    font-weight: bold;
                    padding: 0px;
                    margin: 0px;
                }
            """)
            editor.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
            editor.setFixedHeight(self.estimate_height(editor))
            editor.textChanged.connect(lambda: self.update_block_height(editor))
            editor.keyPressEvent = self._handle_key_event(editor, next_type="text")
            self.layout.addWidget(editor)
            self.editor = editor

        elif self.block_type == "checkbox":
            layout = QHBoxLayout()
            checkbox = QCheckBox()
            text_input = QLineEdit()
            text_input.setText(self.content)
            text_input.setPlaceholderText("Задача...")
            text_input.setStyleSheet("""
                QLineEdit {
                    border: none;
                    background: transparent;
                    font-size: 14px;
                    padding: 0px;
                    margin: 0px;
                }
            """)
            checkbox.setChecked(self.checked)
            text_input.keyPressEvent = self._handle_key_event(text_input, next_type="checkbox")

            layout.addWidget(checkbox)
            layout.addWidget(text_input)
            layout.addStretch()

            wrapper = QWidget()
            wrapper.setLayout(layout)
            self.layout.addWidget(wrapper)

            self.editor = text_input
            self.checkbox = checkbox

    def estimate_height(self, editor):
        # вычисляем высоту текста
        fm = editor.fontMetrics()
        lines = max(1, editor.toPlainText().count("\n") + 1)
        return lines * fm.lineSpacing() + 8  # чуть воздуха

    def update_block_height(self, editor):
        editor.setFixedHeight(self.estimate_height(editor))

    def _handle_key_event(self, widget, next_type):
        def handler(event):
            if event.key() == Qt.Key_Return and not (event.modifiers() & Qt.ShiftModifier):
                event.accept()
                self.request_new_block.emit(self, next_type)
            elif event.text() == "/":
                self.show_type_menu()
            else:
                type(widget).keyPressEvent(widget, event)
        return handler

    def show_type_menu(self):
        menu = QMenu()
        types = [("Текст", "text"), ("Заголовок", "heading"), ("Чекбокс", "checkbox")]
        for label, type_ in types:
            action = QAction(label, self)
            action.triggered.connect(lambda _, t=type_: self.change_type(t))
            menu.addAction(action)
        menu.exec_(self.mapToGlobal(self.editor.cursorRect().bottomRight()))

    def change_type(self, new_type):
        self.block_type = new_type
        self.init_ui()
        self.block_type_changed.emit()

    def get_data(self):
        if self.block_type == "text":
            return {"type": "text", "content": self.editor.toPlainText()}
        elif self.block_type == "heading":
            return {"type": "heading", "content": self.editor.toPlainText()}
        elif self.block_type == "checkbox":
            return {
                "type": "checkbox",
                "content": self.editor.text(),
                "checked": self.checkbox.isChecked()
            }

    def clear_layout(self):
        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
