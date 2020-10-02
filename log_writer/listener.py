# -*- coding: utf-8 -*-

"""This module contains a listener simulation component that prints out all messages from the message bus."""

import asyncio
import json
import logging
from typing import List, Union

from log_writer.simulation import SimulationMetadata, SimulationMetadataCollection
from tools.callbacks import LOGGER as callback_logger
from tools.clients import RabbitmqClient
from tools.messages import AbstractMessage
from tools.tools import FullLogger

# No info logs about each received message stored.
callback_logger.level = max(callback_logger.level, logging.WARNING)
LOGGER = FullLogger(__name__)

STATISTICS_DISPLAY_INTERVAL = 120
STOP_WAIT_TIMER = 15


class ListenerComponent:
    """Class for the message bus listener component."""
    LISTENED_TOPICS = "#"

    def __init__(self):
        self.__rabbitmq_client = RabbitmqClient()
        self.__rabbitmq_client.add_listener(ListenerComponent.LISTENED_TOPICS, self.simulation_message_handler)

        self.__metadata_collection = SimulationMetadataCollection(stop_function=self.stop)
        self.__is_stopped = False

    async def stop(self) -> None:
        """Stops the log writer."""
        LOGGER.info("Stopping the log writer.")
        await self.__rabbitmq_client.close()
        self.__is_stopped = True

    @property
    def simulations(self) -> List[str]:
        """Returns the received simulation ids as a list."""
        return self.__metadata_collection.simulations

    @property
    def is_stopped(self) -> bool:
        """Returns True, if the log writer has been stopped and is not listening to messages anymore."""
        return self.__is_stopped

    def get_metadata(self, simulation_id: str) -> Union[SimulationMetadata, None]:
        """Returns the simulation metadata object corresponding to the given simulation identifier."""
        return self.__metadata_collection.get_simulation(simulation_id)

    async def simulation_message_handler(self, message_object: Union[AbstractMessage, dict, str],
                                         message_routing_key: str):
        """Handles the received simulation state messages."""
        if isinstance(message_object, str):
            try:
                message_json = json.loads(message_object)
                if isinstance(message_json, dict):
                    message_object = message_json
            except json.decoder.JSONDecodeError:
                LOGGER.warning("Received message could not be decoded into JSON format: {:s}".format(message_object))
                return

        if isinstance(message_object, dict):
            actual_message_object = AbstractMessage.from_json(message_object)
            if actual_message_object is None:
                LOGGER.warning(
                    "Could not create a message object from the received message: {:s}".format(str(message_object)))
                return
            message_object = actual_message_object

        if isinstance(message_object, AbstractMessage):
            LOGGER.debug("{:s} : {:s} : {:s}".format(
                message_routing_key, message_object.simulation_id, message_object.message_id))
            await self.__metadata_collection.add_message(message_object, message_routing_key)

        else:
            LOGGER.warning("Received '{:s}' message when expecting for '{:s}' message or a dictionary".format(
                str(type(message_object)), str(AbstractMessage)))


async def start_listener_component():
    """Start a listener component for the simulation platform."""
    message_listener = ListenerComponent()

    while not message_listener.is_stopped:
        # print out the statistics every two minutes
        await asyncio.sleep(STATISTICS_DISPLAY_INTERVAL)
        log_message = "\nSimulations listened:\n=====================\n"
        log_message += "\n".join([
            str(message_listener.get_metadata(simulation_id))
            for simulation_id in message_listener.simulations
        ])
        LOGGER.info(log_message)

    # short wait before exiting to allow all database writes to finish properly.
    asyncio.sleep(STOP_WAIT_TIMER)


if __name__ == "__main__":
    asyncio.run(start_listener_component())
