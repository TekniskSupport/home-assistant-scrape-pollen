from bs4 import BeautifulSoup
from datetime import timedelta,datetime
import requests, json

import logging
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (CONF_NAME)

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = 'Pollennivå'
CONF_SENSORS = 'sensors'

SENSOR_OPTIONS = {
    'city': ('Stad')
}

SCAN_INTERVAL = timedelta(hours=4)

SENSOR_ICONS = {
    'Al': 'mdi:leaf',
    'Alm': 'mdi:leaf',
    'Asp': 'mdi:leaf',
    'Björk': 'mdi:leaf',
    'Ek': 'mdi:leaf',
    'Gråbo': 'mdi:flower',
    'Gräs': 'mdi:flower',
    'Hassel': 'mdi:leaf',
    'Sälg': 'mdi:leaf',
    'default': 'mdi:leaf'
}

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Required(CONF_SENSORS, default=[]): vol.Optional(cv.ensure_list, [vol.In(SENSOR_OPTIONS)]),
})

def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the Pollen sensor."""
    name = config.get(CONF_NAME)
    sensors = config.get(CONF_SENSORS)
    allergens = [];

    for sensor in sensors:
        page =requests.get('https://pollenkoll.se/pollenprognos/' + sensor["city"])
        soup = BeautifulSoup(page.content, "html.parser")
        for days in soup.select('.pollen-city__day'):
            day=days.get("data-day")
            for item in days.select('.pollen-city__items .pollen-city__item'):
                level       = item.get('data-level')
                name        = item.select('.pollen-city__item-name')[0].text.strip()
                description = item.select('.pollen-city__item-desc')[0].text
                allergens.append({
                    'day' :        day,
                    'name':        name,
                    'description': description,
                    'level':       level
                });
                for zerolevel in days.select('.pollen-city__other-items .items span'):
                    print(zerolevel)
                    allergens.append({
                        'day' :        day,
                        'name':        zerolevel.text,
                        'description': 'Inga halter rapporterade',
                        'level':       0
                    });
    devices = []
    for allergen in allergens:
        devices.append(PollenkollSensor(allergen['name'], sensor, allergen))
    add_devices(devices, True)

# pylint: disable=no-member
class PollenkollSensor(Entity):
    """Representation of a Pollen sensor."""

    page = ""
    updatedAt = datetime.now().timestamp()

    def __init__(self, name, sensor, data, day=0):
        """Initialize a Pollen sensor."""
        self._item       = sensor
        self._city       = sensor['city']
        self._state      = data['level']
        self._day        = data['day']
        self._allergen   = data['name']
        self._name       = "{} {} day {}".format(name, self._city, str(self._day))
        self._attributes = data
        self._result     = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the device."""
        if self._state is not None:
            return self._state
        return None

    @property
    def device_state_attributes(self):
        """Return the state attributes of the monitored installation."""
        if self._attributes is not None:
            return self._attributes

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return ""

    @property
    def icon(self):
        """ Return the icon for the frontend."""
        if self._allergen in SENSOR_ICONS:
            return SENSOR_ICONS[self._allergen]
        return SENSOR_ICONS['default']

    def update(self):
        #update values
        if not PollenkollSensor.page or (datetime.now().timestamp() - PollenkollSensor.updatedAt) >= (3600*4):
            PollenkollSensor.page      = requests.get('https://pollenkoll.se/pollenprognos/' + self._city)
            PollenkollSensor.updatedAt = datetime.now().timestamp()
        self._result     = BeautifulSoup(PollenkollSensor.page.content, "html.parser")
        self._attributes = {}
        for days in self._result.select('.pollen-city__day'):
            day=days.get("data-day")
            for item in days.select('.pollen-city__items .pollen-city__item'):
                level       = item.get('data-level')
                name        = item.select('.pollen-city__item-name')[0].text.strip()
                description = item.select('.pollen-city__item-desc')[0].text
                sensorName = "{} {} day {}".format(name, self._city, str(self._day))
                if  self._name == sensorName:
                    self._state = level
                    self._attributes.update({"day": self._day})
                    self._attributes.update({"name": name})
                    self._attributes.update({"description": description})
                    self._attributes.update({"level": level})
            for zerolevel in days.select('.pollen-city__other-items .items span'):
                day         = day
                description = 'Inga halter rapporterade'
                level       = 0
                name        = zerolevel.text
                sensorName = "{} {} day {}".format(name, self._city, str(self._day))
                if  self._name == sensorName:
                    self._state = level
                    self._attributes.update({"day": self._day})
                    self._attributes.update({"name": name})
                    self._attributes.update({"description": description})
                    self._attributes.update({"level": level})
