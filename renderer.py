#!/usr/bin/env python3
"""
Renderer class for Game of Life OpenGL rendering.
"""
from __future__ import annotations
from typing import Tuple

import OpenGL.GL as gl
import glm

import shaders
import game


class Renderer:
    """Handles all OpenGL rendering operations for the Game of Life."""
    
    def __init__(self, grid_vert_path, grid_frag_path):
        self.vao, self.shader = self._create_grid_shader(grid_vert_path, grid_frag_path)
        
    def _create_grid_shader(self, vert_path, frag_path) -> Tuple[int, shaders.Shaders]:
        """Create and return VAO and compiled shader program."""
        vao = gl.glGenVertexArrays(1)
        gl.glBindVertexArray(vao)
        program = shaders.Shaders(vert_path, frag_path)
        gl.glBindVertexArray(0)
        return vao, program
    
    def render_frame(self, game_instance: game.Game, hover_pos: glm.ivec2, show_hover: bool) -> None:
        """Render a complete frame."""
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        self._draw_unified_grid(game_instance, hover_pos, show_hover)
        
    def _draw_unified_grid(self, game_instance: game.Game, hover_pos: glm.ivec2, show_hover: bool) -> None:
        """Render the unified grid with cells using the game state texture."""
        # Update game state texture
        game_instance.update_texture()
        
        self.shader.use()
        
        # Bind game state texture
        gl.glActiveTexture(gl.GL_TEXTURE0)
        gl.glBindTexture(gl.GL_TEXTURE_2D, game_instance.game_texture)
        
        # Set all uniforms
        self._set_texture_uniforms(game_instance, hover_pos, show_hover)
        
        # Render
        gl.glBindVertexArray(self.vao)
        gl.glDrawArrays(gl.GL_TRIANGLES, 0, 6)
        gl.glBindVertexArray(0)
    
    def _set_texture_uniforms(self, game_instance: game.Game, hover_pos: glm.ivec2, show_hover: bool) -> None:
        """Set all shader uniforms for texture rendering."""
        uniform_data = [
            ("gGameState", 0, gl.glUniform1i),
            ("gGridSize", (game_instance.texture_size, game_instance.texture_size), 
             lambda loc, val: gl.glUniform2i(loc, val[0], val[1])),
            ("gTextureOffset", (game_instance.texture_offset_x, game_instance.texture_offset_y),
             lambda loc, val: gl.glUniform2i(loc, val[0], val[1])),
            ("gHoverPos", (float(hover_pos.x), float(hover_pos.y)), 
             lambda loc, val: gl.glUniform2f(loc, val[0], val[1])),
            ("gShowHover", 1 if show_hover else 0, gl.glUniform1i)
        ]
        
        for uniform_name, value, setter_func in uniform_data:
            loc = gl.glGetUniformLocation(self.shader.ID, uniform_name)
            if loc != -1:
                setter_func(loc, value)
    
    def set_camera_uniforms(self, camera) -> None:
        """Set camera-related uniforms."""
        camera.Matrix(FOVdeg=45, near=0.1, far=100.0, Shader=self.shader)
    
    def cleanup(self) -> None:
        """Clean up OpenGL resources."""
        if self.vao != 0:
            gl.glDeleteVertexArrays(1, [self.vao])
        if hasattr(self.shader, 'ID') and self.shader.ID != 0:
            gl.glDeleteProgram(self.shader.ID)
