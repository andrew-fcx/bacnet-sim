# https://www.youtube.com/watch?v=F_IcLN_HZGg
# https://www.controlscourse.com/bacnet-objects/
# https://bac0.readthedocs.io/en/latest/index.html

import random
from BAC0 import lite, device
from BAC0.core.devices.local.object import ObjectFactory
from BAC0.core.devices.local.models import (
    analog_input,
    analog_output,
    binary_input,
    binary_output,
    make_state_text,
    multistate_input
)
from bacpypes.primitivedata import Real
# import logging

ALARM_STATES = ["OK", "ALARM_LOW", "ALARM_MED", "ALARM_HI", "UNKNOWN"]


class SimDevice(object):
    def __init__(self, port, device_id):
        self.port = port
        self.device_id = device_id
        self.alarm_states = make_state_text(ALARM_STATES)
        self._d = lite(port=port, deviceId=device_id)
        
        self._d._update_local_cov_task.task.stop()
        self._d._update_local_cov_task.running = False
        
        self._define_objects()
        
    def _define_objects(self):
        ObjectFactory.clear_objects()
        
        _new_objects = analog_input(
            name="frequency_0",
            properties={"units": "hertz"},
            description="frequency",
            presentValue=random.uniform(5, 100),
        )
            
        for i in range(0, 50):
            # frequencies
            if i != 0:
                analog_input(
                    name=f"frequency_{i}",
                    properties={"units": "hertz"},
                    description="frequency",
                    presentValue=random.uniform(5, 100),
                )
            
            # temperatures
            sp = random.randint(0, 20)
            t = sp + random.random()
            tf = (t * 9 / 5) + 32
            analog_output(
                name=f"temp_sp_{i}",
                properties={"units": "degreesCelsius"},
                description="temp setpoint",
                presentValue=sp,
            )
            analog_input(
                name=f"temp_degC_{i}",
                properties={"units": "degreesCelsius"},
                description="Temperature - Celsius",
                presentValue=round(t, 2),
            )
            analog_input(
                name=f"temp_degF_{i}",
                properties={"units": "degreesFahrenheit"},
                description="Temperature - Fahrenheit",
                presentValue=round(tf, 2),
            )
            
            # alarms
            multistate_input(
                name=f"alarm_{i}",
                description="Alarm",
                properties={"stateText": self.alarm_states},
                presentValue=random.randint(0, len(ALARM_STATES)-1),
                is_commandable=True,
            )
            
            # on/off
            binary_input(
                name=f"enabled_{i}",
                presentValue= False if random.random() < 0.5 else True,
            )
            
            # Fan speed %
            fan_spd_sp = round(random.uniform(0, 100), 2)
            fan_spd = round(fan_spd_sp + random.random() * 2, 2)
            analog_output(
                name=f"fan_spd_sp_{i}",
                description="Fan Speed Setpoint Percentage",
                presentValue=fan_spd_sp,
            )
            analog_input(
                name=f"fan_spd_pct_{i}",
                description="Fan Speed Percentage",
                presentValue=fan_spd,
            )
            
            # humidity
            rh_sp = round(random.uniform(5, 80), 2)
            rh = round(rh_sp + random.random(), 2)
            analog_output(
                name=f"rh_sp_{i}",
                description="Relative Humidity SP",
                presentValue=rh_sp,
            )
            analog_input(
                name=f"rh_{i}",
                description="Relative Humidity",
                presentValue=rh,
            )

        return _new_objects.add_objects_to_application(self._d)
    
    def _update_sp(self, name, count, range_low=0, range_hi=49, rand_low=0, rand_hi=20):
        for _ in range(count):
            r = random.randint(range_low, range_hi)
            new_sp = random.randint(rand_low, rand_hi)
            self._d[f"{name}_{r}"].presentValue = new_sp
            
    def _update_val(self, name, sp_name, delta_threshold=1.5, delta_scale=4, val_scale=2, range_low=0, range_high=50):
        for i in range(range_low, range_high):
            sp = val(self._d[f"{sp_name}_{i}"].presentValue)
            pv = val(self._d[f"{name}_{i}"].presentValue)
            
            delta = abs(pv - sp)
            adj = 0
            old_v = sp
            if delta >= delta_threshold:
                if sp > pv:
                    adj = delta / delta_scale
                elif pv > sp:
                    adj = -1 * delta / delta_scale
                    
                old_v = pv + adj
                    
            sign = -1 if random.random() < 0.5 else 1
            new_v = old_v + (sign * random.random() / val_scale)
            
            self._d[f"{name}_{i}"].presentValue = round(new_v, 2)
    
    def update_freq(self):
        for i in range(0, 50):
            new_freq = random.uniform(5, 100)
            self._d[f"frequency_{i}"].presentValue = new_freq
    
    # Temperature updates
    def update_temp_sp(self, num):
        self._update_sp("temp_sp", num)
    
    def update_temp(self):
        self._update_val("temp_degC", "temp_sp", delta_scale=20)
        for i in range(50):
            new_t_c = val(self._d[f"temp_degC_{i}"].presentValue)
            
            new_t_f = (new_t_c * 9 / 5) + 32
            self._d[f"temp_degF_{i}"].presentValue = round(new_t_f, 2)
           
    # Humidity updates 
    def update_rh_sp(self, num):
        self._update_sp("rh_sp", num, rand_low=2, rand_hi=80)
            
    def update_rh(self):
        self._update_val("rh", "rh_sp", delta_scale=10)
          
    # Alarm updates  
    def update_alarm(self, num):
        for _ in range(num):
            r = random.randint(0, 49)
            v = random.randint(0, len(ALARM_STATES)-1)
            self._d[f"alarm_{r}"].presentValue = v
            
    # On/off updates
    def update_enabled(self, num):
        for _ in range(num):
            r = random.randint(0, 49)
            v = val(self._d[f"enabled_{r}"].presentValue)
            self._d[f"enabled_{r}"].presentValue = not v
            
    # Fan speed updates
    def update_fan_spd_sp(self, num):
        self._update_sp("fan_spd_sp", num, rand_low=5, rand_hi=90)
            
    def update_fan_spd(self):
        self._update_val("fan_spd_pct", "fan_spd_sp", delta_scale=1, delta_threshold=3, val_scale=0.5)
        
    # Disconnect device
    def disconnect(self):
        self._d.disconnect()
        
    def keep_cov_disabled(self):
        self._d._update_local_cov_task.task.stop()
        self._d._update_local_cov_task.running = False
        print("COV disabled")


def val(v):
    if type(v) == Real:
        return v.value
    return v