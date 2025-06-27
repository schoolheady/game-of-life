#!/usr/bin/env python3
"""
Minimal Pygame + OpenGL grid viewer.

Controls
--------
W A S D         – move camera on XZ plane  
Right-mouse drag – pan  
Mouse-wheel      – zoom  
Esc / window ×   – quit
"""
from __future__ import annotations

from pathlib import Path
from typing import Tuple

import pygame
from pygame import OPENGL, DOUBLEBUF
import OpenGL.GL as gl
import glm
import numpy as np

import shaders           # local module
import camera as cam      # local module


# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #
WIDTH, HEIGHT = 1920, 1080
SHADER_DIR = Path("shaders")

GRID_VERT = SHADER_DIR / "quad.vert"
GRID_FRAG = SHADER_DIR / "grid.frag"
CELL_VERT = SHADER_DIR / "cell.vert"
CELL_FRAG = SHADER_DIR / "cell.frag"
# --------------------------------------------------------------------------- #
# Initialisation helpers
# --------------------------------------------------------------------------- #
def init_window(size: Tuple[int, int]) -> pygame.Surface:
    """Create a Pygame window with an OpenGL context."""
    pygame.init()
    screen = pygame.display.set_mode(size, DOUBLEBUF | OPENGL)
    pygame.display.set_caption("OpenGL Grid")
    return screen


def init_gl() -> None:
    """One-time OpenGL state that never changes."""
    gl.glClearColor(1.0, 1.0, 1.0, 1.0)
    gl.glEnable(gl.GL_DEPTH_TEST)
    gl.glEnable(gl.GL_BLEND)
    gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)


def create_grid_shader() -> tuple[int, shaders.Shaders]:
    """Return (VAO, compiled shader program) for the unified grid+cell renderer."""
    vao = gl.glGenVertexArrays(1)
    gl.glBindVertexArray(vao)          # No vertex buffers needed
    program = shaders.Shaders(GRID_VERT, GRID_FRAG)
    gl.glBindVertexArray(0)
    return vao, program


# --------------------------------------------------------------------------- #
# Draw/cleanup helpers
# --------------------------------------------------------------------------- #
def draw_unified_grid(vao: int, program: shaders.Shaders, game_texture: int, 
                      game_state, grid_size: int, hover_pos: glm.ivec2, show_hover: bool) -> None:
    """Render the unified grid with cells using the game state texture."""
    # Update game state texture
    update_game_state_texture(game_texture, game_state, grid_size)
    
    program.use()
    
    # Bind game state texture
    gl.glActiveTexture(gl.GL_TEXTURE0)
    gl.glBindTexture(gl.GL_TEXTURE_2D, game_texture)
    
    # Set texture uniform
    texture_loc = gl.glGetUniformLocation(program.ID, "gGameState")
    if texture_loc != -1:
        gl.glUniform1i(texture_loc, 0)
    
    # Set grid size uniform
    grid_size_loc = gl.glGetUniformLocation(program.ID, "gGridSize")
    if grid_size_loc != -1:
        gl.glUniform2i(grid_size_loc, grid_size, grid_size)
    
    # Set hover position uniform
    hover_pos_loc = gl.glGetUniformLocation(program.ID, "gHoverPos")
    if hover_pos_loc != -1:
        gl.glUniform2f(hover_pos_loc, float(hover_pos.x), float(hover_pos.y))
    
    # Set show hover uniform
    show_hover_loc = gl.glGetUniformLocation(program.ID, "gShowHover")
    if show_hover_loc != -1:
        gl.glUniform1i(show_hover_loc, 1 if show_hover else 0)
    
    gl.glBindVertexArray(vao)
    gl.glDrawArrays(gl.GL_TRIANGLES, 0, 6)
    gl.glBindVertexArray(0)


def cleanup(vao: int, program: shaders.Shaders) -> None:
    if vao != 0:
        gl.glDeleteVertexArrays(1, [vao])
    if hasattr(program, 'ID') and program.ID != 0:
        gl.glDeleteProgram(program.ID)


# --------------------------------------------------------------------------- #
# Game state
# --------------------------------------------------------------------------- #
class GameState:
    def __init__(self):
        self.alive_cells = set()  # Set of (x, y) tuples for alive cells
        
    def toggle_cell(self, grid_pos):
        """Toggle a cell between alive and dead."""
        pos = (grid_pos.x, grid_pos.y)
        if pos in self.alive_cells:
            self.alive_cells.remove(pos)
        else:
            self.alive_cells.add(pos)
            
    def is_alive(self, grid_pos):
        """Check if a cell is alive."""
        return (grid_pos.x, grid_pos.y) in self.alive_cells


# --------------------------------------------------------------------------- #
# Texture management for game state
# --------------------------------------------------------------------------- #
def create_game_state_texture(width: int, height: int) -> int:
    """Create a texture to store alive/dead cell states"""
    texture_id = gl.glGenTextures(1)
    gl.glBindTexture(gl.GL_TEXTURE_2D, texture_id)
    
    # Create empty texture (0 = dead, 1 = alive)
    gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_R8UI, width, height, 0, 
                   gl.GL_RED_INTEGER, gl.GL_UNSIGNED_BYTE, None)
    
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)
    
    return texture_id

def update_game_state_texture(texture_id: int, game_state, grid_size: int) -> None:
    """Upload current game state to texture"""
    # Create array representing grid (centered around 0,0)
    grid_data = np.zeros((grid_size, grid_size), dtype=np.uint8)
    
    # Set alive cells (offset by grid_size/2 to handle negative coordinates)
    offset = grid_size // 2
    for x, y in game_state.alive_cells:
        tex_x = x + offset
        tex_y = y + offset
        if 0 <= tex_x < grid_size and 0 <= tex_y < grid_size:
            grid_data[tex_y, tex_x] = 1  # 1 = alive
    
    gl.glBindTexture(gl.GL_TEXTURE_2D, texture_id)
    gl.glTexSubImage2D(gl.GL_TEXTURE_2D, 0, 0, 0, grid_size, grid_size,
                      gl.GL_RED_INTEGER, gl.GL_UNSIGNED_BYTE, grid_data)
# --------------------------------------------------------------------------- #
# Main loop
# --------------------------------------------------------------------------- #
def run() -> None:
    _screen = init_window((WIDTH, HEIGHT))  # noqa: F841  (needed for GL ctx)
    init_gl()

    camera = cam.Camera(WIDTH, HEIGHT, start_pos=(0, 5, 0))
    game_state = GameState()
    vao, shader = create_grid_shader()  # Only need one shader now!
    
    # Create game state texture (512x512 grid)
    GRID_SIZE = 512
    game_texture = create_game_state_texture(GRID_SIZE, GRID_SIZE)
    
    clock = pygame.time.Clock()

    print("WASD = move, RMB drag = pan, wheel = zoom, LMB = place/remove cell, Esc = quit.")

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        events = pygame.event.get()

        # ---------- high-level event handling ---------- #
        for e in events:
            if (e.type == pygame.QUIT or
                    (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE)):
                running = False
                break
            elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:  # Left click
                world_pos = camera.ScreentoWorld()
                grid_pos = camera.SnapToGrid(world_pos)
                print(f"Click: world({world_pos.x:.2f}, {world_pos.y:.2f}) -> grid({grid_pos.x}, {grid_pos.y})")
                game_state.toggle_cell(grid_pos)

        # ---------- camera ---------- #
        camera.handle_events(events)
        camera.update(dt)
        
        # Set uniforms for unified shader
        camera.Matrix(FOVdeg=45, near=0.1, far=100.0, Shader=shader)
        
        # Get mouse position in grid coordinates
        world_pos = camera.ScreentoWorld()
        grid_pos = camera.SnapToGrid(world_pos)

        # ---------- draw ---------- #
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        
        # Draw unified grid with cells
        show_hover = not game_state.is_alive(grid_pos)  # Only show hover if cell is dead
        draw_unified_grid(vao, shader, game_texture, game_state, GRID_SIZE, grid_pos, show_hover)
        
        pygame.display.flip()

    # Cleanup
    cleanup(vao, shader)
    gl.glDeleteTextures(1, [game_texture])
    pygame.quit()


if __name__ == "__main__":
    run()
