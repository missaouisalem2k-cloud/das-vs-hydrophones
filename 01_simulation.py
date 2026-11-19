# =====================================================================
# 01_simulation.py
# ÉTAPE 1 : on simule une baleine qui crie, et ce que "voient"
#           un hydrophone et une fibre DAS posés sur le fond.
# Lancer :  python 01_simulation.py
# Résultat : 3 figures dans le dossier "figures"
# =====================================================================

import os                                   # pour créer le dossier des figures
import numpy as np                          # calculs sur tableaux
import matplotlib.pyplot as plt             # dessiner des graphiques

import parametres as P                      # nos réglages
from capteurs import Hydrophone, FibreDAS   # nos deux capteurs
from analyse import filtre_passe_bande, calcul_spectrogramme  # nos outils d'analyse

os.makedirs("figures", exist_ok=True)       # on crée le dossier "figures" s'il n'existe pas

# ---------- 1) L'axe du temps ----------
t = np.arange(0.0, P.DUREE, 1.0 / P.FREQ_ECH)   # instants de 0 à 15 s, un tous les 1/200 s
rng = np.random.default_rng(P.GRAINE)           # générateur de hasard (pour le bruit)

# ---------- 2) Les capteurs ----------
fibre = FibreDAS()                              # une fibre de 6 km, un canal tous les 2 m
x_hydro = 4500.0                                # on pose un hydrophone à 4,5 km le long de la fibre
hydro = Hydrophone(x=x_hydro)                   # l'hydrophone, au même endroit qu'un canal DAS

print("Nombre de canaux DAS :", fibre.x.size)   # affiche combien de "capteurs virtuels" a la fibre
print("Nombre d'échantillons :", t.size)        # affiche combien d'instants on simule

# ---------- 3) Les mesures (signal + bruit) ----------
mesure_das = fibre.mesurer(t, rng)              # matrice : canaux x temps (déformation)
mesure_hydro = hydro.mesurer(t, rng)            # vecteur : temps (pression en Pa)

# ---------- 4) Filtrage dans la bande du cri (10 - 30 Hz) ----------
das_filtre = filtre_passe_bande(mesure_das, P.FREQ_ECH)      # on enlève le bruit hors bande sur chaque canal
hydro_filtre = filtre_passe_bande(mesure_hydro, P.FREQ_ECH)  # même chose pour l'hydrophone

# ---------- 5) Figure 1 : vue espace-temps (t-x) de la fibre ----------
plt.figure(figsize=(10, 6))                                 # nouvelle figure
plt.imshow(np.abs(das_filtre) * 1e9, aspect="auto",         # valeur absolue de la déformation, en nano-déformation
           origin="lower", cmap="magma",                    # couleurs : sombre = rien, clair = signal
           extent=[t[0], t[-1], fibre.x[0] / 1000, fibre.x[-1] / 1000],  # axes en secondes et en km
           vmax=np.percentile(np.abs(das_filtre) * 1e9, 99.9))           # on coupe les valeurs extrêmes pour bien voir
plt.colorbar(label="|déformation| (x 1e-9)")                # légende des couleurs
plt.xlabel("Temps (s)")                                     # titre de l'axe horizontal
plt.ylabel("Position le long de la fibre (km)")             # titre de l'axe vertical
plt.title("DAS simulé : le cri arrive en forme d'hyperbole")  # titre du graphique
plt.tight_layout()                                          # évite que les textes se chevauchent
plt.savefig("figures/01_vue_tx_das.png", dpi=150)           # on enregistre l'image

# ---------- 6) Figure 2 : hydrophone vs canal DAS au même endroit ----------
i_canal = np.argmin(np.abs(fibre.x - x_hydro))              # indice du canal DAS le plus proche de l'hydrophone
fig, axes = plt.subplots(2, 1, figsize=(10, 6), sharex=True)  # 2 graphiques l'un sous l'autre
axes[0].plot(t, hydro_filtre, color="tab:blue")             # signal de l'hydrophone
axes[0].set_ylabel("Pression (Pa)")                         # unité de l'hydrophone
axes[0].set_title(f"Hydrophone à x = {x_hydro / 1000:.1f} km")  # titre du 1er graphique
axes[1].plot(t, das_filtre[i_canal] * 1e9, color="tab:orange")  # signal du canal DAS
axes[1].set_ylabel("Déformation (x 1e-9)")                  # unité du DAS
axes[1].set_title(f"Canal DAS à x = {fibre.x[i_canal] / 1000:.1f} km")  # titre du 2e graphique
axes[1].set_xlabel("Temps (s)")                             # axe du temps
plt.tight_layout()                                          # mise en page propre
plt.savefig("figures/02_hydrophone_vs_das.png", dpi=150)    # on enregistre l'image

# ---------- 7) Figure 3 : spectrogrammes ----------
f_h, t_h, S_h = calcul_spectrogramme(mesure_hydro, P.FREQ_ECH)          # spectrogramme hydrophone
f_d, t_d, S_d = calcul_spectrogramme(mesure_das[i_canal], P.FREQ_ECH)   # spectrogramme du canal DAS
fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))           # 2 graphiques côte à côte
axes[0].pcolormesh(t_h, f_h, S_h, shading="auto", vmin=S_h.max() - 40)  # on affiche 40 dB de dynamique
axes[0].set_title("Spectrogramme hydrophone")               # titre
axes[1].pcolormesh(t_d, f_d, S_d, shading="auto", vmin=S_d.max() - 40)  # même chose pour le DAS
axes[1].set_title("Spectrogramme canal DAS")                # titre
for ax in axes:                                             # pour les deux graphiques...
    ax.set_ylim(0, 50)                                      # ...on regarde seulement 0 - 50 Hz
    ax.set_xlabel("Temps (s)")                              # axe du temps
    ax.set_ylabel("Fréquence (Hz)")                         # axe des fréquences
plt.tight_layout()                                          # mise en page propre
plt.savefig("figures/03_spectrogrammes.png", dpi=150)       # on enregistre l'image

print("Figures enregistrées dans le dossier 'figures'.")    # message de fin
plt.show()                                                  # affiche les figures à l'écran
