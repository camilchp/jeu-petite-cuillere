from datetime import date
import imaplib
from email import message_from_bytes
import re
import smtplib, ssl
from pathlib import Path
from getpass import getpass
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


jeu = Path("Jeu")
joueurs = jeu / "joueurs.csv"
historique = jeu / "historique.txt"

with joueurs.open("r") as f:
    CSV = f.readlines()
    N = len(CSV)

class Joueur(): # T est la liste des joueurs, i est l'indice du joueur dans cette lise

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

# compte mail
try:
    from login import adresse, mot_de_passe
except:
    adresse = input("---adresse mail ?--->")
    mot_de_passe = getpass("---mot de passe de la boite mail ?--->")

def main():

    tueurs = cree_liste_tueurs()
    for tueur in tueurs:
        victime = tueur.tue()
        message_mort(victime, tueur)

    gagnant = jeu_fini()
    if  gagnant:
        print(f"\n============= le jeu est terminé ! ===========\n")
        message_victoire(gagnant)
    
    with joueurs.open("w") as f:
        for line in CSV:
            f.write(line)
    with historique.open("a") as f:
        f.write(f"-------------{date.today()}-------------\n")
        for tueur in tueurs:
            f.write("{tueur.mail} : {tueur.prenom} {tueur.nom} en {tueur.classe}")

#--------------------------------------------------------------------------------------------------------------------
def cree_liste_tueurs(): # TODO : envoyer un mail à tout les joueurs lors d'un triple kill , quintuple kill... ex "Archibald Haddock is on a killing spree !"
    
    # cree une classe IMAP4 avec SSL 
    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    # authentification
    imap.login(adresse, mot_de_passe)
    imap.select('INBOX', readonly=True) # Pour debuger, ajouter en argument readonly=True, le script ne markera pas les messages comme lus à chaque execution
    (retcode, messages) = imap.uid('SEARCH', None, '(UNSEEN)')
    mails_tueurs = []
    nb_mails_non_lus = 0
    nb_morts = 0
    if retcode == 'OK':
        for num in messages[0].split() :
            typ, data = imap.uid('FETCH', num, '(RFC822)')
            nb_mails_non_lus += 1
            for response_part in data:
                if isinstance(response_part, tuple):
                    original = message_from_bytes(response_part[1])
                    if re.search(r'm+o+r+t+', original['Subject'], re.IGNORECASE):
                        nb_morts += 1
                        mail_tueur = re.search('<(.*)>', original['From']).group(1)
                        mails_tueurs.append(mail_tueur)
    else:
        print(f"{bcolors.WARNING}erreur de connexion à la boite mail{bcolors.ENDC}")

                 
    print(f'''

    * {bcolors.OKGREEN}{bcolors.BOLD}connexion à la boite mail réussie{bcolors.ENDC}
    * {bcolors.BOLD}{nb_mails_non_lus}{bcolors.ENDC} nouveaux mails recus, dont {bcolors.BOLD}{nb_morts}{bcolors.ENDC} morts
    * tueurs =  {mails_tueurs}

    ''')
    imap.close()
    imap.logout()

    # On a récupéré une liste des mails des tueurs

    mails_joueurs = [j.mail for j in JOUEURS if not j.est_mort]
    tueurs = []
    for adr in mails_tueurs:
        if adr in mails_joueurs:
            i = mails_joueurs.index(adr)
            tueurs.append(JOUEURS[i])
        else:
            print(f"ATTENTION : {adr} a envoyé {mails_tueurs.count(adr)} mail(s) intitulé mort, mais n'est pas parmis les joueurs vivants !")

    return tueurs

def envoyer_mail(destinataire, message):
    port = 465  # For SSL

    # Create a secure SSL context
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(adresse, mot_de_passe)
        server.sendmail(adresse, destinataire, message.encode("utf8"))

def jeu_fini():
    en_vie = [j for j in JOUEURS if not j.est_mort]
    if len(en_vie) == 1:
        return en_vie[0]
    else:
        return None

def message_mort(mort, tueur):

    message_mort = f"""\
Subject: Décès


Cher {mort.prenom} {mort.nom}, tu as été tué par {tueur.prenom} {tueur.nom}, en {tueur.classe}, bien joué !


PS: En cas d'erreur quelconque, envoie un mail à cette adresse dont l'objet contient le mot "ERREUR" !"""

    envoyer_mail(mort.mail, message_mort)

    print(f"mail de mort envoyé à {mort.mail}")

    victime = tueur.cible()
    message_tueur = f"""\
Subject: Elimination


Cher {tueur.prenom} {mort.nom}, aprés avoir tué {mort.prenom} {mort.nom}, tu dois à présent éliminer {victime.prenom} {victime.nom} en {victime.classe}.

PS: En cas d'erreur quelconque, envoie un mail à cette adresse dont l'objet contient le mot "ERREUR" !
"""

    envoyer_mail(tueur.mail, message_tueur)

    print(f"mail elimination envoyé à {tueur.mail}")

def message_victoire(gagnant):

    message = f"""\
Subject: Victoire !


Cher {gagnant.prenom} {gagnant.nom},

Aujourd'hui, tu es la fierté des {gagnant.classe} ! Tu as remporté le grand jeu de la petite cuillère de la Martinière Monplaisir !

Félicitations !"""

    envoyer_mail(gagnant.mail, message)

    print(f"message de victoire envoye a {gagnant.mail}")

def envoyer_premier_mail():
    n = 0
    for joueur in JOUEURS:
        cible = joueur.cible()
        message = f"""\
Subject: Début du jeu !

Bonsoir {joueur.prenom} {joueur.nom} de {joueur.classe},

Le jeu démarre demain, et ta cible est {cible.prenom} {cible.nom}, en {cible.classe}.

IMPORTANT : pour notifier une élimination, envoyer à cette adresse un unique mail contenat le mot "MORT" dans l'objet, le plus tôt possible après l'élimination.
(Ce mail doit être envoyé dans la journée de l'élimination, la prochaine cible sera alors communiquée par mail.)

Lorsque vous vous faites éliminer, n'oubliez pas de communiquer votre cible à votre assasin afin de fluidifier le jeu. Il est possible d'effectuer plusieurs élimination dans la même journée. 

Pour rappel :

Tu dois éliminer ta cible en la touchant avec une petite cuillère, quelqu'un d'autre cherche également à t'éliminer. Un joueur qui brandit une cuillère devant lui est inataquable.
L'élimination d'une cible est interdite dans les lieux suivants :
- les escaliers
- sa chambre personnelle (si iel est à l'internat)
- le self
- la queue du self
- les bâtiments de cours (pour le bâtiment B, à partir du premier étage)
- la salle G024
- la salle des profs, qui est de toute façon réservée aux enseignants

PS: En cas d'erreur quelconque, envoie un mail à cette adresse dont l'objet contient le mot "ERREUR" !
"""
        envoyer_mail(joueur.mail, message)
        print(f"premier mail envoyé à {joueur.mail}")
        n+=1
    print(f"\npremier mail envoyé à {n} joueurs en tout")

if __name__ == "__main__":
    main()