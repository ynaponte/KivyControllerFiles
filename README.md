# KivyControllerFiles

The "Simpler" folder contains all files from my simpler design

The "kivyController" folder has all files needed to run main.py

To bypass the arduino read stuff do the following:

1. Go to ConfigWidget.analyser and remove the line "comunic.open_port(port_name)"
2. Go to PrincipalWidget.update_devices and change what "dispositivos_online"(sorry forgot to change to english)
   to a list with eleven char elements. The chars can be anything but zero means off.
3. When running the program just type anything on the first page and click "aplicar"
