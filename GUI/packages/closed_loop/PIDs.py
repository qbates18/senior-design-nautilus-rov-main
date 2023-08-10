from simple_pid import PID
import time


#wrapper class that makes it easier to manipulate and store input values going into the PID controller
class altitude_PID:
    def __init__(self, desiredAltitude):
        #initialize PID object
        desiredAltitude = float(desiredAltitude)
        self.pid_instance = PID(8, 4, 4, setpoint = desiredAltitude)
        self.pid_instance.sample_time = 0.05
        self.pid_instance.output_limits = (-34.32, 44.32)
        self.force_to_joystick_ratio = 1/34.32

    def calculate_next(self, currentValue):
        currentValue = float(currentValue)
        output = self.pid_instance(currentValue)
        output = output * self.force_to_joystick_ratio
        return output


class depth_PID:
    def __init__(self, desiredDepth):
        self.vertical_thruster_amount = 4
        desiredDepth = float(desiredDepth)
        self.pid_instance = PID(-7, -1, -3, setpoint=desiredDepth)
        self.pid_instance.sample_time = 0.05
        self.pid_instance.output_limits = (-34.32*self.vertical_thruster_amount, 44.13*self.vertical_thruster_amount)
        self.force_to_joystick_ratio_neg = 1/(34.32*self.vertical_thruster_amount)
        self.force_to_joystick_ratio_pos = 1/(44.13*self.vertical_thruster_amount)

    def calculate_next(self, currentValue):
        currentValue = float(currentValue)
        depth_input = currentValue/(9.8*1)
        output = self.pid_instance(depth_input)
        output = output * self.force_to_joystick_ratio_pos
        return output


class head_PID:
    def __init__(self, desiredHead):
        desiredHead = float(desiredHead)
        self.vector_thruster_amount = 4
        #convert pressure to depth in feet
        self.vector_thrust_contribution = 0.5
        self.max_moment = 156.9*self.vector_thrust_contribution*self.vector_thruster_amount
        self.pid_instance = PID(4, 1, 1, setpoint=desiredHead)
        self.pid_instance.sample_time = 0.05
        self.pid_instance.output_limits = (-self.max_moment, self.max_moment)
        self.force_to_joystick_ratio = 1/self.max_moment

    def calculate_next(self, currentValue):
        currentValue = float(currentValue)
        if abs(currentValue-self.pid_instance.setpoint) <= 180:
            output = self.pid_instance(currentValue)
        else:
            if currentValue > self.pid_instance.setpoint:
                lower_input_value = (360 - currentValue)
                output = self.pid_instance(lower_input_value)
            else:
                higher_input_value = (360 + currentValue)
                output = self.pid_instance(higher_input_value)
        output = output * self.force_to_joystick_ratio
        return output