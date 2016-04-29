__author__ = "roman.subik"


class Phrase():
    def __init__(self):
        self.allowed_words = [
            ["giant", "squealing", "empowered", "frowning", "starving", "violet", "astonishing", "lurking",
             "nice"],

            ["drunk", "sober", "raging", "fearless", "dignified", "straight", "wise", "coarse", "confused"],

            ["dog", "ox", "fox", "penguin", "cat", "lynx", "aurochs", "panda", "sparrow", "squirell", "alpaka",
             "ram", "panda"]
        ]

    def matches(self, phrase):
        words = phrase.split(" ")

        if len(words) != len(self.allowed_words):
            return False

        for i in range(0, len(self.allowed_words)):
            if words[i] not in self.allowed_words[i]:
                return False

        return True
