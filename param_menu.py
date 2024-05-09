
from menu import *
from communicator import *


def print_grid(tab):

    for k in tab.keys():
        print(f"{k} | {tab[k]}")


class ParamMenu(Menu):
    def __init__(self, root):
        super().__init__()
        self.root = root

        self.title = "Measurement parameter menu"

        self.actions = {
            "return to main menu" : self.root.welcome,
        }

        self.settings = {
            "stimulation_mode": 0,
            "attempts_count": 10,
        }
        self.settings_specs = {
            "stimulation_mode" : {"data_type" : int, "range_min": 0, "range_max" : 2, "description" : f"enter {COMBINED_MODE} for COMBINED_MODE\nenter {VISUAL_MODE} for VISUAL_MODE\nenter {AUDIO_MODE} for AUDIO_MODE"},
            "attempts_count" : {"data_type" : int, "range_min" : 1, "range_max" : 200}
        }

    def print_additional_menu(self):
        super().print_additional_menu()

        print_grid(self.settings)
        print()
