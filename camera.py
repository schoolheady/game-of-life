import pygame
from pygame.locals import *
from OpenGL.GL import *
import glm

class Camera:
    def __init__(self, width, height, start_pos=(0,5,0)):
        self.width, self.height = width, height

        # Z is up in world; start at height=5
        self.position    = glm.vec3(start_pos)
        self.orientation = glm.vec3(0, -1, 0)   # look straight down
        self.up          = glm.vec3(0, 0, -1)   # “north” → -Z

        # movement & zoom parameters
        self.base_speed     = 5.0     # world units per second at zoom=1
        self.zoom           = self.position.y
        self.min_zoom, self.max_zoom = 10, 75.0
        self.zoom_speed     = 20.0    # units per wheel click
        self.pan_speed      = 0.008   # improved base multiplier for mouse panning

        # internal state updated by handle_events()
        self._pan_delta     = glm.vec2(0,0)
        self._zoom_delta    = 0

    def handle_events(self, events):
        """Call once per frame with pygame.event.get()."""
        # reset deltas
        self._pan_delta = glm.vec2(0,0)
        self._zoom_delta = 0

        for e in events:
            if e.type == MOUSEMOTION and e.buttons[0]:
                # e.rel is (dx,dy) in pixels
                dx, dy = e.rel
                self._pan_delta += glm.vec2(dx, dy)
            elif e.type == MOUSEWHEEL:
                # e.y is +1 (wheel up), -1 (wheel down)
                self._zoom_delta += e.y

    def update(self, dt):
        """
        dt = seconds since last frame.
        Call after handle_events(), before Matrix().
        """
        # --- Keyboard WASD (world X/Z) ---
        keys = pygame.key.get_pressed()
        # speed scales so you move roughly the same screen-distance
        speed = self.base_speed * dt * (self.zoom / 10.0)
        
        moved = False
        if keys[K_w]:
            self.position.z -= speed
            moved = True
            print(f"W key: moving Z to {self.position.z}")
        if keys[K_s]:
            self.position.z += speed
            moved = True
            print(f"S key: moving Z to {self.position.z}")
        if keys[K_a]:
            self.position.x -= speed
            moved = True
            print(f"A key: moving X to {self.position.x}")
        if keys[K_d]:
            self.position.x += speed
            moved = True
            print(f"D key: moving X to {self.position.x}")
            
        if moved:
            print(f"New camera position: {self.position}")

        # --- Mouse-drag pan ---
        if self._pan_delta.x != 0 or self._pan_delta.y != 0:
            # Improved sensitivity scaling with logarithmic feel
            # This provides fine control at low zoom and appropriate speed at high zoom
            base_sensitivity = self.pan_speed
            zoom_factor = pow(self.zoom / 5.0, 0.7)  # Power scaling for more natural feel
            sensitivity = base_sensitivity * zoom_factor
            
            # move opposite to mouse-drag so it feels like map panning
            self.position.x -= self._pan_delta.x * sensitivity
            # invert vertical drag:
            self.position.z -= self._pan_delta.y * sensitivity
            print(f"Mouse drag: delta({self._pan_delta.x}, {self._pan_delta.y}) -> pos({self.position.x:.3f}, {self.position.z:.3f}) [sens: {sensitivity:.4f}]")

        # --- Mouse-wheel zoom ---
        if self._zoom_delta != 0:
            old_zoom = self.zoom
            self.zoom -= self._zoom_delta * self.zoom_speed * dt
            self.zoom = max(self.min_zoom, min(self.max_zoom, self.zoom))
            self.position.y = self.zoom
            print(f"Zoom: delta={self._zoom_delta}, old={old_zoom:.2f}, new={self.zoom:.2f}")

    def Matrix(self, FOVdeg, near, far, Shader, uniform="gVP"):
        # Build view/proj and upload exactly as before
        view = glm.lookAt(
            self.position,
            self.position + self.orientation,
            self.up
        )
        proj = glm.perspective(
            glm.radians(FOVdeg),
            self.width / self.height,
            near, far
        )
        vp = proj * view

        loc = glGetUniformLocation(Shader.ID, uniform)
        if loc != -1:
            glUniformMatrix4fv(loc, 1, GL_FALSE, glm.value_ptr(vp))
        else:
            print(f"[Warning] '{uniform}' not found")
