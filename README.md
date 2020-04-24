# Pollennivå

- place files in in custom components/pollenniva
- get city name from https://pollenkoll.se/pollenprognos/ (must be same as in URL)
- add to sensors.yaml (or under sensors: in configuration.yaml)

```
- platform: pollenniva
  sensors:
    - city: goteborg
```

- reboot homeasisstant
