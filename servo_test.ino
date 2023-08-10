
#include <Servo.h>
Servo myservo;
Servo myservo2;
int pos = 0;



void setup()
{

Serial.begin(9600);
while (!Serial);
myservo.attach(9);
myservo2.attach(10);
Serial.println("calibrating servo...");
for(pos = 0; pos <= 180; pos += 1)
myservo.write(0);
myservo2.write(0);
delay(1000);
myservo.write(180);
myservo2.write(180);
delay(1000);
myservo.write(90);
myservo2.write(90);
delay(1000);
Serial.println("servo calibrated");

}

void loop() {
  
for(pos = 0; pos <= 180; pos += 1)

if (Serial.available()) {
  int state = Serial.parseInt();
    
if (state < 0) {
Serial.println("cannost execute command, too low number");
}

if (state >= 10 && state < 181) {
  Serial.print("turning servo to ");
  Serial.print(state);
  Serial.println(" degrees");
  myservo.write(state);
  myservo2.write(state);
  
}

}

}
