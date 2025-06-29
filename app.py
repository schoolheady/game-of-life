#!/usr/bin/env python3
"""
Application class that coordinates all Game of Life components.
"""
from __future__ import annotations
from pathlib import Path
from typing import Tuple

import pygame
from pygame import OPENGL, DOUBLEBUF
import OpenGL.GL as gl

import camera as cam
import game
import renderer
import input_handler


class GameOfLifeApp:   
    def __init__(self, width: int = 1920, height: int = 1080):
        self.width = width
        self.height = height
        
        # Initialize components
        self._init_pygame()
        self._init_opengl()
        
        # Create core components
        self.camera = cam.Camera(width, height, start_pos=(0, 5, 0))
        self.game = game.Game(initial_texture_size=512)
        
        # Create rendering and input systems
        shader_dir = Path("shaders")
        self.renderer = renderer.Renderer(
            shader_dir / "quad.vert", 
            shader_dir / "grid.frag"
        )
        self.input_handler = input_handler.InputHandler(self.game, self.camera)
        
        self.clock = pygame.time.Clock()
        
        self._print_controls()
    
    def _init_pygame(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height), DOUBLEBUF | OPENGL)
        pygame.display.set_caption("Conway's Game of Life - Interactive")
    
    def _init_opengl(self) -> None:
        # background color
        gl.glClearColor(0.15, 0.18, 0.25, 1.0)
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
    
    def _print_controls(self) -> None:
        print("Conway's Game of Life - Interactive")
        print("=" * 40)
        print("WASD = move, RMB drag = pan, wheel = zoom")
        print("LMB = place/remove cell (works in all states for interactive editing)")
        print("SPACE = start/pause/resume simulation, R = reset to START state, Esc = quit")
        print(f"Current state: {self.game.get_state_name().upper()}")
        print("=" * 40)
    
    def run(self) -> None:
        # Main application loop.
        running = True
        
        while running:
            dt = self.clock.tick(60) / 1000.0
            events = pygame.event.get()
            
            # Handle input
            running = self.input_handler.handle_events(events)
            if not running:
                break
            
            # Update systems
            self._update(dt, events)
            
            # Render frame
            self._render()
            
            pygame.display.flip()
        
        self._cleanup()
    
    def _update(self, dt: float, events) -> None:
        """Update all game systems."""
        # Update camera
        self.camera.handle_events(events)
        self.camera.update(dt)
        
        # Update game simulation
        self.game.update(dt)
        
        # Set camera uniforms
        self.renderer.set_camera_uniforms(self.camera)
    
    def _render(self) -> None:
        # Get hover information
        hover_pos, show_hover = self.input_handler.get_hover_info()
        
        # Render frame
        self.renderer.render_frame(self.game, hover_pos, show_hover)
    
    def _cleanup(self) -> None:
        self.renderer.cleanup()
        self.game.cleanup()
        pygame.quit()




