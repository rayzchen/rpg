import os
import sys
import pickle
from .core import Game
from .utils import *

def main():
    # save_folder = os.path.expandvars(os.path.join("%localappdata%", "RPG", "saves"))
    save_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "save")
    if sys.stdout.isatty():
        clear()
    if os.path.isdir(save_folder) and len(os.listdir(save_folder)):
        while True:
            save_name = input_slow("Enter save name to be loaded: ")
            if save_name != "":
                if os.path.isfile(os.path.join(save_folder, "save_" + save_name + ".rpg")):
                    with open(os.path.join(save_folder, "save_" + save_name + ".rpg"), "rb") as f:
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
