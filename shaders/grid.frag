#version 330 core

in vec3 WorldPos; // World position from vertex shader
layout(location = 0) out vec4 FragColor;

uniform float gGridMinPixelsBetweenCells = 2.0;
uniform float gGridCellSize = 0.4; // Size of each grid cell
uniform vec4 gGridColorThin = vec4(0.5, 0.5, 0.5, 1.0); // Color for thin grid lines
uniform vec4 gGridColorThick = vec4(0.2, 0.2, 0.2, 1.0); // Color for thick grid lines

// Helper function to get maximum component of a vec2
float max2(vec2 v) {
    return max(v.x, v.y);
}

void main() {
    vec2 dvx = vec2(dFdx(WorldPos.x), dFdy(WorldPos.x));
    vec2 dvy = vec2(dFdx(WorldPos.z), dFdy(WorldPos.z));

    float lx = length(dvx);
    float ly = length(dvy);

    vec2 dudv = vec2(lx, ly);

    float l = length(dudv);

    float LOD = max(0.0, log(l * gGridMinPixelsBetweenCells / gGridCellSize) / log(10.0) + 1.0);

    float GridCellSizeLod0 = gGridCellSize * pow(10.0, floor(LOD));
    dudv *= 4.0;

    vec2 mod_div_dudv = mod(WorldPos.xz, GridCellSizeLod0) / dudv;
    float Lod0a = max2(vec2(1.0) - abs(clamp(mod_div_dudv, 0.0, 1.0) * 2.0 - vec2(1.0)));

    vec4 Color;
    Color = gGridColorThick;
    Color.a *= Lod0a;

    FragColor = Color;
}