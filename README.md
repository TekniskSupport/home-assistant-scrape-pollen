# Pollennivå

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge)](https://github.com/custom-components/hacs)

- place files in in [homeassistant-base]/custom_components/pollenniva
- get city name from https://pollenkoll.se/pollenprognos/ (must be same as in URL)
- add to sensors.yaml (or under sensors: in configuration.yaml)

```
- platform: pollenniva
  sensors:
    - city: goteborg
```

- reboot homeasisstant
