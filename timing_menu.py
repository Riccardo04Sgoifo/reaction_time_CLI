
from menu import *
import re

class M_Timing_menu(Menu):
    def __init__(self, root):
        super().__init__()
        self.root = root

        self.title = "Timing menu"

        self.actions = {
            "return to main menu" : self.root.welcome,
        }

        self.settings = {
            "start_delay" : 3000,
            "interval" : 1000,
            "is_random" : False,
        }

        self.settings_specs = {
            "start_delay": {"data_type":int, "range_min":0, "range_max":20000},
            "interval": {"data_type":int, "range_min":0, "range_max":20000},
            "is_random": {"data_type":bool, "enables": ["min_interval", "max_interval"], "disables": ["interval"]},
            "min_interval" : {"data_type":int, "range_min":0, "range_max":20000},
            "max_interval" : {"data_type":int, "range_min":0, "range_max":20000},
        }

        self.hidden_settings = { # all available settings
            "start_delay": 3000,
            "interval": 1000,
            "is_random": False,
            "min_interval" : 500,
            "max_interval" : 1500,
        }


    def print_additional_menu(self):
        super().print_additional_menu()

        self.print_grid(self.settings)
        print()


    def print_grid(self, tab):

        for k in tab.keys():
            print(f"{k} | {tab[k]}")


