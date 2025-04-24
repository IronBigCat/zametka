from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QListWidget, QListWidgetItem,
    QMenu, QAction, QInputDialog
)
from PyQt5.QtCore import pyqtSignal
from core.storage import Storage

class PageList(QWidget):
    page_selected = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.add_button = QPushButton("Добавить страницу")
        self.add_button.clicked.connect(self.add_page)

        self.list_widget = QListWidget()
        self.list_widget.setContextMenuPolicy(3)  # Qt.CustomContextMenu
        self.list_widget.customContextMenuRequested.connect(self.open_context_menu)
        self.list_widget.itemClicked.connect(self.select_page)

        self.layout.addWidget(self.add_button)
        self.layout.addWidget(self.list_widget)

        self.pages = []
        self.page_counter = 1

        self.storage = Storage()

        for title in self.storage.get_all_titles():
            item = QListWidgetItem(title)
            self.list_widget.addItem(item)
            self.pages.append(title)

    def add_page(self):
        title = f"Новая страница {self.page_counter}"
        self.page_counter += 1
        item = QListWidgetItem(title)
        self.list_widget.addItem(item)
        self.pages.append(title)
        self.page_selected.emit(title)

    def select_page(self, item):
        self.page_selected.emit(item.text())

    def open_context_menu(self, position):
        item = self.list_widget.itemAt(position)
        if not item:
            return

        menu = QMenu()
        rename_action = QAction("Переименовать", self)
        delete_action = QAction("Удалить", self)

        rename_action.triggered.connect(lambda: self.rename_page(item))
        delete_action.triggered.connect(lambda: self.delete_page(item))

        menu.addAction(rename_action)
        menu.addAction(delete_action)
        menu.exec_(self.list_widget.viewport().mapToGlobal(position))

    def delete_page(self, item: QListWidgetItem):
        title = item.text()
        self.storage.delete_page(title)
        self.pages.remove(title)
        self.list_widget.takeItem(self.list_widget.row(item))

    def rename_page(self, item: QListWidgetItem):
        old_title = item.text()
        new_title, ok = QInputDialog.getText(self, "Переименовать", "Новое имя:", text=old_title)
        if ok and new_title and new_title != old_title:
            self.storage.rename_page(old_title, new_title)
            item.setText(new_title)
            index = self.pages.index(old_title)
            self.pages[index] = new_title
            self.page_selected.emit(new_title)