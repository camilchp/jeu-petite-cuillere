from pathlib import Path
import matplotlib.pyplot as plt
import re
import numpy as np
from datetime import date

jeu = Path("jeu_2022_2023")
joueurs = jeu / "joueurs.csv"
historique = jeu / "historique.txt"

with joueurs.open("r") as f:
    CSV = f.readlines()
    N = len(CSV)


class Joueur():  # csv est la liste des joueurs, i est l'indice du joueur dans cette liste

    def __init__(self, i):
        self.indice = i
        ligne = CSV[i].split(',')

        self.nom = ligne[0].strip().capitalize()
        self.prenom = ligne[1].strip().capitalize()
        self.classe = ligne[2]
        self.mail = ligne[3].strip()
        self.est_mort = ligne[-1].strip() == "mort"

    def meurt(self):
        CSV[self.indice] = CSV[self.indice].strip() + ",     mort\n"
        self.est_mort = True

    def cible(self):
        suivant = JOUEURS[(self.indice + 1) % N]
        if not suivant.est_mort:
            return suivant
        else:
            return suivant.cible()  # Un overflow ici doit signifier qu'il n'y a plus qu'un joueur en vie

    def tue(self):
        victime = self.cible()
        victime.meurt()
        return victime


JOUEURS = [Joueur(i) for i in range(N)]


def main():  # Crée quelques graphiques.
    p = {}
    for j in JOUEURS:
        p[j.mail] = {"2022-11-27": 0}

    Kills = {"2022-11-27": 0}

    with historique.open("r") as f:
        H = f.readlines()

    size = len(H)
    idx_list = [idx + 1 for idx, val in enumerate(H) if "-----" in val]
    res = [H[i: j] for i, j in zip([0] + idx_list, idx_list + ([size] if idx_list[-1] != size else []))]

    dbd = []

    while len(res) > 2:
        u = res.pop(0)
        date = [re.sub("-------------", "", u[0])]
        l = res.pop(0)
        k = l[:-1]
        dbd.append(date + k)
        res = [[l[-1]]] + res

    if len(res) == 2:
        u = res.pop(0)
        date = [re.sub("-------------", "", u[0])]
        l = res.pop(0)
        dbd.append(date + l)

    # Crée une liste dbd contenant l'ensemble des messages de kills

    for day in dbd:
        for i in range(len(day)):
            day[i] = re.sub("\n", "", day[i])
            if i != 0:
                mail = (day[i].split(",")[0])
                if not day[0] in p[mail]:
                    p[mail][day[0]] = 1
                else:
                    p[mail][day[0]] += 1
        for mail in p:
            if day[0] not in p[mail]:
                p[mail][day[0]] = 0

        Kills[day[0]] = len(day) - 1

    palmares = {}
    Artour = {}
    Score = {}
    S1 = []
    for joueur in JOUEURS:
        Artour[joueur.indice] = joueur
        palmares[joueur.indice] = p[joueur.mail]
        Score[joueur.indice] = sum(palmares[joueur.indice].values())
        S1.append((joueur.indice, Score[joueur.indice]))

    # Tracé des Graphes
    plt.rcParams['axes.facecolor'] = '#978a84'

    # Plot des kills et des morts par jour
    days = list(Kills.keys())
    kills = list(Kills.values())
    players = [95]
    for i in range(1, len(kills)):
        players.append(players[-1]-kills[i])
    print(players)

    plt.clf()
    plt.figure().patch.set_facecolor('#978a84')
    plt.bar(range(len(Kills)), kills, tick_label = days, color = '#4b0101')
    plt.xlabel("Date", size = "x-large")
    plt.ylabel("Morts", size = "x-large")
    plt.title("Evolution du Nombre d'Eliminations par Jour", size = "x-large")
    plt.savefig(jeu / "kills.png")

    plt.clf()
    plt.figure().patch.set_facecolor('#978a84')
    plt.plot(days, players, '-o', color = "#1f6357")
    plt.xlabel("Date", size = "x-large")
    plt.ylabel("Nombre de Joueurs", size = "x-large")
    plt.title("Evolution du Nombre de Joueurs", size = "x-large")
    plt.savefig(jeu / "joueurs.png")

    # Statistiques de chaque classe sur l'entièreté du jeu_2022_2023
    promotion = {}
    for j in JOUEURS:
        if j.classe in promotion:
            promotion[j.classe][0] += Score[j.indice]
            promotion[j.classe][1] += j.est_mort
        else:
            promotion[j.classe] = [Score[j.indice], 1 if j.est_mort else 0]

    Classes = list(promotion.keys())
    temp = list(promotion.values())
    C_K = [c[0] for c in temp]
    C_D = [c[1] for c in temp]
    C_KD = [round(C_K[i] / C_D[i], 2) for i in range(len(Classes))]
    X_axis = np.arange(len(Classes))
    plt.clf()
    fig = plt.figure()
    fig.patch.set_facecolor('#978a84')
    ax = fig.add_subplot()
    for i in range(len(Classes)):
        ax.text(X_axis[i], max(C_K[i], C_D[i]) + 0.01, f"KD : {C_KD[i]}", verticalalignment = 'bottom', horizontalalignment = "center")
    plt.bar(X_axis - 0.2, C_K, 0.4, label = 'Kills', color = "#4b0101")
    plt.bar(X_axis + 0.2, C_D, 0.4, label = 'Morts', color = "#1f6357")
    plt.xticks(X_axis, Classes)
    plt.xlabel("Classes", size = "x-large", verticalalignment = 'top')
    plt.ylabel("Nombre de Joueurs", size = "x-large", verticalalignment = 'bottom')
    plt.title("Statistiques par classe", size = "x-large", verticalalignment = 'bottom')
    plt.legend(loc = "best")
    plt.savefig(jeu / "filiere.png")

    # Plot des scores des meilleurs Joueurs
    p1 = sorted(S1, key = lambda t: t[1], reverse = True)[:5]
    podium = [p1[3], p1[1], p1[0], p1[2], p1[4]]
    pivert = [(Artour[c[0]].prenom + "\n " + Artour[c[0]].nom + "\n " + Artour[c[0]].classe) for c in podium]
    scores = [c[1] for c in podium]
    y = max(scores)
    plt.clf()
    fig = plt.figure()
    fig.patch.set_facecolor('#978a84')
    ax = fig.add_subplot()
    axes = plt.gca()
    X_axis = np.arange(len(podium))
    for i in range(len(podium)):
        ax.text(X_axis[i], scores[i] + 0.01, f"{pivert[i]}", verticalalignment = 'bottom', horizontalalignment = "center")
    plt.bar(range(len(pivert)), scores, color = '#4b0101')
    axes.set_ylim([0, y + 1])
    plt.xlabel("Joueurs", size = "x-large")
    plt.ylabel("Nombre de Kills", size = "x-large")
    plt.title("Meilleurs Joueurs en Nombre de Kills", size = "x-large")
    plt.savefig(jeu / "podium.png")


main()
