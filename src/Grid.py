"""
Main class representing the grid which will do the heavy lifting of actually trying and placing words in the grid
"""

from WordSlot import *
import re


class Grid():
    def __init__(self, grid_info, dictionnary, debug):
        self.grid_code, (self.h, self.w) = self.get_info_from_grid(grid_info)
        self.grid_array = self.create_grid_array()
        self.debug = debug

        # The temp_slots_grids are grids containing the ids of horizontal (resp vertical) words only
        # at each slot of the grid
        # eg vertical grid will be
        # 0 . 2
        # 0 1 2
        # . 1 2
        # representing the vertical words. They are used for computing the crosses between words.

        # list_of_wSs is the list of word slots, the main objects of the grid
        self.list_of_wSs, temp_horizontal_slots_grid, temp_vertical_slots_grid = self.create_list_of_word_slots()
        self.nb_of_word_slots = len(self.list_of_wSs)
        self.dictionnary = dictionnary.word_dictionnary
        # keeping track of incomplete word slots, initialized to all word slots.
        self.list_of_incomplete_wSs = self.list_of_wSs.copy()
        self.list_of_complete_wSs_idxs = []

        # compute initial crosses and possible words for each word slot at initialisation
        for word_slot in self.list_of_wSs:
            word_slot.compute_crosses(temp_horizontal_slots_grid, temp_vertical_slots_grid)
            word_slot.set_current_possible_words(self.find_possible_words_with_given_letters(word_slot.current_letters))

    def get_info_from_grid(self, path_grid_template):
        """ Gets width, height and grid symbols from description in a text file

        :param path_grid_template: (string) path to the text file describing the grid
        :return grid_symbols: ([char]) grid represented as a series of charcaters
        :return (h,w): ([int, int]) nb of squares long and wide for the grid
        """
        grid_symbols = []
        h = 0
        w = 0
        with open(path_grid_template, "r") as f:
            for line in f:
                line = line.rstrip()
                h += 1
                w = len(line)
                for x in line:
                    grid_symbols.append(x)
        f.close()

        return grid_symbols, (h, w)

    @staticmethod
    def tab2string(tab):
        """ Helper function to transform array into string

        :param tab: ([char]) array to transform
        :return: (string) array transformed into string
        """
        str_ = ""
        for item in tab:
            str_ += item
        return str_

    def check_if_grid_is_filled(self):
        """ check if grid has all words complete

        :return: None
        """

        for word_slot in self.list_of_wSs:
            if not word_slot.check_if_word_is_filled():
                return False
        return True

    def remove_a_word_from_the_dic(self, word):
        """ Remove a specific word from the dictionnary (to prevent words being used more than once)

        :param word: (string) word to delete
        :return: None
        """

        for word_object in self.dictionnary[str(len(word))]:
            if word_object.word == word:
                self.dictionnary[str(len(word))].remove(word_object)

    def fill_up_grid(self):
        """ Iteratively try to fit words until the grid is filled

        :return: None
        """

        success_grid = True
        # While we're not filled
        while not self.check_if_grid_is_filled():
            # Try to add words
            success_word = self.fill_up_one_word()
            # If no more word can be added (even if grid is not complete), exit.
            if not success_word:
                success_grid = False
                break
        return success_grid

    def update_grid(self):
        """ Update the grid_array object wrt the different word slots

        :return: None
        """
        for word_slot in self.list_of_wSs:
            for e, letter in enumerate(word_slot.current_letters):
                if word_slot.direction == "horizontal":
                    if self.debug:
                        print(self.grid_array)
                        print(word_slot.first_letter_position)
                    self.grid_array[word_slot.first_letter_position[0]][word_slot.first_letter_position[1] + e] = letter
                else:
                    self.grid_array[word_slot.first_letter_position[0] + e][word_slot.first_letter_position[1]] = letter

    def find_possible_words_with_given_letters(self, letters):
        """ Given a wordslot with letters and spaces, find all possible words from the dictionnary that could fit

        :param letters: ([char]) description of the word slot
        :return: ([string]) list of words that could fit in the word slot
        """

        r = re.compile(self.tab2string(letters))
        list_of_words_with_correct_length = [word_object.word for word_object in self.dictionnary[str(len(letters))]]
        return list(filter(r.match, list_of_words_with_correct_length))

    def chose_a_word_knowing_their_impact(self, word_impact):
        """ Choose a word from a list of words randomly, weighted by their "impact" on the rest of the grid
        (see fill_up_one_word function for computation of this impact)

        :param word_impact: ([string, [float]]) : list of words and their impact arrays
        :return: (string, [float]) : chosen word with its impact array
        """
        if self.debug:
            print("word imapct ", word_impact)
        # Unpacking arguments
        words = [x[0] for x in word_impact]
        arr = [x[1] for x in word_impact]
        # Number of words
        nb_cw = len(arr[0])
        nb_pw = len(arr)

        # Some heuristics :
        # Checking that among the possible words, there is not one which is the only possibility of some other word slot
        # (not considered at the moment). If so, we won't use it here, because we want to keep it for that word slot
        # later on.
        for wS in self.list_of_incomplete_wSs:
            if wS.number_of_possible_words == 1:
                only_possible_word_for_some_wS_so_we_wanna_keep_it = wS.current_possible_words[0]
                if only_possible_word_for_some_wS_so_we_wanna_keep_it in words:
                    idx = words.index(only_possible_word_for_some_wS_so_we_wanna_keep_it)
                    words.pop(idx)
                    arr.pop(idx)
        # Checking if we didn't take out all possible words. If so, we return None, meaning we can't find a word
        # among the proposed words
        if len(words) == 0:
            return None, None

        # Some manipulations to choose randomly a word, with weigths based on their impact.
        # I tried a bunch of stuff, eg non linear functions to give some probability to rare words to pop up more..
        # but I ended up with something pretty simple.
        arr = np.array(arr)
        arr_min = np.min(arr, axis=1)
        if nb_cw >= 2:
            arr2min = []
            for x in arr:
                x.sort()
                arr2min.append(x[1])
            arr_min = [x1 * x2 for x1, x2 in zip(arr_min, arr2min)]
        if max(arr_min) == 0:
            return None, None
        # Here is where I tried to do some mathy stuff, wihtout much success.
        arr_min = self.some_exp_fct(arr_min)
        # Actual random weighted choice
        chosen_index = np.random.choice(range(nb_pw), p=arr_min)

        return words[chosen_index], arr[chosen_index]

    @staticmethod
    def some_exp_fct(arr):
        """ Normalisation to "sum to one" of impacts.

        :param arr: [float] list of impacts
        :return: [float] list of impacts summing to 1
        """
        return arr / sum(arr)

    def fill_up_one_word(self):
        """ Does the heavy lifting of filling up on word

        :return None:
        """

        # Check and update complete and incomplete word slots
        self.list_of_incomplete_wSs = []
        self.list_of_complete_wSs_idxs = []
        for e, word_slot in enumerate(self.list_of_wSs):
            if not word_slot.check_if_word_is_filled():
                self.list_of_incomplete_wSs.append(word_slot)
            else:
                self.list_of_complete_wSs_idxs.append(e)

        # The word slot we'll try to fill will be the one with the least possible words.
        # The rationale is that each time you fill a word slot, crossing word slots have less and less possible words
        # So if you have eg a word slot with 600 possible words and another with 10, then you fill up first the one with
        # 10 words, such that the other one will have eg 300 words left.
        if self.debug:
            print("----------------------------------------------")
            self.print_current_grid_state()
            for ws in self.list_of_incomplete_wSs:
                print("word ", ws.identifiant, " has ", ws.number_of_possible_words, " possiblites")
        nb_possible_words = [x.number_of_possible_words for x in self.list_of_incomplete_wSs]
        min_npw = min(nb_possible_words)
        wSs_idxs_with_the_least_possible_words = [i for i, x in enumerate(self.list_of_incomplete_wSs)
                                                  if x.number_of_possible_words == min_npw]
        random_min = np.random.choice(wSs_idxs_with_the_least_possible_words)
        # the word slot with the least possible words, noted wlsp, is chosen to be completed for this function call
        wS_with_the_least_possible_words = self.list_of_incomplete_wSs[random_min]

        # Find possible words for the selected word slot
        possible_words_for_wSlp = self.find_possible_words_with_given_letters(
            wS_with_the_least_possible_words.current_letters)

        # To chose between all these words, we'll compute the "impact" of each word, a measure related to how many words will still
        # be possible in all word slots that the current word slot crosses.
        wSs_crossed_by_wSlp = [self.list_of_wSs[idx - 1] for idx in wS_with_the_least_possible_words.dic_crosses.keys()
                               if idx - 1 not in self.list_of_complete_wSs_idxs]

        if self.debug:
            print("We're chosing word ", wS_with_the_least_possible_words.identifiant)
            print("It crosses ", len(wSs_crossed_by_wSlp), " incomplete words.")
            print("the possile words are ", possible_words_for_wSlp)

        # If the current word slot crosses no other incomplete word, just choose a word randomly.
        if len(wSs_crossed_by_wSlp) == 0:
            if self.debug:
                print("This word crosses 0 incomplete words, so we're just gonna one randomly")
            chosen_word = np.random.choice(possible_words_for_wSlp)

        # Else, we're gonna select a word which doesn't block too much the incomplete words
        else:
            # pw_for_wSlp : possible word for wSlp
            how_would_these_words_impact_the_wS_it_crosses = []

            # For each possible word for this word slot,
            for pw_for_wSlp in possible_words_for_wSlp:
                nb_of_possibilities_per_cw = []
                if self.debug:
                    print("possible word ", pw_for_wSlp)
                # For each word slot crossed, compute the number of posibile words given that we choose the current
                # word for the current word slot.
                for wS_crossed_by_wlSp in wSs_crossed_by_wSlp:
                    relevant_cross = list(wS_with_the_least_possible_words.dic_crosses[wS_crossed_by_wlSp.identifiant])
                    wSlp_pos = relevant_cross[0]
                    pw_for_wSlp_letter = pw_for_wSlp[wSlp_pos]
                    cwS_pos = relevant_cross[1]
                    hypothetical_word_for_wS_crossed_by_wlSp = wS_crossed_by_wlSp.what_current_word_would_be_with_an_added_letter(
                        pw_for_wSlp_letter, cwS_pos)
                    if self.debug:
                        print("hypotehtical word ", hypothetical_word_for_wS_crossed_by_wlSp)
                    possible_words_for_hw_for_wS_crossed_by_wlSp = \
                        self.find_possible_words_with_given_letters(hypothetical_word_for_wS_crossed_by_wlSp)
                    if pw_for_wSlp in possible_words_for_hw_for_wS_crossed_by_wlSp:
                        possible_words_for_hw_for_wS_crossed_by_wlSp.remove(pw_for_wSlp)
                    nb_of_possibilities_per_cw.append(len(possible_words_for_hw_for_wS_crossed_by_wlSp))
                how_would_these_words_impact_the_wS_it_crosses.append([pw_for_wSlp, nb_of_possibilities_per_cw])

            # At this point, we have the "impact" of each possible word. We can now choose one following some
            # weighted random function.
            chosen_word, word_impact = self.chose_a_word_knowing_their_impact(
                how_would_these_words_impact_the_wS_it_crosses)
            if self.debug:
                print("We chose word ", chosen_word, " which has impact ", word_impact)
            if chosen_word is None:
                if self.debug:
                    print("No new word could be placed.")
                    self.print_current_grid_state()
                return False

        # Actually place the word in the grid.
        wS_with_the_least_possible_words.set_a_word(chosen_word)
        wS_with_the_least_possible_words.set_current_possible_words(
            self.find_possible_words_with_given_letters(chosen_word))
        self.remove_a_word_from_the_dic(chosen_word)

        # Update all crossed word slots with the new letter that they now have
        for [crossed_word_id, [letter_position_of_this_word, letter_position_in_crossed_word]] in \
                wS_with_the_least_possible_words.dic_crosses.items():
            crossed_wS = self.list_of_wSs[crossed_word_id - 1]
            crossed_wS.current_letters[letter_position_in_crossed_word] = \
                wS_with_the_least_possible_words.current_letters[letter_position_of_this_word]
            crossed_wS.set_current_possible_words(
                self.find_possible_words_with_given_letters(crossed_wS.current_letters))
            if crossed_wS in self.list_of_incomplete_wSs and self.debug:
                print("Crossed word ", crossed_word_id, " now has ", crossed_wS.number_of_possible_words,
                      " possible words.")
                print("which are ", crossed_wS.current_possible_words)
                print("because its letters are ", crossed_wS.current_letters)

        self.update_grid()
        return True

    def print_current_grid_state(self):
        """ Print the current grid in the console (debug purposes)

        :return: None
        """
        for line in self.grid_array:
            print(line)
        return self.grid_array

    def create_grid_array(self):
        """ Create the grid array object from the grid code (conversion between text formalism and code formalism)

        :return: None
        """
        grid_array = [[] for i in range(self.h)]
        i = 0
        j = 0
        for letter_code in self.grid_code:
            if letter_code == "+":
                grid_array[i].append(".")
            elif letter_code.isalpha():
                grid_array[i].append(letter_code.lower())
            else:
                grid_array[i].append("$")
            j += 1
            if j == self.w:
                j = 0
                i += 1
        return grid_array

    def create_list_of_word_slots(self):
        """ Create all word slots objects (and put them in relevant lists) given the grid (called at init)

list_of_word_slots, temp_horizontal_word_slots_grid, temp_vertical_word_slots_grid
        :return list_of_word_slots: ([WordSlot]) list of created word slots
        :return temp_horizontal_word_slots_grid : ([int]) an array representing the grid with the WordSlot IDs in each
        # square (horizontal words only).
        :return temp_vertical_word_slots_grid : ([int]) same as above for vertical words
        """

        list_of_word_slots = []

        temp_horizontal_word_slots_grid = [["0" for x in range(self.w)] for y in range(self.h)]
        temp_vertical_word_slots_grid = [["0" for x in range(self.w)] for y in range(self.h)]

        # Going through the grid in hozirontal then vertical direction, finding word slots, computing their length
        # etc, to create the appropirate word slot objetcs.
        # Horizontal words
        word_slot_counter = 1
        for l in range(self.h):
            line = self.grid_array[l]
            len_of_current_word = 0
            initial_letters = []
            for e, el in enumerate(line):
                if el == "." or el.isalpha():
                    len_of_current_word += 1
                    initial_letters.append(el)
                if el == "$" or e == self.w - 1:
                    correctif = 1 if e == self.w - 1 and (el == "." or el.isalpha()) else 0
                    if len_of_current_word >= 2:
                        word_slot = WordSlot(identifiant=word_slot_counter, length=len_of_current_word,
                                             first_letter_position=[l, e - (len_of_current_word - correctif)],
                                             direction="horizontal", initial_letters=initial_letters)
                        list_of_word_slots.append(word_slot)
                        for e, slot in enumerate(word_slot.slots):
                            temp_horizontal_word_slots_grid[slot[0]][slot[1]] = str(word_slot_counter) + "." + str(e)
                        word_slot_counter += 1
                    len_of_current_word = 0

        # Vertical words
        for c in range(self.w):
            column = [x[c] for x in self.grid_array]
            len_of_current_word = 0
            initial_letters = []
            for e, ec in enumerate(column):
                if ec == "." or ec.isalpha():
                    len_of_current_word += 1
                    initial_letters.append(ec)
                if ec == "$" or e == self.h - 1:
                    correctif = 1 if e == self.h - 1 and (ec == "." or ec.isalpha()) else 0
                    if len_of_current_word >= 2:
                        word_slot = WordSlot(word_slot_counter, len_of_current_word,
                                             [e - (len_of_current_word - correctif), c], "vertical", initial_letters)
                        list_of_word_slots.append(word_slot)
                        for e, slot in enumerate(word_slot.slots):
                            temp_vertical_word_slots_grid[slot[0]][slot[1]] = str(word_slot_counter) + "." + str(e)
                        word_slot_counter += 1
                    len_of_current_word = 0

        return list_of_word_slots, temp_horizontal_word_slots_grid, temp_vertical_word_slots_grid
