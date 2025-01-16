import os
import sys

#from adafruit_blinka.microcontroller.atheros.ar9331.pin import GPIO_1
# os.environ['DISPLAY'] = ":0.0"
# os.environ['KIVY_WINDOW'] = 'egl_rpi'

from kivy.app import App
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from kivy.clock import Clock
from dpea_odrive.odrive_helpers import digital_read

from pidev.MixPanel import MixPanel
from pidev.kivy.PassCodeScreen import PassCodeScreen
from pidev.kivy.PauseScreen import PauseScreen
from pidev.kivy import DPEAButton
from pidev.kivy import ImageButton

from dpea_odrive.odrive_helpers import *

sys.path.append("/home/soft-dev/Documents/dpea-odrive/")
from dpea_odrive.odrive_helpers import *
MIXPANEL_TOKEN = "x"
MIXPANEL = MixPanel("Project Name", MIXPANEL_TOKEN)

SCREEN_MANAGER = ScreenManager()
MAIN_SCREEN_NAME = 'main'
TRAJ_SCREEN_NAME = 'traj'
GPIO_SCREEN_NAME = 'gpio'
ADMIN_SCREEN_NAME = 'admin'


class ProjectNameGUI(App):
    """
    Class to handle running the GUI Application
    """

    def build(self):
        """
        Build the application
        :return: Kivy Screen Manager instance
        """
        return SCREEN_MANAGER


Window.clearcolor = (1, 1, 1, 1)  # White


class MainScreen(Screen):
    """
    Class to handle the main screen and its associated touch events
    """
    def Toggle_CC_CCW(self):
        print("Word?")
        ax.set_vel(0)
        ax.wait_for_motor_to_stop()
        ax.set_relative_pos(5)
        ax.wait_for_motor_to_stop()
        ax.set_relative_pos(-5)
        ax.wait_for_motor_to_stop()
        sleep(3)

    def velocity(self):
        #ax.set_vel(self.ids.velocity.value)
        print("work")
        ax.set_ramped_vel(self.ids.velocity.value, self.ids.accel.value)

    # def home(self):
    #     print("homing")
    #     # ax.home_with_endstop(1, .5, 2)  # Home with velocity 1 to sensor on GPIO Pin 2, then offset .5 rotations
    #     ax.home_without_endstop(1, .5)  # Home with velocity 1 until wall is hit, then offset .5 rotations
    #     print("Current Position in Turns = ", round(ax.get_pos(), 2))  # should be at 0.0

    def switch_to_traj(self):
        SCREEN_MANAGER.transition.direction = "left"
        SCREEN_MANAGER.current = TRAJ_SCREEN_NAME

    def switch_to_gpio(self):
        SCREEN_MANAGER.transition.direction = "right"
        SCREEN_MANAGER.current = GPIO_SCREEN_NAME


    def admin_action(self):
        """
        Hidden admin button touch event. Transitions to passCodeScreen.
        This method is called from pidev/kivy/PassCodeScreen.kv
        :return: None
        """
        SCREEN_MANAGER.current = 'passCode'


class TrajectoryScreen(Screen):
    """
    Class to handle the trajectory control screen and its associated touch events
    """
    acceleration = ObjectProperty(None)
    deceleration = ObjectProperty(None)
    target = ObjectProperty(None)
    velo = ObjectProperty(None)

    def switch_screen(self):
        SCREEN_MANAGER.transition.direction = "right"
        SCREEN_MANAGER.current = MAIN_SCREEN_NAME

    def trapezoid(self):
        print("Trapezoid")
        ax.set_rel_pos_traj(float(self.ids.target.text), float(self.ids.acceleration.text), float(self.ids.velo.text), float(self.ids.deceleration.text))

class GPIOScreen(Screen):
    """
    Class to handle the GPIO screen and its associated touch/listening events
    """
    def switch_screen(self):
        SCREEN_MANAGER.transition.direction = "left"
        SCREEN_MANAGER.current = MAIN_SCREEN_NAME

    def __init__(self, **kwargs):
        super(GPIOScreen, self).__init__(**kwargs)
        self.gpio_pin = 1
        self.motor_move_distance = 5  # Distance for the motor to move when triggered
        self.motor_speed = 10  # Speed at which the motor moves
        self.motor_acceleration = 5  # Acceleration for the motor
        self.motor_deceleration = 5  # Deceleration for the motor
        self.check_gpio_interval = 0.1
        self.motor_running = False

    def on_enter(self):
        ax.set_vel(10)
        Clock.schedule_interval(self.check_gpio_state, self.check_gpio_interval)

    def on_leave(self):
        Clock.unschedule(self.check_gpio_state)

    def check_gpio_state(self, dt):
        switch_state = digital_read(od, self.gpio_pin)

        if switch_state == 0:
            ax.set_vel(0)
        else:
            ax.set_vel(10)

    def start_motor(self):
        self.motor_running = True
        ax.set_rel_pos_traj(self.motor_move_distance, self.motor_acceleration, self.motor_speed, self.motor_deceleration)
    def stop_motor(self):
        self.motor_running = False

class AdminScreen(Screen):
    """
    Class to handle the AdminScreen and its functionality
    """

    def __init__(self, **kwargs):
        """
        Load the AdminScreen.kv file. Set the necessary names of the screens for the PassCodeScreen to transition to.
        Lastly super Screen's __init__
        :param kwargs: Normal kivy.uix.screenmanager.Screen attributes
        """
        Builder.load_file('AdminScreen.kv')

        PassCodeScreen.set_admin_events_screen(
            ADMIN_SCREEN_NAME)  # Specify screen name to transition to after correct password
        PassCodeScreen.set_transition_back_screen(
            MAIN_SCREEN_NAME)  # set screen name to transition to if "Back to Game is pressed"

        super(AdminScreen, self).__init__(**kwargs)

    @staticmethod
    def transition_back():
        """
        Transition back to the main screen
        :return:
        """
        SCREEN_MANAGER.current = MAIN_SCREEN_NAME

    @staticmethod
    def shutdown():
        """
        Shutdown the system. This should free all steppers and do any cleanup necessary
        :return: None
        """
        os.system("sudo shutdown now")

    @staticmethod
    def exit_program():
        """
        Quit the program. This should free all steppers and do any cleanup necessary
        :return: None
        """
        quit()


"""
Widget additions
"""

Builder.load_file('main.kv')
SCREEN_MANAGER.add_widget(MainScreen(name=MAIN_SCREEN_NAME))
SCREEN_MANAGER.add_widget(TrajectoryScreen(name=TRAJ_SCREEN_NAME))
SCREEN_MANAGER.add_widget(GPIOScreen(name=GPIO_SCREEN_NAME))
SCREEN_MANAGER.add_widget(PassCodeScreen(name='passCode'))
SCREEN_MANAGER.add_widget(PauseScreen(name='pauseScene'))
SCREEN_MANAGER.add_widget(AdminScreen(name=ADMIN_SCREEN_NAME))

"""
MixPanel
"""


def send_event(event_name):
    """
    Send an event to MixPanel without properties
    :param event_name: Name of the event
    :return: None
    """
    global MIXPANEL

    MIXPANEL.set_event_name(event_name)
    MIXPANEL.send_event()


if __name__ == "__main__":
    # send_event("Project Initialized")
    # Window.fullscreen = 'auto'
    od = find_odrive("207935A1524B")
    assert od.config.enable_brake_resistor is True, "Check for faulty brake resistor."
    ax = ODriveAxis(od.axis1)
    ax.set_gains()
    dump_errors(od)
    if not ax.is_calibrated():
        print("calibrating...")
        ax.calibrate_with_current_lim(10)
    ax.set_vel(0)
    ax.wait_for_motor_to_stop()
    ProjectNameGUI().run()