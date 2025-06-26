#version 330 core
layout (location = 0) in vec3 aPos;
out vec4 vertex_color;
uniform mat4 camMatrix;
void main()
{
    gl_Position = camMatrix * vec4(aPos, 1.0f);
    vertex_color = vec4(0.0f, 0.5f, 0.2f, 1.0f);
}