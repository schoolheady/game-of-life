#!/usr/bin/env python3

from __future__ import annotations
from enum import Enum
from typing import Tuple

import OpenGL.GL as gl
import glm
import numpy as np

from cells import CellPopulation  


class GameState(Enum):
    START = "start"           
    RUNNING = "running"       
    PAUSED = "paused"         


class Game:
    def __init__(self, initial_texture_size: int = 1024):
        self.texture_size = initial_texture_size  
        self.cell_population = CellPopulation()  
        self.game_texture = self._create_game_state_texture()
        
        # Texture offset for infinite world support
        self.texture_offset_x = 0
        self.texture_offset_y = 0
        
        # Game state management
        self.state = GameState.START
        self.step_timer = 0.0
        self.step_interval = 0.1  # Time between simulation steps
        
    def toggle_cell(self, grid_pos: glm.ivec2) -> bool:
        """Toggle a cell between alive and dead"""
        result = self.cell_population.toggle_cell_at(grid_pos)
        print(f"DEBUG: Toggled cell at ({grid_pos.x}, {grid_pos.y}), alive={result}")
        print(f"DEBUG: Current texture offset: ({self.texture_offset_x}, {self.texture_offset_y})")
        return result
            
    def is_alive(self, grid_pos: glm.ivec2) -> bool:
        """Check if a cell is alive."""
        return self.cell_population.is_alive_at(grid_pos)
    
    def get_alive_count(self) -> int:
        """Get the number of alive cells."""
        return self.cell_population.count()
    
    def clear(self) -> None:
        """Clear all alive cells."""
        self.cell_population.clear()
    
    def start_simulation(self) -> bool:
        if self.state == GameState.START:
            self.state = GameState.RUNNING
            self.step_timer = 0.0
            return True
        return False
    
    def pause_simulation(self) -> bool:
        if self.state == GameState.RUNNING:
            self.state = GameState.PAUSED
            return True
        return False
    
    def resume_simulation(self) -> bool:
        if self.state == GameState.PAUSED:
            self.state = GameState.RUNNING
            self.step_timer = 0.0
            return True
        return False
    
    def toggle_simulation(self) -> str:
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
        self.cell_population.clear()
        self.state = GameState.START
        self.step_timer = 0.0
    
    def can_edit_cells(self) -> bool:
        return True  
    
    def is_simulation_running(self) -> bool:
        return self.state == GameState.RUNNING
    
    def get_state_name(self) -> str:
        return self.state.value
    
    def update(self, dt: float) -> None:
        if self.state == GameState.RUNNING:
            self.step_timer += dt
            if self.step_timer >= self.step_interval:
                self.step()
                self.step_timer = 0.0
    
    def _create_game_state_texture(self) -> int:
        texture_id = gl.glGenTextures(1)
        gl.glBindTexture(gl.GL_TEXTURE_2D, texture_id)
        
        # Create empty texture 0 = dead, 1 = alive
        gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_R8UI, self.texture_size, self.texture_size, 0, 
                       gl.GL_RED_INTEGER, gl.GL_UNSIGNED_BYTE, None)
        
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)
        
        return texture_id

    def _get_required_texture_bounds(self) -> Tuple[int, int, int, int]:
        if not self.cell_population.get_positions():
            return (-self.texture_size//4, -self.texture_size//4, 
                    self.texture_size//4, self.texture_size//4)
        
        # Get bounding box of all alive cells with some padding
        min_x, min_y, max_x, max_y = self.cell_population.get_bounds()
        padding = 64  # Padding for future expansion
        return (min_x - padding, min_y - padding, max_x + padding, max_y + padding)

    def _resize_texture_if_needed(self) -> None:
        required_bounds = self._get_required_texture_bounds()
        min_x, min_y, max_x, max_y = required_bounds
        
        required_width = max_x - min_x + 1
        required_height = max_y - min_y + 1
        required_size = max(required_width, required_height)
        
        # Round up 
        new_size = 1
        while new_size < required_size:
            new_size *= 2
        
        # Only resize if bigger texture
        if new_size > self.texture_size:
            print(f"Expanding texture from {self.texture_size}x{self.texture_size} to {new_size}x{new_size}")
            self.texture_size = new_size
            
            # Delete old texture and create new one
            gl.glDeleteTextures(1, [self.game_texture])
            self.game_texture = self._create_game_state_texture()

    def update_texture(self) -> None:
        self._resize_texture_if_needed()
        
        # Calculate the center offset for the current texture
        bounds = self._get_required_texture_bounds()
        min_x, min_y, max_x, max_y = bounds
        
        # Center the pattern in the texture
        center_offset_x = (self.texture_size - (max_x - min_x + 1)) // 2 - min_x
        center_offset_y = (self.texture_size - (max_y - min_y + 1)) // 2 - min_y
        
        # Store the offset for shader use
        self.texture_offset_x = center_offset_x
        self.texture_offset_y = center_offset_y
        
        # Create array representing grid
        grid_data = np.zeros((self.texture_size, self.texture_size), dtype=np.uint8)
        
        # Set alive cells
        for x, y in self.cell_population.get_positions():
            tex_x = x + center_offset_x
            tex_y = y + center_offset_y
            if 0 <= tex_x < self.texture_size and 0 <= tex_y < self.texture_size:
                grid_data[tex_y, tex_x] = 1  # 1 = alive
        
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.game_texture)
        gl.glTexSubImage2D(gl.GL_TEXTURE_2D, 0, 0, 0, self.texture_size, self.texture_size,
                          gl.GL_RED_INTEGER, gl.GL_UNSIGNED_BYTE, grid_data)
    
    def step(self) -> None:
        """Perform one step of Game of Life simulation using Conway's rules."""
        # Delegate to the CellPopulation class which implements Conway's rules
        self.cell_population.evolve()
    
    def cleanup(self) -> None:
        if hasattr(self, 'game_texture') and self.game_texture != 0:
            gl.glDeleteTextures(1, [self.game_texture])
