# Ties2022

## Setup
### Installation
You should be running Python3.7+. To install all global project dependencies for python, use
```sh
pip3 install -r requirements.txt
```

## Structure
### Main code

Our main functional parts lie in different modules and are strictly splitted. Coupling to some degree is totally ok.

src
├── main.py # Main end-point for a car
├── movement # High dev priority
├── painting # Low dev priority
├── sound # low dev priority    
└── vision # high research priority

### Tests and examples

For each module we have, we need to have the corresponding example subdir with the simple use case of existing functionality.

examples
├── movement
├── painting
├── sound
└── vision


### Utils

Those are for third-party functions, e.g. to create  a simple camera video stream via local http page

*tbc...*

