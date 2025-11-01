from gameState import *
from collections import deque    # using queue to store path to next pellet

class PacbotAgent:

    def __init__(self, state):
        self.state: GameState = state
        self.tmp_state: GameState = state

        # BFS variables
        self.pellet_path = deque()     # Queue of directions to follow
        self.nearest_pellet = None     # Current target pellet (row, col)


    # Safety cost currently not implemented
    # def safetyCost(self) -> int:
    #     pass

    def bfs_nearest_pellet(self) -> list[Directions]:
        """
        Implement bfs to find nearest pellet.
        Then return a path to pellet.
        """

        # Get coordinates for pacman
        pacman_row = self.state.pacmanLoc.row
        pacman_col = self.state.pacmanLoc.col
        
        # Store visited coordinates in set, including current coordinates
        visited = set()
        visited.add((pacman_row, pacman_col))
        
        # Queue coordinates to explore
        # Keep path to coordinates inside of queue (to avoid reconstructing path from scratch)
        path = deque([(pacman_row, pacman_col, [])])

        # While there are directions stored in queue
        while path:
            row, col, route = path.popleft()
            
            # If we're at a pellet, no need to explore
            if self.state.pelletAt(row, col):
                self.nearest_pellet = (row, col)
                return route

            # From gamestate.py, enum class Directions
            # Check all four directions around pacman, add them to be explored by queue
            for direction in [Directions.UP, Directions.DOWN, Directions.LEFT, Directions.RIGHT]:
                
                # get coordinates
                explored_row = row + D_ROW[direction]
                explored_col = col + D_COL[direction]

                # If not a wall and not visited
                if not self.state.wallAt(explored_row, explored_col) and (explored_row, explored_col) not in visited:
                    # add to visited set and path queue 
                    visited.add((explored_row, explored_col))
                    path.append((explored_row, explored_col, route + [direction]))  # append direction to route list

        # No more pellets
        return []

    def act(self):

        # Skip if the game is paused
        if self.state.gameMode == GameModes.PAUSED:
            return

        # Deepcopy the game state
        decompressGameState(self.tmp_state, compressGameState(self.state))
        # Not sure what this does

        # Check if pellets are all collected
        if self.state.numPellets() == 0:
            print("Finished collecting pellets, exiting!")
            return

        # Follow path queue as long as there are coordinates to travel to
        if len(self.pellet_path) > 0:
            # Get the next direction from our planned path
            next_direction = self.pellet_path.popleft()
            
            # Queue the action to move in that direction
            self.state.queueAction(
                numTicks=4,  # Number of ticks to wait before executing
                pacmanDir=next_direction
            )
            return
        
        # Check if pacman is at the target pellet (pellet collected)
        pacman_row = self.state.pacmanLoc.row
        pacman_col = self.state.pacmanLoc.col
        
        if self.nearest_pellet == (pacman_row, pacman_col):
            self.nearest_pellet = None
        
        # Plan a new path if we don't have a pellet path
        if self.nearest_pellet is None:

            # do BFS to find nearest pellet, store path
            path = self.bfs_nearest_pellet()
            
            # move immediately instead of waiting for decisionModule.py loop to call function again
            if path:
                # Store the path as a queue of directions
                self.pellet_path = deque(path)
                
                # Move pacman by popping queue
                next_direction = self.pellet_path.popleft()
                self.state.queueAction(numTicks=4, pacmanDir=next_direction)
