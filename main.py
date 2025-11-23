from PyQt6 import QtWidgets, QtCore, QtGui
from ui_main_window import Ui_MainWindow
import sys


class MainApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.load_stylesheet("style.qss")

        # Grid setup
        self.rows = 10
        self.cols = 10
        self.ui.dungeonWidget.setRowCount(self.rows)
        self.ui.dungeonWidget.setColumnCount(self.cols)
        self.ui.dungeonWidget.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.ui.dungeonWidget.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.NoSelection)
        self.ui.dungeonWidget.horizontalHeader().setVisible(False)
        self.ui.dungeonWidget.verticalHeader().setVisible(False)
        self.ui.dungeonWidget.setShowGrid(False)
        self.ui.dungeonWidget.setMaximumSize(QtCore.QSize(606, 606))
        self.ui.searchComboBox.addItems(["BFS", "DFS", "Dijkstra", "A*"])

        for i in range(self.rows):
            self.ui.dungeonWidget.setRowHeight(i, 60)
        for j in range(self.cols):
            self.ui.dungeonWidget.setColumnWidth(j, 60)

        # Fill cells
        for i in range(self.rows):
            for j in range(self.cols):
                item = QtWidgets.QTableWidgetItem()
                item.setBackground(QtGui.QColor("brown"))
                self.ui.dungeonWidget.setItem(i, j, item)

        self.ui.dungeonWidget.cellClicked.connect(self.cell_clicked)
        self.cell_data = [["brown" for _ in range(self.cols)] for _ in range(self.rows)]

        # Create player & controller
        QtCore.QTimer.singleShot(0, self.setup_game)

    def setup_game(self):
        """Create Player and GameController after UI is loaded."""
        self.player = Player(self.ui.centralwidget, self.ui.dungeonWidget)
        self.controller = GameController(self.player, self)

        # Button to trigger path movement
        self.ui.moveButton.clicked.connect(self.controller.start_movement)

    def cell_clicked(self, row, col):
        current = self.cell_data[row][col]
        new_color = "grey" if current == "brown" else "brown"
        self.cell_data[row][col] = new_color
        self.ui.dungeonWidget.item(row, col).setBackground(QtGui.QColor(new_color))

    def load_stylesheet(self, file_path):
        with open(file_path, "r") as f:
            self.setStyleSheet(f.read())


# ---------------------------- PLAYER CLASS ----------------------------

class Player(QtWidgets.QWidget):
    def __init__(self, parent, table_widget, row=0, col=0, color="lime", size=45):
        super().__init__(parent)
        self.table = table_widget
        self.row = row
        self.col = col
        self.cell_size = size

        self.setFixedSize(size, size)
        self.setStyleSheet(f"background-color: {color}; border-radius: 10px;")
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_StyledBackground, True)

        self.animation = QtCore.QPropertyAnimation(self, b"pos")
        self.animation.setDuration(250)
        self.animation.setEasingCurve(QtCore.QEasingCurve.Type.InOutQuad)

        self.place_at(row, col)
        self.show()
        self.raise_()

    def place_at(self, row, col):
        table_pos = self.table.mapTo(self.parent(), QtCore.QPoint(0, 0))
        x = table_pos.x() + col * self.table.columnWidth(0) + 10
        y = table_pos.y() + row * self.table.rowHeight(0) + 10
        self.move(x, y)
        self.row = row
        self.col = col

    def animate_move(self, row, col):
        table_pos = self.table.mapTo(self.parent(), QtCore.QPoint(0, 0))
        end_pos = QtCore.QPoint(
            table_pos.x() + col * self.table.columnWidth(0) + 10,
            table_pos.y() + row * self.table.rowHeight(0) + 10
        )
        self.animation.stop()
        self.animation.setStartValue(self.pos())
        self.animation.setEndValue(end_pos)
        self.animation.start()
        self.row, self.col = row, col
        self.raise_()


# ---------------------------- GAME CONTROLLER ----------------------------

class GameController:
    def __init__(self, player, main_app):
        self.player = player
        self.table = main_app.ui.dungeonWidget
        self.main_app = main_app
        self.timer = QtCore.QTimer()
        self.timer.setInterval(300)
        self.timer.timeout.connect(self.move_step)
        self.path = []  # Will be filled by Pathfinder

    def start_movement(self):
        """Ask Pathfinder for path and begin moving."""
        algorithm = self.main_app.ui.searchComboBox.currentText()
        print(f"Using algorithm: {algorithm}")
        self.path = Pathfinder.get_path(self.player.row, self.player.col, algorithm)  # TODO
        if not self.path:
            print("No path returned!")
            return
        self.timer.start()

    def move_step(self):
        if not self.path:
            self.timer.stop()
            return
        next_row, next_col = self.path.pop(0)
        self.player.animate_move(next_row, next_col)


# ---------------------------- PATHFINDER ----------------------------

class Pathfinder:
    @staticmethod
    def get_path(start_row, start_col, algorithm):
       
        # TODO: implement search algorithms
        print(f"Finding path from ({start_row}, {start_col}) using {algorithm}")
        return [(0,1),(0,2)]  # placeholder
    


# ---------------------------- RUN APP ----------------------------

app = QtWidgets.QApplication(sys.argv)
window = MainApp()
window.show()
sys.exit(app.exec())
