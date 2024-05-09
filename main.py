import re
import os

from visualizing_menu import VisualizingMenu
from timing_menu import M_Timing_menu
from connect_menu import Connect_menu
from menu import *
from param_menu import *
import json

class Main:

    def __init__(self):
        self.saved_measures = []

        self.timing_menu = M_Timing_menu(self)
        self.connect_menu = Connect_menu(self)
        self.param_menu = ParamMenu(self)
        self.visual_menu = VisualizingMenu(self)

        self.welcome()
        self.handle_input()


    def save(self):

        clear_terminal()
        print(f"{bcolors.HEADER}\t** Save **")
        print("enter file path")
        fpath = input(f"{bcolors.OKGREEN}>> ")

        while os.path.isdir(fpath):
            print(f"{bcolors.FAIL}this path is a directory, insert a valid file path")
            fpath = input(f"{bcolors.OKGREEN}>> ")

        extension = os.path.splitext(fpath)[-1]
        if extension != '.json':
            print(f"{bcolors.WARNING}warning, file extension is not json")
        with open(fpath, "w") as file:
            file.write(json.dumps(self.saved_measures))
        print(f"{bcolors.HEADER}file saved, enter any character to continue")
        input(f"{bcolors.OKGREEN}>> ")

        self.welcome()

    def load(self):

        clear_terminal()
        print(f"{bcolors.HEADER}\t** Load **")
        print()
        print(f"{bcolors.WARNING}warning, loaded scores with a name matching an already present name will be numbered")

        print(f"{bcolors.HEADER}enter file path")
        fpath = input(f"{bcolors.OKGREEN}>> ")

        while not os.path.exists(fpath) or os.path.isdir(fpath):
            print(f"{bcolors.FAIL}this path is invalid, it is either a directory or non existant, insert a valid file path")
            fpath = input(f"{bcolors.OKGREEN}>> ")

        extension = os.path.splitext(fpath)[-1]
        if extension != ".json":
            print(f"{bcolors.WARNING}warning, file extension is not json")

        with open(fpath, "r") as file:
            content = json.load(file)
            saved_keys = [measure["name"] for measure in self.saved_measures]
            for c in content:
                b = c.copy()
                if b["name"] in saved_keys: #if the name is already there, append a number to the new one

                    numbers = re.findall(r'(?<=-)\d+', b["name"]) # if the number was already there, increase it
                    if numbers is not []:
                        b["name"] = b["name"][:-len(numbers[-1])] + str(int(numbers[-1])+1)
                    else:
                        b["name"] = b["name"] + "-1"

                self.saved_measures.append(b)

        self.welcome()

    def print_title(self):
        clear_terminal()

        print(f"{bcolors.HEADER}\t*** Reaction speed measurement CLI ***")
        print("\n")

    def welcome(self):

        self.print_title()

        #print(f"for help insert : 'h'")
        print(f"to connect to the sensors insert : 'c'")
        print(f"to start insert : 'e'")
        print(f"to visualize the results insert : 'v'")
        print(f"to change timing settings insert : 't'")
        print(f"to change measurement parameters insert : 'p'")
        print(f"to save insert : 's'")
        print(f"to load insert : 'l'")

        if self.saved_measures is not []:
            print()
            for n, measure in enumerate(self.saved_measures):

                print(f"measure {n} | {measure['name']}")


        print("\n")

        self.handle_input()


    def handle_input(self):


        ins = input(f"{bcolors.OKGREEN}>> ")

        if ins == "t":
            self.timing_menu.print_menu()


        if ins == "c":
            self.connect_menu.print_menu()

        if ins == "e":
            self.connect_menu.start()

        if ins == "p":
            self.param_menu.print_menu()

        if ins == "s":
            self.save()

        if ins == "l":
            self.load()

        if ins == "v":
            self.visual_menu.print_menu()



        else:
            self.welcome()






main = Main()
