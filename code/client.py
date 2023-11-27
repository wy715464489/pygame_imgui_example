import pygame
import imgui
from imgui.integrations.pygame import PygameRenderer
import OpenGL.GL as gl
from OpenGL.GL import *
import image_manager as imgmgr
from path_util import PathUtils as pathutil

import tkinter as tk
from tkinter import filedialog


def open_file_dialog(text, file_types):
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口

    file_path = filedialog.askopenfilename(filetypes=[(text, file_types)])
    return file_path
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

        # 初始化imgui
        imgui.create_context()
        # imgui 中文支持
        io = imgui.get_io()
        # io.fonts.add_font_default()
        io.fonts.add_font_from_file_ttf(
            "C:/Windows/Fonts/simhei.ttf", 16, None, io.fonts.get_glyph_ranges_chinese())
        self.renderer = PygameRenderer()

        # 初始化图片管理器
        self.image_manager = imgmgr.ImageManager()

        self.selected_image = -1

        self.textures = {}

    # 主循环
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                self.renderer.process_event(event)

            # 设置imgui的DisplaySize
            io = imgui.get_io()
            io.display_size = self.screen.get_size()

            # 开始imgui框架
            imgui.new_frame()

            # 创建一个imgui窗口,设置窗口位置在左边居中，size.y大小为高度的0.7倍
            toolWndPos = imgui.Vec2(20, io.display_size.y * 0.15)
            toolWndSize = imgui.Vec2(200, io.display_size.y * 0.7)
            imgui.set_next_window_position(toolWndPos.x, toolWndPos.y)
            imgui.set_next_window_size(toolWndSize.x, toolWndSize.y)
            imgui.begin("图片处理")

            if imgui.button("+"):
                # 打开文件对话框
                file = open_file_dialog(
                    "图片文件", "*.png;*.jpg;*.bmp;*.jpeg;*.tga;*.dds")
                if file != None:
                    print(file)
                    self.image_manager.add_image(
                        pathutil(file).get_filename(), file)
            imgui.same_line()
            if imgui.button("-"):
                # 删除选中的图片
                for idx, (name, path) in enumerate(self.image_manager.get_images().items()):
                    if self.selected_image.get(idx, False):
                        self.selected_image.pop(idx)
                        self.image_manager.remove_image(name)
                        break

            # 显示图片列表
            images = list(self.image_manager.get_images().items())
            names = [name for name, _ in images]

            if imgui.begin_child("##Images", width=-1, height=-1):
                clicked, current = imgui.listbox(
                    "##Images", self.selected_image, names)
                if clicked:
                    self.selected_image = current
                imgui.end_child()

            # 显示选中的图片
            if self.selected_image != -1:
                name, path = images[self.selected_image]
                # test
                if name not in self.textures:
                    image = pygame.image.load(path)
                    image = pygame.transform.scale(image, (200, 200))
                    image_data = pygame.image.tostring(image, "RGBA", 1)

                    texture_id = glGenTextures(1)
                    glBindTexture(GL_TEXTURE_2D, texture_id)
                    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image.get_width(
                    ), image.get_height(), 0, GL_RGBA, GL_UNSIGNED_BYTE, image_data)
                    self.textures[name] = texture_id

                # set position
                imageWndPos = imgui.Vec2(280, io.display_size.y * 0.15)
                imageWndSize = imgui.Vec2(200, 200)
                imgui.set_next_window_position(imageWndPos.x, imageWndPos.y)
                imgui.set_next_window_size(imageWndSize.x, imageWndSize.y)
                
                imgui.image_button(self.textures[name],
                                   200, 200, border_color=(0, 0, 0, 0))

                # imgui.text(name)
                # imgui.image_button(
                #     self.renderer.get_texture(path), 200, 200, border_color=(0, 0, 0, 0))

            # 结束imgui窗口
            imgui.end()

            # 渲染imgui界面
            gl.glClearColor(0, 0, 0, 1)
            gl.glClear(gl.GL_COLOR_BUFFER_BIT)
            imgui.render()
            self.renderer.render(imgui.get_draw_data())

            pygame.display.flip()

        # 清理资源
        self.renderer.shutdown()
        pygame.quit()
