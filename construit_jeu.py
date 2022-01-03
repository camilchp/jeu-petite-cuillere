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
    #T_split = [ligne.split for ligne in T]
    #n = len(T)
    return None

if __name__ == "__main__" :
    main()
