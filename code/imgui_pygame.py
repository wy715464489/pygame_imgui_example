import pygame
import imgui
from imgui.integrations.pygame import PygameRenderer
import OpenGL.GL as gl
# 引入 client.py
from client import Client
window_size = (800, 600)
title = "imgui and pygame Example"
# 定义main函数


def main():
    # 创建一个Client对象
    client = Client(window_size, title)
    # 调用run方法
    client.run()


if __name__ == "__main__":
    main()
