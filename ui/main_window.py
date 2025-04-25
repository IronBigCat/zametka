from PyQt5.QtWidgets import QMainWindow, QSplitter, QWidget, QVBoxLayout
from ui.page_list import PageList
from ui.editor import Editor

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Заметка")
        self.resize(1000, 700)

        splitter = QSplitter()
        self.page_list = PageList()
        self.editor = Editor()

        splitter.addWidget(self.page_list)
        splitter.addWidget(self.editor)

        container = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(splitter)
        container.setLayout(layout)

        self.setCentralWidget(container)

        self.page_list.page_selected.connect(self.load_page)

    def load_page(self, title: str):
        self.editor.load_content(title)
