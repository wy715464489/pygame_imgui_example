from OpenGL.GL import *
from path_util import PathUtils as pathutil
import pygame
import numpy as np
import cv2

class Texture:
    def __init__(self):
        self.path = ""
        self.gl_tex_id = 0
        self.origin_gl_tex_id = 0
        self.width = 1
        self.height = 1
    
    def delete(self):
        if (self.origin_gl_tex_id != 0):
            if (self.origin_gl_tex_id != self.gl_tex_id):
                glDeleteTextures([self.origin_gl_tex_id])
                self.origin_gl_tex_id = 0
        if (self.gl_tex_id != 0):
            if (self.origin_gl_tex_id == self.gl_tex_id):
                self.origin_gl_tex_id = 0;
            glDeleteTextures([self.gl_tex_id])
            self.gl_tex_id = 0

    def perspective_transform(self, x, y, w, h):
        # 使用opencv的透视变换
        # 透视变换的四个点
        pts_dst = np.float32([[0, 0], [self.width, 0], [0, self.height], [self.width, self.height]])
        pts_src = np.float32([[x, y], [x + w, y], [x, y + h], [x + w, y + h]])
        # 生成透视变换矩阵
        M = cv2.getPerspectiveTransform(pts_src, pts_dst)
        # 透视变换
        img = pygame.image.load(self.path)
        img = pygame.image.tostring(img, "RGBA", 1)
        img = np.frombuffer(img, dtype=np.uint8)
        img = img.reshape((self.height, self.width, 4))
        img = cv2.warpPerspective(img, M, (self.width, self.height))
        img = img.reshape((self.height, self.width, 4))
        img = img.astype(np.uint8)
        img = pygame.image.frombuffer(img.tobytes(), (self.width, self.width), 'RGBA')
        img = pygame.image.tostring(img, "RGBA", 1)
        # 重新生成纹理
        tex_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex_id)
        # texture wrapping params
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        # texture filtering params
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.width, self.height,
                     0, GL_RGBA, GL_UNSIGNED_BYTE, img)
        glBindTexture(GL_TEXTURE_2D, 0)
        self.origin_gl_tex_id = self.gl_tex_id
        self.gl_tex_id = tex_id

    def create_texture(self, path: str):
        self.path = path
        gl_tex_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, gl_tex_id)
        # texture wrapping params
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        # texture filtering params
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        
        image = pygame.image.load(path)
        width, height = image.get_size()
        image = pygame.image.tostring(image, "RGBA", 1)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height,
                     0, GL_RGBA, GL_UNSIGNED_BYTE, image)
        #glGenerateMipmap(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, 0)
        self.gl_tex_id = gl_tex_id
        self.origin_gl_tex_id = gl_tex_id
        self.width = width
        self.height = height
        return self



# singleton
class TextureMgr:
    __instance = None
    def __init__(self):
        if TextureMgr.__instance is None:
            TextureMgr.__instance = self
            # key is path of texture, value is Texture object
            self.textures = {}
        else:
            raise Exception("You cannot create another TextureMgr class")
    
    @staticmethod
    def get_instance():
        if not TextureMgr.__instance:
            TextureMgr()
        return TextureMgr.__instance
    
    def create_get_texture(self, path):
        if path in self.textures:
            return self.textures[path]
        else:
            texture = self.create_texture(path)
            self.textures[path] = texture
            return texture

    def create_texture(self, path):
        # create Texture object
        texture = Texture()
        texture.create_texture(path)
        return texture
    
    def remove_texture(self, path):
        if path in self.textures:
            # delete texture
            self.textures[path].delete()
            self.textures.pop(path)

    def destroy(self):
        for texture in self.textures.values():
            texture.delete()
        self.textures.clear()