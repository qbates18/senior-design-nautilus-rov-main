# senior-design-nautilus-rov
Senior Design Project, working on Nautilus ROV for Robotics Systems Lab at Santa Clara University 2023-2024

To start up Nautilus, first make sure all cables are properly connected. The tether should be connected securely on both ends (The blue box labeled FXTI and the spool of the rest of the tether). The tether interface (blue FXTI box) should be connected with the usb-b cable and the ethernet cable to the laptop (if video is not needed, the ethernet cable is not needed, but if vice versa, the usb cable is still needed for power to the FXTI). The power swtich on the tether side of the tether interface should be in the on position, where it is farthest away from the tether connection. 

Once that is done, follow the procedure to power on Nautilus. If doing brief testing, one battery is acceptable, but for any sustained testing (using thrusters for more than a minute or two) USE ALL THREE BATTERIES (this became a large issue in previous years when a group only used one battery at a deployment). 

It is important to start Nautilus first before the GUI on the laptop as Nautilus starts by waiting for a message from the laptop. The laptop starts by sending a message, then waiting for a response. If the laptop starts first and sends the message before Nautilus is powered up and waitng to recieve and respond, they will both get stuck waiting for each other to send a message. 

Once Nautilus is on and all conections are in place, the main GUI can be opened. With the working directory as /GUI, run "python3 main.py". The camera can be opened by clicking the button labeled "Windows" in the menu bar and choosing the "add camera" option from the drop down menu. NOTE: CURRENTLY THE CAMERA FUNCTIONALITY WITHIN THE GUI IS NOT WORKING! TO RUN THE CAMERA, OPEN A SEPERATE TERMINAL, RUN "cd /GUI/packages/camera/" THEN "python3 camtest.py". A NEW WINDOW SHOULD POP UP WITH THE CAMERA FEED AFTER ABOUT 30 SECONDS. 

To close the GUI, there is a "x" in the top right corner of the window which should prompt the user to quit. Alternitavely, the terminal which ran "python3 main.py" can be used to close the program. CTRL + C should force laptop to quit the GUI, though is most often necessary to spam CTRL + C several times until everything stops entirely. On VSCode, the keyboard shortcut "CTRL + SHIFT + ~" will bring up a fresh terminal if reopening the GUI is desired.