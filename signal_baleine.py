# =====================================================================
# signal_baleine.py
# Fabrique le cri d'une baleine (un "chirp" descendant de 25 Hz à 15 Hz).
# =====================================================================

import numpy as np                      # numpy : calcul sur des tableaux de nombres
from scipy.signal import chirp          # chirp : fonction qui fabrique un signal dont la fréquence varie

import parametres as P                  # on récupère nos réglages sous le nom court "P"


def cri_baleine(t):
    """Renvoie le cri de la baleine aux instants t (t en secondes, t = 0 au début du cri)."""
    t = np.asarray(t, dtype=float)                          # on s'assure que t est un tableau numpy
    signal = chirp(t, f0=P.FREQ_DEBUT_CRI, t1=P.DUREE_CRI,  # chirp qui part de 25 Hz...
                   f1=P.FREQ_FIN_CRI, method="linear")      # ...et arrive à 15 Hz à t = 1 s
    fenetre = 0.5 - 0.5 * np.cos(2 * np.pi * t / P.DUREE_CRI)  # fenêtre de Hann : le cri monte puis s'éteint doucement
    signal = signal * fenetre                               # on applique la fenêtre au chirp
    pendant_le_cri = (t >= 0) & (t <= P.DUREE_CRI)          # vrai seulement pendant la durée du cri
    signal = np.where(pendant_le_cri, signal, 0.0)          # en dehors du cri, le signal vaut zéro
    return signal                                           # on renvoie le cri (amplitude max = 1)
