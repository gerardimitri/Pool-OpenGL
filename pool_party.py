from OBJreader import *
from collisions import *
from skybox import *
import json

__author__ = "Gerardo Trincado"
__license__ = "MIT"

SPEED = 12
move_ball=[False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False]

# A class to store the application control
class Controller:
    def __init__(self):
        self.fillPolygon = True
        self.ballCollisions = True
        self.useGravity = False
        self.upcam = 0

# we will use the global controller as communication with the callback function
controller = Controller()


def on_key(window, key, scancode, action, mods):

    if action != glfw.PRESS:
        return
    
    global controller

    if key == glfw.KEY_SPACE:
        controller.fillPolygon = not controller.fillPolygon
    
    if key == glfw.KEY_UP:
        for i in range(len(balls)):
            ball=balls[i]
            if np.linalg.norm(ball.velocity)<0.1:
                move_ball[i] = True
            else:
                move_ball[i] = False
        
        if False not in move_ball:
            balls[0].velocity = np.array([-SPEED*np.sin(camera_theta), -SPEED*np.cos(camera_theta), 0])
    
    elif key == glfw.KEY_1:
        controller.upcam = 0

    elif key == glfw.KEY_2:
        controller.upcam = 1

    elif key == glfw.KEY_3:
        controller.upcam = 2

    elif key == glfw.KEY_ESCAPE:
        glfw.set_window_should_close(window, True)

ball_radius = 0.33
ball_pos=[np.array([8, 0, 0], dtype=np.float32),
    np.array([-5, 0, 0], dtype=np.float32),
    np.array([-5-np.sqrt(3)*ball_radius, ball_radius, 0], dtype=np.float32),
    np.array([-5-np.sqrt(3)*ball_radius, -ball_radius, 0], dtype=np.float32),
    np.array([-5-2*np.sqrt(3)*ball_radius, 0, 0], dtype=np.float32),
    np.array([-5-2*np.sqrt(3)*ball_radius, 2*ball_radius, 0], dtype=np.float32),
    np.array([-5-2*np.sqrt(3)*ball_radius, -2*ball_radius, 0], dtype=np.float32),
    np.array([-5-3*np.sqrt(3)*ball_radius, ball_radius, 0], dtype=np.float32),
    np.array([-5-3*np.sqrt(3)*ball_radius, -ball_radius, 0], dtype=np.float32),
    np.array([-5-3*np.sqrt(3)*ball_radius, 3*ball_radius, 0], dtype=np.float32),
    np.array([-5-3*np.sqrt(3)*ball_radius, -3*ball_radius, 0], dtype=np.float32),
    np.array([-5-4*np.sqrt(3)*ball_radius, 0, 0], dtype=np.float32),
    np.array([-5-4*np.sqrt(3)*ball_radius, 2*ball_radius, 0], dtype=np.float32),
    np.array([-5-4*np.sqrt(3)*ball_radius, -2*ball_radius, 0], dtype=np.float32),
    np.array([-5-4*np.sqrt(3)*ball_radius, 4*ball_radius, 0], dtype=np.float32),
    np.array([-5-4*np.sqrt(3)*ball_radius, -4*ball_radius, 0], dtype=np.float32),
    ]

ball_rgb =[]
counter_red=0
counter_yellow=0
red_pos=np.array([1,3,5,7,10,13,14])
for i in range(16):
    if i ==0:
        ball_rgb.append(np.array([1,1,1]))
    elif i ==4:
        ball_rgb.append(np.array([0.1,0.1,0.1]))
    elif counter_red<7 and i in red_pos:
        ball_rgb.append(np.array([1,0,0]))
        counter_red+=1
    else:
        ball_rgb.append(np.array([1,1,0]))
        counter_yellow+=1

if __name__ == "__main__":
    jason = str(sys.argv[1])
    #jason = 'config.json'
    jason_file = open (jason, "r")
    jason_dic = json.loads(jason_file.read())[0]
    #print(jason_dic)

    FRICTION = jason_dic['friction']
    RESTITUTION = jason_dic['restitution']

    # Initialize glfw
    if not glfw.init():
        glfw.set_window_should_close(window, True)

    width = 1280
    height = 720
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
    textureShaderProgram = es.SimpleTextureModelViewProjectionShaderProgram()

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

    skybox = create_skybox(textureShaderProgram)
    gpuPoint = createGPUShape(mvpPipeline, bs.createColorCircle(20, 0.9, 0.9, 0.9))
    shapePoolTable = readOBJ('assets/pool_table.obj')
    gpuPoolTable = createGPUShape(phongPipeline, shapePoolTable)
    gpuPoolTable.texture = es.textureSimpleSetup('assets/pool_table.jpg', GL_REPEAT, GL_REPEAT, GL_LINEAR, GL_LINEAR)
    gpuArrow = createTextureGPUShape(bs.createTextureQuad(1,1), textureShaderProgram, "assets/arrow.png" )

    shapePoolCue = readOBJ('assets/pool_cue.obj')
    gpuPoolCue = createGPUShape(phongPipeline, shapePoolCue)
    gpuPoolCue.texture = es.textureSimpleSetup('assets/pool_cue.jpg', GL_REPEAT, GL_REPEAT, GL_LINEAR, GL_LINEAR)


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

    glUseProgram(textureShaderProgram.shaderProgram)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glUniformMatrix4fv(glGetUniformLocation(textureShaderProgram.shaderProgram, "projection"), 1, GL_TRUE, projection)
    #glUniformMatrix4fv(glGetUniformLocation(textureShaderProgram.shaderProgram, "model"), 1, GL_TRUE, tr.identity())


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
        ball = Ball(rgbPhongPipeline, position, velocity, r, g, b, textureShaderProgram)
        balls += [ball]

    #cue
    draw_cue=[False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False]

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
            # moving each ball
            ball.action(FRICTION, deltaTime)
            # checking and processing collisions against the border
            collideWithBorder(ball)

        # checking and processing collisions among balls
        if controller.ballCollisions:
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
        if controller.upcam == 0:
            camX = 0
            camY = 0
            viewPos = np.array([camX, camY, 20])
            viewAt = np.array([0,0,0])
            viewUp = np.array([0,1,0])

        elif controller.upcam == 1:
            R = 20
            camX = R * np.sin(camera_theta)
            camY = R * np.cos(camera_theta)
            viewPos = np.array([camX, camY, 20])
            viewAt = np.array([0,0,0])
            viewUp = np.array([0,0,1])
        else:
            R = 5
            camX = balls[0].position[0] + R * np.sin(camera_theta)
            camY = balls[0].position[1] + R * np.cos(camera_theta)
            viewPos = np.array([camX, camY, 2])
            viewAt = np.array([balls[0].position[0], balls[0].position[1], 0])
            viewUp = np.array([0,0,1])

            
        view = tr.lookAt(
            viewPos,
            viewAt,
            viewUp
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
            tr.translate(0,0,-7.4),tr.uniformScale(0.1)]))
        phongPipeline.drawCall(gpuPoolTable)

        for i in range(len(balls)):
            if np.linalg.norm(balls[i].velocity) <0.02:
                draw_cue[i] = True
            else:
                draw_cue[i] = False

        if False not in draw_cue:
            cue_delta = 16.5
            cue_pos=balls[0].position
            cueX = cue_pos[0] + cue_delta * np.sin(camera_theta)
            cueY = cue_pos[1] + cue_delta * np.cos(camera_theta)
            cueZ = cue_pos[2]
            glUniformMatrix4fv(glGetUniformLocation(phongPipeline.shaderProgram, "model"), 1, GL_TRUE, tr.matmul([
                tr.translate(cueX, cueY, cueZ),
                tr.rotationZ(-camera_theta),
                tr.rotationX(np.pi/2-0.02),
                tr.uniformScale(0.1)]))
            phongPipeline.drawCall(gpuPoolCue)

        glUseProgram(mvpPipeline.shaderProgram)
        #mvpPipeline.drawCall(gpuAxis, GL_LINES)
        points=[]
        for ball in balls:
            if False in draw_cue:
                if ball.velocity.any() > 0.001:
                    glUniformMatrix4fv(glGetUniformLocation(mvpPipeline.shaderProgram, "model"), 1, GL_TRUE, 
                        tr.translate(ball.position[0], ball.position[1], 0.1)
                            )
                    mvpPipeline.drawCall(gpuPoint)

        glUseProgram(textureShaderProgram.shaderProgram)
        glUniformMatrix4fv(glGetUniformLocation(textureShaderProgram.shaderProgram, "view"), 1, GL_TRUE, view)
        sg.drawSceneGraphNode(skybox, textureShaderProgram, "model")

        if False not in draw_cue and controller.upcam < 2:
            arrow_delta = 1.5
            arrow_pos=balls[0].position
            arrowX = arrow_pos[0] - arrow_delta * np.sin(camera_theta)
            arrowY = arrow_pos[1] - arrow_delta * np.cos(camera_theta)
            arrowZ = arrow_pos[2] - 0.32
            glUniformMatrix4fv(glGetUniformLocation(textureShaderProgram.shaderProgram, "model"), 1, GL_TRUE, tr.matmul([
                    tr.translate(arrowX, arrowY, arrowZ),
                    tr.rotationZ(-camera_theta - np.pi/2),
                    tr.scale(3,1,1)]))
            textureShaderProgram.drawCall(gpuArrow)
            
        elif False not in draw_cue and controller.upcam > 1:
            arrow_delta = 3.5
            arrow_pos=balls[0].position
            arrowX = arrow_pos[0] - arrow_delta * np.sin(camera_theta)
            arrowY = arrow_pos[1] - arrow_delta * np.cos(camera_theta)
            arrowZ = arrow_pos[2] - 0.32
            glUniformMatrix4fv(glGetUniformLocation(textureShaderProgram.shaderProgram, "model"), 1, GL_TRUE, tr.matmul([
                    tr.translate(arrowX, arrowY, arrowZ),
                    tr.rotationZ(-camera_theta - np.pi/2),
                    tr.scale(2,0.5,1)]))
            textureShaderProgram.drawCall(gpuArrow)

        for ball in balls:
            if ball.exists:
                ball.draw_shadow()

        glUseProgram(rgbPhongPipeline.shaderProgram)
        glUniform3f(glGetUniformLocation(rgbPhongPipeline.shaderProgram, "viewPosition"), viewPos[0], viewPos[1], viewPos[2])
        glUniformMatrix4fv(glGetUniformLocation(rgbPhongPipeline.shaderProgram, "view"), 1, GL_TRUE, view)

        # drawing all the balls
        for ball in balls:
            if ball.exists:
                ball.draw()
            else:
                balls.remove(ball)
                draw_cue.pop(0)
                move_ball.pop(0)

        #Once the drawing is rendered, buffers are swap so an uncomplete drawing is never seen.
        glfw.swap_buffers(window)

    # freeing GPU memory
    skybox.clear()
    gpuAxis.clear()
    gpuPoolTable.clear()
    gpuPoolCue.clear()
    gpuArrow.clear()
    for ball in balls:
        ball.gpuShape.clear()

    glfw.terminate()

