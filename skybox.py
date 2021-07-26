import glfw
import math
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import sys
import os.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import grafica.transformations as tr
import grafica.basic_shapes as bs
import grafica.easy_shaders as es
import grafica.scene_graph as sg
from grafica.assets_path import getAssetPath


def create_skybox(pipeline):
    
    shapeSide1 = bs.createTextureQuad(1,1)
    gpuSide1 = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuSide1)
    gpuSide1.fillBuffers(shapeSide1.vertices, shapeSide1.indices, GL_STATIC_DRAW)
    gpuSide1.texture = es.textureSimpleSetup(
        getAssetPath("fov90lado.png"), GL_REPEAT, GL_REPEAT, GL_LINEAR, GL_LINEAR)

    shapeSide2 = bs.createTextureQuad(1,1)
    gpuSide2 = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuSide2)
    gpuSide2.fillBuffers(shapeSide2.vertices, shapeSide1.indices, GL_STATIC_DRAW)
    gpuSide2.texture = es.textureSimpleSetup(
        getAssetPath("fov90_test.png"), GL_REPEAT, GL_REPEAT, GL_LINEAR, GL_LINEAR)
    


    ##########################################################
    Side1 = sg.SceneGraphNode("Side1")
    Side1.transform = tr.matmul([tr.translate(1.0, 0, 0.30), tr.uniformScale(2)])
    Side1.childs += [gpuSide1]

    Side2 = sg.SceneGraphNode("Side2")
    Side2.transform = tr.matmul([tr.translate(0.0, 1.0, 0.30), tr.rotationZ(math.pi/2), tr.uniformScale(2)])
    Side2.childs += [gpuSide2]

    Side3 = sg.SceneGraphNode("Side3")
    Side3.transform = tr.matmul([tr.translate(1.0, 0, 0.30), tr.rotationZ(math.pi), tr.uniformScale(2)])
    Side3.childs += [gpuSide1]

    Side4 = sg.SceneGraphNode("Side4")
    Side4.transform = tr.matmul([tr.translate(0.0, 1.0, 0.30), tr.rotationZ(3*math.pi/2), tr.uniformScale(2)])
    Side4.childs += [gpuSide1]

    newSkybox = sg.SceneGraphNode("Skybox")
    newSkybox.transform = tr.identity()
    newSkybox.childs += [Side1, Side2, Side3, Side4]
    ############################################################
    return newSkybox