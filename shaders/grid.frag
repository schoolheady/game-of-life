#version 330 core

in vec3 WorldPos;
layout(location = 0) out vec4 FragColor;

uniform float gGridCellSize = 0.4;
uniform vec4 gGridColorThick = vec4(0.5, 0.55, 0.65, 1.0);

uniform usampler2D gGameState;
uniform ivec2 gGridSize;
uniform ivec2 gTextureOffset;
uniform vec2 gHoverPos;
uniform bool gShowHover;

void main() {
    vec2 cellCoord = WorldPos.xz / gGridCellSize;
    vec2 grid = abs(fract(cellCoord - 0.5) - 0.5) / fwidth(cellCoord);
    float line = min(grid.x, grid.y);
    float grid_strength = 1.0 - min(line, 1.0);
    
    ivec2 cellIndex = ivec2(floor(cellCoord));
    
    uint cellState = 0u;
    ivec2 texCoord = cellIndex + gTextureOffset;
    if (texCoord.x >= 0 && texCoord.x < gGridSize.x && 
        texCoord.y >= 0 && texCoord.y < gGridSize.y) {
        cellState = texelFetch(gGameState, texCoord, 0).r;
    }
    
    bool isHoverCell = gShowHover && 
                       cellIndex.x == int(floor(gHoverPos.x)) && 
                       cellIndex.y == int(floor(gHoverPos.y));
    
    vec4 Color = gGridColorThick;
    Color.a *= grid_strength;
    
    if (cellState == 1u) {
        vec2 cellLocalPos = fract(cellCoord);
        vec2 cellDerivative = fwidth(cellCoord);
        float adaptivePadding = max(0.005, max(cellDerivative.x, cellDerivative.y) * 1.5);
        adaptivePadding = min(adaptivePadding, 0.15);
        
        if (cellLocalPos.x > adaptivePadding && cellLocalPos.x < (1.0 - adaptivePadding) &&
            cellLocalPos.y > adaptivePadding && cellLocalPos.y < (1.0 - adaptivePadding)) {
            Color = mix(Color, vec4(1.0, 0.7, 0.3, 1.0), 0.9);
        }
    } else if (isHoverCell) {
        vec2 cellLocalPos = fract(cellCoord);
        vec2 cellDerivative = fwidth(cellCoord);
        float adaptivePadding = max(0.005, max(cellDerivative.x, cellDerivative.y) * 1.5);
        adaptivePadding = min(adaptivePadding, 0.15);
        
        if (cellLocalPos.x > adaptivePadding && cellLocalPos.x < (1.0 - adaptivePadding) &&
            cellLocalPos.y > adaptivePadding && cellLocalPos.y < (1.0 - adaptivePadding)) {
            Color = mix(Color, vec4(0.4, 0.8, 0.5, 0.7), 0.6);
        }
    }

    FragColor = Color;
}