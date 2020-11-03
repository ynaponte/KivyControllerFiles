from kivy.app import App
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.properties import ObjectProperty
from random import randint


class PageOne(Widget):

    pass


class UpdateLeds(Widget):

    led = []

    interval = None

    def schedule(self):

        self.led = [self.ids["led1"], self.ids["led2"], self.ids["led3"]]

        self.interval = Clock.schedule_interval(self.update_led_state, 1/20)

    def update_led_state(self, *args):

        led_state = [randint(0, 1), randint(0, 1), randint(0, 1)]
        print(led_state)
        for i in range(0, 3):

            if led_state[i] != 0:

                self.led[i].basecolor = [0, 1, 0, 1]

            else:

                self.led[i].basecolor = [0, 0, 0, 1]


class ControlApp(App):

    def build(self):

        return UpdateLeds()


if __name__ == "__main__":

    ControlApp().run()
