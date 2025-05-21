__kernel void game_of_life_step(
    __global const int* current_state,
    __global int* next_state,
    const int width,
    const int height)
{
    // Get the index of the current element
    const int x = get_global_id(0);
    const int y = get_global_id(1);
    
    // Check if within bounds
    if (x >= width || y >= height)
        return;
    
    // Calculate 1D index from 2D coordinates
    const int current_idx = y * width + x;
    
    // Count alive neighbors using wrapped boundaries (toroidal grid)
    int alive_neighbors = 0;
    
    for (int dy = -1; dy <= 1; dy++) {
        for (int dx = -1; dx <= 1; dx++) {
            // Skip the cell itself
            if (dx == 0 && dy == 0)
                continue;
                
            // Calculate neighbor coordinates with wrapping
            int nx = (x + dx + width) % width;
            int ny = (y + dy + height) % height;
            
            // Get neighbor index
            int neighbor_idx = ny * width + nx;
            
            // Add to count if neighbor is alive
            alive_neighbors += current_state[neighbor_idx];
        }
    }
    
    // Apply Conway's Game of Life rules:
    // 1. Any live cell with fewer than two live neighbors dies (underpopulation)
    // 2. Any live cell with two or three live neighbors lives on
    // 3. Any live cell with more than three live neighbors dies (overpopulation)
    // 4. Any dead cell with exactly three live neighbors becomes a live cell (reproduction)
    
    int current_cell_state = current_state[current_idx];
    int next_cell_state = 0;
    
    if (current_cell_state == 1) {
        // Cell is currently alive
        if (alive_neighbors == 2 || alive_neighbors == 3) {
            next_cell_state = 1;  // Survival
        } else {
            next_cell_state = 0;  // Death
        }
    } else {
        // Cell is currently dead
        if (alive_neighbors == 3) {
            next_cell_state = 1;  // Birth
        } else {
            next_cell_state = 0;  // Remain dead
        }
    }
    
    // Write the new state
    next_state[current_idx] = next_cell_state;
}
