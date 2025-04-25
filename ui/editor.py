from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit
from PyQt5.QtCore import QTimer
from core.storage import Storage

class Editor(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.title_label = QLabel("Выберите страницу")
        self.text_edit = QTextEdit()

        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.text_edit)

        self.storage = Storage()
        self.current_title = None

        self.timer = QTimer()
        self.timer.timeout.connect(self.auto_save)
        self.timer.start(500)

    def load_content(self, title: str):
        self.current_title = title
        self.title_label.setText(f"Редактируется: {title}")
        content = self.storage.load_page(title)
        self.text_edit.setText(content)

    def auto_save(self):
        if self.current_title:
            content = self.text_edit.toPlainText()
            self.storage.save_page(self.current_title, content)
