from PyQt6 import QtCore
from pathfinder import Pathfinder


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
        # Prevent painting on start (0,0) or finish (bottom-right) positions
        if (row == 0 and col == 0) or (row == self.grid_model.rows - 1 and col == self.grid_model.cols - 1):
            return
        
        # Get selected brush mode
        brush_id = self.main_window.brush_group.checkedId()
        
        if brush_id == 0:  # Toggle mode
            new_color = self.grid_model.toggle_cell(row, col)
            self.paint_color = new_color
        elif brush_id == 1:  # Normal (brown)
            self.grid_model.set_cell_color(row, col, "brown")
            self.paint_color = "brown"
        elif brush_id == 2:  # Difficult (maroon)
            self.grid_model.set_cell_color(row, col, "maroon")
            self.paint_color = "maroon"
        elif brush_id == 3:  # Obstacle (grey)
            self.grid_model.set_cell_color(row, col, "grey")
            self.paint_color = "grey"
    
    def handle_cell_drag(self, row, col):
        # Prevent painting on start (0,0) or finish (bottom-right) positions
        if (row == 0 and col == 0) or (row == self.grid_model.rows - 1 and col == self.grid_model.cols - 1):
            return
        
        # Paint with the same color as the initial click
        if self.paint_color is not None:
            self.grid_model.set_cell_color(row, col, self.paint_color)

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
