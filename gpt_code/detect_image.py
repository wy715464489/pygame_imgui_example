import cv2
import numpy as np

class ImageEdgeDetector:
    def __init__(self, image_path):
        self.image_path = image_path

    def load_and_detect_edges(self):
        """ 加载图片并进行边缘检测 """
        img = cv2.imread(self.image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)
        edged = cv2.Canny(gray, 75, 200)

        # 寻找轮廓
        contours, _ = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]

        # 寻找边缘的四个点
        for c in contours:
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.02 * peri, True)

            if len(approx) == 4:
                return img, approx.reshape(4, 2)
        
        return img, None

# 测试函数
# 注意：这段代码需要在本地环境中运行，因为它需要图形界面交互
# show_image_and_adjust("path_to_your_image.jpg")

