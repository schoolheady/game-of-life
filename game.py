#!/usr/bin/env python3
"""
Game of Life game logic and state management.
"""
from __future__ import annotations
from enum import Enum

import OpenGL.GL as gl
import glm
import numpy as np


class GameState(Enum):
    """Game states for the Game of Life."""
    START = "start"           # Initial state - can edit cells
    RUNNING = "running"       # Simulation is running - no editing
    PAUSED = "paused"         # Simulation is paused - no editing


class Game:
    """Game of Life game state and logic."""
    
    def __init__(self, grid_size: int = 512):
        self.grid_size = grid_size
        self.alive_cells = set()  # Set of (x, y) tuples for alive cells
        self.game_texture = self._create_game_state_texture()
        
        # Game state management
        self.state = GameState.START
        self.step_timer = 0.0
        self.step_interval = 0.1  # Time between simulation steps (in seconds)
        
    def toggle_cell(self, grid_pos: glm.ivec2) -> bool:
        """Toggle a cell between alive and dead. Returns True if successful, False if not allowed."""
        if self.state != GameState.START:
            return False  # Can only edit cells in START state
            
        pos = (grid_pos.x, grid_pos.y)
        if pos in self.alive_cells:
            self.alive_cells.remove(pos)
        else:
            self.alive_cells.add(pos)
        return True
            
    def is_alive(self, grid_pos: glm.ivec2) -> bool:
        """Check if a cell is alive."""
        return (grid_pos.x, grid_pos.y) in self.alive_cells
    
    def get_alive_count(self) -> int:
        """Get the number of alive cells."""
        return len(self.alive_cells)
    
    def clear(self) -> None:
        """Clear all alive cells."""
        self.alive_cells.clear()
    
    def start_simulation(self) -> bool:
        """Start the simulation. Only allowed from START state."""
        if self.state == GameState.START:
            self.state = GameState.RUNNING
            self.step_timer = 0.0
            return True
        return False
    
    def pause_simulation(self) -> bool:
        """Pause the simulation. Only allowed from RUNNING state."""
        if self.state == GameState.RUNNING:
            self.state = GameState.PAUSED
            return True
        return False
    
    def resume_simulation(self) -> bool:
        """Resume the simulation. Only allowed from PAUSED state."""
        if self.state == GameState.PAUSED:
            self.state = GameState.RUNNING
            self.step_timer = 0.0
            return True
        return False
    
    def toggle_simulation(self) -> str:
        """Toggle simulation state. Returns status message."""
        if self.state == GameState.START:
            if self.start_simulation():
                return "Simulation started"
        elif self.state == GameState.RUNNING:
            if self.pause_simulation():
                return "Simulation paused"
        elif self.state == GameState.PAUSED:
            if self.resume_simulation():
                return "Simulation resumed"
        return "State change not allowed"
    
    def reset(self) -> None:
        """Reset the game - clear all cells and return to START state."""
        self.alive_cells.clear()
        self.state = GameState.START
        self.step_timer = 0.0
    
    def can_edit_cells(self) -> bool:
        """Check if cells can be edited in the current state."""
        return self.state == GameState.START
    
    def is_simulation_running(self) -> bool:
        """Check if the simulation is currently running."""
        return self.state == GameState.RUNNING
    
    def get_state_name(self) -> str:
        """Get the current state as a string."""
        return self.state.value
    
    def update(self, dt: float) -> None:
        """Update the game simulation."""
        if self.state == GameState.RUNNING:
            self.step_timer += dt
            if self.step_timer >= self.step_interval:
                self.step()
                self.step_timer = 0.0
    
    def _create_game_state_texture(self) -> int:
        """Create a texture to store alive/dead cell states"""
        texture_id = gl.glGenTextures(1)
        gl.glBindTexture(gl.GL_TEXTURE_2D, texture_id)
        
        # Create empty texture (0 = dead, 1 = alive)
        gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_R8UI, self.grid_size, self.grid_size, 0, 
                       gl.GL_RED_INTEGER, gl.GL_UNSIGNED_BYTE, None)
        
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)
        
        return texture_id

    def update_texture(self) -> None:
        """Upload current game state to texture"""
        # Create array representing grid (centered around 0,0)
        grid_data = np.zeros((self.grid_size, self.grid_size), dtype=np.uint8)
        
        # Set alive cells (offset by grid_size/2 to handle negative coordinates)
        offset = self.grid_size // 2
        for x, y in self.alive_cells:
            tex_x = x + offset
            tex_y = y + offset
            if 0 <= tex_x < self.grid_size and 0 <= tex_y < self.grid_size:
                grid_data[tex_y, tex_x] = 1  # 1 = alive
        
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.game_texture)
        gl.glTexSubImage2D(gl.GL_TEXTURE_2D, 0, 0, 0, self.grid_size, self.grid_size,
                          gl.GL_RED_INTEGER, gl.GL_UNSIGNED_BYTE, grid_data)
    
    def step(self) -> None:
        """Perform one step of Game of Life simulation using Conway's rules."""
        # Count neighbors for all relevant cells
        neighbor_counts = {}
        
        # Check all alive cells and their neighbors
        cells_to_check = set()
        for x, y in self.alive_cells:
            cells_to_check.add((x, y))
            # Add all 8 neighbors
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx != 0 or dy != 0:  # Don't add the cell itself
                        cells_to_check.add((x + dx, y + dy))
        
        # Count neighbors for each cell to check
        for x, y in cells_to_check:
            count = 0
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx != 0 or dy != 0:  # Don't count the cell itself
                        neighbor_x, neighbor_y = x + dx, y + dy
                        if (neighbor_x, neighbor_y) in self.alive_cells:
                            count += 1
            neighbor_counts[(x, y)] = count
        
        # Apply Conway's Game of Life rules
        new_alive_cells = set()
        for (x, y), count in neighbor_counts.items():
            is_alive = (x, y) in self.alive_cells
            
            if is_alive:
                # Rule 1: Any live cell with 2 or 3 neighbors survives
                if count == 2 or count == 3:
                    new_alive_cells.add((x, y))
                # Rule 2: Any live cell with < 2 or > 3 neighbors dies (underpopulation/overpopulation)
            else:
                # Rule 3: Any dead cell with exactly 3 neighbors becomes alive (reproduction)
                if count == 3:
                    new_alive_cells.add((x, y))
        
        self.alive_cells = new_alive_cells
    
    def cleanup(self) -> None:
        """Clean up OpenGL resources."""
        if hasattr(self, 'game_texture') and self.game_texture != 0:
            gl.glDeleteTextures(1, [self.game_texture])
