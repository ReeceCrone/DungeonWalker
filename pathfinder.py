from collections import deque
import heapq


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
