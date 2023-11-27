import json


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
