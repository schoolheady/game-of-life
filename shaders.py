from OpenGL.GL import *


class Shaders:
    def __init__(self, Vertex_path=str, Fragment_path=str):
        try:
            with open(Vertex_path, 'r') as vfile:
                vertexcode = vfile.read()
            with open(Fragment_path, 'r') as ffile:
                fragmentcode = ffile.read()
        except FileNotFoundError:
            print("[SHADERS][ERROR] read error")
            return
            
        # Create and compile vertex shader
        vertex = glCreateShader(GL_VERTEX_SHADER)
        glShaderSource(vertex, vertexcode)
        glCompileShader(vertex)
        self.check_shader(vertex)
        
        # Create and compile fragment shader
        fragment = glCreateShader(GL_FRAGMENT_SHADER)
        glShaderSource(fragment, fragmentcode)
        glCompileShader(fragment)
        self.check_shader(fragment)
        
        # Create shader program
        self.ID = glCreateProgram()
        glAttachShader(self.ID, vertex)
        glAttachShader(self.ID, fragment)
        glLinkProgram(self.ID)
        
        # Check for linking errors
        success = glGetProgramiv(self.ID, GL_LINK_STATUS)
        if not success:
            infolog = glGetProgramInfoLog(self.ID)
            print(f"[SHADERS][ERROR] SHADER program linking failed: {infolog.decode('utf-8')}")
        
        # Delete shaders as they're linked into the program now
        glDeleteShader(vertex)
        glDeleteShader(fragment)

    def check_shader(self, shader):
        success = glGetShaderiv(shader, GL_COMPILE_STATUS)
        if not success:
            # Get the actual error message
            infolog = glGetShaderInfoLog(shader)
            print(f"[SHADERS][ERROR] SHADER compilation FAILED: {infolog.decode('utf-8')}")
        else:
            print("[SHADERS] Shader compilation successful")
        
    def use(self):
        glUseProgram(self.ID)

    def setbool(self, name=str, value=bool):
        glUniform1i(glGetUniformLocation(self.ID, name), value)
    def SetINT(self ,name=str, value=str):
        glUniform1i(glGetUniformLocation(self.ID, name), value)
    def setFLOAT(self, name=str, value=float):
        glUniform1f(glGetUniformLocation(self.ID, name), value); 

    


    


    