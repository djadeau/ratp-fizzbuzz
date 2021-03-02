from typing import Dict
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
        self._count_series = {}
        self._list_zooms = {}
        self._ignored_lines = 0

    def update_display_mode_counters(self, display_mode : str) -> None:
        """
        Fonction mettant à jour le dictionnaire enregistrant les séries max
        par mode d'affichage.
        Si le mode d'affichage n'est pas dans le dictionnaire celui-ci est ajouté.
        Le compteur de série est incrémenté jusqu'à ce que le mode d'affichage de 
        la ligne de log différent de celui de la ligne précédente.
        
        @params: display_mode: mode d'affichage trouvé dans la ligne de log.
        """
        if display_mode != self._last_display_mode:
            if self._last_display_mode in self._count_series:
                if self._count_series[self._last_display_mode] < self._display_mode_counter:
                    self._count_series[self._last_display_mode] = self._display_mode_counter
            else:
                if self._last_display_mode != "":
                    self._count_series[self._last_display_mode] = self._display_mode_counter

            self._display_mode_counter = 1
            self._last_display_mode = display_mode
        else:
            self._display_mode_counter += 1
            

    def update_zoom_values(self, display_mode : str, zoom : str) -> None:
        """
        Cette fonction enregistre le niveau de zoom par mode d'affichage dans un dictionnaire
        de liste.
        Si le niveau de zoom pour le mode d'affichage n'existe pas dans la liste associée, alors
        celui-ci est ajouté dans la liste.

        @params: display_mode: mode d'affichage trouvé dans la ligne de log.
        @params: zoom: niveau de zoom trouvé dans la ligne de log.
        """
        if display_mode in self._list_zooms:
            list_of_zooms = self._list_zooms[display_mode]
            if zoom not in list_of_zooms:
                list_of_zooms.append(zoom)
                self._list_zooms[display_mode] = list_of_zooms

        else:
            self._list_zooms[display_mode] = [zoom]

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
                    self.update_display_mode_counters(current_display_mode)
                    if len(url) > __URL__["zoom"]:
                        current_zoom = url[__URL__["zoom"]]
                        self.update_zoom_values(current_display_mode, current_zoom)
        else:
            self._ignored_lines += 1

    def get_list_zooms(self) -> Dict:
        """
        Retourne le dictionnaire de listes de zoom par mode d'affichage

        @returns : Dict
        """
        return self._list_zooms

    def get_count_series(self) -> Dict:
        """
        Retourne le dictionnaire de series par mode d'affichage

        @returns : Dict
        """
        return self._count_series
    
    def get_ignored_lines(self) -> int:
        """
        Retourne le nombre de lignes ignorées

        @returns : int
        """
        return self._ignored_lines



def write_output(dict_display_mode : Dict, dict_zooms : Dict, output : str) -> None:
    """
    Cette fonction gère le formatage des lignes et l'écriture dans le fichier 
    de résultats.
    Le formatage se fait en joignant les deux dictionnaires générés par le parser.

    @params: dict_display_mode:
    @params: dict_zooms:
    @params: output: Fichier de sortie
    """
    ouput_file = open(output, 'w')
    lines = []
    for elems in dict_display_mode:
        key = elems
        serie = dict_display_mode[elems]
        zooms = ','.join(sorted(dict_zooms[elems]))
        lines.append((f"{key}\t{serie}\t{zooms}\r\n"))
    
    ouput_file.writelines(lines)


def parse_logs(filename : str, output : str) -> None:
    """
    Cette fonction permet d'orchestrer le parsing du fichier de log.
    Le fichier est parcourru ligne à ligne et chaque ligne est passée
    à l'instance de l'objet Parser pour être analysé.

    @params: filename: Nom du fichier à parser
    @params: output: Fichier de sortie
    """
    parser = Parser()
    
    print("Lecture du fichier de log.")
    file = open(filename, "r")
    line = file.readline()
    while line:
        parser.parse_line(line)
        line = file.readline()

    print("Génération du fichier de résultats.")
    write_output(parser.get_count_series(), parser.get_list_zooms(), output)
    print("Nombre de lignes ignorées: " + str(parser.get_ignored_lines()))


if __name__ == "__main__":
    """
    Point d'entrée du programme.
    Ce programme peut prendre en ligne de commande deux arguments.
    Le premier argument est le fichier de log à analyser.
    Le second argument est le fichier de sortie contenant les résultats.
    Si aucun argument n'est passé, le programme travail avec les fichiers
    fournis par défaut avec le projet.
    """

    print("Début du traitement!!!")
    filename = ""
    if len(sys.argv) == 3:
        filename = sys.argv[1]
        output = sys.argv[2]
    else:
        filename = "tornik-map-20171006.10000.tsv"
        output = "tornik-map-20171006.10000.output"

    try:
        parse_logs(filename, output)
    except Exception as ex:
        print("Une exception a été levée lors de l'exécution. Veuilliez vérifier vos paramètres.")
        print(ex)
    print("Fin du traitement!!!")
    