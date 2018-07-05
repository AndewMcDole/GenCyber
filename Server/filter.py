import os
import sys
import pickle

def main(argv):
    currDir = os.getcwd()
    path = os.path.join(currDir, ".badwords.txt")
    wordfile = open(path, "r")
    list = []
    for line in wordfile:
        list.append(line.strip("\n").encode("cp037"))

    pickle.dump(list, open(".words.txt", "wb"))


if __name__ == "__main__":
    main(sys.argv)
