from gameState import *
import random

class PacbotAgent:

    def __init__(self, state):
        self.state: GameState = state
        self.tmp_state: GameState = state
        self.target = None               # <- keep current pellet target
        self.prev_positions = []         # <- to detect if Pacman is stuck

    def safetyCost(self) -> int:
        # Placeholder for later ghost avoidance
        return 0

    def act(self):
        # Skip if the game is paused
        if self.state.gameMode == GameModes.PAUSED:
            return

        # Deepcopy the game state (so we can simulate without mutating it)
        decompressGameState(self.tmp_state, compressGameState(self.state))

        pac_row, pac_col = self.tmp_state.pacmanLoc.row, self.tmp_state.pacmanLoc.col

        # --- 1️⃣ Update our previous positions for stuck detection ---
        self.prev_positions.append((pac_row, pac_col))
        if len(self.prev_positions) > 6:
            self.prev_positions.pop(0)

        # --- 2️⃣ If Pacman is bouncing (stuck), break the loop randomly ---
        if len(self.prev_positions) == 6:
            last3 = self.prev_positions[-3:]
            if len(set(last3)) == 2:  # moving back and forth between 2 tiles
                valid_dirs = [d for d in [Directions.UP, Directions.DOWN, Directions.LEFT, Directions.RIGHT]
                              if not self.tmp_state.wallAt(pac_row + D_ROW[d], pac_col + D_COL[d])]
                if valid_dirs:
                    escape_dir = random.choice(valid_dirs)
                    self.state.queueAction(numTicks=1, pacmanDir=escape_dir)
                    return  # skip normal logic this tick

        # --- 3️⃣ Keep or pick a pellet target ---
        if (self.target is None or
            not self.tmp_state.pelletAt(self.target[0], self.target[1])):
            # find new pellet target
            pellets = []
            for r in range(31):
                for c in range(28):
                    if self.tmp_state.pelletAt(r, c):
                        pellets.append((r, c))

            if not pellets:
                return  # no pellets left

            # pick nearest pellet
            nearest = min(pellets, key=lambda p: abs(p[0] - pac_row) + abs(p[1] - pac_col))
            self.target = nearest

        target_row, target_col = self.target

        # --- 4️⃣ Move in direction that reduces distance to target ---
        best_dir = Directions.NONE
        best_dist = float("inf")

        for direction in [Directions.UP, Directions.LEFT, Directions.DOWN, Directions.RIGHT]:
            new_row = pac_row + D_ROW[direction]
            new_col = pac_col + D_COL[direction]

            if self.tmp_state.wallAt(new_row, new_col):
                continue  # skip walls

            dist = abs(new_row - target_row) + abs(new_col - target_col)
            if dist < best_dist:
                best_dist = dist
                best_dir = direction

        # --- 5️⃣ Move 1 tick toward target ---
        self.state.queueAction(numTicks=1, pacmanDir=best_dir)
