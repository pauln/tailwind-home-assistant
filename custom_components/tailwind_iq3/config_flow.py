"""Config flow for tailwind_iq3."""
from __future__ import annotations
from typing import Any, Final
import logging

from homeassistant import config_entries
from homeassistant.const import (
    CONF_HOST,
    CONF_NAME,
    CONF_IP_ADDRESS,
    CONF_API_TOKEN,
)
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.typing import DiscoveryInfoType

import ipaddress
from scapy.layers.l2 import getmacbyip
import voluptuous as vol

from .const import DOMAIN, CONF_NUM_DOORS

_LOGGER: Final = logging.getLogger(__name__)


class TailwindConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    def __init__(self):
        """Initialize the config flow."""
        self._hostname = None
        self._name = "Tailwind iQ3"
        self._ip_address = None
        self._num_doors = 0
        self._api_token = ""

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        errors = {}
        if user_input is not None:
            if user_input[CONF_NAME] != "":
                self._name = user_input[CONF_NAME]

            mac = None
            try:
                ip_address = ipaddress.ip_address(user_input[CONF_IP_ADDRESS])
            except ValueError:
                # Invalid IP address specified.
                pass
            else:
                # IP address is valid.  Look up MAC address for unique ID.
                mac = getmacbyip(user_input[CONF_IP_ADDRESS])

            if ip_address is not None and mac is not None:
                # MAC address retrieved.
                # Build a unique ID matching what would be autodiscovered.
                flat_mac = mac.replace(":", "").lower()
                self._hostname = f"tailwind-{flat_mac}"
                await self.async_set_unique_id(self._hostname)
                self._abort_if_unique_id_configured({CONF_HOST: self._hostname})

                return self.async_create_entry(
                    title=self._name,
                    data=user_input,
                )

            errors["base"] = "invalid_ip"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_IP_ADDRESS,
                    ): str,
                    vol.Optional(
                        CONF_NAME,
                        default=self._name,
                    ): str,
                    vol.Required(
                        CONF_NUM_DOORS,
                        default=1,
                    ): vol.All(vol.Coerce(int), vol.Clamp(min=1, max=3)),
                    vol.Required(
                        CONF_API_TOKEN,
                    ): str,
                }
            ),
            errors=errors,
        )

    async def async_step_homekit(self, discovery_info: DiscoveryInfoType) -> FlowResult:
        self._ip_address = discovery_info.host
        self._hostname = discovery_info.hostname.replace(".local.", "")
        await self.async_set_unique_id(self._hostname)
        self._abort_if_unique_id_configured({CONF_HOST: self._hostname})

        return await self.async_step_discovery_confirm()

    async def async_step_zeroconf(
        self, discovery_info: DiscoveryInfoType
    ) -> FlowResult:
        self._ip_address = discovery_info.host
        self._hostname = discovery_info.hostname.replace(".local.", "")
        await self.async_set_unique_id(self._hostname)
        self._abort_if_unique_id_configured({CONF_HOST: self._hostname})

        return await self.async_step_discovery_confirm()

    async def async_step_discovery_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle user-confirmation of discovered node."""
        if user_input is not None:
            if user_input[CONF_NAME] != "":
                self._name = user_input[CONF_NAME]

            self._num_doors = user_input[CONF_NUM_DOORS]
            self._api_token = user_input[CONF_API_TOKEN]

            config_data = {
                CONF_HOST: self._hostname,
                CONF_IP_ADDRESS: self._ip_address,
                CONF_NUM_DOORS: self._num_doors,
                CONF_API_TOKEN: self._api_token,
            }
            return self.async_create_entry(
                title=self._name,
                data=config_data,
            )

        return self.async_show_form(
            step_id="discovery_confirm",
            description_placeholders={"name": self._hostname},
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_NAME,
                        default=self._name,
                    ): str,
                    vol.Required(
                        CONF_NUM_DOORS,
                        default=1,
                    ): vol.All(vol.Coerce(int), vol.Clamp(min=1, max=3)),
                    vol.Required(
                        CONF_API_TOKEN,
                    ): str,
                }
            ),
        )
