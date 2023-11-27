import pygame
import imgui
from imgui.integrations.pygame import PygameRenderer
import OpenGL.GL as gl

# 初始化pygame
pygame.init()

# 设置窗口大小和标题
window_size = (800, 600)
screen = pygame.display.set_mode(window_size, pygame.OPENGL | pygame.DOUBLEBUF)
pygame.display.set_caption("imgui and pygame Example")

# 初始化imgui
imgui.create_context()
renderer = PygameRenderer()

# 主循环
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        renderer.process_event(event)

    # 设置imgui的DisplaySize
    io = imgui.get_io()
    io.display_size = window_size

    # 开始imgui框架
    imgui.new_frame()

    # 创建一个imgui窗口
    imgui.begin("Hello, imgui!")

    # 添加一些imgui控件
    imgui.text("Welcome to imgui and pygame example!")
    if imgui.button("Click Me"):
        print("Button clicked!")

    # 结束imgui窗口
    imgui.end()

    # 渲染imgui界面
    gl.glClearColor(0, 0, 0, 1)
    gl.glClear(gl.GL_COLOR_BUFFER_BIT)
    imgui.render()
    renderer.render(imgui.get_draw_data())

    pygame.display.flip()

# 清理资源
renderer.shutdown()
pygame.quit()
