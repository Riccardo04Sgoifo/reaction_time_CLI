import time

import serial
from menu import *

START_LOOP = 's'.encode('utf-8')
REACTION_TIME_PRINT = 'r'.encode('utf-8')
FINISHED = 'f'.encode('utf-8')
COPY = 'k'.encode('utf-8')
END_PRINT = 'e'.encode('utf-8')
BREAK_LOOP = 'b'.encode('utf-8')
STIMULATION_MODE_BOTH = 'b'.encode('utf-8')
STIMULATION_MODE_VISUAL = 'v'.encode('utf-8')
STIMULATION_MODE_AUDITORY = 'a'.encode('utf-8')
# for comunication with esp
COMBINED_MODE = 0  # both audio and visual
VISUAL_MODE = 1    # use LEDs
AUDIO_MODE = 2     # use buzzer

ACTIVE_SENSOR = 'l'.encode('utf-8')

REACTION_TIME_MESSAGE_LENGTH = 5
INSTRUCTION_MESSAGE_LENGTH = 12
ACTIVE_SENSOR_MESSAGE_LENGTH = 2

class CommunicatorWorker(threading.Thread):
    def __init__(self, root, name="sensor-comm-thread"):
        super().__init__(name=name, daemon=True)

        self.root = root
        self.print_error = self.root.print_error
        self.device = self.root.device
        self.is_connected = False
        self.shallStop = False
        self.has_thread_started = False
        self.is_running = False

        self.outside_settings = {
            "start_delay": 0,
            "min_interval": 1000,  # if it's not random, just set them to the same value
            "max_interval": 1000,
            "stimulation_mode": 0,
            "attempts_count": 10,

        }
        self.score_lines = []



    def run(self) -> None:
        self.is_running = True
        self.doWork() # like this i don't have to put is_running = False to every exit point
        self.is_running = False

    def doWork(self):


        self.score_lines = [] #_empty score lines

        self.has_thread_started = True # prevent starting two times the thread

        # check if board is open
        if not self.device.is_open:
            self.print_error("tried to start the loop without connection to the board")
            return

        # start on esp8266

        time.sleep(self.outside_settings["start_delay"] / 1000)  # waitid_result the starting delay in ms

        while self.device.in_waiting:  # empty what was there
            self.device.read()

        dataToSendBytes = self.getMessage(START_LOOP, self.outside_settings["min_interval"],
                                          self.outside_settings["max_interval"],
                                          self.outside_settings["stimulation_mode"],
                                          self.outside_settings["attempts_count"], 4)  # TODO lightnum is useless

        self.device.write(dataToSendBytes)

        t = time.time()
        while not self.device.in_waiting:
            if time.time() - t > 0.1:  # after 100 ms there is no response
                self.print_error("Time out while waiting for a response on start")
                return
        time.sleep(0.01)  # wait 10ms for the esp to write everything

        data_received = bytearray()
        while self.device.in_waiting:
            data_received += self.device.read()

        if data_received[0].to_bytes(1, "big") != COPY:  # ok code
            self.print_error(f"can't start loop on esp8266\n\n{data_received}\n")
            return

        # everything went well up to here so the attempt is started

        # disables start button and enables stop button

        run = True
        i = 0


        while run:

            if self.shallStop:
                self.shallStop = False
                run = False

                # stop, set mode to visual to hopefully stop the noise
                stopMessageBytes = self.getMessage(BREAK_LOOP, 0, 0, VISUAL_MODE, 0, 0)

                self.device.write(stopMessageBytes)

                t = time.time()
                while not self.device.in_waiting:
                    if time.time() - t > 0.1:  # after 100 ms there is no response
                        self.print_error("Time out while waiting for a response")
                        return
                time.sleep(0.01)

                data_received = bytearray()

                data_received = bytearray()
                while self.device.in_waiting:
                    data_received += self.device.read()

                if data_received[0].to_bytes(1, "big") != COPY:  # ok code
                    self.print_error(f"can't stop loop on esp8266\n\n{data_received}\n")
                    self.attemptFinished()  # tell mainLogic that the attempt is finished (not in the best way)
                    return
                break

            # wait for a response
            t = time.time()
            while not self.device.in_waiting:
                if time.time() - t > 10:  # after 10 s there is no response
                    self.print_error("Time out while waiting for a response")
                    return
            time.sleep(0.01)

            data_received = self.device.read(1)

            # qDebug() << QString("command is %1").arg(dataReceived[0]);

            if data_received[0].to_bytes(1, "big") == REACTION_TIME_PRINT:
                # qDebug() << "Into the loop..."
                while self.device.in_waiting < REACTION_TIME_MESSAGE_LENGTH - 1:
                    time.sleep(0.0001)  # wait for 4 bytes (reaction time unsigned int)

                # qDebug() << "Out of the loop!"
                data_received = self.device.read(REACTION_TIME_MESSAGE_LENGTH - 1)
                # qDebug() << dataReceived[0];
                # qDebug() << dataReceived[1];
                # qDebug() << dataReceived[2];
                # qDebug() << dataReceived[3];

                # char *dr = new char[REACTION_TIME_MESSAGE_LENGTH - 1] {0};
                # qDebug() << "reaction time:";

                # qDebug() << serial->read(dr, REACTION_TIME_MESSAGE_LENGTH - 1);
                dr = data_received

                reactionTime = 0

                reactionTime |= dr[0]
                reactionTime <<= 8
                reactionTime |= dr[1]
                reactionTime <<= 8
                reactionTime |= dr[2]
                reactionTime <<= 8
                reactionTime |= dr[3]

                i += 1

                self.addScore(f"attempt {i}:  {reactionTime}ms")


            elif data_received[0].to_bytes(1, "big") == FINISHED:
                self.print_error("received finish signal")
                run = False


            elif data_received[0].to_bytes(1, "big") == ACTIVE_SENSOR:
                # don't care about this with a CLI
                """dataReceived = QByteArray();
                while (serial->bytesAvailable() < ACTIVE_SENSOR_MESSAGE_LENGTH - 1) { }
                dataReceived = serial->read(ACTIVE_SENSOR_MESSAGE_LENGTH - 1);

                unsigned char* msg = new unsigned char[ACTIVE_SENSOR_MESSAGE_LENGTH - 1];
                std::memcpy(msg, dataReceived.constData(), ACTIVE_SENSOR_MESSAGE_LENGTH - 1);

                uint8_t activeSensor = msg[0];

                delete[] msg;

                emit lightChanged((int) activeSensor + 1); // removing one the second light was mapped to the first, the third to the second..."""


            else:

                while self.device.in_waiting:
                    data_received += self.device.read()
                # for some astrological reason random stuff get sent but ignoring it works...
                # self.print_error(f"Unrecognized command {data_received[0].to_bytes(1, 'big')}, followed by:\n\n{data_received}\n")

        # tell mainLogic that the attempt is finished
        self.attemptFinished()

    def getMessage(self, command: bytes, from_: int, to_: int, mode: int, attempts: int, sensors: int) -> bytearray:

        data = bytearray()

        data += command
        data += from_.to_bytes(4, byteorder="big")  # big endian
        data += to_.to_bytes(4, byteorder="big")
        data += mode.to_bytes(1, byteorder="big")
        data += attempts.to_bytes(1, byteorder="big")
        data += sensors.to_bytes(1, byteorder="big")

        return data

    def attemptFinished(self):
        return

    def addScore(self, score: str):
        self.score_lines.append(score)



class MeasureSaver(Menu):
    def __init__(self, root):
        super().__init__()
        self.root = root

        self.actions = {
            "discard" : self.discard,
            "save" : self.save,
        }

        self.settings = {
            "name" : None
        }

        self.settings_specs = {
            "name" : {"data_type" : str}
        }

    def save(self):

        if self.settings["name"] is None:
            self.root.print_error("modify the name setting before saving")
            self.print_menu()
            return
        else:
            self.root.root.root.saved_measures.append({"name": self.settings["name"], "score_lines" : self.root.comm_thread.score_lines})
            self.root.root.root.welcome()

    def print_grid(self, tab):
        for k in tab.keys():
            print(f"{k} | {tab[k]}")

    def print_additional_menu(self):
        print()
        self.print_grid(self.settings)

    def discard(self):

        self.print_title()
        print(f"{bcolors.WARNING}are you sure you want to discard?\ndiscarded measurement will be unrecoverable")
        print(f"{bcolors.HEADER}\nto discard insert : 'Y'")
        print("to go back insert : any character")

        text = input(f"{bcolors.OKGREEN}>> ")
        if text != 'Y':
            self.print_menu()
            return
        else:
            self.root.comm_thread.score_lines = []
            self.root.root.root.welcome()


class Communicator9000(Menu):
    def __init__(self, root):
        super().__init__()
        self.root = root

        #self.is_running = True # used to run the non blocking serial interface with sensors while they're active
        self.is_connected = False
        self.device = None

        self.comm_thread = CommunicatorWorker(self)
        self.saver = MeasureSaver(self)


        self.actions = {}

        self.outside_settings = {
            "start_delay": 0,
            "min_interval": 1000,  # if it's not random, just set them to the same value
            "max_interval": 1000,
            "stimulation_mode": 0,
            "attempts_count": 10,

        }


    def update_enabled_options(self):
        # don't need to disable/enable much stuff here
        if self.comm_thread.is_running:
            self.actions["break"] = self.stop
            if "continue (save or discard)" in self.actions.keys():
                self.actions.pop("continue (save or discard)")

        else:
            if "break" in self.actions.keys():
                self.actions.pop("break")
            self.actions["continue (save or discard)"] = self.saver.print_menu

    def stop(self):
        if self.comm_thread.is_running:
            self.comm_thread.shallStop = True
        self.root.root.welcome()

    def connect_to_device(self, device):

        try :
            self.device = serial.Serial(
                device,
                9600,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=0.1
            )
            self.is_connected = True
        except serial.SerialException:
            self.print_error("connection has failed")
            self.is_connected = False

   # def connect_to_device(self, device):
   #     self.comm_thread.connect_to_device(device)
   #     self.is_connected = self.comm_thread.is_connected


        print(f"urpo {device}")

    def print_error(self, error):
        clear_terminal()

        print(f"{bcolors.HEADER}\t** Communicator9000 **")
        print("\n")
        print(f"{bcolors.FAIL}{error}")
        print()
        print(f"{bcolors.HEADER}enter any character to continue:")
        input(f"{bcolors.OKGREEN}>> ")


    def disconnect(self):
        if self.device is not None and self.is_connected:
            self.device.close()
            self.is_connected = False
        else:
            self.print_error("no device was connected")

    # def disconnect(self):
    #     self.comm_thread.disconnect()
    #     self.is_connected = self.comm_thread.is_connected



    def attemptFinished(self):
        return

    def print_additional_menu(self):
        print()
        for line in self.comm_thread.score_lines:
            print(line)


    def doWork(self):


        self.comm_thread = CommunicatorWorker(self)
        # get the settings from the menus, not really nice the root.root.root....
        self.outside_settings["start_delay"] = self.root.root.timing_menu.settings["start_delay"]
        if self.root.root.timing_menu.settings["is_random"]:
            self.outside_settings["min_interval"] = self.root.root.timing_menu.settings["min_interval"]
            self.outside_settings["max_interval"] = self.root.root.timing_menu.settings["max_interval"]
        else:
            self.outside_settings["min_interval"] = self.root.root.timing_menu.settings["interval"]
            self.outside_settings["max_interval"] = self.root.root.timing_menu.settings["interval"]

        self.outside_settings["stimulation_mode"] = self.root.root.param_menu.settings["stimulation_mode"]
        self.outside_settings["attempts_count"] = self.root.root.param_menu.settings["attempts_count"]

        self.comm_thread.outside_settings = self.outside_settings

        self.comm_thread.start()
        # if not self.comm_thread.has_thread_started:
        #     self.comm_thread.start()
        # else:
        #     self.comm_thread.run()
        # self.print_error("after? if before ok")
        self.print_menu()


