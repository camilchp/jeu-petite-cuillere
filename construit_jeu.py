from random import shuffle
from pathlib import Path

def main():
    with open("reponses.csv", "r") as f:
        f.readline()
        T = f.readlines()
        T[-1] += "\n"
        shuffle(T)
    
    verification_triche(T)

    jeu = Path('jeu')
    jeu.mkdir()

    with (jeu / "joueurs.csv").open(mode="w+") as f:
        for line in T:
            line = ",".join([texte.strip().strip('''"''') for texte in line.split(",")[1::]]) + "\n" # convertit les lignes du csv d'un google forms en Nom,Prenom,Classe,Mail
            f.write(line)

    # Il semble que copier le premier fichier avec les bibliotheques standard est plus difficile que de le reecrire...
    with (jeu / "situation_initiale.csv").open(mode="w+") as f:
        for line in T:
            line = ",".join([texte.strip().strip('''"''') for texte in line.split(",")[1::]]) + "\n" # convertit les lignes du csv d'un google forms en Nom,Prenom,Classe,Mail
            f.write(line)

    with (jeu / "historique.txt").open(mode="w+") as f:
        pass

def verification_triche(T):
    T_split = [ligne.split(',') for ligne in T]

    mails = [ligne[-1].strip() for ligne in T_split]
    if len(mails) != len(set(mails)):
        raise RuntimeError("Il y a au moins un doublon parmis les adresses mail.")

    nom_prenom = [(ligne[0], ligne[1]) for ligne in T_split]
    if len(nom_prenom) != len(set(nom_prenom)):
        raise RuntimeError("Il y a au moins un doublon parmis les noms.")

    return None

if __name__ == "__main__" :
    main()
    from mise_a_jour import envoyer_premier_mail
    envoyer_premier_mail()
