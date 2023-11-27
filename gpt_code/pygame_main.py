import pygame
import detect_image
import cv2
import numpy as np


class ImageDisplayer:
    def __init__(self, img, screenSize=None):
        self.img = img
        self.screenSize = screenSize

    def show_image(self):
        """ 使用 pygame 展示图片 """
        pygame.init()

        # 将OpenCV图像格式转换为pygame
        img = cv2.cvtColor(self.img, cv2.COLOR_BGR2RGB)
        pygame_img = pygame.surfarray.make_surface(img)

        # 计算新的尺寸
        new_size = (int(self.screenSize[0] * 0.6), int(self.screenSize[1] * 0.6))
        pygame_img = pygame.transform.scale(pygame_img, new_size)

        # 创建窗口并设置窗口大小
        screen = pygame.display.set_mode(self.screenSize)
        pygame.display.set_caption("Image Display")

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # 计算图片应该被放置的位置
            position = (int(self.screenSize[0] * 0.2), int(self.screenSize[1] * 0.2))
            screen.blit(pygame_img, position)
            pygame.display.flip()

        pygame.quit()

if __name__ == "__main__":
    # 这里需要先加载图片，然后传入ImageDisplayer
    img = cv2.imread("test.jpg")
    displayer = ImageDisplayer(img, (1280,720))
    displayer.show_image()