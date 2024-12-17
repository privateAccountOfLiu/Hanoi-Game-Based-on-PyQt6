import sys
import os
from PyQt6 import QtCore, QtGui, QtWidgets


def get_dir(path):
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath('.')
    return os.path.join(base_path, path)


class UiMainWindow(QtWidgets.QMainWindow):
    def __init__(self, level):
        super().__init__()
        self.level = level
        self.setObjectName("MainWindow")
        self.resize(800, 600)
        self.central_widget = QtWidgets.QGraphicsView(parent=self)
        self.scene_1 = QtWidgets.QGraphicsScene(parent=self.central_widget)
        self.reset_button = QtWidgets.QPushButton('重置游戏', parent=self.central_widget)
        self.timer = QtCore.QTimer()
        self.elapsed_time = QtCore.QTime(0, 0)
        self.label = QtWidgets.QLabel('00:00:00', parent=self.central_widget)
        self.rect_lst = [QtCore.QRectF(80, 470, 160, 30), QtCore.QRectF(80, 440, 140, 30),
                         QtCore.QRectF(80, 410, 120, 30), QtCore.QRectF(80, 380, 100, 30),
                         QtCore.QRectF(80, 350, 80, 30), QtCore.QRectF(80, 330, 60, 30),
                         QtCore.QRectF(80, 300, 40, 30), QtCore.QRectF(80, 270, 20, 30)]
        self.rects = [MovableGraphicItem(i) for i in self.rect_lst[0:self.level]]
        self.stack_1 = BeginStack(QtCore.QRectF(80, 135, 160, 450), self.rects, self.reset_button)
        self.stack_2 = Stack(QtCore.QRectF(320, 135, 160, 450), self.rects)
        self.stack_3 = TargetStack(QtCore.QRectF(560, 135, 160, 450), self.rects, self.elapsed_time, self.timer, self)
        self.game_main()

    def game_main(self):
        self.scene_1.setSceneRect(0, 0, 795, 595)
        self.reset_button.setGeometry(QtCore.QRect(20, 20, 80, 25))
        self.label.setGeometry(700, 20, 100, 25)
        self.label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.add_rects()
        for stack in (self.stack_1, self.stack_2, self.stack_3):
            self.scene_1.addItem(stack)
        self.game_setup_ui()
        self.reset_button.clicked.connect(lambda: self.reset_game(self.stack_1))
        self.timer.timeout.connect(self.timer_update)
        self.timer.start(1000)
        self.central_widget.setFixedSize(800, 600)
        self.setCentralWidget(self.central_widget)

    def game_setup_ui(self):
        self.central_widget.setMouseTracking(True)
        self.central_widget.setObjectName("central_widget")
        self.central_widget.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        self.scene_1.setObjectName('scene')
        self.game_re_translate_ui()
        self.central_widget.setScene(self.scene_1)
        QtCore.QMetaObject.connectSlotsByName(self)

    def game_re_translate_ui(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Hanoi Game", "Hanoi Game"))
        self.setWindowIcon(QtGui.QIcon(get_dir('./ui/Hanoi.png')))

    def timer_update(self):
        self.elapsed_time = self.elapsed_time.addSecs(1)
        self.label.setText(self.elapsed_time.toString('hh:mm:ss'))
        self.stack_3.timeing = self.elapsed_time

    def add_rects(self):
        for rect in self.rects:
            self.scene_1.addItem(rect)

    def reset_game(self, begin_stack):
        result = QtWidgets.QMessageBox.warning(self, '游戏提示', '是否要重置游戏？',
                                               QtWidgets.QMessageBox.StandardButton.Ok |
                                               QtWidgets.QMessageBox.StandardButton.No)
        if result == QtWidgets.QMessageBox.StandardButton.Ok:
            for rect in self.rects:
                rect.setPos(QtCore.QPointF(0, 0) - rect.rect().topLeft())
            for stack in [self.stack_1, self.stack_2, self.stack_3]:
                stack.rects = []
                stack.stack_reset()
            for rect in self.rects:
                rect.setPos(begin_stack.top_point - rect.rect().topLeft() - QtCore.QPointF(rect.rect().left(), 0))
                begin_stack.update()
            self.elapsed_time = QtCore.QTime(0, 0)
            self.update()


class MovableGraphicItem(QtWidgets.QGraphicsRectItem):
    def __init__(self, rect: QtCore.QRectF):
        super().__init__(rect)
        self.rect_i = rect
        self.memory = {'stack_pos': self.pos()}
        self.timer = QtCore.QTimer()
        self.setFlag(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges, True)
        self.setCacheMode(QtWidgets.QGraphicsItem.CacheMode.DeviceCoordinateCache)
        self.timer.timeout.connect(self.check_self)
        self.timer.start(150)

    def paint(self, painter, option, widget=None):
        painter.setBrush(QtGui.QBrush(QtCore.Qt.GlobalColor.blue))
        painter.setPen(QtGui.QPen(QtCore.Qt.GlobalColor.green, 2))
        n = 7
        points = [self.rect().topLeft() + QtCore.QPointF(n, 0), self.rect().topRight() + QtCore.QPointF(-n, 0),
                  self.rect().topRight() + QtCore.QPointF(0, n), self.rect().bottomRight() + QtCore.QPointF(0, -n),
                  self.rect().bottomRight() + QtCore.QPointF(-n, 0), self.rect().bottomLeft() + QtCore.QPointF(n, 0),
                  self.rect().bottomLeft() + QtCore.QPointF(0, -n), self.rect().topLeft() + QtCore.QPointF(0, n)]
        painter.drawPolygon(*points)

    def itemChange(self, change, value):
        if change == QtWidgets.QGraphicsItem.GraphicsItemChange.ItemPositionChange:
            scene_rect = self.scene().sceneRect()
            new_pos = value
            new_pos.setX(max(scene_rect.left() - self.rect().x(),
                             min(new_pos.x(), scene_rect.right() - self.rect().width() - self.rect().x())))
            new_pos.setY(max(scene_rect.top() - self.rect().y(),
                             min(new_pos.y(), scene_rect.bottom() - self.rect().height() - self.rect().y())))
            return new_pos
        return super().itemChange(change, value)

    def check_self(self):
        if not self.memory['is_in']:
            self.setPos(self.memory['stack_pos'])
        else:
            self.setPos(self.memory['stack_pos'])


class Stack(QtWidgets.QGraphicsRectItem):
    def __init__(self, rect: QtCore.QRectF, rects):
        super().__init__(rect)
        self.rect, self.top_point = rect, QtCore.QPointF((rect.left() + rect.right()) / 2, rect.bottom())
        self.rects = []
        self.color = QtCore.Qt.GlobalColor.cyan
        self.draw_pen = QtGui.QPen(QtCore.Qt.GlobalColor.lightGray, 2)
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(lambda: self.check_if_collisions(rects))
        self.timer.start(150)
        self.setZValue(-1)

    def paint(self, painter, option, widget=0):
        painter.setPen(self.draw_pen)
        rect1 = QtCore.QRectF(self.rect.bottomLeft(), self.rect.bottomRight() + QtCore.QPointF(0, 10))
        rect2 = QtCore.QRectF(self.rect.topLeft() + QtCore.QPointF(self.rect.width()/2 - 4, 0),
                              self.rect.bottomLeft() + QtCore.QPointF(self.rect.width()/2 + 4, 0))
        painter.drawRect(rect1)
        painter.fillRect(rect1, QtGui.QBrush(self.color))
        painter.fillRect(rect2, QtGui.QBrush(QtCore.Qt.GlobalColor.lightGray))

    def check_if_collisions(self, tars: list[MovableGraphicItem]):
        for tar in tars:
            if self.collidesWithItem(tar):
                if tar not in self.rects:
                    self.rects.append(tar)
                    self.top_point = QtCore.QPointF(self.rect.left() + (self.rect.width() - tar.rect().width()) / 2,
                                                    self.top_point.y() - tar.rect().height())
                    memory_stack_pos = QtCore.QPointF(self.top_point.x() - tar.rect().x(),
                                                      self.top_point.y() - tar.rect().y())
                    if (len(self.rects) > 1 and tar == self.rects[-1]
                            and tar.rect().width() > self.rects[-2].rect().width()):
                        tar.setPos(tar.memory['stack_pos'])
                    else:
                        tar.memory['stack_pos'] = memory_stack_pos
                        tar.setPos(tar.memory['stack_pos'])
                        tar.memory['is_in'] = True
                else:
                    if self.rects[-1] == tar:
                        tar.setFlag(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
                    else:
                        tar.setFlag(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
            else:
                if tar in self.rects:
                    self.rects.pop(self.rects.index(tar))
                    self.top_point = QtCore.QPointF(self.rect.left() - (self.rect.width() - tar.rect().width()) / 2,
                                                    self.top_point.y() + tar.rect().height())
                    tar.memory['is_in'] = False

    def stack_reset(self):
        self.top_point = QtCore.QPointF((self.rect.left() + self.rect.right()) / 2, self.rect.bottom())


class BeginStack(Stack):
    def __init__(self, rect: QtCore.QRectF, rects, begin_button):
        super().__init__(rect, rects)
        self.color = QtCore.Qt.GlobalColor.green
        self.all_rects = rects
        self.reset_button = begin_button
        self.timer_check_win = QtCore.QTimer()
        self.timer_check_win.timeout.connect(self.check_begin)
        self.timer_check_win.start(100)

    def check_begin(self):
        if len(self.rects) == len(self.all_rects):
            self.reset_button.setDisabled(True)
        else:
            self.reset_button.setDisabled(False)


class TargetStack(Stack):
    def __init__(self, rect: QtCore.QRectF, rects, timeing, timer_global, main_window):
        super().__init__(rect, rects)
        self.color = QtCore.Qt.GlobalColor.magenta
        self.timeing, self.timer_global, self.main_window = timeing, timer_global, main_window
        self.all_rects = rects
        self.timer_check_win = QtCore.QTimer()
        self.timer_check_win.timeout.connect(lambda: self.check_win(self.timeing))
        self.timer_check_win.start(500)

    def check_win(self, time: QtCore.QTime):
        if len(self.rects) == len(self.all_rects):
            self.timer_global.stop()
            QtWidgets.QMessageBox.warning(self.main_window, '游戏提示',
                                          f'游戏结束\nGrade: {time.toString("hh:mm:ss")}',
                                          QtWidgets.QMessageBox.StandardButton.Ok)
            sys.exit(0)
