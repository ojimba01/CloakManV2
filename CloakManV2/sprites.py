import pygame

def transformsprites(filename):
    trans = pygame.image.load(filename)
    trans1 = pygame.transform.scale(trans, (32,32))
    return trans1