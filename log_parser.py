from typing import Dict, List
import sys

"""
Initialisation des constantes.
__LINE__ : Constantes correspondant à la structure de la ligne de log
__URL__ : Structure de l'URL pour les informations qui nous intéressent
"""


__LINE__ = {
    "date" : 0,
    "time" : 1,
    "url" : 2
}

__URL__ = {
    "page" : 1,
    "display_mode" : 4,
    "zoom" : 6
}
    

class Parser:
    """
    Cette classe prend en charge le parsing des lignes de log
    et la gestion des compteurs.
    """
    def __init__(self) -> None:
        """
        Constructeur initialisant les variables de classe
        """
        self._last_display_mode = ""
        self._display_mode_counter = 0
        self._count_series = []
        self._list_zooms = []
        self._ignored_lines = 0

    def update_display_mode_counters(self, display_mode : str, zoom : str) -> None:
        """
        Fonction mettant à jour la liste des séries trouvées dans les lignes de log.
        Le compteur de série est incrémenté jusqu'à ce que le mode d'affichage de 
        la ligne de log différent de celui de la ligne précédente.
        Si les différents niveaux de zoom par série sont également enregistrés.
        
        @params: display_mode: mode d'affichage trouvé dans la ligne de log.
        @params: zoom: niveau de zoom trouvé dans la ligne de log.
        """
        if display_mode != self._last_display_mode:
            if self._last_display_mode != "":
                self._count_series.append({"display_mode" : self._last_display_mode, \
                    "serie" : self._display_mode_counter, \
                    "zooms" : sorted(self._list_zooms)})

            self._display_mode_counter = 1
            self._last_display_mode = display_mode
            self._list_zooms = [zoom]
        else:
            self._display_mode_counter += 1
            if zoom not in self._list_zooms:
                self._list_zooms.append(zoom)
            
    def parse_line(self, line : str) -> None:
        """
        Cette fonction orchestre le parsing de la ligne de log.
        La fonction commence par parser la ligne et s'assure que le
        nombre d'éléments composant la ligne est correct (sinon la ligne
        est ignorée).
        La fonction par alors l'URL qui est trouvée dans la ligne de log,
        s'assure qu'il s'agit bien d'une map.
        La fonction récupère alors le mode d'affichage et le niveau de zoom
        est lance la mise à jour des compteurs.

        @params: line: ligne de log à parser
        """
        line_elems = line.split()
        
        if len(line_elems) == 3:
            url = line_elems[__LINE__["url"]].split("/")
            if len(url) > __URL__["display_mode"]:
                if url[__URL__["page"]] == "map":
                    current_display_mode = url[__URL__["display_mode"]]
                    current_zoom = None
                    if len(url) > __URL__["zoom"]:
                        current_zoom = url[__URL__["zoom"]]
                    self.update_display_mode_counters(current_display_mode, current_zoom)
                    
        else:
            self._ignored_lines += 1

    def get_count_series(self) -> List:
        """
        Retourne le dictionnaire de series par mode d'affichage

        @returns : List
        """
        return self._count_series
    
    def get_ignored_lines(self) -> int:
        """
        Retourne le nombre de lignes ignorées

        @returns : int
        """
        return self._ignored_lines



def write_output(list_display_mode : List, output : str) -> None:
    """
    Cette fonction gère le formatage des lignes et l'écriture dans le fichier 
    de résultats.

    @params: list_display_mode:
    @params: output: Fichier de sortie
    """
    ouput_file = open(output, 'w')
    lines = []
    for elems in list_display_mode:
        display_mode = elems["display_mode"]
        serie = str(elems["serie"])
        zooms = ','.join(elems["zooms"])
        lines.append((f"{display_mode}\t{serie}\t{zooms}\r\n"))
    
    ouput_file.writelines(lines)


def parse_logs(file_content : List, output : str) -> None:
    """
    Cette fonction permet d'orchestrer le parsing du fichier de log.
    Le fichier est parcourru ligne à ligne et chaque ligne est passée
    à l'instance de l'objet Parser pour être analysé.

    @params: file_content: Liste des éléments du log à parser
    @params: output: Fichier de sortie
    """
    parser = Parser()
    
    print("Lecture de l'entrée.")
    for line in file_content:
        parser.parse_line(line)

    print("Génération du fichier de résultats.")
    write_output(parser.get_count_series(), output)
    print("Nombre de lignes ignorées: " + str(parser.get_ignored_lines()))


if __name__ == "__main__":
    """
    Point d'entrée du programme.
    Ce programme lit les lignes de log fournis en entrée standard.
    L'argument est le fichier de sortie contenant les résultats.
    Si aucun argument n'est passé, le programme travail avec les fichiers
    fournis par défaut avec le projet.
    """

    print("Début du traitement!!!")
    file_content = sys.stdin.readlines()
    if len(sys.argv) == 2:
        output = sys.argv[2]
    else:
        #filename = "tornik-map-20171006.10000.tsv"
        output = "tornik-map-20171006.10000.output"

    try:
        parse_logs(file_content, output)
    except Exception as ex:
        print("Une exception a été levée lors de l'exécution. Veuilliez vérifier vos paramètres.")
        print(ex)
    print("Fin du traitement!!!")
    