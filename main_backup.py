from PyQt6 import QtWidgets, QtCore, QtGui
import sys
from models import GridModel, PlayerModel
from views import DungeonView, Player, PathOverlay
from controller import GameController
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






# ======================= VIEW =======================

class DungeonView(QtWidgets.QTableWidget):
    cellClickedSignal = QtCore.pyqtSignal(int, int)
    cellDraggedSignal = QtCore.pyqtSignal(int, int)

    def __init__(self, rows, cols, grid_model):
        super().__init__(rows, cols)
        self.configure_table()
        self.grid_model = grid_model
        grid_model.updateSignal.connect(self.draw_grid)
        
        # Track mouse dragging
        self.is_dragging = False
        self.last_cell = None
        self.setMouseTracking(True)


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
    
    def mousePressEvent(self, event):
        """Start dragging when mouse is pressed"""
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.is_dragging = True
            item = self.itemAt(event.pos())
            if item:
                row = self.row(item)
                col = self.column(item)
                self.last_cell = (row, col)
                self.cellClickedSignal.emit(row, col)
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """Paint cells while dragging"""
        if self.is_dragging:
            item = self.itemAt(event.pos())
            if item:
                row = self.row(item)
                col = self.column(item)
                # Only emit if we moved to a different cell
                if (row, col) != self.last_cell:
                    self.last_cell = (row, col)
                    self.cellDraggedSignal.emit(row, col)
        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        """Stop dragging when mouse is released"""
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.is_dragging = False
            self.last_cell = None
        super().mouseReleaseEvent(event)

    def update_cell_color(self, row, col, color):
        self.item(row, col).setBackground(QtGui.QColor(color))

    def draw_grid(self):
        for i in range(self.grid_model.rows):
            for j in range(self.grid_model.cols):
                color = self.grid_model.get_cell_color(i, j)
                self.update_cell_color(i, j, color)



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

    # Place player at specific cell without animation
    def place_at(self, row, col):
        table_pos = self.table.mapTo(self.parent(), QtCore.QPoint(0, 0))
        print(self.table.columnWidth(0), self.table.rowHeight(0))
        x = table_pos.x() + col * self.table.columnWidth(0) + 10
        y = table_pos.y() + row * self.table.rowHeight(0) + 10
        self.move(x, y)

    # Animate movement to new cell
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


class PathOverlay(QtWidgets.QWidget):
    """Overlay widget to display visited cells and final path"""
    def __init__(self, parent, table_widget):
        super().__init__(parent)
        self.table = table_widget
        self.visited_cells = []
        self.final_path = []
        self.cell_size = 60
        
        # Make background transparent
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        
        # Position overlay over the table
        QtCore.QTimer.singleShot(0, self.position_overlay)
        
        self.show()
    
    def position_overlay(self):
        """Position and size the overlay to match the table"""
        table_pos = self.table.mapTo(self.parent(), QtCore.QPoint(0, 0))
        self.setGeometry(table_pos.x(), table_pos.y(), 
                        self.table.width(), self.table.height())
    
    def add_visited_cell(self, row, col):
        """Add a cell to the visited list"""
        if (row, col) not in self.visited_cells:
            self.visited_cells.append((row, col))
            self.update()
    
    def set_final_path(self, path):
        """Set the final path to display"""
        self.final_path = path
        self.update()
    
    def clear(self):
        """Clear all overlays"""
        self.visited_cells = []
        self.final_path = []
        self.update()
    
    def paintEvent(self, event):
        """Draw the visited cells and final path"""
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        
        # Draw visited cells in semi-transparent light blue
        painter.setBrush(QtGui.QColor(173, 216, 230, 100))  # lightblue with alpha
        painter.setPen(QtCore.Qt.PenStyle.NoPen)
        
        for row, col in self.visited_cells:
            x = col * self.cell_size + 11
            y = row * self.cell_size + 11
            painter.drawRect(x, y, self.cell_size - 20, self.cell_size - 20)
        
        # Draw final path in semi-transparent cyan
        painter.setBrush(QtGui.QColor(0, 255, 255, 150))  # cyan with alpha
        
        for row, col in self.final_path:
            x = col * self.cell_size + 16
            y = row * self.cell_size + 16
            painter.drawRect(x, y, self.cell_size - 30, self.cell_size - 30)








# ======================= CONTROLLER =======================

class GameController:
    def __init__(self, grid_model, player_model, dungeon_view, player_widget, path_overlay, main_window):
        self.grid_model = grid_model
        self.player_model = player_model
        self.view = dungeon_view
        self.player_widget = player_widget
        self.path_overlay = path_overlay
        self.main_window = main_window

        # Handle cell clicks and dragging
        self.view.cellClickedSignal.connect(self.handle_cell_click)
        self.view.cellDraggedSignal.connect(self.handle_cell_drag)
        
        # Track paint mode for dragging
        self.paint_color = None

        # Movement timer
        self.timer = QtCore.QTimer()
        self.timer.setInterval(300)
        self.timer.timeout.connect(self.move_step)
        self.path = []
        self.final_path = []  # Store the optimal path
        self.visited_cells = []  # Store cells visited during search

    def handle_cell_click(self, row, col):
        # Get selected brush mode
        brush_id = self.main_window.brush_group.checkedId()
        
        if brush_id == 0:  # Toggle mode
            new_color = self.grid_model.toggle_cell(row, col)
            self.view.update_cell_color(row, col, new_color)
            self.paint_color = new_color
        elif brush_id == 1:  # Normal (brown)
            self.grid_model.grid[row][col] = "brown"
            self.view.update_cell_color(row, col, "brown")
            self.paint_color = "brown"
        elif brush_id == 2:  # Difficult (maroon)
            self.grid_model.grid[row][col] = "maroon"
            self.view.update_cell_color(row, col, "maroon")
            self.paint_color = "maroon"
        elif brush_id == 3:  # Obstacle (grey)
            self.grid_model.grid[row][col] = "grey"
            self.view.update_cell_color(row, col, "grey")
            self.paint_color = "grey"
    
    def handle_cell_drag(self, row, col):
        # Paint with the same color as the initial click
        if self.paint_color is not None:
            self.grid_model.grid[row][col] = self.paint_color
            self.view.update_cell_color(row, col, self.paint_color)

    def start_movement(self):
        algorithm = self.main_window.searchComboBox.currentText()
        result = Pathfinder.get_path(self.player_model.row, self.player_model.col, algorithm, self.grid_model)
        if not result:
            print("No path found.")
            return
        
        # Result contains both search history and final path
        self.path = result['search_history']
        self.final_path = result['final_path']
        self.visited_cells = []
        
        if not self.path:
            print("No path found.")
            return
        self.main_window.moveButton.setEnabled(False)
        self.main_window.resetButton.setEnabled(False)
        self.main_window.clearButton.setEnabled(False)
        self.timer.start()

    def reset_obstacles(self):
        self.grid_model.reset_grid()
        # Update the view to reflect the reset
        for i in range(self.grid_model.rows):
            for j in range(self.grid_model.cols):
                self.view.update_cell_color(i, j, "brown")

    def reset_player(self):
        self.player_model.reset_position()
        self.player_widget.place_at(0, 0)
        self.path_overlay.clear()  # Clear the overlay

    def move_step(self):
        if not self.path:
            self.timer.stop()
            # Show the final optimal path on overlay
            self.path_overlay.set_final_path(self.final_path)
            self.main_window.moveButton.setEnabled(True)
            self.main_window.resetButton.setEnabled(True)
            self.main_window.clearButton.setEnabled(True)
            return

        next_row, next_col = self.path.pop(0)
        
        # Add visited cell to overlay
        self.path_overlay.add_visited_cell(next_row, next_col)
        
        self.player_model.update_position(next_row, next_col)
        self.player_widget.animate_move(next_row, next_col)







# ======================= SEARCH / PATHFINDING =======================

class Pathfinder:
    @staticmethod
    def get_path(start_row, start_col, algorithm, grid_model):
        print(f"Pathfinding using {algorithm} from ({start_row}, {start_col})")
        match algorithm:
            case "BFS":
                return Pathfinder.bfs(start_row, start_col, grid_model)
            case "DFS":
                return Pathfinder.dfs(start_row, start_col, grid_model)
            case "Dijkstra":
                return Pathfinder.dijkstra(start_row, start_col, grid_model)
            case "A*":
                return Pathfinder.a_star(start_row, start_col, grid_model)
            
    @staticmethod
    def bfs(start_row, start_col, grid_model):
        """Breadth-First Search pathfinding - returns search history and final path"""
        from collections import deque
        
        rows, cols = grid_model.rows, grid_model.cols
        goal_row, goal_col = rows - 1, cols - 1  # Bottom-right corner
        
        # BFS uses a queue
        queue = deque([(start_row, start_col)])
        visited = set()
        visited.add((start_row, start_col))
        parent = {}  # To reconstruct path
        search_history = []  # Track every cell visited in order
        
        # Directions: up, down, left, right
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        
        while queue:
            row, col = queue.popleft()
            search_history.append((row, col))  # Add to search history
            
            # Check if we reached the goal
            if row == goal_row and col == goal_col:
                # Reconstruct the optimal path
                final_path = []
                current = (goal_row, goal_col)
                while current in parent:
                    final_path.append(current)
                    current = parent[current]
                final_path.append((start_row, start_col))
                final_path.reverse()
                
                return {
                    'search_history': search_history,
                    'final_path': final_path
                }
            
            # Explore neighbors
            for dr, dc in directions:
                new_row, new_col = row + dr, col + dc
                
                # Check bounds
                if 0 <= new_row < rows and 0 <= new_col < cols:
                    # Check if not visited and not an obstacle (grey)
                    if (new_row, new_col) not in visited and grid_model.get_cell_color(new_row, new_col) != "grey":
                        visited.add((new_row, new_col))
                        parent[(new_row, new_col)] = (row, col)
                        queue.append((new_row, new_col))
        
        # No path found
        return {'search_history': search_history, 'final_path': []}
    
    @staticmethod
    def dfs(start_row, start_col, grid_model):
        """Depth-First Search pathfinding - returns search history and final path"""
        stack = [(start_row, start_col)]
        visited = set()
        search_history = []
        parent = {}  # Track parent for path reconstruction
        
        rows, cols = grid_model.rows, grid_model.cols
        goal_row, goal_col = rows - 1, cols - 1  # Bottom-right corner
        
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        while stack:
            row, col = stack.pop()
            if (row, col) in visited:
                continue
            visited.add((row, col))
            search_history.append((row, col))

            # Check if we reached the goal
            if row == goal_row and col == goal_col:
                # Reconstruct path
                final_path = []
                current = (goal_row, goal_col)
                while current in parent:
                    final_path.append(current)
                    current = parent[current]
                final_path.append((start_row, start_col))
                final_path.reverse()
                
                return {
                    'search_history': search_history,
                    'final_path': final_path
                }

            # Explore neighbors
            for dr, dc in directions:
                new_row, new_col = row + dr, col + dc

                # Check bounds
                if 0 <= new_row < rows and 0 <= new_col < cols:
                    # Check if not visited and not an obstacle (grey)
                    if (new_row, new_col) not in visited and grid_model.get_cell_color(new_row, new_col) != "grey":
                        if (new_row, new_col) not in parent:
                            parent[(new_row, new_col)] = (row, col)
                        stack.append((new_row, new_col))
        
        return {'search_history': search_history, 'final_path': []}

    
    @staticmethod
    def dijkstra(start_row, start_col, grid_model):
        """Dijkstra's algorithm - finds shortest path with weighted costs"""
        import heapq
        
        rows, cols = grid_model.rows, grid_model.cols
        goal_row, goal_col = rows - 1, cols - 1
        
        # Priority queue: (cost, row, col)
        pq = [(0, start_row, start_col)]
        visited = set()
        search_history = []
        costs = {(start_row, start_col): 0}
        parent = {}  # Track parent for path reconstruction
        
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        
        while pq:
            current_cost, row, col = heapq.heappop(pq)
            
            if (row, col) in visited:
                continue
            
            visited.add((row, col))
            search_history.append((row, col))
            
            # Check if goal reached
            if row == goal_row and col == goal_col:
                # Reconstruct path
                final_path = []
                current = (goal_row, goal_col)
                while current in parent:
                    final_path.append(current)
                    current = parent[current]
                final_path.append((start_row, start_col))
                final_path.reverse()
                
                return {
                    'search_history': search_history,
                    'final_path': final_path
                }
            
            # Explore neighbors
            for dr, dc in directions:
                new_row, new_col = row + dr, col + dc
                
                if 0 <= new_row < rows and 0 <= new_col < cols:
                    if (new_row, new_col) not in visited:
                        move_cost = grid_model.get_cell_cost(new_row, new_col)
                        if move_cost is not None:
                            new_cost = current_cost + move_cost
                            
                            if (new_row, new_col) not in costs or new_cost < costs[(new_row, new_col)]:
                                costs[(new_row, new_col)] = new_cost
                                parent[(new_row, new_col)] = (row, col)
                                heapq.heappush(pq, (new_cost, new_row, new_col))
        
        return {'search_history': search_history, 'final_path': []}
    
    @staticmethod
    def a_star(start_row, start_col, grid_model):
        """A* algorithm - finds shortest path using heuristic (Manhattan distance)"""
        import heapq
        
        rows, cols = grid_model.rows, grid_model.cols
        goal_row, goal_col = rows - 1, cols - 1
        
        # Heuristic function: Manhattan distance to goal
        def heuristic(row, col):
            return abs(row - goal_row) + abs(col - goal_col)
        
        # Priority queue: (f_score, g_score, row, col)
        start_h = heuristic(start_row, start_col)
        pq = [(start_h, 0, start_row, start_col)]
        visited = set()
        search_history = []
        g_scores = {(start_row, start_col): 0}
        parent = {}  # Track parent for path reconstruction
        
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        
        while pq:
            f_score, g_score, row, col = heapq.heappop(pq)
            
            if (row, col) in visited:
                continue
            
            visited.add((row, col))
            search_history.append((row, col))
            
            # Check if goal reached
            if row == goal_row and col == goal_col:
                # Reconstruct path
                final_path = []
                current = (goal_row, goal_col)
                while current in parent:
                    final_path.append(current)
                    current = parent[current]
                final_path.append((start_row, start_col))
                final_path.reverse()
                
                return {
                    'search_history': search_history,
                    'final_path': final_path
                }
            
            # Explore neighbors
            for dr, dc in directions:
                new_row, new_col = row + dr, col + dc
                
                if 0 <= new_row < rows and 0 <= new_col < cols:
                    if (new_row, new_col) not in visited:
                        move_cost = grid_model.get_cell_cost(new_row, new_col)
                        if move_cost is not None:
                            new_g_score = g_score + move_cost
                            
                            if (new_row, new_col) not in g_scores or new_g_score < g_scores[(new_row, new_col)]:
                                g_scores[(new_row, new_col)] = new_g_score
                                parent[(new_row, new_col)] = (row, col)
                                h_score = heuristic(new_row, new_col)
                                f_score = new_g_score + h_score
                                heapq.heappush(pq, (f_score, new_g_score, new_row, new_col))
        
        return {'search_history': search_history, 'final_path': []}






# ======================= MAIN WINDOW =======================

class MainApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(800, 800)
        self.setWindowTitle("Dungeon Walker")
        self.setStyleSheet("""
            QWidget {
                background-color: #ddd;
            }
            
            QTableWidget {
                border: 2px solid black;
                border-radius: 10px;
                background-color: brown;
            }
            
            QTableWidget::item:hover {
                border-radius: 5px;
                background-color: #555;
            }
            
            QPushButton:disabled {
                background-color: #222;
                color: #888;
                border-radius: 6px;
                padding: 6px;
            }
            
            QPushButton:enabled {
                background-color: #fc0;
                color: black;
                border: 3px solid black;
                padding: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            
            QPushButton:hover {
                background-color: #a82;
            }
            
            QComboBox {
                background-color: #fc0;
                border: 3px solid black;
                padding: 6px;
                color: black;
                font-weight: bold;
                font-size: 14px;
            }
        """)


        # --- Basic UI ---
        central = QtWidgets.QWidget()
        main_layout = QtWidgets.QHBoxLayout(central)  # Changed to horizontal for side panel
        left_layout = QtWidgets.QVBoxLayout()
        button_layout = QtWidgets.QHBoxLayout()
        algo_layout = QtWidgets.QHBoxLayout()
        self.setCentralWidget(central)

        self.titleLabel = QtWidgets.QLabel("Dungeon Walker")
        font = QtGui.QFont("Roboto mono", 24, QtGui.QFont.Weight.ExtraBold)
        font.setItalic(True)
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


        #Grid
        rows, cols = 10, 10
        self.grid_model = GridModel(rows, cols)
        self.dungeonView = DungeonView(rows, cols, self.grid_model)
        
        self.dungeonView.setMaximumSize(QtCore.QSize(606, 606))
        self.dungeonView.setMinimumSize(QtCore.QSize(606, 606))


        #Algorithm layout
        algo_layout.addWidget(self.algoLabel)
        algo_layout.addWidget(self.searchComboBox)
        algo_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
    

        #Brush Selector Panel
        brush_panel = QtWidgets.QWidget()
        brush_panel.setMaximumWidth(200)
        brush_layout = QtWidgets.QVBoxLayout(brush_panel)
        
        brush_title = QtWidgets.QLabel("Terrain Brush")
        brush_title.setFont(QtGui.QFont("Arial", 16, QtGui.QFont.Weight.Bold))
        brush_title.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        brush_layout.addWidget(brush_title)
        
        # Radio buttons for brush selection
        self.brush_group = QtWidgets.QButtonGroup()
        
        self.toggleBrush = QtWidgets.QRadioButton("Toggle Mode")
        self.toggleBrush.setChecked(True)
        self.brush_group.addButton(self.toggleBrush, 0)
        
        self.normalBrush = QtWidgets.QRadioButton("Normal (Brown)")
        self.brush_group.addButton(self.normalBrush, 1)
        
        self.difficultBrush = QtWidgets.QRadioButton("Difficult (Maroon)")
        self.brush_group.addButton(self.difficultBrush, 2)
        
        self.obstacleBrush = QtWidgets.QRadioButton("Obstacle (Grey)")
        self.brush_group.addButton(self.obstacleBrush, 3)
        
        brush_layout.addWidget(self.toggleBrush)
        brush_layout.addWidget(self.normalBrush)
        brush_layout.addWidget(self.difficultBrush)
        brush_layout.addWidget(self.obstacleBrush)
        
        # Add spacing
        brush_layout.addSpacing(20)
        
        # Key/Legend section
        key_title = QtWidgets.QLabel("Legend")
        key_title.setFont(QtGui.QFont("Arial", 14, QtGui.QFont.Weight.Bold))
        key_title.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        brush_layout.addWidget(key_title)
        
        # Create color samples
        key_layout = QtWidgets.QVBoxLayout()
        
        # Normal terrain
        normal_widget = QtWidgets.QWidget()
        normal_layout = QtWidgets.QHBoxLayout(normal_widget)
        normal_layout.setContentsMargins(0, 0, 0, 0)
        normal_color = QtWidgets.QLabel()
        normal_color.setFixedSize(30, 30)
        normal_color.setStyleSheet("background-color: saddlebrown; border: 1px solid black;")
        normal_text = QtWidgets.QLabel("Normal (Cost: 1)")
        normal_layout.addWidget(normal_color)
        normal_layout.addWidget(normal_text)
        normal_layout.addStretch()
        key_layout.addWidget(normal_widget)
        
        # Difficult terrain
        difficult_widget = QtWidgets.QWidget()
        difficult_layout = QtWidgets.QHBoxLayout(difficult_widget)
        difficult_layout.setContentsMargins(0, 0, 0, 0)
        difficult_color = QtWidgets.QLabel()
        difficult_color.setFixedSize(30, 30)
        difficult_color.setStyleSheet("background-color: maroon; border: 1px solid black;")
        difficult_text = QtWidgets.QLabel("Difficult (Cost: 3)")
        difficult_layout.addWidget(difficult_color)
        difficult_layout.addWidget(difficult_text)
        difficult_layout.addStretch()
        key_layout.addWidget(difficult_widget)
        
        # Obstacle
        obstacle_widget = QtWidgets.QWidget()
        obstacle_layout = QtWidgets.QHBoxLayout(obstacle_widget)
        obstacle_layout.setContentsMargins(0, 0, 0, 0)
        obstacle_color = QtWidgets.QLabel()
        obstacle_color.setFixedSize(30, 30)
        obstacle_color.setStyleSheet("background-color: grey; border: 1px solid black;")
        obstacle_text = QtWidgets.QLabel("Obstacle (Blocked)")
        obstacle_layout.addWidget(obstacle_color)
        obstacle_layout.addWidget(obstacle_text)
        obstacle_layout.addStretch()
        key_layout.addWidget(obstacle_widget)
        
        # Player
        player_widget = QtWidgets.QWidget()
        player_layout = QtWidgets.QHBoxLayout(player_widget)
        player_layout.setContentsMargins(0, 0, 0, 0)
        player_color = QtWidgets.QLabel()
        player_color.setFixedSize(30, 30)
        player_color.setStyleSheet("background-color: lime; border: 1px solid black; border-radius: 5px;")
        player_text = QtWidgets.QLabel("Player")
        player_layout.addWidget(player_color)
        player_layout.addWidget(player_text)
        player_layout.addStretch()
        key_layout.addWidget(player_widget)
        
        brush_layout.addLayout(key_layout)
        brush_layout.addStretch()

        # Left side layout (main content)
        left_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        left_layout.setSpacing(20)
        left_layout.addWidget(self.titleLabel)
        left_layout.addWidget(self.dungeonView)
        left_layout.addLayout(button_layout)
        left_layout.addLayout(algo_layout)
        
        # Add to main horizontal layout
        main_layout.addLayout(left_layout)
        main_layout.addWidget(brush_panel)
  
       

        # Player setup
        self.player_model = PlayerModel()
        
        # Create path overlay
        self.path_overlay = PathOverlay(self, self.dungeonView)
        
        # Create player widget
        self.player_widget = Player(self, self.dungeonView, self.player_model)

        # Controller
        self.controller = GameController(
            self.grid_model, self.player_model,
            self.dungeonView, self.player_widget, 
            self.path_overlay, self
        )

        # Connect buttons to Controller methods
        self.moveButton.clicked.connect(self.controller.start_movement)
        self.clearButton.clicked.connect(self.controller.reset_obstacles)
        self.resetButton.clicked.connect(self.controller.reset_player)
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "player_widget"):  # Make sure player widget exists
            self.player_widget.place_at(
                self.player_model.row,
                self.player_model.col
            )
        if hasattr(self, "path_overlay"):  # Reposition path overlay
            self.path_overlay.position_overlay()


# ======================= EXECUTION =======================

app = QtWidgets.QApplication(sys.argv)
window = MainApp()
window.show()
sys.exit(app.exec())