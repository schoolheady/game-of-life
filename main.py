import pygame
import ctypes
import numpy as np

from pygame.locals import *
from OpenGL.GL import *

import shaders 

VERTEX_PATH   = "shaders/vertex.GLSL"
FRAGMENT_PATH = "shaders/fragment.GLSL"

vertices = np.array([
     0.5,  0.5, 0.0,  
     0.5, -0.5, 0.0,  
    -0.5, -0.5, 0.0,  
    -0.5,  0.5, 0.0   
], dtype=np.float32)

indeces = np.array([
    0, 1, 3,
    1, 2, 3
], dtype=np.uint32)
    


def check_SProgam(program):
    success = glGetProgramiv(program, GL_LINK_STATUS)
    if not success:
        infolog = glGetProgramInfoLog(program)
        print(f"[ERROR] PROGRAM linking FAILED: {infolog.decode('utf-8')}")
    else:
        print("Program linking successful")



# function to initialize OpenGL settings
def init(vertices=np.array([]), indeces=np.array([])):
    # Create vertex array object
    VAO = glGenVertexArrays(1) 
    VBO = glGenBuffers(1)
    EBO = glGenBuffers(1)
    glBindVertexArray(VAO)
    ShaderProgam = shaders.Shaders(VERTEX_PATH,FRAGMENT_PATH)
    # Create vertex buffer object
    glBindBuffer(GL_ARRAY_BUFFER, VBO) 
    # Fill buffer with data
    glBufferData(GL_ARRAY_BUFFER,
                 vertices.nbytes,
                 vertices,
                 GL_STATIC_DRAW)
    
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER,
                 indeces.nbytes, 
                 indeces,
                 GL_STATIC_DRAW)


    
    # Setup vertex attributes
    glVertexAttribPointer(0, 3, 
                          GL_FLOAT, GL_FALSE, 
                          3 * vertices.itemsize, 
                          ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)
    
    # Unbind to prevent accidental modification
    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindVertexArray(0)

    
    return VAO, VBO , ShaderProgam

def draw(VAO , program=shaders.Shaders):
    # Clear the screen first
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    # Use the shader program
    program.use()
    
    # Bind the VAO and draw
    glBindVertexArray(VAO)
    glDrawElements(GL_TRIANGLES,6, GL_UNSIGNED_INT, ctypes.c_void_p(0))
    
    # Unbind the VAO
    glBindVertexArray(0)
    
    # Swap buffers
    pygame.display.flip()



    
def main():
    pygame.init()
    display_surface = pygame.display.set_mode((1920, 1080), DOUBLEBUF | pygame.OPENGL)
    # clock for frames
    self_clock = pygame.time.Clock()
    pygame.display.set_caption("My OpenGL Code")
    
    # Basic OpenGL setup
    glClearColor(1, 1, 1, 1.0)  # Set background color
    glEnable(GL_DEPTH_TEST)  # Enable depth testing
    
    # Initialize our objects
    VAO, VBO, ShaderProgram_ = init(vertices, indeces)
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Draw our triangle
                if event.button == 1:
                    draw(VAO, ShaderProgram_)
        # Clear the screen if no mouse button is pressed
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Use the clock for timing
        self_clock.tick(60)
    
    # Clean up resources
    glDeleteVertexArrays(1, [VAO])
    glDeleteBuffers(1, [VBO])
    glDeleteProgram(ShaderProgram_)
    pygame.quit()

if __name__ == "__main__":
    main()