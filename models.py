from PyQt6 import QtCore


class GridModel(QtCore.QObject):
    updateSignal = QtCore.pyqtSignal()
    """Holds the logical state of the dungeon grid."""
    def __init__(self, rows, cols, default_color="brown"):
        super().__init__()
        self.rows = rows
        self.cols = cols
        self.grid = [[default_color for _ in range(cols)] for _ in range(rows)]

    def toggle_cell(self, row, col):
        """Cycle through tile types: brown (normal) -> #652921 (difficult) -> grey (obstacle) -> brown."""
        current = self.grid[row][col]
        if current == "brown":
            self.grid[row][col] = "maroon"
        elif current == "maroon":
            self.grid[row][col] = "grey"
        else:  # grey
            self.grid[row][col] = "brown"
        self.updateSignal.emit()
        return self.grid[row][col]

    def get_cell_color(self, row, col):
        return self.grid[row][col]
    
    def get_cell_cost(self, row, col):
        """Get movement cost for a cell. Grey (obstacle) returns None."""
        color = self.grid[row][col]
        if color == "grey":
            return None  # Impassable
        elif color == "maroon":
            return 3  # Difficult terrain
        else:  # brown
            return 1  # Normal terrain
    
    def reset_grid(self):
        for i in range(self.rows):
            for j in range(self.cols):
                self.grid[i][j] = "brown"
        self.updateSignal.emit()


class PlayerModel:
    """Holds player's logical position."""
    def __init__(self, row=0, col=0):
        self.row = row
        self.col = col

    def update_position(self, row, col):
        self.row, self.col = row, col

    def reset_position(self):
        self.row, self.col = 0, 0
