# =====================================================================
# 02_comparaison_snr.py
# ÉTAPE 2 : on compare DAS et hydrophone avec un critère chiffré : le SNR.
#   A) SNR tout le long de la fibre  -> effet de la DIRECTIVITÉ
#   B) SNR en fonction de la gauge length -> compromis résolution / bruit
# Lancer :  python 02_comparaison_snr.py
# =====================================================================

import os                                   # pour créer le dossier des figures
import numpy as np                          # calculs sur tableaux
import matplotlib.pyplot as plt             # graphiques

import parametres as P                      # nos réglages
from capteurs import FibreDAS               # la fibre
from propagation import pression_recue      # la pression reçue en un point
from analyse import snr_db                  # le calcul du SNR

os.makedirs("figures", exist_ok=True)       # dossier des figures

t = np.arange(0.0, P.DUREE, 1.0 / P.FREQ_ECH)   # axe du temps

# =====================================================================
# A) SNR le long de la fibre
# =====================================================================
fibre = FibreDAS()                                  # fibre avec les réglages par défaut
das_propre = fibre.signal_propre(t)                 # signal DAS sans bruit (on le connaît : c'est une simulation)
snr_das = snr_db(das_propre, fibre.bruit)           # SNR de chaque canal DAS

# Pour comparer : SNR qu'aurait un hydrophone posé à chaque position de la fibre
p_propre = pression_recue(fibre.x, t)               # pression sans bruit à chaque position
snr_hydro = snr_db(p_propre, P.BRUIT_HYDROPHONE)    # SNR d'un hydrophone à chaque position

# Aux deux bouts de la fibre, la moyenne "gauge length" est incomplète : on les met de côté
loin_des_bords = (fibre.x > 200) & (fibre.x < fibre.x[-1] - 200)  # vrai à plus de 200 m des extrémités
x_km = fibre.x[loin_des_bords] / 1000                # positions gardées, en km

plt.figure(figsize=(10, 5))                                         # nouvelle figure
plt.plot(x_km, snr_hydro[loin_des_bords], label="Hydrophone (si placé à cette position)")  # courbe hydrophone
plt.plot(x_km, snr_das[loin_des_bords], label=f"DAS (gauge length = {fibre.gauge_length:.0f} m)")  # courbe DAS
plt.axvline(P.SOURCE_X / 1000, color="gray", linestyle="--", label="En face de la baleine")  # repère de la source
plt.xlabel("Position le long de la fibre (km)")                     # axe horizontal
plt.ylabel("SNR (dB)")                                              # axe vertical
plt.title("SNR le long de la fibre : le DAS est 'sourd' en face de la source")  # titre
plt.ylim(bottom=max(-40, np.min(snr_das)))                          # on évite les valeurs -infini
plt.legend()                                                        # légende
plt.grid(alpha=0.3)                                                 # grille légère
plt.tight_layout()                                                  # mise en page
plt.savefig("figures/04_snr_le_long_de_la_fibre.png", dpi=150)      # on enregistre

i_face = np.argmin(np.abs(fibre.x - P.SOURCE_X))    # canal juste en face de la baleine
i_meilleur = np.argmax(np.where(loin_des_bords, snr_das, -np.inf))  # canal DAS avec le meilleur SNR
print("--- A) Directivité ---")  # titre de la partie A
print(f"SNR hydrophone en face de la baleine : {snr_hydro[i_face]:.1f} dB")  # SNR de l'hydrophone au plus près de la baleine
print(f"SNR DAS en face de la baleine        : {snr_das[i_face]:.1f} dB")  # SNR du DAS au même endroit : très faible
print(f"Meilleur SNR DAS : {snr_das[i_meilleur]:.1f} dB à x = {fibre.x[i_meilleur] / 1000:.2f} km")  # meilleur canal DAS

# =====================================================================
# B) Effet de la gauge length
# =====================================================================
liste_gl = list(range(10, 201, 5))                 # gauge lengths testées : 10, 15, 20... 200 m
x_test = 4500.0                                     # on regarde toujours le même endroit : x = 4,5 km
snr_max = []                                        # on va ranger le SNR pour chaque gauge length
for gl in liste_gl:                                 # pour chaque gauge length...
    f_gl = FibreDAS(gauge_length=gl)                # ...on crée une fibre avec ce réglage
    propre = f_gl.signal_propre(t)                  # signal sans bruit
    i_test = np.argmin(np.abs(f_gl.x - x_test))     # canal le plus proche de x = 4,5 km
    snr_max.append(snr_db(propre[i_test], f_gl.bruit)[0])  # SNR de ce canal
    print(f"Gauge length {gl:4d} m -> SNR DAS à 4,5 km = {snr_max[-1]:.1f} dB")  # affichage du résultat

longueur_onde = P.VITESSE_SON / 20.0                # longueur d'onde à 20 Hz (m) = 75 m

plt.figure(figsize=(8, 5))                                          # nouvelle figure
plt.plot(liste_gl, snr_max, "o-")                                   # SNR en fonction de la gauge length
plt.axvline(longueur_onde, color="gray", linestyle="--",            # repère : longueur d'onde du cri
            label=f"Longueur d'onde à 20 Hz ≈ {longueur_onde:.0f} m")  # texte de la légende
plt.xlabel("Gauge length (m)")                                      # axe horizontal
plt.ylabel("SNR du canal DAS à 4,5 km (dB)")                       # axe vertical
plt.title("Gauge length : moins de bruit, mais le signal est 'moyenné'")  # titre
plt.legend()                                                        # légende
plt.grid(alpha=0.3)                                                 # grille
plt.tight_layout()                                                  # mise en page
plt.savefig("figures/05_effet_gauge_length.png", dpi=150)           # on enregistre

print("Figures enregistrées dans le dossier 'figures'.")            # message de fin
plt.show()                                                          # affichage
