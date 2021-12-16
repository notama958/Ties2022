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
├── main.py     # Our main file which will be our main end-point for a car.
├── movement    # Module for all car movements. Ride, turn, use arm (high dev priority)
├── painting    # Module for painting the road marking (should be in movement? Low dev priority)
├── sound       # Module for making noize with the speaker (low dev priority)
└── vision		# Module for image processing (high research priority)

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

