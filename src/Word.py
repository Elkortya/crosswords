"""
Glorified String with some bells and whistles
"""

import unidecode

class Word():

    def __init__(self,raw_word, scrabble_scores):
        # cleaning up dictionnary quirks
        self.word = self.clean_up_word(raw_word)
        self.word_length = len(self.word)
        # can be used to use words which will in theory be more "crossword-friendly"
        self.scrabble_score = self.compute_scrabble_score(scrabble_scores)
        self.probability = 0

    @staticmethod
    def clean_up_word(word):
        """ putting a word in lowercase, and taking out puncutation signs, and diacritics

        :param word:  (string) word, uncleaned
        :return: (string) clean word
        """

        return unidecode.unidecode(word.lower().rstrip().replace("-","").replace(" ","").replace("\'",""))

    def compute_scrabble_score(self, scrabble_scores):
        """ compute the "Scrabble score" of a word to judge its rarity and plyability

        :param scrabble_scores: (dictionnary) Scrabble score of each letter
        :return: (int) Scrabble score of the word
        """
        # Scrabble score is the sum of scrabble score of each letter composing the word
        scrabble_score = 0
        for letter in self.word:
            scrabble_score += int(scrabble_scores[letter])
        return scrabble_score