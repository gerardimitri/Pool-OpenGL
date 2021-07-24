import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import random
import sys
import os.path

from numpy.core.defchararray import array
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import grafica.transformations as tr
import grafica.basic_shapes as bs
import grafica.easy_shaders as es
import grafica.lighting_shaders as ls
import grafica.performance_monitor as pm
from grafica.assets_path import getAssetPath
from OBJreader import *
from collisions import *

__author__ = "Gerardo Trincado"
__license__ = "MIT"

CIRCLE_DISCRETIZATION = 20
RADIUS = 0.4
SPEED = 12
FRICTION = 0.2

# A class to store the application control
class Controller:
    def __init__(self):
        self.fillPolygon = True
        self.circleCollisions = True
        self.useGravity = False
        self.upcam = True

# we will use the global controller as communication with the callback function
controller = Controller()


def on_key(window, key, scancode, action, mods):

    if action != glfw.PRESS:
        return
    
    global controller

    if key == glfw.KEY_SPACE:
        controller.fillPolygon = not controller.fillPolygon
    
    if key == glfw.KEY_UP:
            balls[0].velocity = np.array([-SPEED*np.sin(camera_theta), -SPEED*np.cos(camera_theta), 0])
    
    elif key == glfw.KEY_DOWN:
        controller.upcam = not controller.upcam

    elif key == glfw.KEY_ESCAPE:
        glfw.set_window_should_close(window, True)


ball_pos=[np.array([8, 0, 0], dtype=np.float32),
    np.array([-5, 0, 0], dtype=np.float32),
    np.array([-5-np.sqrt(3)*RADIUS, RADIUS, 0], dtype=np.float32),
    np.array([-5-np.sqrt(3)*RADIUS, -RADIUS, 0], dtype=np.float32),
    np.array([-5-2*np.sqrt(3)*RADIUS, 0, 0], dtype=np.float32),
    np.array([-5-2*np.sqrt(3)*RADIUS, 2*RADIUS, 0], dtype=np.float32),
    np.array([-5-2*np.sqrt(3)*RADIUS, -2*RADIUS, 0], dtype=np.float32),
    np.array([-5-3*np.sqrt(3)*RADIUS, RADIUS, 0], dtype=np.float32),
    np.array([-5-3*np.sqrt(3)*RADIUS, -RADIUS, 0], dtype=np.float32),
    np.array([-5-3*np.sqrt(3)*RADIUS, 3*RADIUS, 0], dtype=np.float32),
    np.array([-5-3*np.sqrt(3)*RADIUS, -3*RADIUS, 0], dtype=np.float32),
    np.array([-5-4*np.sqrt(3)*RADIUS, 0, 0], dtype=np.float32),
    np.array([-5-4*np.sqrt(3)*RADIUS, 2*RADIUS, 0], dtype=np.float32),
    np.array([-5-4*np.sqrt(3)*RADIUS, -2*RADIUS, 0], dtype=np.float32),
    np.array([-5-4*np.sqrt(3)*RADIUS, 4*RADIUS, 0], dtype=np.float32),
    np.array([-5-4*np.sqrt(3)*RADIUS, -4*RADIUS, 0], dtype=np.float32),
    ]

ball_rgb =[]
counter_red=0
counter_yellow=0
for i in range(16):
    color_id=random.randint(0,1)
    if i ==0:
        ball_rgb.append(np.array([1,1,1]))
    elif i ==4:
        ball_rgb.append(np.array([0.1,0.1,0.1]))
    elif counter_red<7 and color_id==0:
        ball_rgb.append(np.array([1,0,0]))
        counter_red+=1
    elif counter_yellow<7 and color_id==1:
        ball_rgb.append(np.array([1,1,0]))
        counter_yellow+=1
    elif counter_red<7:
        ball_rgb.append(np.array([1,0,0]))
        counter_red+=1
    else:
        ball_rgb.append(np.array([1,1,0]))
        counter_yellow+=1

if __name__ == "__main__":

    # Initialize glfw
    if not glfw.init():
        glfw.set_window_should_close(window, True)

    width = 600
    height = 600
    title = "Pool Party"
    window = glfw.create_window(width, height, title, None, None)

    if not window:
        glfw.terminate()
        glfw.set_window_should_close(window, True)

    glfw.make_context_current(window)

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, on_key)

    # Defining shader programs
    pipeline = ls.SimpleGouraudShaderProgram()
    phongPipeline = ls.SimpleTexturePhongShaderProgram()
    rgbPhongPipeline = ls.SimplePhongShaderProgram()
    mvpPipeline = es.SimpleModelViewProjectionShaderProgram()

    # Telling OpenGL to use our shader program
    glUseProgram(pipeline.shaderProgram)

    # Setting up the clear screen color
    glClearColor(0.85, 0.85, 0.85, 1.0)

    # As we work in 3D, we need to check which part is in front,
    # and which one is at the back
    glEnable(GL_DEPTH_TEST)

    # Convenience function to ease initialization
    def createGPUShape(pipeline, shape):
        gpuShape = es.GPUShape().initBuffers()
        pipeline.setupVAO(gpuShape)
        gpuShape.fillBuffers(shape.vertices, shape.indices, GL_STATIC_DRAW)
        return gpuShape

    # Creating shapes on GPU memory
    gpuAxis = createGPUShape(mvpPipeline, bs.createAxis(7))

    shapePoolTable = readOBJ('assets/pool_table.obj')
    gpuPoolTable = createGPUShape(phongPipeline, shapePoolTable)
    gpuPoolTable.texture = es.textureSimpleSetup('assets/pool_table.jpg', GL_REPEAT, GL_REPEAT, GL_LINEAR, GL_LINEAR)


    # Setting uniforms that will NOT change on each iteration
    
    glUseProgram(phongPipeline.shaderProgram)
    glUniform3f(glGetUniformLocation(phongPipeline.shaderProgram, "La"), 1.0, 1.0, 1.0)
    glUniform3f(glGetUniformLocation(phongPipeline.shaderProgram, "Ld"), 1.0, 1.0, 1.0)
    glUniform3f(glGetUniformLocation(phongPipeline.shaderProgram, "Ls"), 1.0, 1.0, 1.0)

    glUniform3f(glGetUniformLocation(phongPipeline.shaderProgram, "Ka"), 0.4, 0.4, 0.4)
    glUniform3f(glGetUniformLocation(phongPipeline.shaderProgram, "Kd"), 0.9, 0.9, 0.9)
    glUniform3f(glGetUniformLocation(phongPipeline.shaderProgram, "Ks"), 1.0, 1.0, 1.0)

    glUniform3f(glGetUniformLocation(phongPipeline.shaderProgram, "lightPosition"), 0, 0, 20)
    
    glUniform1ui(glGetUniformLocation(phongPipeline.shaderProgram, "shininess"), 100)
    glUniform1f(glGetUniformLocation(phongPipeline.shaderProgram, "constantAttenuation"), 0.001)
    glUniform1f(glGetUniformLocation(phongPipeline.shaderProgram, "linearAttenuation"), 0.1)
    glUniform1f(glGetUniformLocation(phongPipeline.shaderProgram, "quadraticAttenuation"), 0.01)

    # Setting up the projection transform
    projection = tr.perspective(60, float(width)/float(height), 0.1, 100)
    glUniformMatrix4fv(glGetUniformLocation(phongPipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)

    glUseProgram(mvpPipeline.shaderProgram)
    glUniformMatrix4fv(glGetUniformLocation(mvpPipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
    glUniformMatrix4fv(glGetUniformLocation(mvpPipeline.shaderProgram, "model"), 1, GL_TRUE, tr.identity())

    t0 = glfw.get_time()
    camera_theta = -3*np.pi/4

    perfMonitor = pm.PerformanceMonitor(glfw.get_time(), 0.5)

    #Pelotas, seteamos el shader
    glUseProgram(rgbPhongPipeline.shaderProgram)
    glUniform3f(glGetUniformLocation(rgbPhongPipeline.shaderProgram, "La"), 1.0, 1.0, 1.0)
    glUniform3f(glGetUniformLocation(rgbPhongPipeline.shaderProgram, "Ld"), 1.0, 1.0, 1.0)
    glUniform3f(glGetUniformLocation(rgbPhongPipeline.shaderProgram, "Ls"), 1.0, 1.0, 1.0)

    glUniform3f(glGetUniformLocation(rgbPhongPipeline.shaderProgram, "Ka"), 0.6, 0.6, 0.6)
    glUniform3f(glGetUniformLocation(rgbPhongPipeline.shaderProgram, "Kd"), 0.8, 0.8, 0.8)
    glUniform3f(glGetUniformLocation(rgbPhongPipeline.shaderProgram, "Ks"), 1.0, 1.0, 1.0)

    glUniform3f(glGetUniformLocation(rgbPhongPipeline.shaderProgram, "lightPosition"), 0, 0, 20)
    
    glUniform1ui(glGetUniformLocation(rgbPhongPipeline.shaderProgram, "shininess"), 100)
    glUniform1f(glGetUniformLocation(rgbPhongPipeline.shaderProgram, "constantAttenuation"), 0.001)
    glUniform1f(glGetUniformLocation(rgbPhongPipeline.shaderProgram, "linearAttenuation"), 0.1)
    glUniform1f(glGetUniformLocation(rgbPhongPipeline.shaderProgram, "quadraticAttenuation"), 0.01)

    # Setting up the projection transform
    projection = tr.perspective(60, float(width)/float(height), 0.1, 100)
    glUniformMatrix4fv(glGetUniformLocation(rgbPhongPipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)


    #balls
    # Creating shapes on GPU memory
    balls = []
    for i in range(16):
        position = ball_pos[i]
        velocity = np.array([
            0.0,
            0.0,
            0.0
        ])
        r, g, b = ball_rgb[i][0], ball_rgb[i][1], ball_rgb[i][2]
        ball = Circle(rgbPhongPipeline, position, velocity, r, g, b)
        balls += [ball]

    perfMonitor = pm.PerformanceMonitor(glfw.get_time(), 0.5)


    # glfw will swap buffers as soon as possible
    glfw.swap_interval(0)

    while not glfw.window_should_close(window):


        # Measuring performance
        perfMonitor.update(glfw.get_time())
        glfw.set_window_title(window, title + str(perfMonitor))
        deltaTime = perfMonitor.getDeltaTime()

        # Using GLFW to check for input events
        glfw.poll_events()

        # Getting the time difference from the previous iteration
        t1 = glfw.get_time()
        dt = t1 - t0
        t0 = t1
        
        # Physics!
        for ball in balls:
            # moving each circle
            ball.action(FRICTION, deltaTime)
            # checking and processing collisions against the border
            collideWithBorder(ball)

        # checking and processing collisions among circles
        if controller.circleCollisions:
            for i in range(len(balls)):
                for j in range(i+1, len(balls)):
                    if areColliding(balls[i], balls[j]):
                        collide(balls[i], balls[j])

        #Camera Setup
        if (glfw.get_key(window, glfw.KEY_LEFT) == glfw.PRESS):
            camera_theta -= 2 * dt

        if (glfw.get_key(window, glfw.KEY_RIGHT) == glfw.PRESS):
            camera_theta += 2* dt

        # Setting up the view transform
        if controller.upcam:
            R = 20
            camX = R * np.sin(camera_theta)
            camY = R * np.cos(camera_theta)
            viewPos = np.array([camX, camY, 20])
            viewAt = np.array([0,0,0])
        else:
            R = 5
            camX = balls[0].position[0] + R * np.sin(camera_theta)
            camY = balls[0].position[1] + R * np.cos(camera_theta)
            viewPos = np.array([camX, camY, 2])
            viewAt = np.array([balls[0].position[0], balls[0].position[1], 0])

            
        view = tr.lookAt(
            viewPos,
            viewAt,
            np.array([0,0,1])
        )

        

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Filling or not the shapes depending on the controller state
        if (controller.fillPolygon):
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        

        # Drawing shapes
        glUseProgram(phongPipeline.shaderProgram)
        glUniform3f(glGetUniformLocation(phongPipeline.shaderProgram, "viewPosition"), viewPos[0], viewPos[1], viewPos[2])
        glUniformMatrix4fv(glGetUniformLocation(phongPipeline.shaderProgram, "view"), 1, GL_TRUE, view)

        glUniformMatrix4fv(glGetUniformLocation(phongPipeline.shaderProgram, "model"), 1, GL_TRUE, tr.matmul([
            tr.translate(0,0,-7.5),tr.uniformScale(0.1)]))
        phongPipeline.drawCall(gpuPoolTable)

        
        glUseProgram(mvpPipeline.shaderProgram)
        glUniformMatrix4fv(glGetUniformLocation(mvpPipeline.shaderProgram, "view"), 1, GL_TRUE, view)
        mvpPipeline.drawCall(gpuAxis, GL_LINES)

        glUseProgram(rgbPhongPipeline.shaderProgram)
        glUniform3f(glGetUniformLocation(rgbPhongPipeline.shaderProgram, "viewPosition"), viewPos[0], viewPos[1], viewPos[2])
        glUniformMatrix4fv(glGetUniformLocation(rgbPhongPipeline.shaderProgram, "view"), 1, GL_TRUE, view)
        # drawing all the circles
        for ball in balls:
            ball.draw()


        # Once the drawing is rendered, buffers are swap so an uncomplete drawing is never seen.
        glfw.swap_buffers(window)

    # freeing GPU memory
    gpuAxis.clear()
    gpuPoolTable.clear()
    for ball in balls:
        ball.gpuShape.clear()

    glfw.terminate()

