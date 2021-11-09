#!/usr/bin/env python
from __future__ import print_function
import threading
import time
import subprocess
import psutil

# ##################################################################################

""" Xbox 360 controller support for Python
11/9/13 - Steven Jacobs

This class module supports reading a connected Xbox controller under Python 2 and 3.

You'll need to first install xboxdrv:

    sudo apt-get install xboxdrv

See http://pingus.seul.org/~grumbel/xboxdrv/ for details on xboxdrv

Example usage:

    import xbox
    joy = xbox.Joystick()         #Initialize joystick

    if joy.A():                   #Test state of the A button (1=pressed, 0=not pressed)
        print 'A button pressed'
    x_axis   = joy.leftX()        #X-axis of the left stick (values -1.0 to 1.0)
    (x,y)    = joy.leftStick()    #Returns tuple containing left X and Y axes (values -1.0 to 1.0)
    trigger  = joy.rightTrigger() #Right trigger position (values 0 to 1.0)

    joy.close()                   #Cleanup before exit

All controller buttons are supported.  See code for all functions.
"""

import subprocess
import select
import time


class Joystick:
    """Initializes the joystick/wireless receiver, launching 'xboxdrv' as a subprocess
    and checking that the wired joystick or wireless receiver is attached.
    The refreshRate determines the maximnum rate at which events are polled from xboxdrv.
    Calling any of the Joystick methods will cause a refresh to occur, if refreshTime has elapsed.
    Routinely call a Joystick method, at least once per second, to avoid overfilling the event buffer.

    Usage:
        joy = xbox.Joystick()
    """

    def __init__(self, refreshRate=30):
        self.proc = subprocess.Popen(['xboxdrv', '--no-uinput', '--detach-kernel-driver'], stdout=subprocess.PIPE,
                                     bufsize=0)
        self.pipe = self.proc.stdout
        #
        self.connectStatus = False  # will be set to True once controller is detected and stays on
        self.reading = '0' * 140  # initialize stick readings to all zeros
        #
        self.refreshTime = 0  # absolute time when next refresh (read results from xboxdrv stdout pipe) is to occur
        self.refreshDelay = 1.0 / refreshRate  # joystick refresh is to be performed 30 times per sec by default
        #
        # Read responses from 'xboxdrv' for upto 2 seconds, looking for controller/receiver to respond
        found = False
        waitTime = time.time() + 2
        while waitTime > time.time() and not found:
            readable, writeable, exception = select.select([self.pipe], [], [], 0)
            if readable:
                response = self.pipe.readline()
                # Hard fail if we see this, so force an error
                if response[0:7] == b'No Xbox':
                    raise IOError('No Xbox controller/receiver found')
                # Success if we see the following
                if response[0:12].lower() == b'press ctrl-c':
                    found = True
                # If we see 140 char line, we are seeing valid input
                if len(response) == 140:
                    found = True
                    self.connectStatus = True
                    self.reading = response
        # if the controller wasn't found, then halt
        if not found:
            self.close()
            raise IOError('Unable to detect Xbox controller/receiver - Run python as sudo')

    """Used by all Joystick methods to read the most recent events from xboxdrv.
    The refreshRate determines the maximum frequency with which events are checked.
    If a valid event response is found, then the controller is flagged as 'connected'.
    """

    def refresh(self):
        # Refresh the joystick readings based on regular defined freq
        if self.refreshTime < time.time():
            self.refreshTime = time.time() + self.refreshDelay  # set next refresh time
            # If there is text available to read from xboxdrv, then read it.
            readable, writeable, exception = select.select([self.pipe], [], [], 0)
            if readable:
                # Read every line that is availabe.  We only need to decode the last one.
                while readable:
                    response = self.pipe.readline()
                    # A zero length response means controller has been unplugged.
                    if len(response) == 0:
                        raise IOError('Xbox controller disconnected from USB')
                    readable, writeable, exception = select.select([self.pipe], [], [], 0)
                # Valid controller response will be 140 chars.
                if len(response) == 140:
                    self.connectStatus = True
                    self.reading = response
                else:  # Any other response means we have lost wireless or controller battery
                    self.connectStatus = False

    """Return a status of True, when the controller is actively connected.
    Either loss of wireless signal or controller powering off will break connection.  The
    controller inputs will stop updating, so the last readings will remain in effect.  It is
    good practice to only act upon inputs if the controller is connected.  For instance, for
    a robot, stop all motors if "not connected()".

    An inital controller input, stick movement or button press, may be required before the connection
    status goes True.  If a connection is lost, the connection will resume automatically when the
    fault is corrected.
    """

    def connected(self):
        self.refresh()
        return self.connectStatus

    # Left stick X axis value scaled between -1.0 (left) and 1.0 (right) with deadzone tolerance correction
    def leftX(self, deadzone=4000):
        self.refresh()
        raw = int(self.reading[3:9])
        return self.axisScale(raw, deadzone)

    # Left stick Y axis value scaled between -1.0 (down) and 1.0 (up)
    def leftY(self, deadzone=4000):
        self.refresh()
        raw = int(self.reading[13:19])
        return self.axisScale(raw, deadzone)

    # Right stick X axis value scaled between -1.0 (left) and 1.0 (right)
    def rightX(self, deadzone=4000):
        self.refresh()
        raw = int(self.reading[24:30])
        return self.axisScale(raw, deadzone)

    # Right stick Y axis value scaled between -1.0 (down) and 1.0 (up)
    def rightY(self, deadzone=4000):
        self.refresh()
        raw = int(self.reading[34:40])
        return self.axisScale(raw, deadzone)

    # Scale raw (-32768 to +32767) axis with deadzone correcion
    # Deadzone is +/- range of values to consider to be center stick (ie. 0.0)
    def axisScale(self, raw, deadzone):
        if abs(raw) < deadzone:
            return 0.0
        else:
            if raw < 0:
                return (raw + deadzone) / (32768.0 - deadzone)
            else:
                return (raw - deadzone) / (32767.0 - deadzone)

    # Dpad Up status - returns 1 (pressed) or 0 (not pressed)
    def dpadUp(self):
        self.refresh()
        return int(self.reading[45:46])

    # Dpad Down status - returns 1 (pressed) or 0 (not pressed)
    def dpadDown(self):
        self.refresh()
        return int(self.reading[50:51])

    # Dpad Left status - returns 1 (pressed) or 0 (not pressed)
    def dpadLeft(self):
        self.refresh()
        return int(self.reading[55:56])

    # Dpad Right status - returns 1 (pressed) or 0 (not pressed)
    def dpadRight(self):
        self.refresh()
        return int(self.reading[60:61])

    # Back button status - returns 1 (pressed) or 0 (not pressed)
    def Back(self):
        self.refresh()
        return int(self.reading[68:69])

    # Guide button status - returns 1 (pressed) or 0 (not pressed)
    def Guide(self):
        self.refresh()
        return int(self.reading[76:77])

    # Start button status - returns 1 (pressed) or 0 (not pressed)
    def Start(self):
        self.refresh()
        return int(self.reading[84:85])

    # Left Thumbstick button status - returns 1 (pressed) or 0 (not pressed)
    def leftThumbstick(self):
        self.refresh()
        return int(self.reading[90:91])

    # Right Thumbstick button status - returns 1 (pressed) or 0 (not pressed)
    def rightThumbstick(self):
        self.refresh()
        return int(self.reading[95:96])

    # A button status - returns 1 (pressed) or 0 (not pressed)
    def A(self):
        self.refresh()
        return int(self.reading[100:101])

    # B button status - returns 1 (pressed) or 0 (not pressed)
    def B(self):
        self.refresh()
        return int(self.reading[104:105])

    # X button status - returns 1 (pressed) or 0 (not pressed)
    def X(self):
        self.refresh()
        return int(self.reading[108:109])

    # Y button status - returns 1 (pressed) or 0 (not pressed)
    def Y(self):
        self.refresh()
        return int(self.reading[112:113])

    # Left Bumper button status - returns 1 (pressed) or 0 (not pressed)
    def leftBumper(self):
        self.refresh()
        return int(self.reading[118:119])

    # Right Bumper button status - returns 1 (pressed) or 0 (not pressed)
    def rightBumper(self):
        self.refresh()
        return int(self.reading[123:124])

    # Left Trigger value scaled between 0.0 to 1.0
    def leftTrigger(self):
        self.refresh()
        return int(self.reading[129:132]) / 255.0

    # Right trigger value scaled between 0.0 to 1.0
    def rightTrigger(self):
        self.refresh()
        return int(self.reading[136:139]) / 255.0

    # Returns tuple containing X and Y axis values for Left stick scaled between -1.0 to 1.0
    # Usage:
    #     x,y = joy.leftStick()
    def leftStick(self, deadzone=4000):
        self.refresh()
        return (self.leftX(deadzone), self.leftY(deadzone))

    # Returns tuple containing X and Y axis values for Right stick scaled between -1.0 to 1.0
    # Usage:
    #     x,y = joy.rightStick()
    def rightStick(self, deadzone=4000):
        self.refresh()
        return (self.rightX(deadzone), self.rightY(deadzone))

    # Cleanup by ending the xboxdrv subprocess
    def close(self):
        self.proc.kill()


# ##################################################################################
class Stick():
    def __init__(self):
        # joystick pushed
        #   all the way down: y = -1.0
        #   all the way up: y ~= 1.0
        #   all the way left: x = -1.0
        #   all the way right: x ~= 1.0
        self.x = 0.0
        self.y = 0.0
        # normalized signed 16 bit integers to be in the range [-1.0, 1.0]
        self.norm = float(pow(2, 15))

    def update_x(self, abs_x):
        self.x = int(abs_x) / self.norm

    def update_y(self, abs_y):
        self.y = -int(abs_y) / self.norm

    def print_string(self):
        return 'x: {0:4.2f}, y:{1:4.2f}'.format(x, y)


class Button():
    def __init__(self):
        self.pressed = False

    def update(self, state):
        if state == 0:
            self.pressed = False
        elif state == 1:
            self.pressed = True

    def print_string(self):
        return str(self.pressed)


class Trigger():
    def __init__(self, xbox_one=False):
        # Xbox One trigger
        #   not pulled = 0
        #   max pulled = 1023
        # normalize unsigned 10 bit integer to be in the range [0.0, 1.0]

        # Xbox 360 trigger
        #   not pulled = 0
        #   max pulled = 255
        # normalize unsigned 8 bit integer to be in the range [0.0, 1.0]
        if xbox_one:
            # xbox one
            num_bits = 10
        else:
            # xbox 360
            num_bits = 8
        self.norm = float(pow(2, num_bits) - 1)
        self.pulled = 0.0

    def update(self, state):
        self.pulled = int(state) / self.norm
        # Ensure that the pulled value is not greater than 1.0, which
        # will can happen with the use of an Xbox One controller, if
        # the option was not properly set.
        if self.pulled > 1.0:
            self.pulled = 1.0

    def print_string(self):
        return '{0:4.2f}'.format(self.pulled)

#See https://github.com/FRC4564/Xbox

class XboxController():
    '''Successfully tested with the following controllers:
            + EasySMX wireless controller set to appropriate mode (Xbox 360 mode with upper half of ring LED illuminated - top two LED quarter circle arcs)
    '''

    def __init__(self):
        self.left_stick = Stick()
        self.right_stick = Stick()

        self.left_stick_button = Button()
        self.right_stick_button = Button()

        self.middle_led_ring_button = Button()

        self.bottom_button = Button()
        self.top_button = Button()
        self.left_button = Button()
        self.right_button = Button()

        self.right_shoulder_button = Button()
        self.left_shoulder_button = Button()

        self.select_button = Button()
        self.start_button = Button()

        self.left_trigger = Trigger(xbox_one=False)
        self.right_trigger = Trigger(xbox_one=False)

        self.left_pad = Button()
        self.right_pad = Button()
        self.top_pad = Button()
        self.bottom_pad = Button()
        self.joy=None
        self.lock = threading.Lock()

    def start(self):
        try:
            #Kill existing driver if running
            if "xboxdrv" in (p.name() for p in psutil.process_iter()):
                subprocess.Popen(['killall', '-9', 'xboxdrv'])#, stdout=subprocess.DEVNULL, bufsize=0)
            self.joy = xbox.Joystick()
        except IOError as inst:
            print(inst)
            if self.joy is not None:
                self.joy.close()
                self.joy=None
        return True

    def stop(self):
        if self.joy is not None:
            self.joy.close()
            self.joy=None

    def update(self):
        try:
            if self.joy is not None:
                with self.lock:
                    self.left_stick.x = self.joy.leftX(deadzone=0)  # update_x(event.state)
                    self.left_stick.y = self.joy.leftY(deadzone=0)  # update_x(event.state)

                    self.right_stick.x = self.joy.rightX(deadzone=0)
                    self.right_stick.y = self.joy.rightY(deadzone=0)

                    self.left_pad.pressed = self.joy.dpadLeft()
                    self.right_pad.pressed = self.joy.dpadRight()
                    self.top_pad.pressed = self.joy.dpadUp()
                    self.bottom_pad.pressed= self.joy.dpadDown()

                    self.bottom_button.pressed=self.joy.A()
                    self.top_button.pressed = self.joy.Y()
                    self.left_button.pressed = self.joy.X()
                    self.right_button.pressed = self.joy.B()

                    self.left_stick_button.pressed=self.joy.leftThumbstick()
                    self.right_stick_button.pressed=self.joy.rightThumbstick()

                    self.left_shoulder_button.pressed=self.joy.leftBumper()
                    self.right_shoulder_button.pressed = self.joy.rightBumper()

                    self.left_trigger.pulled=self.joy.leftTrigger()
                    self.right_trigger.pulled = self.joy.rightTrigger()

                    self.start_button.pressed=self.joy.Start()
                    self.select_button.pressed=self.joy.Back()
                    self.middle_led_ring_button.pressed=self.joy.Guide()


                    #
                    # # 4-way pad
                    # if event.code == 'ABS_HAT0Y':  # -1 up / 1 down
                    #     if event.state == 0:
                    #         self.top_pad.update(0)
                    #         self.bottom_pad.update(0)
                    #     elif event.state == 1:
                    #         self.top_pad.update(0)
                    #         self.bottom_pad.update(1)
                    #     elif event.state == -1:
                    #         self.bottom_pad.update(0)
                    #         self.top_pad.update(1)
                    #
                    # if event.code == 'ABS_HAT0X':  # -1 left / 1 right
                    #     if event.state == 0:
                    #         self.left_pad.update(0)
                    #         self.right_pad.update(0)
                    #     elif event.state == 1:
                    #         self.left_pad.update(0)
                    #         self.right_pad.update(1)
                    #     elif event.state == -1:
                    #         self.right_pad.update(0)
                    #         self.left_pad.update(1)

        except IOError as inst:
            print(inst)
            if self.joy is not None:
                self.joy.close()
                self.joy=None
            return


    def get_state(self):
        self.update()
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
    xbox_controller = XboxController()
    xbox_controller.start()
    try:
        while True:
            state = xbox_controller.get_state()
            print('------------------------------')
            print('XBOX CONTROLLER STATE')
            for k in state.keys():
                print(k, ' : ', state[k])
            print('------------------------------')
            time.sleep(.1)
    except (KeyboardInterrupt, SystemExit):
        pass


if __name__ == "__main__":
    main()
