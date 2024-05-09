
from menu import *
from serial.tools import list_ports
from communicator import Communicator9000

class Connect_menu(Menu):
    def __init__(self, root):
        super().__init__()
        self.root = root

        self.title = "Connect menu"

        self.actions = {
            "return to main menu" : self.root.welcome,
            "scan for available devices" : self.scan_devices,
            "connect to a device" : self.connect_to_device,
            "disconnect" : self.disconnect,
        }

        self.available_devices = []
        self.selected_device = None
        self.communicator = Communicator9000(self)

    def scan_devices(self):
        self.available_devices = list_ports.comports()

    def print_additional_menu(self):

        if len(self.available_devices) > 0:
            for device in self.available_devices:
                print(f"{device.name} | {device.description}")
            print()

        if self.selected_device is not None:
            print(f"\nselected device: {self.selected_device.name}")
            print()


        print("state : " + (bcolors.OKGREEN + "connected") if self.communicator.is_connected else (bcolors.FAIL + "not connected"))
        print()

    def disconnect(self):
        self.selected_device = None
        self.communicator.disconnect()

    def start(self):
        if self.selected_device is not None and self.communicator.is_connected:
            self.communicator.doWork()
            self.communicator.print_menu()


        else:
            self.communicator.print_error("cannot start when not connected")

        self.root.welcome() # in each case, return to main menu


    def connect_to_device(self):

        self.print_title()

        print("to return to connect menu insert : '0'")


        if len(self.available_devices) == 0:
            print("no available devices, try scanning for available devices")
            print()

        else:
            for n, dev in enumerate(self.available_devices):
                print(f"to connect to {dev.name} insert : '{n + 1}'")

        # request an input now

        def get_selected_dev():
            inp = input(f"{bcolors.OKGREEN}>> ")

            if inp.lower().strip() == "exit":
                return 0 # exit will do the same as return to connect menu

            int_part = (re.findall("\d+", inp) + [""])[0]
            if int_part == "":
                print("that's not a number")
                return -1
            num = int(int_part)
            if 0 <= num <= len(self.available_devices):
                return num # number is in range so it's good
            else:
                print("number not in range")
                return -1 # bad

        num = get_selected_dev()
        while num == -1: # 0 is still to return to main
            num = get_selected_dev() # ask until you get a valid number

        if num == 0:

            self.print_menu()
        else:
            self.selected_device = self.available_devices[num - 1]
            self.communicator.connect_to_device(self.selected_device.name)






