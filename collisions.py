import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import random
import sys
import os.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import grafica.transformations as tr
import grafica.basic_shapes as bs
import grafica.easy_shaders as es
import grafica.lighting_shaders as ls
import grafica.performance_monitor as pm
from grafica.assets_path import getAssetPath

NUMBER_OF_BALLS = 10
BALL_DISCRETIZATION = 20
RADIUS = 0.4

def createGPUShape(pipeline, shape):
     # Funcion Conveniente para facilitar la inicializacion de un GPUShape
    gpuShape = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuShape)
    gpuShape.fillBuffers(shape.vertices, shape.indices, GL_STATIC_DRAW)
    return gpuShape

def createTextureGPUShape(shape, pipeline, path):
    # Funcion Conveniente para facilitar la inicializacion de un GPUShape con texturas
    gpuShape = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuShape)
    gpuShape.fillBuffers(shape.vertices, shape.indices, GL_STATIC_DRAW)
    gpuShape.texture = es.textureSimpleSetup(
        path, GL_CLAMP_TO_EDGE, GL_CLAMP_TO_EDGE, GL_NEAREST, GL_NEAREST)
    return gpuShape

def createColorNormalSphere(N, r, g, b, rho=RADIUS):
    # Funcion para crear una esfera con normales

    vertices = []           # lista para almacenar los verices
    indices = []            # lista para almacenar los indices
    dTheta = 2 * np.pi /N   # angulo que hay entre cada iteracion de la coordenada theta
    dPhi = 2 * np.pi /N     # angulo que hay entre cada iteracion de la coordenada phi
    c = 0                   # contador de vertices, para ayudar a indicar los indices

    # Se recorre la coordenada theta
    for i in range(N - 1):
        theta = i * dTheta # angulo theta en esta iteracion
        theta1 = (i + 1) * dTheta # angulo theta en la iteracion siguiente
        # Se recorre la coordenada phi
        for j in range(N):
            phi = j*dPhi # angulo phi en esta iteracion
            phi1 = (j+1)*dPhi # angulo phi en la iteracion siguiente

            # Se crean los vertices necesarios son coordenadas esfericas para cada iteracion

            # Vertice para las iteraciones actuales de theta (i) y phi (j) 
            v0 = [rho*np.sin(theta)*np.cos(phi), rho*np.sin(theta)*np.sin(phi), rho*np.cos(theta)]
            # Vertice para las iteraciones siguiente de theta (i + 1) y actual de phi (j) 
            v1 = [rho*np.sin(theta1)*np.cos(phi), rho*np.sin(theta1)*np.sin(phi), rho*np.cos(theta1)]
            # Vertice para las iteraciones actual de theta (i) y siguiente de phi (j + 1) 
            v2 = [rho*np.sin(theta1)*np.cos(phi1), rho*np.sin(theta1)*np.sin(phi1), rho*np.cos(theta1)]
            # Vertice para las iteraciones siguientes de theta (i + 1) y phi (j + 1) 
            v3 = [rho*np.sin(theta)*np.cos(phi1), rho*np.sin(theta)*np.sin(phi1), rho*np.cos(theta)]
            
            # Se crean los vectores normales para cada vertice segun los valores de rho tongo 
            n0 = [np.sin(theta)*np.cos(phi), np.sin(theta)*np.sin(phi), np.cos(theta)]
            n1 = [np.sin(theta1)*np.cos(phi), np.sin(theta1)*np.sin(phi), np.cos(theta1)]
            n2 = [np.sin(theta1)*np.cos(phi1), np.sin(theta1)*np.sin(phi1), np.cos(theta1)]
            n3 = [np.sin(theta)*np.cos(phi1), np.sin(theta)*np.sin(phi1), np.cos(theta)]


            # Creamos los triangulos superiores
            #        v0
            #       /  \
            #      /    \
            #     /      \
            #    /        \
            #   /          \
            # v1 ---------- v2
            if i == 0:
                #           vertices              color    normales
                vertices += [v0[0], v0[1], v0[2], r, g, b, n0[0], n0[1], n0[2]]
                vertices += [v1[0], v1[1], v1[2], r, g, b, n1[0], n1[1], n1[2]]
                vertices += [v2[0], v2[1], v2[2], r, g, b, n2[0], n2[1], n2[2]]
                indices += [ c + 0, c + 1, c +2 ]
                c += 3

            # Creamos los triangulos inferiores
            # v0 ---------- v3
            #   \          /
            #    \        /
            #     \      /
            #      \    /
            #       \  /
            #        v1
            elif i == (N-2):
                #           vertices              color    normales
                vertices += [v0[0], v0[1], v0[2], r, g, b, n0[0], n0[1], n0[2]]
                vertices += [v1[0], v1[1], v1[2], r, g, b, n1[0], n1[1], n1[2]]
                vertices += [v3[0], v3[1], v3[2], r, g, b, n3[0], n3[1], n3[2]]
                indices += [ c + 0, c + 1, c +2 ]
                c += 3
            
            # Creamos los quads intermedios
            #  v0 -------------- v3
            #  | \                |
            #  |    \             |
            #  |       \          |
            #  |          \       |
            #  |             \    |
            #  |                \ |
            #  v1 -------------- v2
            else: 
                #           vertices              color    normales
                vertices += [v0[0], v0[1], v0[2], r, g, b, n0[0], n0[1], n0[2]]
                vertices += [v1[0], v1[1], v1[2], r, g, b, n1[0], n1[1], n1[2]]
                vertices += [v2[0], v2[1], v2[2], r, g, b, n2[0], n2[1], n2[2]]
                vertices += [v3[0], v3[1], v3[2], r, g, b, n3[0], n3[1], n3[2]]
                indices += [ c + 0, c + 1, c +2 ]
                indices += [ c + 2, c + 3, c + 0 ]
                c += 4
    return bs.Shape(vertices, indices)

class Ball:
    def __init__(self, pipeline, position, velocity, r, g, b, texture_pipeline):
        shape = createColorNormalSphere(BALL_DISCRETIZATION, r, g, b)
        # addapting the size of the ball's vertices to have a ball
        # with the desired radius
        scaleFactor = 2 * RADIUS
        bs.scaleVertices(shape, 9, (scaleFactor, scaleFactor, scaleFactor))
        self.pipeline = pipeline
        self.texpipeline = texture_pipeline
        self.gpuShape = createGPUShape(self.pipeline, shape)
        self.gpuShapeShadow = createTextureGPUShape(bs.createTextureQuad(1, 1), self.texpipeline, 'assets/shadow.png')
        self.position = position
        self.radius = RADIUS
        self.velocity = velocity
        self.exists = True

    def action(self, Friction, deltaTime):
        # Euler integration
        if np.linalg.norm(self.velocity)<0.001:
            self.velocity = np.array([0.0, 0.0, 0.0])
        if np.linalg.norm(self.velocity)==0:
            acceleration=Friction*(self.velocity)*-10
        else:
            acceleration=Friction*(self.velocity/np.linalg.norm(self.velocity))*-10
        self.velocity += deltaTime * acceleration
        self.position += self.velocity * deltaTime

    def draw(self):
        glUniformMatrix4fv(glGetUniformLocation(self.pipeline.shaderProgram, "model"), 1, GL_TRUE, 
        tr.translate(self.position[0], self.position[1], 0.0)
        )
        self.pipeline.drawCall(self.gpuShape)

    def draw_shadow(self):
        glUniformMatrix4fv(glGetUniformLocation(self.texpipeline.shaderProgram, "model"), 1, GL_TRUE, tr.matmul([
        tr.translate(self.position[0], self.position[1], -self.radius+0.1),
        tr.uniformScale(1.5)
        ]))
        self.texpipeline.drawCall(self.gpuShapeShadow)
    

def rotate2D(vector, theta):
    """
    Direct application of a 2D rotation
    """
    sin_theta = np.sin(theta)
    cos_theta = np.cos(theta)

    return np.array([
        cos_theta * vector[0] - sin_theta * vector[1],
        sin_theta * vector[0] + cos_theta * vector[1],
        0.0
    ], dtype = np.float32)


def collide(ball1, ball2):
    """
    If there are a collision between the balls, it modifies the velocity of
    both balls in a way that preserves energy and momentum.
    """
    
    assert isinstance(ball1, Ball)
    assert isinstance(ball2, Ball)

    normal = ball2.position - ball1.position
    normal /= np.linalg.norm(normal)

    ball1MovingToNormal = np.dot(ball2.velocity, normal) > 0.0
    ball2MovingToNormal = np.dot(ball1.velocity, normal) < 0.0

    if not (ball1MovingToNormal and ball2MovingToNormal):

        # obtaining the tangent direction
        tangent = rotate2D(normal, np.pi/2.0)

        # Projecting the velocity vector over the normal and tangent directions
        # for both balls, 1 and 2.
        v1n = np.dot(ball1.velocity, normal) * normal
        v1t = np.dot(ball1.velocity, tangent) * tangent

        v2n = np.dot(ball2.velocity, normal) * normal
        v2t = np.dot(ball2.velocity, tangent) * tangent

        # swaping the normal components...
        
        ball1.velocity = (v2n + v1t)
        ball2.velocity = (v1n + v2t)


def areColliding(ball1, ball2):
    assert isinstance(ball1, Ball)
    assert isinstance(ball2, Ball)

    difference = ball2.position - ball1.position
    distance = np.linalg.norm(difference)
    collisionDistance = ball2.radius + ball1.radius
    return distance < collisionDistance


def collideWithBorder(ball):
    hole_radius = 0.55
    holes=[
        np.array([11.6, 5.2, 0],),
        np.array([11.6, -5.2, 0],),
        np.array([-11.6, 5.2, 0],),
        np.array([-11.6, -5.2, 0],),
        np.array([0, 5.2, 0],),
        np.array([0, -5.2, 0],)
    ]

    for hole in holes:
        if abs(ball.position[0]-hole[0])<hole_radius and abs(ball.position[1]-hole[1])<hole_radius:
            ball.exists=False

    # Right
    if ball.position[0] + ball.radius > 11.6:
        ball.velocity[0] = -abs(ball.velocity[0])

    # Left
    if ball.position[0] < -11.6 + ball.radius:
        ball.velocity[0] = abs(ball.velocity[0])

    # Top
    if ball.position[1] > 5.2 - ball.radius:
        ball.velocity[1] = -abs(ball.velocity[1])

    # Bottom
    if ball.position[1] < -5.2 + ball.radius:
        ball.velocity[1] = abs(ball.velocity[1])

