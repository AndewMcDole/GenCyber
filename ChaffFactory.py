#!/usr/local/bin/python3

import random
import Hashing
from termcolor import colored, cprint


class ChaffFactory:

    def __init__(self):
        self.numberOfChaffs = 3 # Includes the one True message
        self.phrases = []

    def constructMessage(self, SECRET_KEY, delimeter):
        phrase = input ("Enter your correct message: ")
        phrase = phrase + delimeter + Hashing.get_hash_(phrase, str(SECRET_KEY)) + delimeter
        self.phrases.append(phrase)
        for x in range (self.numberOfChaffs - 1):
            phrase = input ("Enter a fake message: ")
            phrase = phrase + delimeter + Hashing.get_hash_(phrase, str(random.random() * SECRET_KEY)) + delimeter
            self.phrases.append(phrase)
        random.shuffle(self.phrases)
        phrase = ""
        for x in self.phrases:
            phrase += x
        return phrase

    def winnow(self, message, SECRET_KEY, delimeter):
        list = message.split(delimeter)
        line = ""
        for x in range(len(list)):
            if x % 2 == 0:
                line += list[x]
                line += " "
            else:
                line += list[x]
                hash_result = Hashing.check_hash(list[x - 1], list[x], str(SECRET_KEY))
                if hash_result:
                    line = line + " Hashes Match"
                    print (colored(line, "green"))
                else:
                    line = line + " Hashes Do Not Match"
                    print (colored(line, "red"))
                line = ""

    def compareStrings(self, str1, str2):
        str1 = str1.replace(" ", "")
        str2 = str2.replace(" ", "")
        if str1.lower() == str2.lower():
            # print ("Comparing {} and {}".format(str1.lower(), str2.lower()))
            return True
        return False

if __name__ == "__main__":
    cf = ChaffFactory()
    # print (cf.constructMessage())
    cf.winnow(cf.constructMessage())
