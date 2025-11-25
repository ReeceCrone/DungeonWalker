from PyQt6 import QtWidgets, QtCore, QtGui
import sys



# ======================= MODEL =======================

class GridModel:
    """Holds the logical state of the dungeon grid."""
    def __init__(self, rows, cols, default_color="brown"):
        self.rows = rows
        self.cols = cols
        self.grid = [[default_color for _ in range(cols)] for _ in range(rows)]

    def toggle_cell(self, row, col):
        """Toggle between brown and grey."""
        self.grid[row][col] = "grey" if self.grid[row][col] == "brown" else "brown"
        return self.grid[row][col]

    def get_cell_color(self, row, col):
        return self.grid[row][col]
    
    def reset_grid(self):
        for i in range(self.rows):
            for j in range(self.cols):
                self.grid[i][j] = "brown"


class PlayerModel:
    """Holds player's logical position."""
    def __init__(self, row=0, col=0):
        self.row = row
        self.col = col

    def update_position(self, row, col):
        self.row, self.col = row, col

# ======================= VIEW =======================

class DungeonView(QtWidgets.QTableWidget):
    cellClickedSignal = QtCore.pyqtSignal(int, int)

    def __init__(self, rows, cols):
        super().__init__(rows, cols)
        self.configure_table()

    def configure_table(self):
        self.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.NoSelection)
        self.horizontalHeader().setVisible(False)
        self.verticalHeader().setVisible(False)
        self.setShowGrid(False)

        for i in range(self.rowCount()):
            self.setRowHeight(i, 60)
        for j in range(self.columnCount()):
            self.setColumnWidth(j, 60)

        # Fill with items
        for i in range(self.rowCount()):
            for j in range(self.columnCount()):
                self.setItem(i, j, QtWidgets.QTableWidgetItem())

        self.cellClicked.connect(self.cellClickedSignal.emit)

    def update_cell_color(self, row, col, color):
        self.item(row, col).setBackground(QtGui.QColor(color))


class Player(QtWidgets.QWidget):
    """Visual representation of the player."""
    def __init__(self, parent, table_widget, model, size=45):
        super().__init__(parent)
        self.table = table_widget
        self.model = model
        self.cell_size = size

        # Appearance
        self.setFixedSize(size, size)
        self.setStyleSheet("background-color: lime; border-radius: 10px;")
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_StyledBackground, True)

        # Animation setup
        self.animation = QtCore.QPropertyAnimation(self, b"pos")
        self.animation.setDuration(250)
        self.animation.setEasingCurve(QtCore.QEasingCurve.Type.InOutQuad)

        QtCore.QTimer.singleShot(0, lambda: self.place_at(0, 0))

        self.show()
        self.raise_()

    def place_at(self, row, col):
        table_pos = self.table.mapTo(self.parent(), QtCore.QPoint(0, 0))
        print(self.table.columnWidth(0), self.table.rowHeight(0))
        x = table_pos.x() + col * self.table.columnWidth(0) + 10
        y = table_pos.y() + row * self.table.rowHeight(0) + 10
        self.move(x, y)

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
        self.raise_()


# ======================= CONTROLLER =======================

class GameController:
    def __init__(self, grid_model, player_model, dungeon_view, player_widget, main_window):
        self.grid_model = grid_model
        self.player_model = player_model
        self.view = dungeon_view
        self.player_widget = player_widget
        self.main_window = main_window

        # Handle cell clicks
        self.view.cellClickedSignal.connect(self.handle_cell_click)

        # Movement timer
        self.timer = QtCore.QTimer()
        self.timer.setInterval(300)
        self.timer.timeout.connect(self.move_step)
        self.path = []

    def handle_cell_click(self, row, col):
        new_color = self.grid_model.toggle_cell(row, col)
        self.view.update_cell_color(row, col, new_color)

    def start_movement(self):
        algorithm = self.main_window.searchComboBox.currentText()
        self.path = Pathfinder.get_path(self.player_model.row, self.player_model.col, algorithm)
        if not self.path:
            print("No path found.")
            return
        self.main_window.moveButton.setEnabled(False)
        self.timer.start()

    def reset_obstacles(self):
        self.grid_model.reset_grid()
        # Update the view to reflect the reset
        for i in range(self.grid_model.rows):
            for j in range(self.grid_model.cols):
                self.view.update_cell_color(i, j, "brown")

    def move_step(self):
        if not self.path:
            self.timer.stop()
            self.main_window.moveButton.setEnabled(True)
            return

        next_row, next_col = self.path.pop(0)
        self.player_model.update_position(next_row, next_col)
        self.player_widget.animate_move(next_row, next_col)


# ======================= SEARCH / PATHFINDING =======================

class Pathfinder:
    @staticmethod
    def get_path(start_row, start_col, algorithm):
        print(f"Pathfinding using {algorithm} from ({start_row}, {start_col})")
        # TODO: Implement pathfinding here
        return [(start_row, i) for i in range(1, 10)]  # Example


# ======================= MAIN WINDOW =======================

class MainApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(800, 800)
        self.setWindowTitle("Dungeon Walker")
        self.load_stylesheet("style.qss")




        # --- Basic UI ---
        central = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(central)
        button_layout = QtWidgets.QHBoxLayout()
        algo_layout = QtWidgets.QHBoxLayout()
        self.setCentralWidget(central)

        self.titleLabel = QtWidgets.QLabel("DUNGEON WALKER")
        font = QtGui.QFont("Arial", 24, QtGui.QFont.Weight.Bold)
        self.titleLabel.setFont(font)
        self.titleLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        self.algoLabel = QtWidgets.QLabel("Select Search Algorithm:")
        self.algoLabel.setFont(QtGui.QFont("Arial", 14))
        

        self.searchComboBox = QtWidgets.QComboBox()
        self.searchComboBox.addItems(["BFS", "DFS", "Dijkstra", "A*"])
        
        self.moveButton = QtWidgets.QPushButton("Move Player")
 
        self.resetButton = QtWidgets.QPushButton("Reset Player")

        self.clearButton = QtWidgets.QPushButton("Clear Obstacles")
  

        button_layout.addWidget(self.moveButton)
        button_layout.addWidget(self.resetButton)  
        button_layout.addWidget(self.clearButton)


        # --- Grid ---
        rows, cols = 10, 10
        self.grid_model = GridModel(rows, cols)
        self.dungeonView = DungeonView(rows, cols)
        
        self.dungeonView.setMaximumSize(QtCore.QSize(606, 606))
        self.dungeonView.setMinimumSize(QtCore.QSize(606, 606))


        #Algorithm layout
        algo_layout.addWidget(self.algoLabel)
        algo_layout.addWidget(self.searchComboBox)
        algo_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
    


        # Layout
        layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)
        layout.addWidget(self.titleLabel)
        layout.addWidget(self.dungeonView)
        layout.addLayout(button_layout)
        layout.addLayout(algo_layout)
  
       

        # Player setup
        self.player_model = PlayerModel()
        self.player_widget = Player(self, self.dungeonView, self.player_model)

        # Controller
        self.controller = GameController(
            self.grid_model, self.player_model,
            self.dungeonView, self.player_widget, self
        )

        self.moveButton.clicked.connect(self.controller.start_movement)
        self.clearButton.clicked.connect(self.controller.reset_obstacles)
    
    
    def load_stylesheet(self, file_path):
        with open(file_path, "r") as f:
            self.setStyleSheet(f.read())

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "player_widget"):  # Make sure player widget exists
            self.player_widget.place_at(
                self.player_model.row,
                self.player_model.col
        )


# ======================= EXECUTION =======================

app = QtWidgets.QApplication(sys.argv)
window = MainApp()
window.show()
sys.exit(app.exec())