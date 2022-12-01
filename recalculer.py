#!/usr/local/bin/python3

from pathlib import Path
from mise_a_jour import Joueur
from datetime import date

jeu = Path("jeu_2022_2023")
initial = jeu / "situation_initiale.csv"
historique = jeu / "historique.txt"

joueurs_recalcule = jeu / "joueurs_recalculé.csv"
historique_reecrit = jeu / "historique_réécrit.txt"

with initial.open("r") as i:
    CSV = i.readlines()
    N = len(CSV)

class Joueur(): # csv est la liste des joueurs, i est l'indice du joueur dans cette liste

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

JOUEURS = [Joueur(i) for i in range(len(CSV))]

def main():

    with historique_reecrit.open("r") as h:
        hist = h.readlines()
        for ligne in hist:
            print(i)
            if ligne[0] == "-":
                pass
            else:
                mail_tueur = ligne.split(",")[0]
                for j in JOUEURS:
                    if j.mail == mail_tueur:
                        cible = j.cible()
                        print(f"{j.nom} {j.prenom} : {cible.nom} {cible.prenom}")
                        j.tue()
    
    with joueurs_recalcule.open("w+") as f:
        for ligne in CSV:
            f.write(ligne)

if __name__ == "__main__":
    main()