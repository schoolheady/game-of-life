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
import game               # local module


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
    # Dark background that's easier on the eyes - soft dark blue-gray
    gl.glClearColor(0.15, 0.18, 0.25, 1.0)  # Warm dark background
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
def draw_unified_grid(vao: int, program: shaders.Shaders, game_instance: game.Game, 
                      hover_pos: glm.ivec2, show_hover: bool) -> None:
    """Render the unified grid with cells using the game state texture."""
    # Update game state texture
    game_instance.update_texture()
    
    program.use()
    
    # Bind game state texture
    gl.glActiveTexture(gl.GL_TEXTURE0)
    gl.glBindTexture(gl.GL_TEXTURE_2D, game_instance.game_texture)
    
    # Set texture uniform
    texture_loc = gl.glGetUniformLocation(program.ID, "gGameState")
    if texture_loc != -1:
        gl.glUniform1i(texture_loc, 0)
    
    # Set grid size uniform
    grid_size_loc = gl.glGetUniformLocation(program.ID, "gGridSize")
    if grid_size_loc != -1:
        gl.glUniform2i(grid_size_loc, game_instance.grid_size, game_instance.grid_size)
    
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
# Main loop
# --------------------------------------------------------------------------- #
def run() -> None:
    _screen = init_window((WIDTH, HEIGHT))  # noqa: F841  (needed for GL ctx)
    init_gl()

    camera = cam.Camera(WIDTH, HEIGHT, start_pos=(0, 5, 0))
    game_instance = game.Game(grid_size=512)  # Create game instance
    vao, shader = create_grid_shader()  # Only need one shader now!
    
    clock = pygame.time.Clock()

    print("WASD = move, RMB drag = pan, wheel = zoom")
    print("LMB = place/remove cell (works in all states for interactive editing)")
    print("SPACE = start/pause/resume simulation, R = reset to START state, Esc = quit")
    print(f"Current state: {game_instance.get_state_name().upper()}")

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
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_SPACE:
                    # Toggle simulation state
                    status = game_instance.toggle_simulation()
                    print(f"{status} - Current state: {game_instance.get_state_name().upper()}")
                elif e.key == pygame.K_r:
                    # Reset the game (return to START state)
                    game_instance.reset()
                    print(f"Game reset - Current state: {game_instance.get_state_name().upper()}")
            elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:  # Left click
                # Allow cell placement/removal in all states for interactive editing
                world_pos = camera.ScreentoWorld()
                grid_pos = camera.SnapToGrid(world_pos)
                
                was_alive = game_instance.is_alive(grid_pos)
                if game_instance.toggle_cell(grid_pos):
                    action = "removed" if was_alive else "placed"
                    state_info = f" (during {game_instance.get_state_name().upper()})" if game_instance.get_state_name() != "start" else ""
                    print(f"Cell {action} at grid({grid_pos.x}, {grid_pos.y}){state_info}")

        # ---------- camera ---------- #
        camera.handle_events(events)
        camera.update(dt)
        
        # ---------- game simulation ---------- #
        game_instance.update(dt)
        
        # Set uniforms for unified shader
        camera.Matrix(FOVdeg=45, near=0.1, far=100.0, Shader=shader)
        
        # Get mouse position in grid coordinates
        world_pos = camera.ScreentoWorld()
        grid_pos = camera.SnapToGrid(world_pos)

        # ---------- draw ---------- #
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        
        # Draw unified grid with cells
        show_hover = not game_instance.is_alive(grid_pos)  # Only show hover if cell is dead
        draw_unified_grid(vao, shader, game_instance, grid_pos, show_hover)
        
        pygame.display.flip()

    # Cleanup
    cleanup(vao, shader)
    game_instance.cleanup()
    pygame.quit()


if __name__ == "__main__":
    run()
