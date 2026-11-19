# =====================================================================
# capteurs.py
# Les deux capteurs que l'on compare :
#   - Hydrophone : mesure la PRESSION en UN point.
#   - FibreDAS   : mesure la DÉFORMATION de la fibre en des milliers de points.
# =====================================================================

import numpy as np                                  # numpy pour les calculs
from scipy.ndimage import uniform_filter1d          # moyenne glissante (sert pour la gauge length)

import parametres as P                              # nos réglages
from propagation import pression_recue, cos_angle_avec_fibre  # la physique de la propagation


class Hydrophone:
    """Un hydrophone posé au fond, à la position x le long de la fibre."""

    def __init__(self, x, bruit=P.BRUIT_HYDROPHONE):
        self.x = x                                  # position de l'hydrophone (m)
        self.bruit = bruit                          # niveau de bruit (Pa, écart-type)

    def signal_propre(self, t):
        """Ce que l'hydrophone mesurerait sans aucun bruit (Pa)."""
        return pression_recue(self.x, t)[0]         # [0] : un seul point, on récupère la ligne

    def mesurer(self, t, rng):
        """Mesure réelle = signal propre + bruit aléatoire."""
        propre = self.signal_propre(t)                       # le signal sans bruit
        bruit = rng.normal(0.0, self.bruit, size=t.size)     # bruit gaussien de même taille
        return propre + bruit                                # ce que l'on enregistre vraiment


class FibreDAS:
    """Une fibre optique posée au fond, le long de l'axe x."""

    def __init__(self, longueur=P.LONGUEUR_FIBRE, pas=P.PAS_CANAUX,  # réglages par défaut pris dans parametres.py
                 gauge_length=P.GAUGE_LENGTH):
        self.pas = pas                                       # distance entre deux canaux (m)
        self.gauge_length = gauge_length                     # gauge length (m)
        self.x = np.arange(0.0, longueur, pas)               # positions de tous les canaux (m)
        # Hypothèse simple : plus la gauge length est longue, moins il y a de bruit
        # (on moyenne sur plus de fibre), le bruit varie en 1/racine(gauge length).
        self.bruit = P.BRUIT_DAS * np.sqrt(P.GAUGE_LENGTH_REF / gauge_length)  # bruit d'un canal pour cette gauge length

    def deformation_ponctuelle(self, t):
        """Déformation de la fibre en chaque point, AVANT l'effet de gauge length."""
        p = pression_recue(self.x, t)                        # pression vue par chaque point de fibre
        module = P.MASSE_VOLUMIQUE * P.VITESSE_SON**2        # "raideur" de l'eau (Pa)
        cos_theta = cos_angle_avec_fibre(self.x)             # angle entre le son et la fibre
        directivite = cos_theta**2                           # la fibre ne sent que la partie du son dans son axe
        return (p / module) * directivite[:, None]           # déformation = pression / raideur x directivité

    def signal_propre(self, t):
        """Ce que le DAS mesurerait sans bruit : déformation moyennée sur la gauge length."""
        eps = self.deformation_ponctuelle(t)                 # déformation point par point
        nb_points = max(1, int(round(self.gauge_length / self.pas)))  # nombre de canaux dans une gauge length
        return uniform_filter1d(eps, size=nb_points, axis=0, mode="nearest")  # moyenne glissante le long de la fibre

    def mesurer(self, t, rng):
        """Mesure réelle = signal propre + bruit sur chaque canal."""
        propre = self.signal_propre(t)                       # matrice canaux x temps sans bruit
        bruit = rng.normal(0.0, self.bruit, size=propre.shape)  # un bruit différent sur chaque canal
        return propre + bruit                                # ce que l'interrogateur DAS enregistre
