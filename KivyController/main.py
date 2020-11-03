from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock
import serial as ser
import json


class Gerenciador(ScreenManager):
    pass


class PrincipalPage(Screen):
    pass


class ConfigPage(Screen):
    pass


class Comms:

    porta = str()

    def __init__(self, **kwargs):
        self.comportName = ""
        self.baud = 9600
        self.timeout = 0.4
        self.isopen = False
        self.serialport = ser.Serial()

    def serial_read(self):  # Automation for filtering information received from arduino
        byte = self.serialport.readline()
        decoded = str(byte[0:len(byte) - 2].decode())  # decodes serial data until "\n"

        if decoded != "":
            return decoded.split(',')
        else:
            return self.serial_read()

    def open_port(self, portname):
        if not self.isopen:
            self.serialport.port = portname
            self.serialport.baudrate = self.baud
            self.serialport.timeout = self.timeout

            try:
                self.serialport.open()
                self.isopen = True

            except:
                print("Error while opening serial port")

    @staticmethod
    def com_test(test_port):  # if possible to initiate object returns true and allows to proceed
        try:
            test = ser.Serial(port=test_port.upper(), baudrate=9600, timeout=1)
            return True
        except ser.SerialException:
            return False


comunic = Comms()


class PrincipalWidget(Widget):
    # Objects for communication within kivy and python
    consumo = ObjectProperty()
    arcond = ObjectProperty()
    tv = ObjectProperty()
    lampada = ObjectProperty()
    chuv = ObjectProperty()
    gelad = ObjectProperty()
    tempo = ObjectProperty()

    # Dict responsible for getting the specified powers from json file
    power = dict()

    # misc variables
    con = float()
    control = dict()
    function_interval = None
    # Responsible for getting what devices are on from arduino
    dispositivos_online = []

    def start_sim(self):
        # preparing to initiate. Setting everything to zero
        self.con = 0.0
        self.consumo.text = "0.0"

        # Generating power dict from json file
        json_file = open("consumo.json", "r")
        potencias = json.load(json_file)
        self.power = potencias.copy()
        json_file.close()

        # generating control dict according to user input in the Kivy GUI
        self.control = {
            "a": self.arcond.text,
            "l": self.lampada.text,
            "c": self.chuv.text,
            "g": self.gelad.text,
            "t": self.tv.text,
            "0": "A"
        }

        # Initiating simulation
        self.function_interval = Clock.schedule_interval(self.update_consumo, 0.5)
        # The button doesn't operates the simulation method directly.
        # It schedules an interval to call the sim. Will stay on until "stop_sim" is called.

    def stop_sim(self):  # Stops the simulation canceling function_intervval
        try:
            self.function_interval.cancel()
        except AttributeError:
            pass

    def update_consumo(self, *args):

        for powered in self.dispositivos_online:
            try:
                self.con += (self.power[powered][self.control[powered]]) / (float(self.tempo.text) * 120)
                # values of consumption is raised by accessing the "power dict" that was created in "start_sim" method

            except KeyError:

                self.function_interval.cancel()
                break

            except ValueError:
                self.function_interval.cancel()
                break

        self.consumo.text = f"{self.con:.1f}"

    def update_text_box(self, value):  # method utilized for automation of text boxes with buttons "A B C"
        # Only one value is passed through therefore the next "for" updates text in "text_inputs"
        # They are the ones whom control the simulation not the buttons.

        for i in (self.arcond, self.chuv, self.gelad, self.lampada, self.tv):
            i.text = value

    @staticmethod
    def update_devices(*args):
        PrincipalWidget.dispositivos_online = comunic.serial_read()


class ConfigWidget(Widget):  # Class that contains logical and graphical info from config page

    possivel = 0  # Controls screen changes whenever is possible to establish comm with arduino.

    error_msg = ObjectProperty()
    comm_input = ObjectProperty()  # Receives user input of what port should be used

    def analyser(self):  # Tests if its possible to initiate by calling com_test
        if Comms.com_test(test_port=self.comm_input.text):
            self.error_msg.text = ""
            global comunic
            port_name = self.comm_input.text
            comunic.open_port(port_name)

            self.possivel = 1
            Clock.schedule_interval(PrincipalWidget().update_devices, 1/40)
            MaqueteIterativa().schedule()

        else:
            self.error_msg.text = "Porta invalida!"
            self.possivel = 0


class IteractiveImage(FloatLayout):  # Class that contains the logic to change color

    # All of the LED objects
    leds = []

    interval = None

    def schedule(self):
        print("entrou no schedule")
        self.leds = [self.ids.gel, self.ids.lamp1, self.ids.lamp2, self.ids.ar1, self.ids.chuv, self.ids.lamp3,
                     self.ids.lamp4, self.ids.lamp5, self.ids.ar2, self.ids.tv1, self.ids.tv2]

        self.interval = Clock.schedule_interval(self.update_image, 1 / 20)
        print(self.leds)

    def update_image(self, *args):
        print("entrou no update image")
        led_state = PrincipalWidget.dispositivos_online
        for i in range(0, 11):
            if led_state[i] != 0:

                self.leds[i].basecolor = [0, 1, 0, 1]

            else:
                self.leds[i].basecolor = [0, 0, 0, 1]


class ControllerApp(App):

    def build(self):

        return Gerenciador()


if __name__ == '__main__':
    ControllerApp().run()
