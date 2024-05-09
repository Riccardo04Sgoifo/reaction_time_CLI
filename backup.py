
class Timing_menu:
    def __init__(self, root):
        self.root = root

        self.settings = {
            "start_delay" : 0,
            "interval" : 0,
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
            "start_delay": 0,
            "interval": 0,
            "is_random": False,
            "min_interval" : 0,
            "max_interval" : 0,
        }


        return

    def print_title(self):

        clear_terminal()

        print(f"{bcolors.HEADER}\t** Timing menu **")
        print("\n")

    def print_timing_menu(self):

        self.print_title()

        print("to return to main menu insert : '0'") # this is always 0

        for n, key in enumerate(self.settings.keys()): # print all settings that can be modified
            print(f"to modify {key} insert : '{n+1}'") # 0 is return to menu

        print() # space

        """print("to return to main menu insert : '0'")
        print(f"to modify starting delay insert : '1'")
        print(f"to modify the measure interval insert : '2'")
        print(f"to switch interval randomness insert '3'")
        print()"""

        self.print_grid(self.settings)
        print('\n')

        self.handle_input()

    def update_enabled_options(self):

        # only bool type options can enable or disable stuff
        for setting_spec in self.settings_specs.keys():
            if not setting_spec in self.settings:
                continue # skip if the current setting is not enabled itself

            is_enables_there = "enables" in self.settings_specs[setting_spec].keys()
            is_disables_there = "disables" in self.settings_specs[setting_spec].keys()

            if is_enables_there or is_disables_there:
                enabled_options = {sett_ : "enables" for sett_ in self.settings_specs[setting_spec]["enables"] if is_enables_there}
                enabled_options |= {sett_ : "disables" for sett_ in self.settings_specs[setting_spec]["disables"] if is_disables_there}

                if self.settings_specs[setting_spec]["data_type"] != bool: # data type of enabling option should be bool
                    print(f"{bcolors.WARNING}warning: non bool value {setting_spec} used to enable options")



                activation = self.settings[setting_spec]# this must work as it has been checked previously if the current setting is enabled

                is_active_when_enabled = lambda x: True if x == "enables" else False# used to simplify th eif statement

                for setting in enabled_options.keys():
                    if setting not in self.settings_specs.keys():  # the setting was not found in the spec dictionary
                        print(f"{bcolors.WARNING}error: enabled setting {setting} not in setting_spec")
                        continue
                    elif is_active_when_enabled(enabled_options[setting]) == bool(activation): # in this case == is an xnor
                        # enable the setting
                        if setting not in self.settings.keys(): # if the setting isn't already enabled:
                            self.settings[setting] = self.hidden_settings[setting]

                    else: # then disable it
                        if setting in self.settings.keys():
                            self.hidden_settings[setting] = self.settings.pop(setting) # save for the future and remove it

    def request_setting_input(self, setting_name, input_specs):

        """

        :param setting_name:
        :param input_specs: {"data_type": type, "range_min": only if number, "range_max": only if number, "enables": enabled options list if bool, "disabled": disabled options list if bool}
        :return:
        """

        # check input_specs dict for typing errors
        for i in input_specs.keys():
            if i not in ["data_type", "range_min", "range_max"]:
                print(f"invalid input_specs dict key: {i}")

        self.print_title() # start fresh

        print(f"insert new {setting_name}:") #get input string to convert




        inp = input(">> ")
        if inp.lower().strip() == "exit": # exit if needed
                return

        to_float = lambda x: (re.findall("[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?", x)+[""])[0] # re expression to filter floats
        # + [""] is added to make this work when no number is inserted, so an empty array is returned and gives error when indexed

        if "data_type" not in input_specs.keys():
            print("missing data_type parameter!")
            return

        # same procedure for number types

        if input_specs["data_type"] == int or input_specs["data_type"] == float:
            rinp = to_float(inp)
            def check_num(num, specs):

                if num == "":
                    return 1
                fnum = float(num) # after che check this should always work
                if "range_min" in specs.keys():
                    if fnum < specs["range_min"]:
                        return 1

                if "range_max" in specs.keys():
                    if fnum > specs["range_max"]:
                        return 1

                return 0 # it's good

            while check_num(rinp, input_specs):
                print("number not in range, insert a new one")
                inp = input(">> ")
                if inp.lower().strip() == "exit":  # exit if needed, this is copied two times but a function wasn't possible beacause of the return statement
                    return
                rinp = to_float(inp)

            self.settings[setting_name] = input_specs["data_type"](rinp)

        elif input_specs["data_type"] == bool:
            value = str_to_bool(inp)

            self.settings[setting_name] = input_specs["data_type"](value)

        elif input_specs["data_type"] == str:

            self.settings[setting_name] = inp

        else:
            print("invalid data type")


    def print_grid(self, tab):

        for k in tab.keys():
            print(f"{k} | {tab[k]}")


    def handle_input(self):
        ins = input(">> ")

        def check_valid_modify_num(text):
            only_int = (re.findall("\d+", text) + [""])[0]
            if only_int == "":
                return False, -1
            num = int(only_int)
            if len(self.settings.keys()) >= num > 0:
                return True, num

            return False, -1

        valid_modify_num = check_valid_modify_num(ins) # have to do this before to not interfere with if - elif

        if ins == '0':
            self.root.welcome()

        elif valid_modify_num[0]:
            key = list(self.settings.keys())[valid_modify_num[1]-1]
            self.request_setting_input(key, self.settings_specs[key] )

            # after a setting has been modified enabled and disabled options must be updated
            self.update_enabled_options()

            self.print_timing_menu()

        else:
            self.print_timing_menu()


