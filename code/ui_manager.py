import math
import imgui
from imgui.integrations.pygame import PygameRenderer
import OpenGL.GL as gl
from OpenGL.GL import *
import numpy as np
import image_manager as imgmgr
from path_util import PathUtils as pathutil
import tkinter as tk
from tkinter import filedialog
import pygame
from texture_manager import TextureMgr as texmgr
import cv2
from enumrate_util import PostProcessEnum as PostProcess
from fpdf import FPDF
import os


# 定义后处理枚举

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

        # 设置imgui的DisplaySize
        self.io = imgui.get_io()
        self.io.display_size = window_size
        self.texture = None
        self.show_edge_points = None
        self.image_edge_points = None
        self.imageWndPos = imgui.Vec2(280, self.io.display_size.y * 0.15)
        self.imageWndSize = imgui.Vec2(620, 620)
        self.innerImageWndSize = imgui.Vec2(self.imageWndSize.x - 20, self.imageWndSize.y - 20)
        # 显示的imgui image windows size 与 原始图片的比例
        self.imageWndScale = imgui.Vec2(1.0,1.0)
        self.current_post_process = PostProcess.NoneProcess

        # self.post_process_items = ["None", "去除阴影", "亮度增强", "增强锐化", "超清", "上采样", "黑白", "灰度"]
        self.post_process_items = ["None",  "亮度增强", "增亮锐化"]

    def shutdown(self):
        texmgr.get_instance().destroy()
        self.renderer.shutdown()

    # 处理事件
    def process_event(self, event):
        self.io = imgui.get_io()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.io.mouse_down[0] = True
            elif event.button == 2:
                self.io.mouse_down[1] = True
            elif event.button == 3:
                self.io.mouse_down[2] = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.io.mouse_down[0] = False
            elif event.button == 2:
                self.io.mouse_down[1] = False
            elif event.button == 3:
                self.io.mouse_down[2] = False
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

    #处理输入事件
    def __input_event(self):
        # 处理鼠标事件
        if self.io.mouse_down[0]:
            # 打印鼠标位置
            # print(self.io.mouse_pos)
            # 当前是否有图片被选中
            if self.selected_image != -1:
                # 是否在图片窗口内
                if self.io.mouse_pos[0] >= self.imageWndPos.x and self.io.mouse_pos[0] <= self.imageWndPos.x + self.imageWndSize.x and self.io.mouse_pos[1] >= self.imageWndPos.y and self.io.mouse_pos[1] <= self.imageWndPos.y + self.imageWndSize.y:
                    # 是否点击到了图片边缘的点
                    if self.show_edge_points is not None:
                        for i in range(len(self.show_edge_points)):
                            # 计算鼠标位置与点的距离
                            distance_sqr = ((self.io.mouse_pos[0] - self.show_edge_points[i][0]) ** 2 + (self.io.mouse_pos[1] - self.show_edge_points[i][1]) ** 2)
                            if distance_sqr < 64:
                                # 拖动点
                                self.show_edge_points[i][0] = self.io.mouse_pos[0]
                                self.show_edge_points[i][1] = self.io.mouse_pos[1]
                                # 计算image_edge_points
                                self.__calc_image_edge()
                                break

    # 裁剪图片
    def __perspective_transform_image(self):
        if self.image_edge_points is None:
            return
        # self.texture.height
        # reverse y
        # image edge points to x,y,w,h
        self.texture.perspective_transform(self.image_edge_points)
        self.image_edge_points = None
        self.show_edge_points = None

    def __sort_edge_points(self, points):
        #逆时针排序
        if points is None:
            return None
        # 计算四边形的中心点
        center_x = sum(point[0] for point in points) / 4
        center_y = sum(point[1] for point in points) / 4
        # 如果 points 是一个 NumPy 数组，将它转换为列表
        if isinstance(points, np.ndarray):
            points = points.tolist()    
        # 按照每个点相对于中心点的角度进行排序
        points.sort(key=lambda point: math.atan2(point[1] - center_y, point[0] - center_x))
        return points

    # 主循环
    def update(self):
        self.__input_event()
        # 开始imgui框架
        imgui.new_frame()

        self.__show_image_list()

        # 显示选中的图片
        if self.selected_image != -1:
            images = list(self.image_manager.get_images().items())
            _, path = images[self.selected_image]
            texture = texmgr.get_instance().create_get_texture(path)
            self.__show_image(texture.gl_tex_id)
            if (self.texture == None or self.texture.gl_tex_id != texture.gl_tex_id):
                self.texture = texture
                self.imageWndScale = imgui.Vec2(self.texture.width / self.innerImageWndSize.x, self.texture.height / self.innerImageWndSize.y)
                # image edge detection
                edge_points = self.__edge_detection(path, 1)
                edge_points = self.__sort_edge_points(edge_points)
                if edge_points is None:
                    #逆时针
                    edge_points = [[0,0],[self.texture.width,0],[self.texture.width,self.texture.height],[0,self.texture.height]]
                # deep copy
                self.image_edge_points = [point.copy() for point in edge_points]
                # add cur imgui window pos
                offsetX = imgui.get_style().window_border_size + imgui.get_style().window_padding.x
                offsetY = imgui.get_style().window_border_size + imgui.get_style().window_padding.y
                for i in range(len(edge_points)):
                    # scale to image window size
                    edge_points[i][0] /= self.imageWndScale.x
                    edge_points[i][1] /= self.imageWndScale.y
                    edge_points[i][0] += self.imageWndPos.x
                    edge_points[i][1] += self.imageWndPos.y
                    # add wnd border
                    edge_points[i][0] += offsetX
                    edge_points[i][1] += offsetY
                self.show_edge_points = edge_points
                
                # for i in range(len(self.image_edge_points)):
                #     print(self.image_edge_points[i])

        # 结束imgui窗口
        imgui.end()
        imgui.render()
        draw_data = imgui.get_draw_data()
        if draw_data is not None:
            self.renderer.render(imgui.get_draw_data())
    
    # 返回四个点的坐标,expand为扩大的像素
    def __edge_detection(self, path:str, expand:int):
        # use opencv to detect edge
        img = cv2.imread(path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        canny = cv2.Canny(blur, 50, 150)

        # 寻找轮廓，只寻找外轮廓
        contours, _ = cv2.findContours(canny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]

        # 寻找边缘的四个点
        for c in contours:
            # 计算轮廓近似
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.02 * peri, True)
            if len(approx) == 4:
                points = approx.reshape(4, 2)
                # reverse y
                points[:, 1] = img.shape[0] - points[:, 1]
                # 计算四边形的中心点
                center_x = sum(point[0] for point in points) / 4
                center_y = sum(point[1] for point in points) / 4

                # 将每个点向四边形的外部移动
                for i in range(len(points)):
                    direction_x = points[i][0] - center_x
                    direction_y = points[i][1] - center_y
                    length = (direction_x ** 2 + direction_y ** 2) ** 0.5
                    direction_x /= length
                    direction_y /= length
                    points[i][0] += direction_x * expand
                    points[i][1] += direction_y * expand
                return points
        return None

    def __show_image_edge(self):
        # show image edge
        if self.show_edge_points is None:
            return
        
        for i in range(len(self.show_edge_points)):
            imgui.get_window_draw_list().add_line(
                self.show_edge_points[i][0], self.show_edge_points[i][1],
                self.show_edge_points[(i + 1) % 4][0], self.show_edge_points[(i + 1) % 4][1],
                imgui.get_color_u32_rgba(255, 0, 0, 255), 2.0)
            # 显示可调节的空心圆
            imgui.get_window_draw_list().add_circle(
                self.show_edge_points[i][0], self.show_edge_points[i][1],
                5, imgui.get_color_u32_rgba(255, 0, 0, 255), 12, 2.0)
            
    def __calc_image_edge(self):
        #根据show_edge_points 计算 image_edge_points
        offsetX = imgui.get_style().window_border_size + imgui.get_style().window_padding.x
        offsetY = imgui.get_style().window_border_size + imgui.get_style().window_padding.y
        for i in range(len(self.show_edge_points)):
            # remove wnd border
            self.image_edge_points[i][0] = self.show_edge_points[i][0] - offsetX
            self.image_edge_points[i][1] = self.show_edge_points[i][1] - offsetY
            # offset
            self.image_edge_points[i][0] -= self.imageWndPos.x
            self.image_edge_points[i][1] -= self.imageWndPos.y
            # scale
            self.image_edge_points[i][0] *= self.imageWndScale.x
            self.image_edge_points[i][1] *= self.imageWndScale.y

    def __combine_to_pdf(self):
        # 所有的image list 若没生成纹理则生成纹理
        images = list(self.image_manager.get_images().items())
        textures = []
        for idx, (name, path) in enumerate(images):
            texture = texmgr.get_instance().create_get_texture(path)
            textures.append(texture)
        # 生成pdf
        pdf_path = "combine.pdf"
        pdf = FPDF()
        for idx, texture in enumerate(textures):
            pdf.add_page()
            # 通过texture 的cpu_cache_data 生成图片
            image = pygame.image.frombuffer(texture.cpu_cache_data, (texture.width, texture.height), "RGBA")
            # 保存图片到tmp目录
            # python 获取tmp目录
            tmp_dir = os.path.join(os.path.dirname(__file__), "tmp")
            if not os.path.exists(tmp_dir):
                os.mkdir(tmp_dir)
            
            # add idx
            image_tmp_path = os.path.join(tmp_dir, "tmp" + str(idx) + ".png")
            pygame.image.save(image, image_tmp_path)
            # 添加图片到pdf
            pdf.image(image_tmp_path, 0, 0, 210, 297)
        # 保存pdf
        pdf.output(pdf_path, "F")



    def __show_image(self, texId):
        # set position
        
        imgui.set_next_window_position(self.imageWndPos.x, self.imageWndPos.y)
        imgui.set_next_window_size(self.imageWndSize.x, self.imageWndSize.y)
        imgui.set_next_window_bg_alpha(0.0)

        flags = imgui.WINDOW_NO_TITLE_BAR | imgui.WINDOW_NO_BACKGROUND | imgui.WINDOW_NO_RESIZE | imgui.WINDOW_NO_MOVE | imgui.WINDOW_NO_SCROLLBAR
        imgui.begin("图片", flags=flags)
        imgui.image(texId, self.imageWndSize.x - 20, self.imageWndSize.y - 20, border_color=(1, 0, 1, 1))
        self.__show_image_edge()

        imgui.end()

    def __post_process(self, post_process: PostProcess):
        if self.texture is None:
            return
        self.texture.post_process(post_process)
        
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

        if imgui.button("透视变换"):
            if self.selected_image != -1:
                self.__perspective_transform_image()
        #imgui combox box post process
    
        textSize = imgui.calc_text_size("增强锐化").x + 24;
        imgui.set_next_item_width(textSize)
        idx = self.current_post_process.value
        with imgui.begin_combo("##后处理", self.post_process_items[idx]) as combo:
            if combo.opened:
                for i in range(len(self.post_process_items)):
                    is_selected = (idx == i)
                    if imgui.selectable(self.post_process_items[i], is_selected)[0]:
                        self.current_post_process = PostProcess(i)
                    if is_selected:
                        imgui.set_item_default_focus()
        imgui.same_line()
        if imgui.button("后处理"):
            self.__post_process(self.current_post_process)

        if imgui.button("合并为PDF"):
            self.__combine_to_pdf()


        # 显示图片列表
        images = list(self.image_manager.get_images().items())
        names = [name for name, _ in images]

        if imgui.begin_child("##Images", width=-1, height=-1):
            clicked, current = imgui.listbox(
                "##Images", self.selected_image, names)
            if clicked:
                self.selected_image = current
        imgui.end_child()
