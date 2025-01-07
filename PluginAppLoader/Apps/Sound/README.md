# Sound

The Sound App for RoboDK adds programmable sound effects and background music/noise to RoboDK stations.
You can use this App to create immersive VR stations.

## Features

- Add Sound: adds a sound effect to the selected robot program
- Add Sound Player Script: adds a special script for calling sound commands (this action is optional, it will still be executed automatically when the first sound effect is added)
- Toggle Sounds: enables or disables the sound playback server
- For sounds attached to objects, the volume will depend on the distance between the object and the RoboDK camera.

## Usage

Click on `Add Sound` to open the Add Sound Instruction dialog box. The following parameters are available in the dialog:
1. Instruction: defines the type of action to be taken
    - Play Sound (Blocking): starts playing a sound and pauses the program until the sound is played completely
    - Start Playing a Sound: starts playing sound and continues program execution
    - Wait for the End of Playback: pauses program execution until the previously played sound is completely played
    - Stop Playing a Sound: stops playback of the sound being played
    - Stop Playing All Sounds: stops playback of all previously played sounds
2. Robot Program: name of the robot program to which the audio instruction will be added (if the program does not exist, it will be created)
3. Sound File: name of the sound file to play (all sound files are stored in the `sounds` subfolder of the application)
4. Bind to: name of the object to which the sound is attached (use _Nothing_ for background playback)
5. Repeats: number of times the sound is repeated (not including the first playback)
6. Loop: enable infinite playback (only for non-blocking playback)
7. Volume Left: set the volume of the left channel
8. Volume Right: set the volume of the right channel


 ## Prerequisites
- [RoboDK](https://robodk.com/download)
- [RoboDK API](https://pypi.org/project/robodk/) (bundled with RoboDK)
- Content of requirements.txt, if any (automatically installed by RoboDK)


## Installation

Apps are usually packaged as RoboDK Packages (.rdkp), which are automatically installed when opened with RoboDK.
To manually install this App, copy this folder to your RoboDK Apps folder (typically `C:/RoboDK/Apps`).


## Configuration

1. Enable the Add-in Loader (Tools->Add-ins or Shift+I)
2. Enable the App (Tools->AppLoader or Shift+A)


## About RoboDK Apps

RoboDK allows you to easily load scripts and executable files as if they were plug-ins in RoboDK software.

You can integrate scripts as part of the RoboDK user interface and easily customize RoboDK for offline programming and simulation purposes. Adding scripts to an App will add buttons in the menu and the toolbar automatically. A settings file allows you to easily customize the appearance of a specific set of buttons/actions.

Once you complete developing your App you can easily distribute your App as a self-contained package file (.rdkp).

Apps are handled by RoboDK with the AppLoader Add-in, and [roboapps](https://robodk.com/doc/en/PythonAPI/robodk.html#roboapps-py) provides the necessary Python tools to build your App.

You can find more information about the AppLoader and sample Apps in the [AppLoader GitHub](https://github.com/RoboDK/Plug-In-Interface/tree/master/PluginAppLoader) and the [documentation](https://robodk.com/doc/en/PythonAPI/app.html).

For more information about the RoboDK API for Python, visit our [RoboDK documentation](https://robodk.com/doc/en/RoboDK-API.html) and the [RoboDK Python API documentation](https://robodk.com/doc/en/PythonAPI/index.html).
