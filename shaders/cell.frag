#version 330 core

in vec2 cellUV;
layout(location = 0) out vec4 FragColor;

uniform int gCellState = 1;  // 1=alive, 2=hovering, etc.

void main() {
    vec3 color;
    float alpha = 1.0;
    
    if (gCellState == 1) {
        // Alive cell - white
        color = vec3(0.0, 1.0, 1.0);
    } else if (gCellState == 2) {
        // Hovering cell - semi-transparent blue
        color = vec3(0.0, 0.5, 1.0);
        alpha = 0.6;
    }
    else {
        // Dead cell - transparent
        color = vec3(0.0, 0.0, 0.0);
        alpha = 0.0;
    }
    
    // Optional: Add rounded corners
    vec2 center = cellUV - 0.5;
    float dist = length(center);
    float roundness = 0.1;
    //alpha *= smoothstep(0.5, 0.5 - roundness, dist);
    
    FragColor = vec4(color, 1.0);
}