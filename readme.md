# Streaming Music Player

This is a streaming music player application built with Python and PySide6. It allows you to play music from various online radio stations.

## Requirements

To run this application, you need to install the following libraries:

- `PySide6`
- `numpy`
- `soundfile`
- `requests`

You can install these libraries using `pip`:

```sh
pip install PySide6 numpy soundfile requests
```
Creating an Executable with PyInstaller
To create an executable for the application using PyInstaller, follow these steps:
Install PyInstaller if you haven't already:

 ```sh
 pip install pyinstaller
 ```


Navigate to the directory containing `mediaAI.py`.


Run the following command to create the executable:

 ```sh
 pyinstaller --onefile --windowed mediaAI.py
 ```

 This will generate a `dist` folder containing the `mediaAI.exe` executable.

Creating an Installer with Inno Setup
To create an installer for the application using Inno Setup, follow these steps:
Download and install Inno Setup from [here](https://jrsoftware.org/isinfo.php).


Open Inno Setup and load the `setup.iss` script provided in the project.


Compile the script to create the installer.

This will generate an installer executable that you can use to install the Streaming Music Player application on other systems.
