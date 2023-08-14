from __future__ import print_function
from stretch_body.prismatic_joint import PrismaticJoint
from stretch_body.device import Device
from stretch_body.trajectories import PrismaticTrajectory

import time
import math


class Arm(PrismaticJoint):
    """
    API to the Stretch Arm
    """
    def __init__(self,usb=None):
        PrismaticJoint.__init__(self, name='arm',usb=usb)

    # ######### Utilties ##############################

    def motor_rad_to_translate_m(self,ang): #input in rad, output m
        return (self.params['chain_pitch']*self.params['chain_sprocket_teeth']/self.params['gr_spur']/(math.pi*2))*ang

    def translate_m_to_motor_rad(self, x):
        return x/(self.params['chain_pitch']*self.params['chain_sprocket_teeth']/self.params['gr_spur']/(math.pi*2))


    def home(self, end_pos=0.1,to_positive_stop=False, measuring=False):
        return PrismaticJoint.home(self,end_pos=end_pos,to_positive_stop=to_positive_stop,measuring=measuring)

    def set_velocity(self, v_m, a_m=None, stiffness=None, contact_thresh_pos_N=None, contact_thresh_neg_N=None, req_calibration=True, contact_thresh_pos=None, contact_thresh_neg=None):
        if self.params['safe_set_velocit']==1:
            return PrismaticJoint.set_safe_velocity(v_m, a_m, stiffness, contact_thresh_pos_N, contact_thresh_neg_N, req_calibration, contact_thresh_pos, contact_thresh_neg)
        else:
            return PrismaticJoint.set_velocity(v_m, a_m, stiffness, contact_thresh_pos_N, contact_thresh_neg_N, req_calibration, contact_thresh_pos, contact_thresh_neg)
