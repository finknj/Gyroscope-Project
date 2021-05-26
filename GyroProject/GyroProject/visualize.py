import OpenGL.GL
import OpenGL.GLUT
import OpenGL.GLU

print("Imports Successful!")

ax = ay = az = 0.0
yaw_mode = False

def init():
    glShadeMode(GL_SMOOTH)