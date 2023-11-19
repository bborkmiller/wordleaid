class WordleAid:
    """
    Functions to help solve the Wordle puzzle, without solving it for you.

    Attributes
    ----------
    output_style : {'blocks', 'alpha'}
        Sets the output of the `compare_words` function to either colored emoji
        blocks or text (_?Y)

    default_word_list : {True, False}
        True (the default) will load the built-in list of accepted Wordle words
    """

    def __init__(self, output_style="blocks", default_word_list=True):
        output_style = output_style.lower()
        if output_style not in ["alpha", "blocks"]:
            raise ValueError("Style parameters must be either 'alpha' or 'blocks'")

        self.YES = ["Y", "🟩"]
        self.MAYBE = ["?", "🟨"]
        self.NO = ["_", "⬛", "⬜"]

        if output_style == "blocks":
            self.Y_DISPLAY = "🟩"
            self.M_DISPLAY = "🟨"
            self.N_DISPLAY = "⬛"
        elif output_style == "alpha":
            self.Y_DISPLAY = "Y"
            self.M_DISPLAY = "?"
            self.N_DISPLAY = "_"

        if default_word_list:
            self.load_word_list()

    def load_word_list(self, f="accepted_words.txt"):
        with open("accepted_words.txt") as f:
            self.accepted_words = f.read().splitlines()

    def compare_words(self, guess, wordle):
        """
        Compare two words according to Wordle rules and return the result.

        Wordle Rules:
            Right letter, right position: 🟩
            Wrong letter: ⬛
            Right letter, wrong position: 🟨
                ~ unless the same letter in the other position(s) is already green ~
                ~ For example: SLOSH compared to SHUNT should yield 🟩⬛⬛⬛🟨,
                            not 🟩⬛⬛🟨🟨

        Parameters
        ----------
        guess : str
            The "guessed" word.
        wordle : str
            The Wordle word. (In reality, the guess and wordle can be in any order)

        Returns
        -------
        str
            The tilestring resulting from the comparison of `guess` and `wordle`.
            The tilestring's format will depend on the output_style setting of the
            class.
        """

        if len(guess) != 5 or len(wordle) != 5:
            raise ValueError(
                f"`guess` and `wordle` must both be 5-character strings. Received '{guess}' and '{wordle}.'"
            )

        tiles = ""
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
        """
        Find eligible words, given a set of known information

        Identifies the words in a list of words that are still eligible solutions, given a set
        of known results from past guesses.

        Parameters
        ----------
        known_info : list of tuples
            A list containing one or more comparisons of guessed words to the Wordle,
            in the format [('word1', 'tilestring1'), ... ('wordn', 'tsn')].
        wordlist : list of str
            The list of candidates. By default this will use the built-in list of all
            the accepted Wordle answers.

        Returns
        -------
        list
            The list of words (if any) that satisfy the provided set of comparisons.
        """

        if wordlist is None:
            wordlist = self.accepted_words

        for i in known_info:
            wd, ts = i
            if len(wd) !=5 or len(ts) !=5:
                raise ValueError(f"The known info list can only contain 5 character strings. Received {i}.")

        # Get a list of all the green letters that have been found so far so that
        # we can do a proper check of black tiles. A black tile could mean either
        # a) that letter does not exist in the word b) it does, but in a different
        # (green) square
        green_letters = [None] * 5
        for guessed_word, tilestring in known_info:
            for i, (l, tile) in enumerate(zip(guessed_word, tilestring)):
                if tile in self.YES:
                    green_letters[i] = l

        candidates = []
        # Loop through the words we want to compare to the known info
        for word in wordlist:
            qualified = True
            # Loop through the known info
            for guessed_word, tilestring in known_info:
                # Loop through the letter positions in this word/tilestring
                for i, tile in enumerate(tilestring):
                    # Candidate doesn't have a 🟩 letter in the proper position
                    if tile in self.YES and word[i] != guessed_word[i]:
                        qualified = False
                        break
                    # Candidate contains a ⬛ letter, unless it's also a 🟩 letter in the right spot
                    elif (
                        tile in self.NO
                        and guessed_word[i] in word
                        and not (
                            guessed_word[i] in green_letters
                            and word[green_letters.index(guessed_word[i])]
                            == guessed_word[i]
                            and not word[i] == guessed_word[i]
                        )
                    ):
                        qualified = False
                        break
                    # Candidate does not contain a 🟨 letter, or it's in the same (wrong) spot
                    elif tile in self.MAYBE and (
                        guessed_word[i] not in word or guessed_word[i] == word[i]
                    ):
                        qualified = False
                        break
                # If this word has been disqualified, we can break out of the loop
                if not qualified:
                    break
            if qualified:
                candidates.append(word)

        return candidates
