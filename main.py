from PyQt6 import QtWidgets, QtCore, QtGui
import sys
from models import GridModel, PlayerModel
from views import DungeonView, Player, PathOverlay
from controller import GameController


class MainApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(800, 800)
        self.setWindowTitle("Dungeon Walker")
        self.setStyleSheet(open("style.qss", "r").read())


        # --- Basic UI ---
        central = QtWidgets.QWidget()
        main_layout = QtWidgets.QHBoxLayout(central)
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


        # Grid
        rows, cols = 10, 10
        self.grid_model = GridModel(rows, cols)
        self.dungeonView = DungeonView(rows, cols, self.grid_model)
        
        self.dungeonView.setMaximumSize(QtCore.QSize(606, 606))
        self.dungeonView.setMinimumSize(QtCore.QSize(606, 606))


        # Algorithm layout
        algo_layout.addWidget(self.algoLabel)
        algo_layout.addWidget(self.searchComboBox)
        algo_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
    

        # Brush Selector Panel
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
        
        # Goal
        goal_widget = QtWidgets.QWidget()
        goal_layout = QtWidgets.QHBoxLayout(goal_widget)
        goal_layout.setContentsMargins(0, 0, 0, 0)
        goal_color = QtWidgets.QLabel()
        goal_color.setFixedSize(30, 30)
        goal_color.setStyleSheet("background-color: gold; border: 1px solid black;")
        goal_text = QtWidgets.QLabel("Goal")
        goal_layout.addWidget(goal_color)
        goal_layout.addWidget(goal_text)
        goal_layout.addStretch()
        key_layout.addWidget(goal_widget)
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
        if hasattr(self, "player_widget"):
            self.player_widget.place_at(
                self.player_model.row,
                self.player_model.col
            )
        if hasattr(self, "path_overlay"):
            self.path_overlay.position_overlay()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec())
