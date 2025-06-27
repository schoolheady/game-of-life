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
        if keys[K_s]:
            self.position.z += speed
            moved = True
        if keys[K_a]:
            self.position.x -= speed
            moved = True
        if keys[K_d]:
            self.position.x += speed
            moved = True

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

        # --- Mouse-wheel zoom ---
        if self._zoom_delta != 0:
            old_zoom = self.zoom
            self.zoom -= self._zoom_delta * self.zoom_speed * dt
            self.zoom = max(self.min_zoom, min(self.max_zoom, self.zoom))
            self.position.y = self.zoom

    def Matrix(self, FOVdeg, near, far, Shader=None, uniform="gVP"):
        # Build view/proj matrices
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
        
        # Store matrices for ScreentoWorld calculations
        self._last_view = view
        self._last_proj = proj
        
        # If no shader provided, just update matrices
        if Shader is None:
            return
            
        # Ensure shader is bound before setting uniforms
        Shader.use()

        # Upload gVP matrix
        loc = glGetUniformLocation(Shader.ID, uniform)
        if loc != -1:
            glUniformMatrix4fv(loc, 1, GL_FALSE, glm.value_ptr(vp))
        else:
            print(f"[Warning] '{uniform}' not found in shader")
        
        # Upload gCameraWorldPos to shader (required by some vertex shaders)
        camera_pos_loc = glGetUniformLocation(Shader.ID, "gCameraWorldPos")
        if camera_pos_loc != -1:
            glUniform3f(camera_pos_loc, self.position.x, self.position.y, self.position.z)
        
    def ScreentoWorld(self):
        """
        Convert screen coordinates (x, y) to world coordinates.
        If no coordinates provided, uses current mouse position.
        Returns the world position where the mouse is pointing on the Y=0 plane.
        """
        screen_x, screen_y = pygame.mouse.get_pos()
        
        # Store matrices from last Matrix() call for consistency
        if not hasattr(self, '_last_view') or not hasattr(self, '_last_proj'):
            print("Warning: Call Matrix() before ScreentoWorld()")
            return glm.vec2(0, 0)
        
        # Convert screen coordinates to normalized device coordinates (-1 to 1)
        ndc_x = (2.0 * screen_x) / self.width - 1.0
        ndc_y = 1.0 - (2.0 * screen_y) / self.height  # Flip Y axis
        
        # Get inverse matrices
        inv_proj = glm.inverse(self._last_proj)
        inv_view = glm.inverse(self._last_view)
        
        # Convert to clip space
        clip_coords = glm.vec4(ndc_x, ndc_y, -1.0, 1.0)
        
        # Convert to eye space
        eye_coords = inv_proj * clip_coords
        eye_coords = glm.vec4(eye_coords.x, eye_coords.y, -1.0, 0.0)
        
        # Convert to world space direction
        world_coords = inv_view * eye_coords
        ray_direction = glm.normalize(glm.vec3(world_coords))
        
        # Ray-plane intersection with Y=0 plane (where your grid is)
        if abs(ray_direction.y) < 0.0001:  # Ray is parallel to plane
            return glm.vec2(0, 0)
        
        # Solve for intersection: camera_pos + t * ray_direction
        # Where Y component equals 0 (ground plane)
        t = -self.position.y / ray_direction.y
        world_point = self.position + ray_direction * t
    
        #print(f"World point at screen ({screen_x}, {screen_y}): {world_point}")
        return glm.vec2(world_point.x, world_point.z)
    
    def WorldToGrid(self, world_pos, grid_cell_size=0.4):
        """
        Convert world coordinates to grid coordinates.
        Returns grid coordinates (floats).
        """
        return glm.vec2(world_pos.x / grid_cell_size, world_pos.y / grid_cell_size)
    
    def SnapToGrid(self, world_pos, grid_cell_size=0.4):
        """
        Snap world coordinates to the grid cell that contains the coordinate.
        Returns grid coordinates (integers).
        Uses floor() to match shader behavior for perfect alignment.
        """
        grid_coords = self.WorldToGrid(world_pos, grid_cell_size)
        import math
        return glm.ivec2(int(math.floor(grid_coords.x)), int(math.floor(grid_coords.y)))
    
    def GridToWorld(self, grid_pos, grid_cell_size=0.4):
        """
        Convert grid coordinates to world coordinates (cell center).
        """
        return glm.vec2(grid_pos.x * grid_cell_size, grid_pos.y * grid_cell_size)