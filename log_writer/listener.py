# -*- coding: utf-8 -*-

"""This module contains a listener simulation component that prints out all messages from the message bus."""

import asyncio
import logging
from typing import Any, Union

from log_writer.simulation import SimulationMetadataCollection
from tools.callbacks import LOGGER as callback_logger
from tools.clients import RabbitmqClient
from tools.messages import AbstractMessage
from tools.tools import FullLogger

# No info logs about each received message stored.
callback_logger.level = max(callback_logger.level, logging.WARNING)
LOGGER = FullLogger(__name__)

STATISTICS_DISPLAY_INTERVAL = 600


class ListenerComponent:
    """Class for the message bus listener component."""
    LISTENED_TOPICS = "#"

    def __init__(self):
        self.__rabbitmq_client = RabbitmqClient()
        self.__rabbitmq_client.add_listener(ListenerComponent.LISTENED_TOPICS, self.simulation_message_handler)

        self.__metadata_collection = SimulationMetadataCollection()

    @property
    def simulations(self):
        """Returns the received simulation ids as a list."""
        return self.__metadata_collection.simulations

    def get_metadata(self, simulation_id: str):
        """Returns the simulation metadata object corresponding to the given simulation identifier."""
        return self.__metadata_collection.get_simulation(simulation_id)

    async def simulation_message_handler(self, message_object: Union[AbstractMessage, Any], message_routing_key: str):
        """Handles the received simulation state messages."""
        if isinstance(message_object, AbstractMessage):
            LOGGER.debug("{:s} : {:s} : {:s}".format(
                message_routing_key, message_object.simulation_id, message_object.message_id))

            await self.__metadata_collection.add_message(message_object, message_routing_key)

        else:
            LOGGER.warning("Received '{:s}' message when expecting for '{:s}' message".format(
                str(type(message_object)), str(AbstractMessage)))


async def start_listener_component():
    """Start a listener component for the simulation platform."""
    message_listener = ListenerComponent()

    while True:
        # print out the statistics every ten minutes
        await asyncio.sleep(STATISTICS_DISPLAY_INTERVAL)
        log_message = "\nSimulations listened:\n=====================\n"
        log_message += "\n".join([
            str(message_listener.get_metadata(simulation_id))
            for simulation_id in message_listener.simulations
        ])
        LOGGER.info(log_message)


if __name__ == "__main__":
    asyncio.run(start_listener_component())
