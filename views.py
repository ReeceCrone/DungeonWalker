from PyQt6 import QtWidgets, QtCore, QtGui


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
