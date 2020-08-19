# -*- coding: utf-8 -*-

"""This module contains a listener simulation component that prints out all messages from the message bus."""

import asyncio
import logging

from log_writer.simulation import Simulation
from tools.callbacks import LOGGER as callback_logger
from tools.clients import RabbitmqClient
from tools.messages import AbstractMessage
from tools.tools import FullLogger

# No info logs about each received message stored.
callback_logger.level = max(callback_logger.level, logging.WARNING)
LOGGER = FullLogger(__name__)


class ListenerComponent:
    """Class for the message bus listener component."""
    LISTENED_TOPICS = "#"

    def __init__(self):
        self.__rabbitmq_client = RabbitmqClient()
        self.__rabbitmq_client.add_listener(ListenerComponent.LISTENED_TOPICS, self.simulation_message_handler)

        self.__listened_simulations = {}

    @property
    def listened_simulations(self):
        """Returns the received simulation ids as a list."""
        return list(self.__listened_simulations.keys())

    def get_simulation(self, simulation_id: str):
        """Returns the simulation object corresponding to the given simulation identifier."""
        return self.__listened_simulations.get(simulation_id, None)

    async def simulation_message_handler(self, message_object, message_routing_key):
        """Handles the received simulation state messages."""
        if isinstance(message_object, AbstractMessage):
            LOGGER.debug("{:s} : {:s} : {:s}".format(
                message_routing_key, message_object.simulation_id, message_object.message_id))
            if message_object.simulation_id not in self.__listened_simulations:
                self.__listened_simulations[message_object.simulation_id] = Simulation(message_object.simulation_id)

        else:
            LOGGER.warning("Received '{:s}' message when expecting for '{:s}' message".format(
                str(type(message_object)), str(AbstractMessage)))


async def start_listener_component():
    """Start a listener component for the simulation platform."""
    message_listener = ListenerComponent()

    while True:
        await asyncio.sleep(60)
        LOGGER.info("Simulations listened: {:s}".format(", ".join(message_listener.listened_simulations)))


if __name__ == "__main__":
    asyncio.run(start_listener_component())
