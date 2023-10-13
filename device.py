import random
from BAC0 import lite
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

ALARM_STATES = ["OK", "ALARM_LOW", "ALARM_MED", "ALARM_HI", "UNKNOWN"]


class SimDevice(object):
    def __init__(self, port, device_id):
        self.port = port
        self.device_id = device_id
        self.alarm_states = make_state_text(ALARM_STATES)
        self._d = lite(port=port, deviceId=device_id)
        self._define_objects()
        
    def _define_objects(self):
        ObjectFactory.clear_objects()
        
        _new_objects = analog_input(
            name="frequency_0",
            properties={"units": "hertz"},
            description="frequency",
            presentValue=random.uniform(5, 100),
        )
            
        for i in range(0, 20):
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
            analog_input(
                name=f"fan_spd_pct_{i}",
                description="Fan Speed Percentage",
                presentValue=round(random.uniform(0, 100), 2),
            )
            
            # humidity
            rh_sp = random.uniform(5, 80)
            rh = rh_sp + random.random()
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
            
        
        for i in range(20, 50):
            # More alarms
            multistate_input(
                name=f"alarm_{i}",
                description="Alarm",
                properties={"stateText": self.alarm_states},
                presentValue=random.randint(0, len(ALARM_STATES)-1),
                is_commandable=True,
            )
            
            # More on/off
            binary_input(
                name=f"enabled_{i}",
                presentValue= False if random.random() < 0.5 else True,
            )
            
            
        return _new_objects.add_objects_to_application(self._d)
    
    def update_freq(self):
        for i in range(0, 20):
            new_freq = random.uniform(5, 100)
            self._d[f"frequency_{i}"].presentValue = new_freq
            
            # print(f"Frequency {i}:", new_freq)
    
    def update_temp_sp(self, num):
        for _ in range(num):
            r = random.randint(0, 19)
            new_sp = random.randint(0, 20)
            self._d[f"temp_sp_{r}"].presentValue = new_sp
    
    def update_temp(self):
        for i in range(0, 20):
            sp = val(self._d[f"temp_sp_{i}"].presentValue)
            pv = val(self._d[f"temp_degC_{i}"].presentValue)
            
            delta = abs(pv - sp)
            adj = 0
            old_t = sp
            if delta >= 1.5:
                if sp > pv:
                    adj = delta / 4
                elif pv > sp:
                    adj = -1 * delta / 4
                    
                old_t = pv + adj
                    
            sign = -1 if random.random() < 0.5 else 1
            new_t = old_t + (sign * random.random() / 2)
            new_tf = (new_t * 9 / 5) + 32
            
            self._d[f"temp_degC_{i}"].presentValue = round(new_t, 2)
            self._d[f"temp_degF_{i}"].presentValue = round(new_tf, 2)
            
    def update_rh_sp(self, num):
        for _ in range(num):
            r = random.randint(0, 19)
            new_sp = random.randint(2, 80)
            self._d[f"rh_sp_{r}"].presentValue = new_sp
            
    def update_rh(self):
        for i in range(0, 20):
            sp = val(self._d[f"rh_sp_{i}"].presentValue)
            pv = val(self._d[f"rh_{i}"].presentValue)
            
            delta = abs(pv - sp)
            adj = 0
            old_rh = sp
            if delta >= 1.5:
                if sp > pv:
                    adj = delta / 4
                elif pv > sp:
                    adj = -1 * delta / 4
                    
                old_rh = pv + adj
                    
            sign = -1 if random.random() < 0.5 else 1
            new_rh = old_rh + (sign * random.random() / 2)
            
            self._d[f"rh_{i}"].presentValue = round(new_rh, 2)
            
    def update_alarm(self, num):
        for _ in range(num):
            r = random.randint(0, 49)
            v = random.randint(0, len(ALARM_STATES)-1)
            self._d[f"alarm_{r}"].presentValue = v
            
    def update_enabled(self, num):
        for _ in range(num):
            r = random.randint(0, 49)
            v = val(self._d[f"enabled_{r}"].presentValue)
            self._d[f"enabled_{r}"].presentValue = not v
            
    def update_fan_speed(self):
        for i in range(20):
            spd = val(self._d[f"fan_spd_pct_{i}"].presentValue)
            
            sign = -1 if random.random() < 0.5 else 1
            r1 = random.random()
            r2 = random.uniform(0, 5)
            new_spd = spd + sign * r1 * r2
            new_spd = max(0, min(100, new_spd))
            
            self._d[f"fan_spd_pct_{i}"].presentValue = new_spd
        
    def disconnect(self):
        self._d.disconnect()


def val(v):
    if type(v) == Real:
        return v.value
    return v