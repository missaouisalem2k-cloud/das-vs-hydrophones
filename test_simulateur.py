# =====================================================================
# test_simulateur.py
# VALIDATION : on vérifie le simulateur sur des cas où l'on connaît
#              la bonne réponse à l'avance.
# Lancer :  python -m pytest test_simulateur.py -v
# =====================================================================

import numpy as np                              # calculs

import parametres as P                          # nos réglages
from propagation import distance_source, pression_recue, cos_angle_avec_fibre  # la physique
from capteurs import FibreDAS                   # la fibre


def test_retard_egal_distance_sur_vitesse():
    """Le cri doit arriver après un temps = distance / vitesse du son."""
    t = np.arange(0.0, P.DUREE, 1.0 / P.FREQ_ECH)            # axe du temps
    x = 4500.0                                               # un point de la fibre
    p = pression_recue(x, t)[0]                              # pression reçue en ce point
    debut_mesure = t[np.argmax(np.abs(p) > 0)]               # premier instant où le signal n'est plus nul
    debut_attendu = P.INSTANT_CRI + distance_source(x) / P.VITESSE_SON  # instant théorique
    assert abs(debut_mesure - debut_attendu) <= 1.0 / P.FREQ_ECH        # à un échantillon près


def test_amplitude_en_un_sur_r():
    """Deux fois plus loin -> deux fois moins de pression (onde sphérique)."""
    r1 = distance_source(P.SOURCE_X + 1000.0)                # distance d'un premier point
    r2 = distance_source(P.SOURCE_X + 5000.0)                # distance d'un second point
    rapport_attendu = r1 / r2                                # rapport théorique des amplitudes
    t = np.arange(0.0, 20.0, 1.0 / 2000.0)                   # temps très fin pour bien voir le maximum
    p1 = np.max(np.abs(pression_recue(P.SOURCE_X + 1000.0, t)))  # amplitude max au point 1
    p2 = np.max(np.abs(pression_recue(P.SOURCE_X + 5000.0, t)))  # amplitude max au point 2
    assert np.isclose(p2 / p1, rapport_attendu, rtol=1e-2)   # égal à 1 % près


def test_fibre_sourde_en_face_de_la_source():
    """En face de la baleine, le son arrive perpendiculairement à la fibre : cos = 0."""
    assert np.isclose(cos_angle_avec_fibre(P.SOURCE_X), 0.0)  # directivité nulle à la perpendiculaire


def test_bruit_diminue_avec_gauge_length():
    """Hypothèse du modèle : une gauge length 4 fois plus longue divise le bruit par 2."""
    f1 = FibreDAS(gauge_length=25.0)                         # fibre avec gauge length 25 m
    f2 = FibreDAS(gauge_length=100.0)                        # fibre avec gauge length 100 m
    assert np.isclose(f1.bruit / f2.bruit, 2.0)              # racine(100/25) = 2
