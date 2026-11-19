# =====================================================================
# propagation.py
# Comment le son voyage de la baleine jusqu'au capteur.
# Modèle simple : eau homogène, son en ligne droite, onde sphérique.
# (Limites : pas de réflexion sur le fond ni sur la surface, pas d'absorption.)
# =====================================================================

import numpy as np                      # numpy pour les calculs

import parametres as P                  # nos réglages
from signal_baleine import cri_baleine  # le cri de la baleine


def distance_source(x, y=0.0, z=0.0):
    """Distance (m) entre la baleine et un point (x, y, z)."""
    dx = x - P.SOURCE_X                 # écart le long de la fibre
    dy = y - P.SOURCE_Y                 # écart sur le côté
    dz = z - P.SOURCE_Z                 # écart en hauteur
    return np.sqrt(dx**2 + dy**2 + dz**2)  # Pythagore en 3D


def pression_recue(x, t, y=0.0, z=0.0):
    """Pression (Pa) reçue au point (x, y, z) aux instants t.

    Si x est un tableau de N points, on renvoie un tableau N x len(t).
    """
    x = np.atleast_1d(x)                        # on accepte un seul point ou plusieurs points
    r = distance_source(x, y, z)                # distance baleine -> chaque point
    retard = r / P.VITESSE_SON                  # temps de trajet du son (s)
    amplitude = P.AMPLITUDE_SOURCE / r          # l'onde s'affaiblit en 1/r (onde sphérique)
    t_local = t[None, :] - P.INSTANT_CRI - retard[:, None]  # "horloge" du cri vue par chaque point
    p = amplitude[:, None] * cri_baleine(t_local)           # pression = amplitude x cri retardé
    return p                                    # tableau (nombre de points) x (nombre d'instants)


def cos_angle_avec_fibre(x, y=0.0, z=0.0):
    """Cosinus de l'angle entre la direction du son et l'axe de la fibre (axe x)."""
    r = distance_source(x, y, z)        # distance baleine -> point
    return (x - P.SOURCE_X) / r         # composante le long de x divisée par la distance totale
