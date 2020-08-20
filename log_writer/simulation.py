# -*- coding: utf-8 -*-

"""Module containing a classes for holding the simulation metadata for the simulation platform."""

from tools.datetime_tools import to_utc_datetime_object, to_iso_format_datetime_string
from tools.messages import AbstractMessage, AbstractResultMessage, SimulationStateMessage


class SimulationMetadata:
    """Class for holding simulation metadata."""
    SIMULATION_STARTED, SIMULATION_ENDED = SimulationStateMessage.SIMULATION_STATES

    def __init__(self, simulation_id: str):
        self.__simulation_id = simulation_id
        self.__components = set()
        self.__topic_messages = {}

        self.__start_time = None
        self.__start_flag = False
        self.__end_time = None
        self.__end_flag = False

        self.__epoch_min = None
        self.__epoch_max = None

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

    @property
    def start_flag(self):
        """Returns True if the starting simulation state message has been logged."""
        return self.__start_flag

    @property
    def end_flag(self):
        """Returns True if the ending simulation state message has been logged."""
        return self.__end_flag

    @property
    def epoch_min(self):
        """Returns the smallest logged epoch number."""
        return self.__epoch_min

    @property
    def epoch_max(self):
        """Returns the largest logged epoch number."""
        return self.__epoch_max

    @property
    def components(self):
        """Returns the simulation component names as a list."""
        return self.__components

    @property
    def total_messages(self):
        """Returns the total number of messages logged for the simulation."""
        return sum(self.__topic_messages.values())

    @property
    def topic_messages(self):
        """Returns a dictionary with the topic names as keys and
           the total number of messages logged for that topic as values."""
        return self.__topic_messages

    def add_message(self, message_object: AbstractMessage, message_topic: str):
        """Logs the message to the simulation."""

        # Check for the start or end flags.
        if isinstance(message_object, SimulationStateMessage):
            if message_object.simulation_state == SimulationMetadata.SIMULATION_STARTED:
                self.__start_flag = True
            elif message_object.simulation_state == SimulationMetadata.SIMULATION_ENDED:
                self.__end_flag = True

        # Check the timestamp for the earliest or the latest messages.
        message_timestamp = to_utc_datetime_object(message_object.timestamp)
        if self.start_time is None or message_timestamp < self.start_time:
            self.__start_time = message_timestamp
        if self.end_time is None or message_timestamp > self.end_time:
            self.__end_time = message_timestamp

        # Add to the simulation component list.
        self.__components.add(message_object.source_process_id)

        # Check for the smallest or the largest epoch.
        if isinstance(message_object, AbstractResultMessage):
            if self.epoch_min is None or message_object.epoch_number < self.epoch_min:
                self.__epoch_min = message_object.epoch_number
            if self.epoch_max is None or message_object.epoch_number > self.epoch_max:
                self.__epoch_max = message_object.epoch_number

        # Add to topic message count.
        if message_topic not in self.__topic_messages:
            self.__topic_messages[message_topic] = 0
        self.__topic_messages[message_topic] += 1

    def __str__(self):
        start_time_str = to_iso_format_datetime_string(self.start_time)
        end_time_str = to_iso_format_datetime_string(self.end_time)

        return "\n    ".join([
            self.simulation_id,
            "start time: " + (start_time_str if self.start_flag else "({:s})".format(start_time_str)),
            "end_time: " + (end_time_str if self.end_flag else "({:s})".format(end_time_str)),
            "components: {:s}".format(", ".join(self.components)),
            "epochs: {:s} - {:s}".format(str(self.epoch_min), str(self.epoch_max)),
            "total messages: {:d}".format(self.total_messages),
            "topic messages: {:s}".format(str(self.topic_messages))
        ])


class SimulationMetadataCollection:
    """Class for containing metadata for several simulations."""
    def __init__(self):
        self.__simulations = {}

    @property
    def simulations(self):
        """The simulation ids as a list."""
        return list(self.__simulations.keys())

    def get_simulation(self, simulation_id: str):
        """Returns the metadata object for simulation with the id simulation_id.
           Returns None, if the metadata is not found."""
        return self.__simulations.get(simulation_id, None)

    def add_message(self, message_object: AbstractMessage, message_topic: str):
        """Logs the message to the simulation collection."""
        if message_object.simulation_id not in self.__simulations:
            self.__simulations[message_object.simulation_id] = SimulationMetadata(message_object.simulation_id)
        self.__simulations[message_object.simulation_id].add_message(message_object, message_topic)
