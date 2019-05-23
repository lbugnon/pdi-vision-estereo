#!/usr/bin/python
# -*- coding: latin-1 -*-
import nxt,math,time
import numpy as np
import nxt.locator
from nxt.brick import FileFinder, ModuleFinder, FileReader
from nxt.motor import Motor, PORT_A,  PORT_C, SynchronizedMotors
import ipdb

class NXTControl():

    """ Control super simple de un NXT Lego con dos ruedas para desplazamiento"""
    

    power_base_slow=60
    power_base_fast=60#80
    
    tacho_correct=np.array([1,1.015]) 
    
    valid_states=["do_nothing","turn_left","turn_right","move_forward","move_backwards"]
    
    def __init__(self):

        self.brick_found=False
        
        self.brick = None
        self.motor_left = None 
        self.motor_right = None

        self.started=False
        self.verbose = 2
      
        
        self.state="do_nothing"

        

    def __del__(self):
        print "__del__"
        self.disconnect()
        

    def debug(self, msg):
        if self.verbose >= 2:
            print "%0.3f" % time.clock(), msg

    def log(self, msg):
        if self.verbose >= 1:
            print "%0.3f" % time.clock(), msg

    def get_brick_info(self):
        """Return a dictionary with brich information."""
        try:
            b = self.brick
            name, host, signal_strength, user_flash = b.get_device_info()
            prot_version, fw_version = b.get_firmware_version()
            millivolts = b.get_battery_level()
            return {"status": "ok",
                    "NXT brick name": name.rstrip(chr(0)),
                    "Host address": host,
                    "Free user flash": user_flash,
                    "Protocol version": "%s.%s" % prot_version,
                    "Firmware version": "%s.%s" % fw_version,
                    "Battery level": "%s mV" % millivolts,
                    }
        except Exception, e:
            print "Error with brick:"
            traceback.print_tb(sys.exc_info()[2])
            print str(sys.exc_info()[1])
            return {"status": "error", 
                    "details": str(e)}

            
    def connect(self):
        """Connect with LEGO NXT brick."""
        self.debug("Connecting...")
        self.disconnect()
        try:
            self.brick = nxt.locator.find_one_brick()
        except:
            print("NXT cannot be found, continue without it.")
            return False
            
        self.motor_left = Motor(self.brick, PORT_A)
        self.motor_right = Motor(self.brick, PORT_C)
        self.log("Connected to %s." % self.brick)
        if self.verbose >= 2:
            print(self.get_brick_info())

        return True


    def set_state(self,state):
        if state in self.valid_states:
            self.state=state
            print("State set to %s" %state)
            power=self.power_base_fast*self.tacho_correct
            if self.state=="do_nothing":
                self.motor_idle()
            if self.state=="move_forward":
                self.motor_set_speed(power[0],power[1])
            if self.state=="move_backwards":
                self.motor_set_speed(-power[0],-power[1])

            power=self.power_base_slow*self.tacho_correct
            if self.state=="turn_left":
                self.motor_set_speed(power[0],-power[1])
            if self.state=="turn_right":
                self.motor_set_speed(-power[0],power[1])

    def motor_set_speed(self, left_speed, right_speed):
        self.motor_left.run(left_speed)
        self.motor_right.run(right_speed)

    def motor_idle(self):
        self.motor_left.idle()
        self.motor_right.idle()

    def getTacho(self):
        return self.motor_left.get_tacho().rotation_count, \
               self.motor_right.get_tacho().rotation_count
        
                
                
    def disconnect(self):
        """Close connection and restore defined status.
        
        Should be called at the end of a program, because turtle's destructor
        is not reliably called by Python. 
        """
        if self.brick:
            self.motor_idle()
            self.debug("Disconnecting...")
            time.sleep(1)
            self.motor_left = self.motor_right =  None
            self.brick = None
            self.log("Disconnected.")
        # Brick is disconnected in its destructor
        self.brick = None
        
