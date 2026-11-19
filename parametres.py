# =====================================================================
# parametres.py
# Ici on range TOUS les réglages du projet au même endroit.
# Si on veut changer une valeur, on la change ici et pas ailleurs.
# =====================================================================

# ---------- Le milieu : l'eau de mer ----------
VITESSE_SON = 1500.0          # vitesse du son dans l'eau (m/s), valeur classique
MASSE_VOLUMIQUE = 1025.0      # masse volumique de l'eau de mer (kg/m³)

# ---------- L'échantillonnage dans le temps ----------
FREQ_ECH = 200.0              # fréquence d'échantillonnage (Hz), comme les données OOI du tutoriel
DUREE = 15.0                  # durée simulée (s)

# ---------- La source : un cri de rorqual commun (fin whale) ----------
FREQ_DEBUT_CRI = 25.0         # le cri commence vers 25 Hz...
FREQ_FIN_CRI = 15.0           # ...et descend vers 15 Hz (cri "descendant")
DUREE_CRI = 1.0               # le cri dure environ 1 seconde
INSTANT_CRI = 1.0             # la baleine crie 1 s après le début de l'enregistrement
AMPLITUDE_SOURCE = 2800.0     # pression à 1 m de la baleine (Pa) ≈ 189 dB re 1 µPa (ordre de grandeur)

# Position de la baleine (en mètres)
# x : le long de la fibre, y : sur le côté, z : hauteur au-dessus du fond
SOURCE_X = 3000.0             # la baleine est en face du milieu de la fibre
SOURCE_Y = 1000.0             # à 1 km sur le côté de la fibre
SOURCE_Z = 1000.0             # à 1 km au-dessus du fond (la fibre est posée sur le fond, z = 0)

# ---------- La fibre optique (le DAS) ----------
LONGUEUR_FIBRE = 6000.0       # longueur de fibre simulée (m)
PAS_CANAUX = 2.0              # distance entre deux "capteurs virtuels" (m), comme OOI (~2 m)
GAUGE_LENGTH = 50.0           # gauge length (m) : longueur sur laquelle la fibre moyenne la déformation

# ---------- Les bruits (HYPOTHÈSES à ajuster avec les vraies données) ----------
BRUIT_HYDROPHONE = 0.05       # bruit de l'hydrophone (Pa, écart-type), bruit ambiant de l'océan
BRUIT_DAS = 5e-11             # bruit d'un canal DAS (déformation sans unité, écart-type) pour GAUGE_LENGTH
GAUGE_LENGTH_REF = 50.0       # gauge length pour laquelle BRUIT_DAS est donné

# ---------- Reproductibilité ----------
GRAINE = 0                    # graine du hasard : même bruit à chaque exécution
