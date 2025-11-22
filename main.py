from PyQt6 import QtWidgets
from ui_main_window import Ui_MainWindow
import sys

from PyQt6 import QtGui

class MainApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Grid setup
        self.rows = 10
        self.cols = 10
        self.ui.dungeonWidget.setRowCount(self.rows)
        self.ui.dungeonWidget.setColumnCount(self.cols)
        self.ui.dungeonWidget.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers) # disable text editing in grids
        self.ui.dungeonWidget.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.NoSelection) # disable selection
        

        for i in range(self.rows):
            self.ui.dungeonWidget.setRowHeight(i, 60)
        for j in range(self.cols):
            self.ui.dungeonWidget.setColumnWidth(j, 60)

        # Fill cells white initially
        for i in range(self.rows):
            for j in range(self.cols):
                item = QtWidgets.QTableWidgetItem()
                item.setBackground(QtGui.QColor("white"))
                self.ui.dungeonWidget.setItem(i, j, item)

        # Connect cell click
        self.ui.dungeonWidget.cellClicked.connect(self.cell_clicked)

        # Initialize data structure
        self.cell_data = [["white" for _ in range(self.cols)] for _ in range(self.rows)]

    # Update cell_clicked
    def cell_clicked(self, row, col):
        # Toggle color in data
        current_color = self.cell_data[row][col]
        new_color = "red" if current_color == "white" else "white"
        self.cell_data[row][col] = new_color

        # Update UI
        self.ui.dungeonWidget.item(row, col).setBackground(QtGui.QColor(new_color))


app = QtWidgets.QApplication(sys.argv)
window = MainApp()
window.show()
sys.exit(app.exec())
