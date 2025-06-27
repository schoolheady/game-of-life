# Conway's Game of Life - Interactive Implementation

A modern, interactive implementation of Conway's Game of Life featuring:

- **Infinite World**: Place cells anywhere with dynamic texture management
- **Perfect Mouse-to-Grid Alignment**: Precise cell placement with visual hover preview
- **Interactive Editing**: Edit cells in all game states (Start, Running, Paused)
- **Eye-Friendly Design**: Dark theme with warm colors optimized for extended use
- **Efficient Rendering**: OpenGL-based rendering with unified grid/cell shaders
- **Modular Architecture**: Clean, maintainable codebase with separated concerns

## Technologies Used

- **PyOpenGL**: Hardware-accelerated OpenGL rendering
- **Pygame**: Window management and input handling
- **GLM**: Mathematics library for 3D transformations
- **NumPy**: Efficient array operations for texture management

## Features

### Visual Design
- Dark blue-gray background for eye comfort
- Soft grid lines that adapt to zoom level
- Warm orange cells for alive states
- Soft green hover preview for cell placement
- Adaptive cell padding to maintain grid visibility at all zoom levels

### Interaction
- **Mouse**: Click to place/remove cells, drag to pan, scroll to zoom
- **Keyboard**: 
  - `SPACE`: Start/pause/resume simulation
  - `R`: Reset the world
  - `WASD`: Pan the camera
  - `ESC`: Exit application

### Technical Features
- Dynamic texture resizing for truly infinite world support
- Perfect camera-to-grid coordinate alignment using floor() operations
- State machine with interactive editing capabilities
- Conway's rules implemented with efficient neighbor counting
- Modular codebase with separated rendering, game logic, and input handling

## Project Structure

```
├── main.py              # Entry point (delegates to app.py)
├── app.py               # Main application orchestration
├── game.py              # Game state and logic management
├── cells.py             # Conway's rules and cell management
├── renderer.py          # OpenGL rendering system
├── camera.py            # Camera controls and coordinate transforms
├── input_handler.py     # Input processing and event handling
├── shaders.py           # Shader compilation utilities
├── shaders/
│   ├── quad.vert        # Vertex shader for infinite grid
│   └── grid.frag        # Fragment shader for unified grid/cells
└── requirements.txt     # Python dependencies
```

## Installation and Usage

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Application**:
   ```bash
   python main.py
   ```

3. **Interact with the Game**:
   - Click anywhere to place/remove cells
   - Use mouse drag to pan around the infinite world
   - Scroll to zoom in/out
   - Press SPACE to start the simulation
   - Press R to reset and start over

## Implementation Highlights

### Infinite World Support
The game uses dynamic texture management to support truly infinite cell placement. The texture automatically resizes as needed and maintains proper coordinate mapping between world space and texture space.

### Perfect Alignment
Both the camera system and fragment shader use consistent `floor()` operations to ensure perfect mouse-to-grid alignment at all zoom levels.

### Modular Design
The codebase is organized into focused modules:
- `Cells`: Implements Conway's rules and manages cell states
- `Game`: Coordinates game state and texture management  
- `Renderer`: Handles all OpenGL operations
- `Camera`: Manages viewport and coordinate transformations
- `InputHandler`: Processes user input and maps to game actions

This architecture makes the code maintainable and allows for easy extension of features.

## Conway's Game of Life Rules

1. Any live cell with fewer than two live neighbors dies (underpopulation)
2. Any live cell with two or three live neighbors lives on to the next generation
3. Any live cell with more than three live neighbors dies (overpopulation)
4. Any dead cell with exactly three live neighbors becomes a live cell (reproduction)
