from datetime import date
import imaplib
from email import message_from_bytes
import re
import smtplib, ssl
from pathlib import Path

jeu = Path("Jeu")
joueurs_en_vie = jeu / "joueurs_en_vie.csv"
historique = jeu / "historique.txt"

def main():
    tueurs = cree_liste_tueurs()
    with joueurs_en_vie.open("r") as f:
        T = f.readlines()
        n = len(T)
        joueurs = [T[i].split(',')[-1].strip() for i in range(n)]
        for tueur in tueurs:
            assert tueur in joueurs # Verifie que les tueurs sont toujours en jeu
        for tueur in tueurs:
            i = joueurs.index(tueur)  # TODO : un tueur mort le jour de son crime peut causer une erreur suivant l'heure d'arrivée des mails 
            ligne_tueur = T[i]
            ligne_mort = T[(i+1)%n]
            T.pop((i+1)%n)
            joueurs.pop((i+1)%n)
            n -= 1
            message_mort(ligne_mort, ligne_tueur)
        if len(T) == 1:
            print(f"""
            ================================================================
            ================================================================
            ================================================================

                                LE JEU EST TERMINE !!!

                                un message a été envoyé
                                     au gagnant !

            ================================================================
            ================================================================
            ================================================================
            """)
            message_victoire(T[0])
    with joueurs_en_vie.open("w") as f:
        for line in T:
            f.write(line)
    with historique.open("a") as f:
        f.write(f"-------------{date.today()}-------------\n")
        for tueur in tueurs:
            f.write(tueur + "\n")

#--------------------------------------------------------------------------------------------------------------------
def cree_liste_tueurs(): # TODO : envoyer un mail à tout les joueurs lors d'un triple kill , quintuple kill... ex "Archibald Haddock is on a killing spree !"
    tueurs = []

    # compte mail
    adresse = "lapetitecuillere69@gmail.com"
    mot_de_passe = input("---mot de passe de la boite mail?--->")

    # cree une classe IMAP4 avec SSL 
    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    # authentification
    imap.login(adresse, mot_de_passe)

    imap.select('INBOX') # Pour debuger, ajouter en argument readonly=True, le script ne markera pas les messages comme lus à chaque execution

    (retcode, messages) = imap.uid('SEARCH', None, '(UNSEEN)')

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
                        tueurs.append(mail_tueur)
    else:
        print("erreur de connexion")
                        
    print(f"{nb_mails_non_lus} nouveaux mails recus, dont {nb_morts} morts")
    print("tueurs = ", tueurs, "(doublons => plusieurs kills... la classe !)")
    imap.close()
    imap.logout()

    return tueurs

def envoyer_mail(destinataire, message):
    port = 465  # For SSL

    # Create a secure SSL context
    context = ssl.create_default_context()

    # compte mail
    adresse = "lapetitecuillere69@gmail.com"
    mot_de_passe = input("---mot de passe de la boite mail?--->")

    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(adresse, mot_de_passe)
        server.sendmail(adresse, destinataire, message.encode("utf8"))

def message_mort(ligne_mort, ligne_tueur):
    mort = ligne_mort.split(',')
    tueur = ligne_tueur.split(',')

    mail_mort = mort[-1].strip()

    message = f"""\
Subject: Décès


Cher {mort[1]} {mort[0]}, tu as été tué par {tueur[1]} {tueur[0]}, en {tueur[2]}, bien joué !


PS: Si ceci est une erreur, envoie un mail à cette adresse dont l'objet contient le mot "ERREUR" !"""

    envoyer_mail(mail_mort, message)

    print(f"mail de mort envoyé à {mail_mort}")

def message_victoire(ligne_gagnant):
    gagnant = ligne_gagnant.split(',')

    mail_gagnant = gagnant[-1].strip()

    message = f"""\
Subject: Victoire !


Cher {gagnant[1]} {gagnant[0]},

Aujourd'hui, tu es la fierté des {gagnant[2]} ! Tu as remporté le grand jeu de la petite cuillère de la Martinière Monplaisir !

Félicitations !"""

    envoyer_mail(mail_gagnant, message)

    print(f"message de victoire envoye a {mail_gagnant}")

if __name__ == "__main__":
    main()