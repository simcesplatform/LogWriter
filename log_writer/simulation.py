# -*- coding: utf-8 -*-

"""Module containing a class for the simulation metadata for the simulation platform."""

import datetime


class Simulation:
    """Class for simulation metadata."""
    def __init__(self, simulation_id: str, start_time=None, end_time=None):
        self.__simulation_id = simulation_id
        self.__start_time = start_time
        self.__end_time = end_time

    @property
    def simulation_id(self):
        """The simulation identifier."""
        return self.__simulation_id

    @property
    def start_time(self):
        """The start time for the simulation."""
        return self.__start_time

    @property
    def end_time(self):
        """The end time for the simulation."""
        return self.__end_time

    @start_time.setter
    def start_time(self, start_time: datetime.datetime):
        self.__start_time = start_time

    @end_time.setter
    def end_time(self, end_time: datetime.datetime):
        self.__end_time = end_time
