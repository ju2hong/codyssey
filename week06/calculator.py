import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QGridLayout, QLineEdit, QVBoxLayout
from PyQt5.QtCore import Qt


class Calculator(QWidget):

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Calculator')

        self.display = QLineEdit()
        self.display.setAlignment(Qt.AlignRight)
        self.display.setFixedHeight(60)
        self.display.setReadOnly(True)

        layout = QVBoxLayout()
        layout.addWidget(self.display)

        grid = QGridLayout()

        buttons = [
            ('C', 0, 0), ('±', 0, 1), ('%', 0, 2), ('÷', 0, 3),
            ('7', 1, 0), ('8', 1, 1), ('9', 1, 2), ('×', 1, 3),
            ('4', 2, 0), ('5', 2, 1), ('6', 2, 2), ('-', 2, 3),
            ('1', 3, 0), ('2', 3, 1), ('3', 3, 2), ('+', 3, 3),
            ('0', 4, 0, 1, 2), ('.', 4, 2), ('=', 4, 3)
        ]

        for btn in buttons:
            if len(btn) == 3:
                text, row, col = btn
                button = QPushButton(text)
                button.clicked.connect(self.on_click)
                grid.addWidget(button, row, col)
            else:
                text, row, col, rowspan, colspan = btn
                button = QPushButton(text)
                button.clicked.connect(self.on_click)
                grid.addWidget(button, row, col, rowspan, colspan)

        layout.addLayout(grid)
        self.setLayout(layout)

    def on_click(self):
        sender = self.sender()
        text = sender.text()
        current = self.display.text()

        if text == 'C':
            self.display.clear()

        elif text == '=':
            try:
                expression = current.replace('×', '*').replace('÷', '/')
                result = str(eval(expression))
                self.display.setText(result)
            except Exception:
                self.display.setText('Error')

        elif text == '±':
            if current:
                if current.startswith('-'):
                    self.display.setText(current[1:])
                else:
                    self.display.setText('-' + current)

        else:
            self.display.setText(current + text)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    calc = Calculator()
    calc.show()
    sys.exit(app.exec_())