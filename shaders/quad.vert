#version 330 core

out vec3 WorldPos;

uniform mat4 gVP;
uniform vec3 gCameraWorldPos;

const vec3 Pos[4] = vec3[4](
    vec3(-10.0, 0.0, -10.0),
    vec3( 10.0, 0.0, -10.0),
    vec3( 10.0, 0.0,  10.0),
    vec3(-10.0, 0.0,  10.0)
);
const int Indices[6] = int[6](0,2,1,2,0,3);

void main(){
    int Index = Indices[gl_VertexID];
    float dynamicGridSize = max(1000.0, gCameraWorldPos.y * 100.0);

    vec3 vPos3 = Pos[Index] * dynamicGridSize;
    vPos3.x += gCameraWorldPos.x;
    vPos3.z += gCameraWorldPos.z;
    
    gl_Position = gVP * vec4(vPos3, 1.0);
    WorldPos = vPos3;
}
