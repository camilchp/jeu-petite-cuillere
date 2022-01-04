from random import shuffle

def main():
    with open("reponses.csv", "r") as f:
        f.readline()
        T = f.readlines()
        T[-1] += "\n"
        shuffle(T)
    
    verification_triche(T)

    # TODO: creer un fichier Jeu pour séparer les txt des scripts (utiliser "path" pour rester system-agnostic)

    with open("joueurs_en_vie.txt", "w+") as f:
        for line in T:
            f.write(line)

    # Il semble que copier le premier fichier avec les bibliotheques standard est plus difficile que de le reecrire...
    with open("situation_initiale.txt", "w+") as f:
        for line in T:
            f.write(line)

    with open ("historique.txt", "w+") as f:
        pass

# TODO à completer
def verification_triche(T):
    T_split = [ligne.split(',') for ligne in T]

    mails = [ligne[-1].strip() for ligne in T_split]
    if len(mails) != len(set(mails)):
        raise TricheError("Il y a au moins un doublon parmis les adresses mail.")

    nom_prenom = [(ligne[0], ligne[1]) for ligne in T_split]
    if len(nom_prenom) == len(set(nom_prenom)):
        raise TricheError("Il y a au moins un doublon parmis les adresses mail.")

    return None

if __name__ == "__main__" :
    main()
