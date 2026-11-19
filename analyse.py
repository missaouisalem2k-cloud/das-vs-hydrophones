# =====================================================================
# analyse.py
# Outils pour analyser les mesures : SNR, filtre, spectrogramme.
# =====================================================================

import numpy as np                              # numpy pour les calculs
from scipy.signal import butter, sosfiltfilt, spectrogram  # outils de traitement du signal


def snr_db(signal_propre, ecart_type_bruit):
    """SNR en dB = 10 log10(puissance du signal / puissance du bruit).

    On ne garde que les instants où il y a vraiment du signal
    (sinon les longs silences feraient baisser la moyenne).
    """
    signal_propre = np.atleast_2d(signal_propre)                 # marche pour 1 capteur ou pour N canaux
    seuil = 0.01 * np.max(np.abs(signal_propre), axis=1, keepdims=True)  # 1 % du maximum de chaque canal
    utile = np.abs(signal_propre) > seuil                        # vrai là où le signal est présent
    puissance = np.sum(signal_propre**2 * utile, axis=1) / np.maximum(np.sum(utile, axis=1), 1)  # puissance moyenne du signal
    puissance_bruit = ecart_type_bruit**2                        # puissance du bruit = variance
    return 10 * np.log10(puissance / puissance_bruit + 1e-30)   # conversion en dB (+1e-30 évite log(0))


def filtre_passe_bande(x, fs, fmin=10.0, fmax=30.0, ordre=4):
    """Garde seulement les fréquences entre fmin et fmax (là où crie la baleine)."""
    sos = butter(ordre, [fmin, fmax], btype="bandpass", fs=fs, output="sos")  # on dessine le filtre
    return sosfiltfilt(sos, x, axis=-1)                          # filtrage aller-retour : pas de décalage temporel


def calcul_spectrogramme(x, fs, nfft=128, recouvrement=0.9):
    """Spectrogramme : quelles fréquences sont présentes, et à quel moment."""
    f, t, S = spectrogram(x, fs=fs, nperseg=nfft,                # f : fréquences, t : temps, S : puissance
                          noverlap=int(recouvrement * nfft))     # recouvrement entre fenêtres (90 %)
    S_db = 10 * np.log10(S + 1e-30)                              # puissance en dB, plus lisible
    return f, t, S_db                                            # on renvoie les 3 tableaux
