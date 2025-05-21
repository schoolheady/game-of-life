import pygame
from pygame.locals import *
from OpenGL.GL import *

def init():
    glClearColor(1.0, 1.0, 0.0, 1.0)
    glColor3f(0.2, 0.5, 0.4)
    glPointSize(10.0)
    glOrtho(0, 500, 0, 500, -1, 1)

def display():
    glClear(GL_COLOR_BUFFER_BIT)
    
    glBegin(GL_POINTS)
    glVertex2f(100, 100)
    glVertex2f(300, 200)
    glEnd()
    
    pygame.display.flip()

def main():
    pygame.init()
    display_surface = pygame.display.set_mode((500, 500), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("My OpenGL Code")
    
    init()
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        display()
        pygame.time.wait(10)
    
    pygame.quit()

if __name__ == "__main__":
    main()