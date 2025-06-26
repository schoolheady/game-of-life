import pygame
import ctypes
import numpy as np

from pygame.locals import *
from OpenGL.GL import *

import shaders 
import camera as cam

import glm

WIDTH = 1920
HEIGHT = 1080

VERTEX_PATH   = "shaders/quad.vert"
FRAGMENT_PATH = "shaders/grid.frag"

vertices = np.array([
     0.5,  0.5, 0.0,  
     0.5, -0.5, 0.0,  
    -0.5, -0.5, 0.0,  
    -0.5,  0.5, 0.0   
], dtype=np.float32)

indeces = np.array([
    0, 1, 2,  # First triangle
    0, 2, 3   # Second triangle
], dtype=np.uint32)
    


def check_SProgam(program):
    success = glGetProgramiv(program, GL_LINK_STATUS)
    if not success:
        infolog = glGetProgramInfoLog(program)
        print(f"[ERROR] PROGRAM linking FAILED: {infolog.decode('utf-8')}")
    else:
        print("Program linking successful")



# function to initialize OpenGL settings
def init():
    # The quad.vert shader generates its own geometry, so we only need a VAO
    VAO = glGenVertexArrays(1) 
    glBindVertexArray(VAO)
    ShaderProgam = shaders.Shaders(VERTEX_PATH, FRAGMENT_PATH)
    
    # Unbind VAO
    glBindVertexArray(0)

    return VAO, ShaderProgam

def draw(VAO, program=shaders.Shaders):
    # Clear the screen first
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    # Use the shader program
    program.use()
    
    # Bind the VAO and draw 6 vertices (2 triangles = 1 quad)
    glBindVertexArray(VAO)
    glDrawArrays(GL_TRIANGLES, 0, 6)  # Draw 6 vertices using gl_VertexID
    
    # Unbind the VAO
    glBindVertexArray(0)
    
    # Swap buffers
    pygame.display.flip()



    
def main():
    pygame.init()
    
    # Set up the display with proper flags for keyboard input
    display_surface = pygame.display.set_mode((WIDTH, HEIGHT), DOUBLEBUF | pygame.OPENGL)
    pygame.event.set_grab(False)  # Don't grab input exclusively
    pygame.key.set_repeat()  # Enable key repeat
    
    # clock for frames
    clock = pygame.time.Clock()
    pygame.display.set_caption("My OpenGL Code")
    camera = cam.Camera(WIDTH, HEIGHT, start_pos=(0,5,0))
    # Basic OpenGL setup
    glClearColor(1.0, 1.0, 1.0, 1.0)  # Set background color to dark teal
    glEnable(GL_DEPTH_TEST)  # Enable depth testing
    
    # Initialize our objects (no vertex data needed for procedural quad)
    VAO, ShaderProgram_ = init()
    
    # Initialize timing and rotation variables
    previous_time = 0.0
    rotation = 0.0
    
    running = True
    print("Application started. Use WASD to move, mouse drag to pan, mouse wheel to zoom.")
    
    while running:
        dt = clock.tick(60) / 1000.0
        
        # Handle events - get all events once
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # Update camera with events and time
        camera.handle_events(events)
        camera.update(dt)
        
        # Use the shader program
        ShaderProgram_.use()
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # Set camera matrices (gVP and gCameraWorldPos uniforms)
        camera.Matrix(45, 0.1, 100.0, ShaderProgram_)

        draw(VAO, ShaderProgram_)

    # Clean up resources
    glDeleteVertexArrays(1, [VAO])
    glDeleteProgram(ShaderProgram_.ID)  # Use .ID attribute
    pygame.quit()

if __name__ == "__main__":
    main()