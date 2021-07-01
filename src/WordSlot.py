"""
# WordSlots are the main objects of the grid, they are the word "spaces" to be filled
"""

import numpy as np

class WordSlot():

    def __init__(self, identifiant, length, first_letter_position, direction, initial_letters):
        self.identifiant = identifiant
        self.length = length
        self.first_letter_position = first_letter_position
        self.direction = direction
        self.slots = self.compute_slots()
        self.dic_crosses = {}
        self.current_letters = initial_letters
        self.number_of_possible_words = -1
        self.current_possible_words = []

    def set_current_possible_words(self, possible_words):
        """ Sets the list of words which can fit in the word slot given the letters already in place

        :param possible_words: [string] list of words which can fit in the word slot given the letters already in place
        :return: None
        """

        self.current_possible_words = possible_words
        self.number_of_possible_words = len(possible_words)

    def what_current_word_would_be_with_an_added_letter(self,letter, position):
        """ Helper function to simulate the placement of a new letter

        :param letter: (char) letter we want to add to current word
        :param position: (int) position we want to add the letter to
        :return: (string) current word with the letter added
        """
        new_word = self.current_letters.copy()
        new_word[position] = letter
        return new_word

    def check_if_word_is_filled(self):
        """ Helper function to check it current word is filled or if there are still some empty letters

        :return: None
        """
        if "." not in self.current_letters:
            return True
        else:
            return False

    def propose_a_word_with_current_situation(self):
        """ Given the current letters, choose a possible word at random

        :return: (string) a possible word
        """
        chosen_word = np.random.choice(self.current_possible_words)
        return chosen_word

    def set_a_word(self,word):
        """ Set a given word to be the word of this word slot

        :param word: (string) word to set
        :return:  None
        """
        self.current_letters = [x for x in word]
        self.number_of_possible_words = len(self.current_possible_words)

    @staticmethod
    def tab2string(tab):
        """ Helper function to convert an array to a string

        :param tab: array to convert
        :return:
        """
        str_ = ""
        for item in tab:
            str_+= item
        return str_

    def compute_crosses(self, temp_horizontal_slots_grid, temp_vertical_slots_grid):
        """ Compute crosses with other word slots (updates self.dic_crosses)

        :param temp_horizontal_slots_grid: ([int]) ID of horizontal words for each square
        :param temp_vertical_slots_grid: ([int]) ID of vertical words for each square
        :return: None
        """

        relevant_grid_to_check = temp_horizontal_slots_grid if self.direction == "vertical" else \
            temp_vertical_slots_grid
        for e,slot in enumerate(self.slots):
            corresponding_word_slot_id = relevant_grid_to_check[slot[0]][slot[1]]
            if corresponding_word_slot_id != "0":
                self.dic_crosses[int(corresponding_word_slot_id.split(".")[0])] = [e,int(corresponding_word_slot_id.split(".")[1])]

    def compute_slots(self):
        """ Compute position of spaces spanned by the word slot

        :return: ([int, int]) position of spaces spanned by the word slot
        """
        slots = []
        for i in range(self.length):
            if self.direction == "horizontal":
                slots.append([int(self.first_letter_position[0]), int(self.first_letter_position[1] + i)])
            else:
                slots.append([int(self.first_letter_position[0] + i), int(self.first_letter_position[1])])
        return slots