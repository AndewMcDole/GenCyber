#!/usr/local/bin/python3

import random
import Hashing

SECRET_KEY = 123

class ChaffFactory:

    def __init__(self):
        self.numberOfChaffs = 3 # Includes the one True message
        self.phrases = []

    def constructMessage(self):
        phrase = input ("Enter your correct message: ")
        phrase = phrase + ";" + Hashing.get_hash_(phrase, str(SECRET_KEY)) + ";"
        self.phrases.append(phrase)
        for x in range (self.numberOfChaffs - 1):
            phrase = input ("Enter a fake message: ")
            phrase = phrase + ";" + Hashing.get_hash_(phrase, str(random.random() * SECRET_KEY)) + ";"
            self.phrases.append(phrase)
        random.shuffle(self.phrases)
        phrase = ""
        for x in self.phrases:
            phrase += x
        return phrase

    def winnow(self, message):
        list = message.split(";")
        line = ""
        for x in range(len(list)):
            if x % 2 == 0:
                line += list[x]
                line += " "
            else:
                line += list[x]
                line = line + " " + Hashing.check_hash(list[x - 1], list[x], str(SECRET_KEY))
                print (line)
                line = ""

if __name__ == "__main__":
    cf = ChaffFactory()
    # print (cf.constructMessage())
    cf.winnow(cf.constructMessage())
