from PyQt6 import QtWidgets
from PyQt6 import QtCore
from ui_main_window import Ui_MainWindow
import sys

from PyQt6 import QtGui



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
        self.ui.dungeonWidget.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers) # disable text editing in grids
        self.ui.dungeonWidget.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.NoSelection) # disable selection
        self.ui.dungeonWidget.horizontalHeader().setVisible(False) # hide headers
        self.ui.dungeonWidget.verticalHeader().setVisible(False)
        self.ui.dungeonWidget.setShowGrid(False) # hide grid lines
        self.ui.dungeonWidget.setMaximumSize(QtCore.QSize(606, 606))


        for i in range(self.rows):
            self.ui.dungeonWidget.setRowHeight(i, 60)
        for j in range(self.cols):
            self.ui.dungeonWidget.setColumnWidth(j, 60)

        # Fill cells white initially
        for i in range(self.rows):
            for j in range(self.cols):
                item = QtWidgets.QTableWidgetItem()
                item.setBackground(QtGui.QColor("brown"))
                self.ui.dungeonWidget.setItem(i, j, item)

        # Connect cell click
        self.ui.dungeonWidget.cellClicked.connect(self.cell_clicked)
    

        # Initialize data structure
        self.cell_data = [["brown" for _ in range(self.cols)] for _ in range(self.rows)]

        # Timer for movement
        self.timer = QtCore.QTimer()
        self.timer.setInterval(400)  # milliseconds
        self.timer.timeout.connect(self.move_cube_step)

        # Move button starts movement
        self.ui.moveButton.clicked.connect(self.start_player_move)
        
        # Create player after window is shown (using QTimer.singleShot)
        QtCore.QTimer.singleShot(0, self.create_player)
    
    def create_player(self):
        """Create the player after the layout is complete"""
        self.player = Player(self.ui.centralwidget, self.ui.dungeonWidget)
        self.player.show()
        self.player.raise_()
        
        # Debug output
        print(f"Player position: {self.player.pos()}")
        print(f"Player size: {self.player.size()}")
        print(f"Player visible: {self.player.isVisible()}")
        print(f"Dungeon position: {self.ui.dungeonWidget.pos()}")
        print(f"Dungeon size: {self.ui.dungeonWidget.size()}")



    def start_player_move(self):
        self.timer.start()

    def move_cube_step(self):
        next_row = self.player.row
        next_col = self.player.col + 1

        if next_col >= self.cols:
            next_col = 0
            next_row += 1

        if next_row >= self.rows:
            self.timer.stop()
            return

        # Animate player
        self.player.move_to(next_row, next_col)

    # Update cell_clicked
    def cell_clicked(self, row, col):
        # Toggle color in data
        current_color = self.cell_data[row][col]
        new_color = "grey" if current_color == "brown" else "brown"
        self.cell_data[row][col] = new_color

        # Update UI
        self.ui.dungeonWidget.item(row, col).setBackground(QtGui.QColor(new_color))
        print(f"Cell ({row}, {col}) changed to {new_color}")

    
    def load_stylesheet(self, file_path):
        with open(file_path, "r") as f:
            style = f.read()
            self.setStyleSheet(style)




class Player(QtWidgets.QWidget):
    def __init__(self, parent, table_widget, row=0, col=0, color="green", size=60):
        super().__init__(parent)
        self.table = table_widget
        self.cell_size = size

        # Cube appearance
        self.setFixedSize(size, size)
        self.setStyleSheet(f"background-color: {color}; border-radius: 5px;")
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_StyledBackground, True)  # Ensure background is painted
        self.show()
        

        # Position on the table
        self.row = row
        self.col = col
        self.place_at(self.row, self.col)
        self.raise_()

        # Animation object
        self.animation = QtCore.QPropertyAnimation(self, b"pos")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QtCore.QEasingCurve.Type.InOutQuad)

    def place_at(self, row, col):
        """Move player to a table cell"""
        table_pos = self.table.mapTo(self.parent(), QtCore.QPoint(0, 0))
        x = table_pos.x() + col * self.table.columnWidth(0)
        y = table_pos.y() + row * self.table.rowHeight(0)
        print(f"Player place_at: table_pos={table_pos}, x={x}, y={y}")
        self.move(x, y)
        self.row = row
        self.col = col

    def move_to(self, row, col):
        """Animate player to new cell"""
        table_pos = self.table.mapTo(self.parent(), QtCore.QPoint(0, 0))
        end_pos = QtCore.QPoint(
            table_pos.x() + col * self.table.columnWidth(0),
            table_pos.y() + row * self.table.rowHeight(0)
        )
        self.animation.stop()
        self.animation.setStartValue(self.pos())
        self.animation.setEndValue(end_pos)
        self.animation.start()
        self.row = row
        self.col = col
        self.raise_()  # Ensure player stays on top after moving



app = QtWidgets.QApplication(sys.argv)
window = MainApp()
window.show()

sys.exit(app.exec())
