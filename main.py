import sys
import time

from PyQt6 import QtWidgets, uic, QtGui
import hanoi_game_ui


def load_game_before():
    before_widget = uic.loadUi(hanoi_game_ui.get_dir('./ui/game_before.ui'))
    before_widget.setWindowTitle('Hanoi Game')
    before_widget.setWindowIcon(QtGui.QIcon(hanoi_game_ui.get_dir('./ui/Hanoi.png')))
    game_start_btn: QtWidgets.QPushButton = before_widget.pushButton
    level_combox: QtWidgets.QComboBox = before_widget.comboBox
    game_start_btn.clicked.connect(lambda: game_start(before_widget, level_combox))
    before_widget.show()


def game_start(widget: QtWidgets.QWidget, combox: QtWidgets.QComboBox):
    main_window = hanoi_game_ui.UiMainWindow(int(combox.currentText()))
    widget.hide()
    time.sleep(0.5)
    main_window.show()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    load_game_before()
    sys.exit(app.exec())
