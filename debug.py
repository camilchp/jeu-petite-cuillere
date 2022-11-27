import mise_a_jour
from pathlib import Path

jeu = Path("Jeu")
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


def premier_mail():
    for joueur in JOUEURS[50:]:
        cible = joueur.cible()
        message = f"""\
            Subject: Début du jeu !

            Bonsoir {joueur.prenom} {joueur.nom} de {joueur.classe},

            Le jeu démarre demain, et ta cible est {cible.prenom} {cible.nom}, en {cible.classe}.

            IMPORTANT : Pour notifier une élimination, le TUEUR doit envoyer à cette adresse un UNIQUE mail contenant le mot "MORT" dans l'objet, le plus tôt possible après l'élimination.
            (Ce mail doit être envoyé dans la journée de l'élimination, la prochaine cible sera alors communiquée par mail.)

            Lorsque vous vous faites éliminer, n'oubliez pas de communiquer votre cible à votre assasin afin de fluidifier le jeu. Il est possible d'effectuer plusieurs éliminations dans la même journée. 

            Pour rappel :

            Tu dois éliminer ta cible en la touchant avec une petite cuillère, quelqu'un d'autre cherche également à t'éliminer. Un joueur qui brandit une cuillère devant lui est inattaquable.
            L'élimination d'une cible est interdite dans les lieux suivants :
            - les escaliers
            - sa chambre personnelle (si iel est à l'internat)
            - le self
            - la queue du self
            - les bâtiments de cours (pour le bâtiment B, à partir du premier étage)
            - la salle G024

            Bonne Chance, tu en auras besoin...

            PS: En cas d'erreur quelconque, envoie un mail à cette adresse dont l'objet contient le mot "ERREUR" !
            """
        mise_a_jour.envoyer_mail(joueur.mail, message)
        print(f"premier mail envoyé à {joueur.mail}")

premier_mail()
