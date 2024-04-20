#!/usr/bin/env python3
from __future__ import print_function
from inputs import DeviceManager, UnpluggedError, GamepadLED, SystemLED
import threading
import time
import click

"""
The GamePadController is a threading class that polls for the gamepad inputs (gamepad_state) by listening
to the gamepad's USB dongle plugged into the robot.
"""

class GamePadController(threading.Thread):
    '''Successfully tested with the following controllers:
            + Xbox One Controller connected using a USB cable (change xbox_one parameter to True for full 10 bit trigger information)
            + EasySMX wireless controller set to appropriate mode (Xbox 360 mode with upper half of ring LED illuminated - top two LED quarter circle arcs)
            + JAMSWALL Xbox 360 Wireless Controller (Sometimes issues would occur after inactivity that would seem to require unplugging and replugging the USB dongle.)

       Unsuccessful tests:
            - Xbox One Controller connected via Bluetooth
            - Xbox 360 Controller connected with an Insten Wireless Controller USB Charging Cable
            +/- VOYEE Wired Xbox 360 Controller mostly worked, but it had various issues including false middle LED button presses, phantom shoulder button presses, and low joystick sensitivity that made small motions more difficult to execute.
    '''

    def __init__(self, print_events=False, print_dongle_status = True):
        threading.Thread.__init__(self, name = self.__class__.__name__)
        self.print_events = print_events
        # self.is_gamepad_dongle = False
        self._i = 0
        self.print_dongle_status = print_dongle_status
        
        self.ros_logger = None

        self.lock = threading.Lock()
        # self.thread = threading.Thread(target=self.update,name="GamepadEvents_thread")
        self.daemon = True
        self.stop_thread = False
        self.shutdown_flag = threading.Event()
        
        self.set_zero_state()
        self.gamepad_state = self.get_state()
    
    def run(self):
        while not self.shutdown_flag.is_set():
            if not self.shutdown_flag.is_set():
                self.update()
        
    # def start(self):
    #     self.stop_thread = False
        # self.thread.start()

    def stop(self):
        if not self.stop_thread:
            with self.lock:
                self.stop_thread = True
            # self.thread.join() # Thread._wait_for_tstate_lock() never returns if trying to join this thread

    def update(self):
        while not self.stop_thread:
            self.gamepad_state = self.get_state()
    
    def set_zero_state(self):
        with self.lock:
            self.middle_led_ring_button.pressed = False
            self.left_stick.x = 0
            self.left_stick.y = 0
            self.right_stick.x = 0
            self.right_stick.y = 0

            self.left_stick_button.pressed = False
            self.right_stick_button.pressed = False
            self.bottom_button.pressed = False
            self.top_button.pressed = False
            self.left_button.pressed = False
            self.right_button.pressed = False
            self.left_shoulder_button.pressed = False
            self.right_shoulder_button.pressed = False
            self.select_button.pressed = False
            self.start_button.pressed = False
            self.bottom_pad.pressed = False
            self.top_pad.pressed = False
            self.left_pad.pressed = False
            self.right_pad.pressed = False
            
            self.left_trigger.pulled = 0
            self.right_trigger.pulled = 0

    def get_state(self):
        with self.lock:
            state = {'middle_led_ring_button_pressed': self.middle_led_ring_button.pressed,
                     'left_stick_x': self.left_stick.x,
                     'left_stick_y': self.left_stick.y,
                     'right_stick_x': self.right_stick.x,
                     'right_stick_y': self.right_stick.y,
                     'left_stick_button_pressed': self.left_stick_button.pressed,
                     'right_stick_button_pressed': self.right_stick_button.pressed,
                     'bottom_button_pressed': self.bottom_button.pressed,
                     'top_button_pressed': self.top_button.pressed,
                     'left_button_pressed': self.left_button.pressed,
                     'right_button_pressed': self.right_button.pressed,
                     'left_shoulder_button_pressed': self.left_shoulder_button.pressed,
                     'right_shoulder_button_pressed': self.right_shoulder_button.pressed,
                     'select_button_pressed': self.select_button.pressed,
                     'start_button_pressed': self.start_button.pressed,
                     'left_trigger_pulled': self.left_trigger.pulled,
                     'right_trigger_pulled': self.right_trigger.pulled,
                     'bottom_pad_pressed': self.bottom_pad.pressed,
                     'top_pad_pressed': self.top_pad.pressed,
                     'left_pad_pressed': self.left_pad.pressed,
                     'right_pad_pressed': self.right_pad.pressed}
        return state


def main():
    gamepad_controller = GamePadController(print_events=False)
    gamepad_controller.start()
    try:
        while True:
            state = gamepad_controller.get_state()
            print('------------------------------')
            print('GAMEPAD CONTROLLER STATE')
            for k in state.keys():
                print(k, ' : ', state[k])
            print('------------------------------')
            time.sleep(1.0)
    except (KeyboardInterrupt, SystemExit):
        pass


if __name__ == "__main__":
    main()
