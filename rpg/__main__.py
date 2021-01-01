import os
import sys
import pickle
from .core import Game
from .utils import *

def main():
    if sys.stdout.isatty():
        clear()
    if os.path.isdir("save") and len(os.listdir("save")):
        while True:
            save_name = input_slow("Enter save name to be loaded: ")
            if save_name != "":
                if os.path.isfile(os.path.join("save", "save_" + save_name + ".rpg")):
                    with open(os.path.join("save", "save_" + save_name + ".rpg"), "rb") as f:
                        save = pickle.load(f)
                    save.mainloop()
                    return
                print_slow("There is no save file named " + save_name + "!")
            else:
                break
    print_slow("Creating new world...\n")
    game = Game()
    game.mainloop()

if __name__ == "__main__":
    main()
    clear()
