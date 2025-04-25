from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QSizePolicy
from PyQt5.QtCore import QTimer, Qt
from core.storage import Storage
from core.models import serialize_blocks, deserialize_blocks
from ui.block_widget import BlockWidget


class Editor(QWidget):
    def __init__(self):
        super().__init__()

        self.storage = Storage()
        self.current_title = None
        self.block_widgets = []

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.title_label = QLabel("Выберите страницу")
        self.layout.addWidget(self.title_label)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.block_container = QWidget()

        # 👇 чтобы контейнер не сжимался
        self.block_container.setSizePolicy(
            self.block_container.sizePolicy().horizontalPolicy(),
            QSizePolicy.Maximum
        )

        self.block_layout = QVBoxLayout()

        # 👇 ключевые правки
        self.block_layout.setContentsMargins(0, 0, 0, 0)
        self.block_layout.setSpacing(2)
        self.block_layout.setAlignment(Qt.AlignTop)  # 👈 прижимаем к верху

        self.block_container.setLayout(self.block_layout)
        self.scroll_area.setWidget(self.block_container)

        self.layout.addWidget(self.scroll_area)

        self.add_first_block()

        self.timer = QTimer()
        self.timer.timeout.connect(self.auto_save)
        self.timer.start(2000)

    def add_first_block(self):
        if not self.block_widgets:
            self.add_block()

    def add_block(self, after=None, block_type="text"):
        block = BlockWidget(block_type)
        block.request_new_block.connect(lambda b, t: self.add_block(after=b, block_type=t))
        block.block_type_changed.connect(self.refresh)

        if after and after in self.block_widgets:
            index = self.block_widgets.index(after) + 1
            self.block_widgets.insert(index, block)
            self.block_layout.insertWidget(index, block)
        else:
            self.block_widgets.append(block)
            self.block_layout.addWidget(block)

        block.editor.setFocus()

        self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        )

        # 👇 чтобы блоки шли вверх, а не центрировались
        if self.block_layout.count() > 0:
            item = self.block_layout.itemAt(self.block_layout.count() - 1)
            if item and item.spacerItem():
                self.block_layout.removeItem(item)
        self.block_layout.addStretch()

    def load_content(self, title: str):
        self.current_title = title
        self.title_label.setText(f"Редактируется: {title}")
        self.clear_blocks()

        content = self.storage.load_page(title)
        for block_data in deserialize_blocks(content):
            block = BlockWidget(
                block_data.get("type", "text"),
                block_data.get("content", ""),
                block_data.get("checked", False)
            )
            block.request_new_block.connect(lambda b, t: self.add_block(after=b, block_type=t))
            block.block_type_changed.connect(self.refresh)
            self.block_widgets.append(block)
            self.block_layout.addWidget(block)

        self.add_first_block()

    def clear_blocks(self):
        for b in self.block_widgets:
            b.setParent(None)
        self.block_widgets = []

    def auto_save(self):
        if not self.current_title:
            return
        data = [b.get_data() for b in self.block_widgets]
        self.storage.save_page(self.current_title, serialize_blocks(data))

    def refresh(self):
        self.auto_save()
