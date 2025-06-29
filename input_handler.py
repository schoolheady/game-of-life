#!/usr/bin/env python3
from __future__ import annotations

import pygame
import glm

import game


class InputHandler:    
    def __init__(self, game_instance: game.Game, camera):
        self.game = game_instance
        self.camera = camera
        
    def handle_events(self, events) -> bool:
#
        for event in events:
            if self._should_quit(event):
                return False
                
            if event.type == pygame.KEYDOWN:
                self._handle_keyboard(event)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._handle_mouse_click()
        
        return True
    
    def _should_quit(self, event) -> bool:
        """Check if this event should quit the application."""
        return (event.type == pygame.QUIT or 
                (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE))
    
    def _handle_keyboard(self, event) -> None:
        # Handle keyboard input events.
        if event.key == pygame.K_SPACE:
            status = self.game.toggle_simulation()
            print(f"{status} - Current state: {self.game.get_state_name().upper()}")
        elif event.key == pygame.K_r:
            self.game.reset()
            print(f"Game reset - Current state: {self.game.get_state_name().upper()}")
    
    def _handle_mouse_click(self) -> None:
        # Handle mouse click for cell placement/removal
        world_pos = self.camera.ScreentoWorld()
        grid_pos = self.camera.SnapToGrid(world_pos)
        
        was_alive = self.game.is_alive(grid_pos)
        if self.game.toggle_cell(grid_pos):
            action = "removed" if was_alive else "placed"
            state_info = f" (during {self.game.get_state_name().upper()})" if self.game.get_state_name() != "start" else ""
            print(f"Cell {action} at grid({grid_pos.x}, {grid_pos.y}){state_info}")
    
    def get_hover_info(self) -> tuple[glm.ivec2, bool]:
        # Get current hover position and whether to show hover preview
        world_pos = self.camera.ScreentoWorld()
        grid_pos = self.camera.SnapToGrid(world_pos)
        show_hover = not self.game.is_alive(grid_pos)
        return grid_pos, show_hover
