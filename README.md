# Projet DAS vs hydrophones

**Objectif du projet :** utiliser une fibre optique posée sur le fond marin comme un réseau de milliers de capteurs acoustiques (DAS, *Distributed Acoustic Sensing*). On cherche ses points forts et ses limites par rapport aux hydrophones classiques.

Références :
- l'article de Léa Bouffaut (NTNU) : https://ntnuopen.ntnu.no/ntnu-xmlui/handle/11250/3044872
- le tutoriel das4whales : https://das4whales.readthedocs.io/en/latest/src/tutorial.html

---

## 1. Installer (une seule fois)

Ouvrir un terminal Anaconda (ou le terminal de VS Code) dans ce dossier, puis :

```
pip install -r requirements.txt
```

## 2. Lancer, dans l'ordre

| Commande | Ce que ça fait | Figures produites |
|---|---|---|
| `python 01_simulation.py` | Simule une baleine qui crie, puis ce que mesurent un hydrophone et une fibre DAS | `01_vue_tx_das.png`, `02_hydrophone_vs_das.png`, `03_spectrogrammes.png` |
| `python 02_comparaison_snr.py` | Compare les SNR : effet de la directivité et de la gauge length | `04_snr_le_long_de_la_fibre.png`, `05_effet_gauge_length.png` |
| `python -m pytest test_simulateur.py -v` | Vérifie le simulateur sur des cas dont on connaît la réponse | – |
| `python 03_donnees_reelles.py` | Ouvre de vraies données DAS (OOI, ~850 Mo) et mesure le vrai bruit | `06_bruit_reel_das.png` |

## 3. Organisation du code

| Fichier | Rôle |
|---|---|
| `parametres.py` | Tous les réglages : eau, baleine, fibre, bruits |
| `signal_baleine.py` | Le cri du rorqual commun : un chirp de 25 Hz à 15 Hz pendant 1 s |
| `propagation.py` | Le trajet du son : retard r/c, atténuation en 1/r, angle avec la fibre |
| `capteurs.py` | Deux classes : `Hydrophone` (mesure la pression) et `FibreDAS` (mesure la déformation) |
| `analyse.py` | SNR, filtre passe-bande, spectrogramme |

## 4. Le modèle physique (simple, à dire à l'oral)

1. **Propagation :** le son part de la baleine et voyage en ligne droite à 1500 m/s. Son amplitude baisse en 1/r (onde sphérique).
2. **Hydrophone :** il mesure directement la pression p, quelle que soit la direction d'arrivée du son (capteur omnidirectionnel).
3. **Fibre DAS :** elle mesure une déformation le long de son axe, approchée par ε ≈ p / (ρc²) × cos²θ, où θ est l'angle entre la direction du son et la fibre.
   - Quand le son arrive perpendiculairement à la fibre (θ = 90°), la fibre ne mesure presque rien : c'est la **directivité**.
4. **Gauge length :** la fibre moyenne la déformation sur une longueur GL (50 m par défaut). Moyenner sur plus de fibre réduit le bruit, mais si GL approche la longueur d'onde vue le long de la fibre, le signal s'annule.
5. **Bruits :** ce sont des **hypothèses**. Le script 03 sert à mesurer le vrai bruit du DAS pour les remplacer.

**Limites actuelles du modèle :** pas de réflexion sur le fond ni sur la surface, pas d'absorption, vitesse du son constante, fibre droite.

## 5. Premiers résultats (simulation)

- **Directivité :** en face de la baleine, l'hydrophone a un SNR d'environ 25 dB, tandis que le DAS tombe à environ −60 dB : il est « sourd » à la perpendiculaire.
- **Ordres de grandeur :** loin de cette zone, le DAS remonte à environ 5 dB avec les bruits choisis. Sa force reste le **nombre de capteurs** : des milliers de canaux, sur des kilomètres.
- **Gauge length :** le SNR passe par un maximum vers 30–50 m, puis chute quand la gauge length approche la longueur d'onde apparente le long de la fibre (environ 100 m ici). Il faut donc faire un compromis entre bruit et résolution.
- **Validation :** les 4 tests passent. Le retard vaut bien r/c, l'amplitude décroît bien en 1/r, et la directivité est bien nulle à 90°.

> ⚠️ Les SNR absolus dépendent des bruits supposés. Les **tendances** sont fiables, les valeurs exactes seront corrigées avec le bruit réel (étape 03).

## 6. Avancement (≈ 40 %)

- [x] Simulateur : source, propagation, hydrophone, fibre DAS (directivité et gauge length), bruit
- [x] Analyse : filtrage, vue t-x, spectrogrammes, SNR
- [x] Comparaison chiffrée : SNR le long de la fibre, effet de la gauge length
- [x] Validation du simulateur (tests pytest)
- [x] Script de lecture des vraies données (das4whales), à lancer sur le PC
- [ ] Lancer `03_donnees_reelles.py` et recaler `BRUIT_DAS` dans `parametres.py`
- [ ] **Localisation** : retrouver la position de la baleine à partir des temps d'arrivée (hyperbole), puis comparer l'erreur de localisation entre le DAS et un petit réseau d'hydrophones
- [ ] Ajouter la réflexion sur la surface et sur le fond (sources images)
- [ ] Étudier l'influence de la distance et de la position de la baleine (plusieurs scénarios)
- [ ] Rapport final : points forts et limites du DAS
