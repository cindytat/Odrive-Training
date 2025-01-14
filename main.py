import os
import sys

# os.environ['DISPLAY'] = ":0.0"
# os.environ['KIVY_WINDOW'] = 'egl_rpi'

from kivy.app import App
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty

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

    def switch_screen(self):
        SCREEN_MANAGER.transition.direction = "right"
        SCREEN_MANAGER.current = MAIN_SCREEN_NAME

    def trapezoid(self):
        print("Trapezoid")
        ax.set_rel_pos_traj(float(self.target.text), float(self.acceleration.text), float(self.velo.text), float(self.deceleration.text))

    acceleration = ObjectProperty(None)
    deceleration = ObjectProperty(None)
    target = ObjectProperty(None)
    velo = ObjectProperty(None)


class GPIOScreen(Screen):
    """
    Class to handle the GPIO screen and its associated touch/listening events
    """

    def switch_screen(self):
        SCREEN_MANAGER.transition.direction = "left"
        SCREEN_MANAGER.current = MAIN_SCREEN_NAME


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