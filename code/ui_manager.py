import imgui
from imgui.integrations.pygame import PygameRenderer
import OpenGL.GL as gl
from OpenGL.GL import *
import image_manager as imgmgr
from path_util import PathUtils as pathutil
import tkinter as tk
from tkinter import filedialog
import pygame
from texture_manager import TextureMgr as texmgr

def open_file_dialog(text, file_types):
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口

    file_path = filedialog.askopenfilename(filetypes=[(text, file_types)])
    return file_path

class UIManager:
    def __init__(self, window_size, title, image_manager):
        '''初始化imgui'''
        # 初始化imgui
        imgui.create_context()
        # imgui 中文支持
        io = imgui.get_io()
        # io.fonts.add_font_default()
        io.fonts.add_font_from_file_ttf(
            "C:/Windows/Fonts/simhei.ttf", 16, None, io.fonts.get_glyph_ranges_chinese())
        
        # 初始化图片管理器
        self.image_manager = image_manager
        self.renderer = self.renderer = PygameRenderer()
        self.selected_image = -1

        self.textures = {}

        # 设置imgui的DisplaySize
        self.io = imgui.get_io()
        self.io.display_size = window_size

    def shutdown(self):
        self.renderer.shutdown()

    # 处理事件
    def process_event(self, event):
        self.io = imgui.get_io()
        # if event.type == pygame.MOUSEBUTTONDOWN:
        #     if event.button == 1:
        #         self.io.mouse_down[0] = True
        #     elif event.button == 2:
        #         self.io.mouse_down[1] = True
        #     elif event.button == 3:
        #         self.io.mouse_down[2] = True
        # elif event.type == pygame.MOUSEBUTTONUP:
        #     if event.button == 1:
        #         self.io.mouse_down[0] = False
        #     elif event.button == 2:
        #         self.io.mouse_down[1] = False
        #     elif event.button == 3:
        #         self.io.mouse_down[2] = False
        # elif event.type == pygame.MOUSEWHEEL:
        #     self.io.mouse_wheel = event.y
        # elif event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
        #     key, mapped_key = self.__map_key(event)
        #     self.io.keys_down[mapped_key] = event.type == pygame.KEYDOWN
        #     self.io.key_shift = event.mod & pygame.KMOD_SHIFT
        #     self.io.key_ctrl = event.mod & pygame.KMOD_CTRL
        #     self.io.key_alt = event.mod & pygame.KMOD_ALT
        #     self.io.key_super = event.mod & pygame.KMOD_META
        # elif event.type == pygame.TEXTINPUT:
        #     self.io.add_input_characters(event.text)
        # elif event.type == pygame.QUIT:
        #     self.io.want_quit = True
        self.renderer.process_event(event)

    # 主循环
    def update(self):
        # 开始imgui框架
        imgui.new_frame()

        self.__show_image_list()

        # 显示选中的图片
        if self.selected_image != -1:
            images = list(self.image_manager.get_images().items())
            name, path = images[self.selected_image]
            texId = texmgr.get_instance().create_get_texture(path)
            self.__show_image(texId)

        
            # imgui.text(name)
            # imgui.image_button(
            #     self.renderer.get_texture(path), 200, 200, border_color=(0, 0, 0, 0))

        # 结束imgui窗口
        imgui.end()

        # # set position
        # imageWndPos = imgui.Vec2(280, self.io.display_size.y * 0.15)
        # imageWndSize = imgui.Vec2(200, 200)
        # imgui.set_next_window_position(imageWndPos.x, imageWndPos.y)
        # imgui.set_next_window_size(imageWndSize.x, imageWndSize.y)
        
        # imgui.image_button(self.textures[name],
        #                     200, 200, border_color=(0, 0, 0, 0))
        imgui.render()
        draw_data = imgui.get_draw_data()
        if draw_data is not None:
            self.renderer.render(imgui.get_draw_data())

    def __show_image(self, texId):
        
        # set position
        imageWndPos = imgui.Vec2(280, self.io.display_size.y * 0.15)
        imageWndSize = imgui.Vec2(420, 420)
        imgui.set_next_window_position(imageWndPos.x, imageWndPos.y)
        imgui.set_next_window_size(imageWndSize.x, imageWndSize.y)
        imgui.set_next_window_bg_alpha(0.0)

        flags = imgui.WINDOW_NO_TITLE_BAR | imgui.WINDOW_NO_BACKGROUND | imgui.WINDOW_NO_RESIZE | imgui.WINDOW_NO_MOVE | imgui.WINDOW_NO_SCROLLBAR
        imgui.begin("图片", flags=flags)
        imgui.image(texId, 400, 400)
        imgui.end()
        
    def __show_image_list(self):
        # 创建一个imgui窗口,设置窗口位置在左边居中，size.y大小为高度的0.7倍
        toolWndPos = imgui.Vec2(20, self.io.display_size.y * 0.15)
        toolWndSize = imgui.Vec2(200, self.io.display_size.y * 0.7)
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
