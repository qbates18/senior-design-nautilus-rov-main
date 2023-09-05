# senior-design-nautilus-rov
Senior Design Project, working on Nautilus ROV for Robotics Systems Lab at Santa Clara University 2023-2024

This repo is currently version controlled by github here: https://github.com/qbates18/senior-design-nautilus-rov-main
For ease of use, the github desktop application is setup with this repo to easily pull from origin, commit, and push to origin without having to deal with terminal, with the added bonus of a helpful visualization of the changes made. 

To start up Nautilus, first make sure all cables are properly connected. The tether should be connected securely on both ends (The blue box labeled FXTI and the spool with the rest of the tether). The tether interface (blue FXTI box) should be connected with the usb-b cable and the ethernet cable to the laptop (if video is not needed, the ethernet cable is not needed, but if video is needed the usb cable is still necessary for power to the FXTI). The power swtich on the tether side of the tether interface should be in the on position, where it is to the left (farthest away from the tether connection). 

Once that is done, follow the procedure to power on Nautilus. If doing brief testing, one battery in the main power tube (silver tube) is acceptable, but for any sustained testing (using thrusters for more than a minute or two) USE ALL THREE BATTERIES (this became a large issue in previous years when a group only used one battery at a deployment resulting in the battery becoming dangerously discharged). 

It is important to start Nautilus first before the GUI on the laptop as the Arduino on the ROV starts by waiting for a message from the laptop. The laptop starts by sending a message, then waiting for a response from the Arduino. If the laptop starts first and sends the message before Nautilus is powered up and waitng to recieve and respond, they will both get stuck waiting for each other to send a message. 

Once Nautilus is on and all conections are in place, the main GUI can be opened. With the working directory as /GUI, run "python3 main.py". The camera can be opened by clicking the button labeled "Windows" in the menu bar and choosing the "add camera" option from the drop down menu. NOTE: CURRENTLY THE CAMERA FUNCTIONALITY WITHIN THE GUI IS NOT WORKING! TO RUN THE CAMERA, OPEN A SEPERATE TERMINAL, RUN "cd /GUI/packages/camera/" THEN "python3 camtest.py". A NEW WINDOW SHOULD POP UP WITH THE CAMERA FEED AFTER ABOUT 30 SECONDS. 

To close the GUI, there is a "x" in the top right corner of the window which should prompt the user to quit. Alternitavely, the terminal which ran "python3 main.py" can be used to close the program. CTRL + C should force laptop to quit the GUI, though is most often necessary to spam CTRL + C several times until everything stops entirely. On VSCode, the keyboard shortcut "CTRL + SHIFT + ~" will bring up a fresh terminal if reopening the GUI is desired.

COMMON ISSUES

- If after you run main.py it throws a ModuleNotFound error, make sure that module is installed under the current version of python. For example, when this happened, the packages wer all downloaded under the folder usr/.local/lib/python3.8, but the laptop was running python3.10. So, I was forced to redownload the packages individually using "pip3.10 install _____". Make sure you replace 3.10 with the current version if this is happening to you. You can check the current version using "python3 -V".

