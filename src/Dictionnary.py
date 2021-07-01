"""
Handles the dictionnary (list of authorized words)
"""

from Word import *

class Dictionnary():

    def __init__(self,path_dictionnary):
        self.scrabble_scores = {"a" : "1", "b" : "2", "c" : "3", "d" : "2", "e" : "1", "f" : "4", "g" : "2", "h" : "4",
                           "i" : "1", "j" : "8", "k" : "10", "l" : "1", "m" : "2", "n" : "1", "o" : "1", "p" : "3",
                           "q" : "8", "r" : "1", "s" : "1", "t" : "1", "u" : "1", "v" : "4", "w" : "10", "x" : "10",
                           "y" : "10", "z" : "10"}

        # actual list of words.
        self.word_dictionnary = {}
        self.load_dic_from_dic_file(path_dictionnary)

    def load_dic_from_dic_file(self, path_dictionnary):
        """ Loads the dictionnary (list of authorized words) into a dictionnary (Python object)

        :param path_dictionnary: (string) path to dictionnary (list of authorized words)
        :return: (dictionnary) words organized by length
        """

        try:
            with open(path_dictionnary, "r") as f:
                for word in f:
                    word_object = Word(word, self.scrabble_scores)
                    # Words are sorted by length for easy lookup in the algorithm.
                    self.word_dictionnary.setdefault(str(word_object.word_length),[]).append(word_object)
            f.close()
        except FileNotFoundError:
            raise Exception(path_dictionnary," not found.")
        except KeyError as key:
            print(key," not found in score tables.")
