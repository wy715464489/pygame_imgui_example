import pygame
import imgui
from imgui.integrations.pygame import PygameRenderer
import OpenGL.GL as gl
from OpenGL.GL import *
import image_manager as imgmgr

from ui_manager import UIManager as uimgr

# 定义python class Client


class Client:
    # 初始化pygame
    def __init__(self, window_size, title):
        pygame.init()

        # 设置窗口大小和标题
        self.screen = pygame.display.set_mode(
            window_size, pygame.OPENGL | pygame.DOUBLEBUF)
        # pygame.display.set_caption("imgui and pygame Example")
        pygame.display.set_caption(title)
        # 初始化图片管理器
        self.image_manager = imgmgr.ImageManager()
        self.ui_manager = uimgr(window_size, title, self.image_manager)

    # 主循环
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                self.ui_manager.process_event(event)

            # 渲染imgui界面
            gl.glClearColor(0, 0, 0, 1)
            gl.glClear(gl.GL_COLOR_BUFFER_BIT)
            self.ui_manager.update()
            

            pygame.display.flip()

        # 清理资源
        self.ui_manager.shutdown()
        pygame.quit()
