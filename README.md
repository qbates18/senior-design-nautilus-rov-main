# senior-design-nautilus-rov
Senior Design Project, working on Nautilus ROV for Robotics Systems Lab at Santa Clara University 2023-2024

This repo is currently version controlled by github here: https://github.com/qbates18/senior-design-nautilus-rov-main
For ease of use, the github desktop application is setup with this repo to easily pull from origin, commit, and push to origin without having to deal with terminal, with the added bonus of a helpful visualization of the changes made. 

------ STARTUP PROCEDURE ------

To start up Nautilus, first make sure all cables are properly connected. The tether should be connected securely on both ends (The blue box labeled FXTI and the spool with the rest of the tether). The tether interface (blue FXTI box) should be connected with the usb-b cable and the ethernet cable to the laptop (if video is not needed, the ethernet cable is not needed, but if video is needed the usb cable is still necessary for power to the FXTI). The power switch on the tether side of the tether interface should be in the on position, where it is to the left (farthest away from the tether connection). 

Once that is done, follow the procedure to power on Nautilus. If doing brief testing in the lab, one battery in the power tube (silver tube) is acceptable, but for any sustained testing (using thrusters for more than a minute or two) USE ALL THREE BATTERIES (this became a large issue in previous years when a group only used one battery at a deployment resulting in the battery becoming dangerously discharged). 

------ COMMON ISSUES ------

- If after you run main.py it throws a ModuleNotFound error, make sure that module is installed under the current version of python. For example, when this happened, the packages were all downloaded under the folder usr/.local/lib/python3.8, but the laptop was running python3.10. So, I was forced to redownload the packages individually using "pip3.10 install _____". Make sure you replace 3.10 with the current version if this is happening to you. You can check the current version using "python3 -V".

- If the logitech controller's little switch on the back is set to "D" instead of "X" The get_numaxes() function from pygame will return 4 eventually causing a index out of bounds error and crashing the topside in ps4.py. Move the switch back to "X" to solve this.
