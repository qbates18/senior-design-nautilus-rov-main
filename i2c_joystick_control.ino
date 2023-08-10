#include "HCPCA9685.h" // Include the HCPCA9685 library created by Andrew Davies

#define I2CAdd 0x40 // Default address of the PCA9685 Module

#define JoyX A0 // Joystick X pin connected to A0 on the UNO
#define JoyY A1 // Joystick Y pin connected to A1 on the UNO
#define JoySW 2 // Joystick switch pin connected to digital 2

// Used to store the mapping of the Joystick X and Y values
int ServoXforward;
int ServoYforward;
int toggle;
int currButtonState;
int lastButtonState;

HCPCA9685 HCPCA9685(I2CAdd); // Define Library to use I2C communication

void setup() 
{
  HCPCA9685.Init(SERVO_MODE); // Set to Servo Mode
  
  HCPCA9685.Sleep(false); // Wake up PCA9685 module
  pinMode(JoySW, INPUT_PULLUP);

  currButtonState = digitalRead(JoySW);
}


void loop() 
{
  lastButtonState = currButtonState;
  currButtonState = digitalRead(JoySW); 
  
  int val1X = analogRead(JoyX); // Read current value of Joystick 1 X axis
  int val1Y = analogRead(JoyY); // Read current value of Joystick 1 Y axis
  
  // Map Joystick Axis values to servo Min and Max position 
  ServoXforward = map(val1X, 0, 1023, 10, 420); // Used to move Servo 0
  
  ServoYforward = map(val1Y, 0, 1023, 10, 420); // Used to move Servo 4

   if(lastButtonState == HIGH && currButtonState == LOW) {
    toggle += 1;
    if (toggle > 1) {
      toggle = 0;
    }

    if (toggle == 1) {
      HCPCA9685.Servo(2, 420);
    }
    else {
      HCPCA9685.Servo(2, 10);
    }
  }
  
  // Move Servos to read postion from Joystick
  HCPCA9685.Servo(0, ServoXforward); // Move Servo 0 
  HCPCA9685.Servo(1, ServoYforward); // Move Servo 4
  
  delay(1);
}
