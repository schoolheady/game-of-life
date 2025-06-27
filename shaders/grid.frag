#version 330 core

in vec3 WorldPos; // World position from vertex shader
layout(location = 0) out vec4 FragColor;

uniform float gGridMinPixelsBetweenCells = 2.0;
uniform float gGridCellSize = 0.4; // Size of each grid cell
uniform vec4 gGridColorThin = vec4(0.4, 0.45, 0.55, 1.0); // Softer grid lines - light blue-gray
uniform vec4 gGridColorThick = vec4(0.5, 0.55, 0.65, 1.0); // Slightly lighter for contrast

// NEW: Game state texture and hover
uniform usampler2D gGameState;  // Texture containing cell states (0=dead, 1=alive)
uniform ivec2 gGridSize;        // Size of the game grid (e.g., 512x512)
uniform ivec2 gTextureOffset;   // Offset for infinite world texture mapping
uniform vec2 gHoverPos;         // Mouse hover position in grid coordinates
uniform bool gShowHover;        // Whether to show hover cell

// Helper function to get maximum component of a vec2
float max2(vec2 v) {
    return max(v.x, v.y);
}

void main() {
    // Simplified grid line calculation - no LOD for perfect alignment
    vec2 cellCoord = WorldPos.xz / gGridCellSize;
    vec2 grid = abs(fract(cellCoord - 0.5) - 0.5) / fwidth(cellCoord);
    float line = min(grid.x, grid.y);
    float grid_strength = 1.0 - min(line, 1.0);
    
    // NEW: Check what's in this cell (use same grid size as visual grid)
    ivec2 cellIndex = ivec2(floor(cellCoord));
    
    // Sample game state texture
    uint cellState = 0u;
    // Use the texture offset to map grid coordinates to texture coordinates
    ivec2 texCoord = cellIndex + gTextureOffset;
    if (texCoord.x >= 0 && texCoord.x < gGridSize.x && 
        texCoord.y >= 0 && texCoord.y < gGridSize.y) {
        cellState = texelFetch(gGameState, texCoord, 0).r;
    }
    
    // Check if this is the hover cell (more precise matching)
    bool isHoverCell = gShowHover && 
                       cellIndex.x == int(floor(gHoverPos.x)) && 
                       cellIndex.y == int(floor(gHoverPos.y));
    
    // Start with grid color
    vec4 Color = gGridColorThick;
    Color.a *= grid_strength;
    
    // NEW: Add cell colors with adaptive padding to show grid lines at all zoom levels
    if (cellState == 1u) {
        // Check if we're in the center of the cell (leaving padding for grid lines)
        vec2 cellLocalPos = fract(cellCoord);
        // Adaptive padding that scales with zoom level, similar to grid line thickness
        vec2 cellDerivative = fwidth(cellCoord);
        float adaptivePadding = max(0.005, max(cellDerivative.x, cellDerivative.y) * 1.5);
        adaptivePadding = min(adaptivePadding, 0.15); // Cap at 15% to make cells bigger
        
        if (cellLocalPos.x > adaptivePadding && cellLocalPos.x < (1.0 - adaptivePadding) &&
            cellLocalPos.y > adaptivePadding && cellLocalPos.y < (1.0 - adaptivePadding)) {
            // Alive cell - warm orange-yellow for better eye comfort
            Color = mix(Color, vec4(1.0, 0.7, 0.3, 1.0), 0.9);
        }
    } else if (isHoverCell) {
        // Check if we're in the center of the cell for hover too
        vec2 cellLocalPos = fract(cellCoord);
        // Same adaptive padding for consistency
        vec2 cellDerivative = fwidth(cellCoord);
        float adaptivePadding = max(0.005, max(cellDerivative.x, cellDerivative.y) * 1.5);
        adaptivePadding = min(adaptivePadding, 0.15); // Cap at 15% to make cells bigger
        
        if (cellLocalPos.x > adaptivePadding && cellLocalPos.x < (1.0 - adaptivePadding) &&
            cellLocalPos.y > adaptivePadding && cellLocalPos.y < (1.0 - adaptivePadding)) {
            // Hover cell - soft green for pleasant preview
            Color = mix(Color, vec4(0.4, 0.8, 0.5, 0.7), 0.6);
        }
    }

    FragColor = Color;
}