import pygame
from pygame.locals import *
import engine3d
import numpy as np
import time
import math


# - initialisation de la lib. pygame
pygame.init()
surf = pygame.display.set_mode((800,600))
couleur_bg = pygame.color.Color('pink')
# limiter les FPS évite d'utiliser trop du temps CPU inutilement
# à cette fin, on utilise les 2 variables ci-dessous
horloge_jeu = pygame.time.Clock()
MAX_FPS = 45  # mettre ce nom de variable en majuscules est simplement une convention pour dire...
# que MAX_FPS ne devrait pas changer au cours du programme

# - initialisation de la variable qui permettra de mesurer le temps
t_actuel = time.time()

# - variables et fonctions utiles pour dessin 3d
cam = engine3d.Camera((0.0, 0.0, 12.0), math.pi/2, 0)
sol = None  # servira à stocker un modèle 3d pour le sol
meshes = list()  # servira à stocker des modèles 3d posés sur le sol


def creation_cube():
    cubeedges = np.array([[0, 1], [1, 2], [2, 3], [3, 0], [4, 5], [5, 6], [6, 7], [7, 4], [0, 4], [1, 5], [2, 6], [3, 7]])
    cubefaces = (0, 1, 2, 3), (4, 5, 6, 7), (0, 1, 5, 4), (2, 3, 7, 6), (0, 3, 7, 4), (1, 2, 6, 5)
    cubecolors = (100, 100, 100), (110, 110, 110), (120, 120, 120), (130, 130, 130), (140, 140, 140), (150, 150, 150)
    res = engine3d.Mesh("gros_cube", 8, cubeedges, cubefaces, cubecolors, 2)
    res.vertices[0] = engine3d.Vector4(-1.0, -1.0, 0, 1)
    res.vertices[1] = engine3d.Vector4(1.0, -1.0, 0, 1)
    res.vertices[2] = engine3d.Vector4(1.0, 1.0, 0, 1)
    res.vertices[3] = engine3d.Vector4(-1.0, 1.0, 0, 1)
    res.vertices[4] = engine3d.Vector4(-1.0, -1.0, 10.0, 1)
    res.vertices[5] = engine3d.Vector4(1.0, -1.0, 10.0, 1)
    res.vertices[6] = engine3d.Vector4(1.0, 1.0, 10.0, 1)
    res.vertices[7] = engine3d.Vector4(-1.0, 1.0, 10.0, 1)
    return res


# - programme principal
sol = creation_cube()
transl_v = [0.0, 0.0, 0.0]

keyp = None  # pour enregistrer touche pressée
game_over = False
tracking_mouse = False
init_mp = None

# -- la boucle de jeu (game loop)
while not game_over:
    # --- etape un : gestion evènements / inputs
    li_ev = pygame.event.get()
    for ev in li_ev:
        if ev.type == QUIT:
            game_over = True
            break  # sortie forcée de la boucle for, inutile de traiter d'autres évènements
        if ev.type == MOUSEBUTTONDOWN:
            tracking_mouse = True
        elif ev.type == MOUSEBUTTONUP:
            tracking_mouse = False
    keyp = pygame.key.get_pressed()

    # --- etape deux : maj logique de jeu
    transl_v[0] = transl_v[1] = transl_v[2] = 0.0
    inc_rota_axe1 = 0
    if keyp[K_w]:
        transl_v[2] = -1.0
    elif keyp[K_s]:
        transl_v[2] = 1.0
    elif keyp[K_a]:
        transl_v[1] = -1.0
    elif keyp[K_d]:
        transl_v[1] = 1
    elif keyp[K_q]:
        inc_rota_axe1 = 0.01
    elif keyp[K_e]:
        inc_rota_axe1 = -0.01
    cam.addToPosition(transl_v)
    cam.addToAngleHorz(inc_rota_axe1)
    if tracking_mouse:
        bt = pygame.mouse.get_pressed()
        if bt[0]:
            cam.addToAngleVert(0.01)
        elif bt[2]:
            cam.addToAngleVert(-0.01)
    
    delta_t = time.time() - t_actuel
    #cam.update(delta_t)
    
    # --- etape trois : maj affichage
    surf.fill(couleur_bg)
    engine3d.render_all_meshes([sol], cam, surf)
    pygame.display.update()
    horloge_jeu.tick(MAX_FPS)  # provoque une micro-pause après dessin de l'écran, si MAX_FPS était dépassé


pygame.quit()
