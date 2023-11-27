from OpenGL.GL import *
from path_util import PathUtils as pathutil
import pygame

# singleton
class TextureMgr:
    __instance = None
    def __init__(self):
        if TextureMgr.__instance is None:
            TextureMgr.__instance = self
            # key is path of texture, value is texture id
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
        texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture)
        # texture wrapping params
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        # texture filtering params
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        
        image = pygame.image.load(path)
        image = pygame.image.tostring(image, "RGBA", 1)
        width, height = pygame.image.load(path).get_size()
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height,
                     0, GL_RGBA, GL_UNSIGNED_BYTE, image)
        #glGenerateMipmap(GL_TEXTURE_2D)
        return texture
    
    def remove_texture(self, path):
        if path in self.textures:
            glDeleteTextures(self.textures[path])
            self.textures.pop(path)

    def destroy(self):
        for texture in self.textures.values():
            glDeleteTextures(texture)
        self.textures.clear()