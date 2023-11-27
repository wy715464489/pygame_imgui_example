import json
import os

class ImageManager:
    def __init__(self):
        # images 为一个字典，key为图片名，value为路径
        self.images = {}
        self.cfg_json = "image_cfg.json"
        self.load_images_from_json()

    def load_images_from_json(self):
        # 从文件加载字典
        with open(self.cfg_json, 'r') as f:
            self.images = json.load(f)
        # make sure image path exists
        to_remove = []
        for name, path in self.images.items():
            if not os.path.exists(path):
                to_remove.append(name)

        for name in to_remove:
            self.images.pop(name)
        if len(to_remove) > 0:
            self.save_images_to_json()


    def add_image(self, name, image):
        self.images[name] = image
        self.save_images_to_json()

    def remvoe_image(self, name):
        self.images.pop(name)
        self.save_images_to_json()

    def save_images_to_json(self):
        # 把字典保存到文件
        with open(self.cfg_json, 'w') as f:
            json.dump(self.images, f)

    def get_image(self, name):
        return self.images[name]

    def get_images(self):
        return self.images
