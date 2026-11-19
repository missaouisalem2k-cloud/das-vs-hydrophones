# =====================================================================
# 03_donnees_reelles.py
# ÉTAPE 3 : on ouvre de VRAIES données DAS (câble OOI, côte de l'Oregon)
#           avec la bibliothèque das4whales, comme dans le tutoriel.
# Objectif : voir de vrais cris et MESURER le vrai bruit du DAS
#            pour remplacer l'hypothèse BRUIT_DAS de parametres.py.
#
# ATTENTION : le fichier fait environ 850 Mo (téléchargé une seule fois
#             dans le dossier "data"). Il faut une bonne connexion.
# Installer avant :  pip install das4whales
# Lancer :           python 03_donnees_reelles.py
# =====================================================================

import numpy as np                          # calculs
import scipy.signal as sp                   # traitement du signal (filtrage, Hilbert)
import matplotlib.pyplot as plt             # graphiques
import das4whales as dw                     # la bibliothèque de Léa Bouffaut pour le DAS

# ---------- 1) Télécharger le fichier (une seule fois) ----------
url = ("http://piweb.ooirsn.uw.edu/das/data/Optasense/NorthCable/TransmitFiber/"   # adresse du serveur OOI
       "North-C1-LR-P1kHz-GL50m-Sp2m-FS200Hz_2021-11-03T15_06_51-0700/"            # dossier de l'expérience
       "North-C1-LR-P1kHz-GL50m-Sp2m-FS200Hz_2021-11-04T020002Z.h5")               # le fichier : 60 s de données
chemin, nom = dw.data_handle.dl_file(url)   # télécharge dans "data/" (ou réutilise le fichier déjà présent)

# ---------- 2) Lire les paramètres d'acquisition (sans charger les données) ----------
meta = dw.data_handle.get_acquisition_parameters(chemin, interrogator="optasense")  # lit l'en-tête du HDF5
fs = meta["fs"]                             # fréquence d'échantillonnage (Hz)
dx = meta["dx"]                             # distance entre canaux (m)
print(f"Fréquence d'échantillonnage : {fs} Hz")  # on affiche les réglages de l'acquisition
print(f"Pas entre canaux            : {dx} m")  # distance entre deux capteurs virtuels
print(f"Gauge length                : {meta['GL']} m")  # longueur de moyennage de la fibre
print(f"Nombre de canaux            : {meta['nx']}")  # combien de capteurs virtuels au total
print(f"Durée du fichier            : {meta['ns'] / fs} s")  # durée = nombre d'échantillons / fs

# ---------- 3) Choisir les canaux : de 20 km à 65 km, un canal tous les 10 m ----------
canaux_m = [20000, 65000, 10]                         # [début, fin, pas] en mètres
canaux = [int(v // dx) for v in canaux_m]             # conversion en numéros de canaux

# ---------- 4) Charger les données en déformation (strain) ----------
tr, temps, dist, debut_utc = dw.data_handle.load_das_data(chemin, canaux, meta)  # matrice canaux x temps
print("Taille des données chargées :", tr.shape)  # (nombre de canaux, nombre d'instants)

# ---------- 5) Filtrer dans la bande des rorquals communs (10 - 30 Hz) ----------
sos = dw.dsp.butterworth_filter([5, [10, 30], "bp"], fs)   # filtre passe-bande d'ordre 5
trf = sp.sosfiltfilt(sos, tr, axis=1)                      # filtrage aller-retour sur chaque canal

# ---------- 6) Vue espace-temps (t-x) : on cherche les hyperboles des cris ----------
dw.plot.plot_tx(sp.hilbert(trf, axis=1), temps, dist, debut_utc,  # enveloppe du signal (Hilbert)
                fig_size=(12, 10), v_min=0, v_max=0.4)            # même échelle que le tutoriel

# ---------- 7) Spectrogramme d'un canal (à 28 km) ----------
i = np.argmin(np.abs(dist - 28000))                        # canal le plus proche de 28 km
p, tt, ff = dw.dsp.get_spectrogram(trf[i, :], fs, nfft=256, overlap_pct=0.95)  # spectrogramme
dw.plot.plot_spectrogram(p, tt, ff, f_min=0, f_max=50, v_min=-50)             # affichage

# ---------- 8) Mesurer le VRAI bruit du DAS ----------
# On utilise la "médiane des écarts absolus" (MAD) : c'est un écart-type
# robuste, peu sensible aux cris de baleine qui passent de temps en temps.
mad = np.median(np.abs(trf - np.median(trf, axis=1, keepdims=True)), axis=1)  # MAD de chaque canal
bruit_canal = 1.4826 * mad                                 # conversion MAD -> écart-type (bruit gaussien)
bruit_typique = np.median(bruit_canal)                     # valeur typique sur tout le câble
print(f"Bruit DAS mesuré dans 10-30 Hz : {bruit_typique:.2e} (déformation)")  # bruit réel dans la bande du cri

# Notre simulateur ajoute un bruit sur toute la bande 0 - 100 Hz.
# Dans 10-30 Hz il n'en reste que 20/100 de la puissance -> écart-type x racine(0,2).
# Pour comparer, on remonte donc à la bande complète :
bruit_bande_complete = bruit_typique / np.sqrt(20.0 / (fs / 2))  # bruit équivalent sur toute la bande
print(f"=> Valeur à mettre dans parametres.py (BRUIT_DAS) : {bruit_bande_complete:.2e}")  # valeur à recopier dans parametres.py

plt.figure(figsize=(10, 4))                                # nouvelle figure
plt.plot(dist / 1000, bruit_canal)                         # bruit le long du câble
plt.xlabel("Distance le long du câble (km)")               # axe horizontal
plt.ylabel("Bruit (écart-type, 10-30 Hz)")                 # axe vertical
plt.title("Bruit réel du DAS le long du câble OOI")        # titre
plt.grid(alpha=0.3)                                        # grille
plt.tight_layout()                                         # mise en page
plt.savefig("figures/06_bruit_reel_das.png", dpi=150)      # on enregistre
plt.show()                                                 # affichage
