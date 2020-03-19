# -*- coding: utf-8 -*-
"""
Implements the PressureRamp class
"""
from xvof.src.boundary_condition.boundary_condition import BoundaryCondition


class PressureRamp(BoundaryCondition):
    """
    A class that defines a ramp between 2 constants steps pressure

                ^
    second value|       ...........
                |      /
                |     /
    first value |..../
                |_________________>
                   start end
    """
    def __init__(self, first_value, second_value, start_time, end_time):
        """
        Pressure ramp

        :param first_value: intial pressure value
        :param second_value: pressure value to reach
        :param start_time: time for starting the ramp
        :param end_time: time for reaching second_value pressure
        """
        self.__first_value = first_value
        self.__second_value = second_value
        self.__start_time = start_time
        self.__end_time = end_time

        if self.__end_time <= self.__start_time:
            raise ValueError("Please respect the chronology")

    def evaluate(self, time, *args, **kwargs):
        if time <= self.__start_time:
            return self.__first_value
        if time > self.__end_time:
            return self.__second_value
        # time is in the slope
        slope = (self.__second_value - self.__first_value) / (self.__end_time - self.__start_time)
        return slope * (time - self.__start_time) + self.__first_value

    @property
    def start_time(self):
        """
        Return the time at which the slope begins
        """
        return self.__start_time

    @property
    def end_time(self):
        """
        Return the time at which the slope ends
        """
        return self.__end_time

    @property
    def first_value(self):
        """
        Return the first value
        """
        return self.__first_value

    @property
    def second_value(self):
        """
        Return the second value
        """
        return self.__second_value