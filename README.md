# Ties2022

## Known Bugs

## Newly Updated

- add example code for sound => please check [/examples/sounds/](./examples/sounds)
- version 1 : robot can now following red color [/examples/v1](./examples/v1)

## Setup

### Installation

You should be running Python3.7+. To install all global project dependencies for python, use

```sh
pip3 install -r requirements.txt
```

## Structure

### Main code

Our main functional parts lie in different modules and are strictly splitted. Coupling to some degree is totally ok.

```bash
    src
    ├── main.py # Main end-point for a car
    ├── movement # High dev priority
    ├── sound # low dev priority
    └── vision # high research priority
```

### Tests and examples

For each module we have, we need to have the corresponding example subdir with the simple use case of existing functionality.

```bash
examples
├── movement
├── sound
└── vision

```

### Utils

Those are for third-party functions, e.g. to create a simple camera video stream via local http page

_tbc..._

```

```
