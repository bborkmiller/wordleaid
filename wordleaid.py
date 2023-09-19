class WordleAid:
    def __init__(self, output_style="blocks", default_word_list=True):
        #self.input_style = input_style.lower()
        output_style = output_style.lower()

        # if self.input_style not in ['alpha', 'blocks']:
        #     raise ValueError("Style parameters must be either 'alpha' or 'blocks'")
        if output_style not in ['alpha', 'blocks']:
            raise ValueError("Style parameters must be either 'alpha' or 'blocks'")
        
        self.YES = ['Y', '🟩']
        self.MAYBE = ['?', '🟨']
        self.NO = ['_',  '⬛', '⬜']
                
        if output_style == 'blocks':
            self.Y_DISPLAY = '🟩'
            self.M_DISPLAY = '🟨'
            self.N_DISPLAY = '⬛'
        elif output_style == 'alpha':
            self.Y_DISPLAY = 'Y'
            self.M_DISPLAY = '?'
            self.N_DISPLAY = '_'

        if default_word_list:
            self.load_word_list()

    def load_word_list(self, f='accepted_words.txt'):
        with open('accepted_words.txt') as f:
            self.accepted_words = f.read().splitlines()

    def compare_words(self, guess, wordle):
        '''
        Compares two words according to the Wordle rules and returns the appropriate tilestring

        Rules:
            Right letter, right position: 🟩
            Wrong letter: ⬛
            Right letter, wrong position: 🟨
                ~ unless the same letter in the other position(s) is already green ~
                ~ For example: SLOSH compared to SHUNT should yield 🟩⬛⬛⬛🟨,
                            not 🟩⬛⬛🟨🟨

        Accepts two words, returns a string
        '''

        tiles = ''
        pairs = list(zip(wordle, guess))
        for w, g in pairs:
            if w == g:
                tiles += self.Y_DISPLAY
            elif [p for p in pairs if p[0] == g and p[1] != g]:
                tiles += self.M_DISPLAY
            else:
                tiles += self.N_DISPLAY

        return tiles
    
    def find_candidates(self, known_info, wordlist=None):
        '''
        Identifies the words in a list of words that are still eligible solutions, given a set
        of known results from past guesses

        Accepts a list of tuples with the form (guessed_word, tilestring)
        Returns a list of candidate words
        '''

        if wordlist is None:
            wordlist = self.accepted_words

        # Get a set of all the green letters that have been found so far so that
        # we can do a proper check of black tiles. A black tile could mean either
        # a) that letter does not exist in the word b) it does, but in a different
        # (green) square
        green_letters = set()
        for guessed_word, tilestring in known_info:
            for l, tile in zip(guessed_word, tilestring):
                if tile in self.YES:
                    green_letters.add(l)
        
        candidates = []
        # Loop through the words we want to compare to the known info
        for word in wordlist:
            qualified = True
            # Loop through the known info
            for guessed_word, tilestring in known_info:
                # Loop through the letter positions in this word/tilestring
                for i, tile in enumerate(tilestring):
                    if tile in self.YES and word[i] != guessed_word[i]:
                        qualified = False
                        break
                    elif tile in self.NO and guessed_word[i] in word and guessed_word[i] not in green_letters:
                        qualified = False
                        break
                    elif tile in self.MAYBE:
                        if guessed_word[i] not in word:
                            qualified = False
                            break
                        elif guessed_word[i] == word[i]:
                            qualified = False
                            break
                # If this word has been disqualified, we can break out of the loop
                if not qualified:
                    break
            if qualified:
                candidates.append(word)

        return candidates