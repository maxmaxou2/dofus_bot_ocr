import json

# Ouvrir le fichier en mode lecture ('r')
with open('mapPositions.json', 'r', encoding='utf-8') as fichier:
    # Charger le contenu du fichier JSON dans une variable
    data = json.load(fichier)

# Vous pouvez maintenant accéder aux données JSON comme un dictionnaire ou une liste Python
def findPos(mapId) :
    for dat in data :
        if dat['id'] == mapId :
            return int(dat['posX']), int(dat['posY'])