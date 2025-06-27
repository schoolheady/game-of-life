#version 330 core

out vec3 WorldPos;

uniform mat4 gVP;
uniform float gGridSize = 10000.0;
uniform vec3 gCameraWorldPos;
// a single full-screen quad via gl_VertexID - made much larger
const vec3 Pos[4] = vec3[4](
    vec3( -10.0,  0.0, -10.0),
    vec3(  10.0,  0.0, -10.0),
    vec3(  10.0,  0.0,  10.0),
    vec3( -10.0,  0.0,  10.0)
);
const int Indices[6] = int[6](0,2,1,2,0,3);

void main(){
    int Index = Indices[gl_VertexID];
    float dynamicGridSize = max(1000.0, gCameraWorldPos.y * 100.0);

    vec3 vPos3 = Pos[Index] * dynamicGridSize;
    
    vPos3.x += gCameraWorldPos.x;
    vPos3.z += gCameraWorldPos.z;
    vec4 vPos4 = vec4(vPos3, 1.0);
    gl_Position = gVP * vPos4;
    WorldPos = vPos3;


}
