/*
    
    Nathan Burke
    Mandeep Singh
    2021-2022 Nautilus Robot Arm Team
 */
 
/*
  GENERAL LIBRARIES
*/
#include <Wire.h>
#include <stdio.h>

/*
  LOCAL LIBRARIES
*/
#include <Adafruit_INA260.h>
#include "TSYS01.h"
#include "MS5837.h"
#include "Adafruit_Sensor.h"
#include "Adafruit_LSM303DLH_Mag.h"
#include "Neptune.h"
#include "ping1d.h"
#include "HCPCA9685.h"

/*
  COMPONENT LIBRARIES
*/
#include <Servo.h>


//lights 37
//servo 36
//ping 14 and 15
//leak 17-low 18-high 19-data

/*
  PINOUTS
*/
#define CAM_TILT 36
#define LIGHT_TOGGLE 37
#define SAMPLER_TOGGLE 6
#define LEAK 19

byte PORT_AFT_VECTOR_PIN = 4;
byte PORT_FWD_VECTOR_PIN = 5;
byte PORT_AFT_VERT_PIN = 6;
byte PORT_FWD_VERT_PIN = 7;
byte STBD_FWD_VERT_PIN = 8;
byte STBD_AFT_VERT_PIN = 9;
byte STBD_FWD_VECTOR_PIN = 10;
byte STBD_AFT_VECTOR_PIN = 11;

/*
#define T_VERTICAL 7
#define T_FORWARD 8
#define T_MANEUVERE 9
#define T_MANEUVERF 10
#define T_MANEUVERG 11
#define T_MANEUVERH 12
*/



/*
  GLOBAL DEFINES
*/
#define FLUID_DENSITY 997// kg/m^3 (997 freshwater, 1029 for seawater)
#define PWM_MID 1500 //the resting state value of the thruster
#define PWM_RANGE 400 //operating range of the thruster = [PWM_MID - PWM_RANGE, PWM_MID + PWM_RANGE]
/*
  GLOBAL VARIABLES
*/



MS5837 pres_sens;                  // pressure sensor
TSYS01 tmpr_sens;                  // temperature sensor
Adafruit_LSM303DLH_Mag_Unified head_sens = Adafruit_LSM303DLH_Mag_Unified(12345); // imu
Adafruit_INA260 ina260 = Adafruit_INA260(); //voltage sensor
HCPCA9685 HCPCA9685(0x41); // adafruit 16 channel servo driver on address 0x41 (default is 0x40, same as INA260)

Parser parser;
Generator generator;
Servo cam_tilt, light_toggle;
int cam_pos = 90;
float Pi = 3.14159;
unsigned long ack;
String str;
char message1[100];
bool leak = false;
bool isValid = false;
static Ping1D ping { Serial3 };
bool first_loop_flag = false;
unsigned long timeSinceLastMessage;

//Thrusters
Servo PORT_FWD_VERT;
Servo PORT_AFT_VERT;
Servo PORT_FWD_VECTOR;
Servo PORT_AFT_VECTOR;
Servo STBD_FWD_VERT;
Servo STBD_AFT_VERT;
Servo STBD_FWD_VECTOR;
Servo STBD_AFT_VECTOR;



void setup()
{
    Serial.begin(115200);
    //Serial1.begin(115200);
    //Serial2.begin(115200);
    Serial3.begin(115200);
    Wire.begin();

    PORT_FWD_VERT.attach(PORT_FWD_VERT_PIN);
    PORT_AFT_VERT.attach(PORT_AFT_VERT_PIN);
    PORT_FWD_VECTOR.attach(PORT_FWD_VECTOR_PIN);
    PORT_AFT_VECTOR.attach(PORT_AFT_VECTOR_PIN);
    STBD_FWD_VERT.attach(STBD_FWD_VERT_PIN);
    STBD_AFT_VERT.attach(STBD_AFT_VERT_PIN);
    STBD_FWD_VECTOR.attach(STBD_FWD_VECTOR_PIN);
    STBD_AFT_VECTOR.attach(STBD_AFT_VECTOR_PIN);

    PORT_FWD_VERT.writeMicroseconds(1500); // send "stop" signal to ESC.
    PORT_AFT_VERT.writeMicroseconds(1500); // send "stop" signal to ESC.
    PORT_FWD_VECTOR.writeMicroseconds(1500); // send "stop" signal to ESC.
    PORT_AFT_VECTOR.writeMicroseconds(1500); // send "stop" signal to ESC.
    STBD_FWD_VERT.writeMicroseconds(1500); // send "stop" signal to ESC.
    STBD_AFT_VERT.writeMicroseconds(1500); // send "stop" signal to ESC.
    STBD_FWD_VECTOR.writeMicroseconds(1500); // send "stop" signal to ESC.
    STBD_AFT_VECTOR.writeMicroseconds(1500); // send "stop" signal to ESC.

    delay(4000);
    
   if (!ina260.begin()) {
      Serial.println("Couldn't find INA260 chip");;
      while (1);
    }
    Serial.println("Found INA260 chip");
   
    // init pressure sensor
    while (!pres_sens.init()) {
      Serial.println("Pressure init failed!");
      Serial.println("\n\n\n");
      delay(5000);
    }
    Serial.println("Pressure init");
    pres_sens.setFluidDensity(FLUID_DENSITY); // kg/m^3 (freshwater, 1029 for seawater)
    
//    init temperature sensor
    tmpr_sens.init();
    Serial.println("Temp init");

    // init IMU sensor - Q: IMU is inertail measurement unit (compass heading + accelerometer)
    if (!head_sens.begin()) {
      Serial.println("IMU init failed!");
    }
    Serial.println("IMU init");

    //init altimeter (BlueRobotics Ping Sensor)
    while (!ping.initialize()) {
        Serial.println("\nPing device failed to initialize!");
        delay(1000); 
    }
    Serial.println("Ping init");

    // setup adafruit servo controller
    HCPCA9685.Init(SERVO_MODE);
    HCPCA9685.Sleep(false);
    Serial.println("Servo Controller initialized");

    // init camera tilt servo
    cam_tilt.attach(CAM_TILT);
    cam_tilt.write(cam_pos); //should be initialized to midpoint 90
    light_toggle.attach(LIGHT_TOGGLE);
    light_toggle.writeMicroseconds(1100); //light set to off
//    Serial.println('c');
    message1[0] = 'A';
    message1[1] = 'B';
    message1[2] = 'C';
    //Serial.print(message1);
    digitalWrite(52,LOW);
    
    pinMode(17, OUTPUT);
    pinMode(18, OUTPUT);
    pinMode(19, INPUT);

    digitalWrite(17, LOW);
    digitalWrite(18, HIGH);
    
    Serial.setTimeout(5); // should this be 6 to match topside timeout? or does that not particularly matter?
}

void loop()
{
  uint16_t i = 0;
  float heading, voltage;
  sensors_event_t event;
  digitalWrite(17, LOW);
  digitalWrite(18, HIGH);

  //Serial.println(leak);
  leak = digitalRead(19);

  
  //wait for data to be read on serial 
  while(Serial.available() == 0){
    
    if(first_loop_flag == true && (millis() - timeSinceLastMessage) > 5000){
      PORT_FWD_VERT.writeMicroseconds(1500); // send "stop" signal to ESC.
      PORT_AFT_VERT.writeMicroseconds(1500); // send "stop" signal to ESC.
      PORT_FWD_VECTOR.writeMicroseconds(1500); // send "stop" signal to ESC.
      PORT_AFT_VECTOR.writeMicroseconds(1500); // send "stop" signal to ESC.
      STBD_FWD_VERT.writeMicroseconds(1500); // send "stop" signal to ESC.
      STBD_AFT_VERT.writeMicroseconds(1500); // send "stop" signal to ESC.
      STBD_FWD_VECTOR.writeMicroseconds(1500); // send "stop" signal to ESC.
      STBD_AFT_VECTOR.writeMicroseconds(1500); // send "stop" signal to ESC.
            
      }


    //wait
    //digitalWrite(52,HIGH);

    
  }

  //receive nmea message from serial buffer
  while(Serial.available() > 0){
    //digitalWrite(52,LOW);
    str = Serial.readString();
    
    //Serial.println(str);
  }

 
  timeSinceLastMessage = millis();

  //converts string to char array in order for message to be in the correct format for the parser
  int str_len = str.length() + 1;
  char message[str_len];
  str.toCharArray(message,str_len);
  
//  Serial.println(message);

  //parse nmea message
  //parser.parse(str1);
   parser.parse(message);
   //Serial.println(parser.ltogop1);
   //Serial.println(parser.ltogop2);

   
  //assign values to components if message was valid
  if(parser.is_valid() == 1){

    //CAMERA TILT
    int cam_read = parser.read_camdir();
    if(cam_read == 2){
      cam_read = -1;
    }
    if(cam_pos + cam_read <= 180 && cam_pos + cam_read >= 0){
      cam_pos += cam_read;
      cam_tilt.write(cam_pos);
    }

    // ROBOT ARM
    HCPCA9685.Servo(0, parser.read_servo1()); //mounted on frame
    HCPCA9685.Servo(2, parser.read_servo2()); //shortest arm link
    HCPCA9685.Servo(12, parser.read_servo3()); //longest arm link
    HCPCA9685.Servo(14, parser.read_servo4()); //claw
    HCPCA9685.Servo(15, parser.read_servo5()); //not used by 2022-2023

    
    //LIGHTS
    if(parser.read_ltog() == 1){
      light_toggle.writeMicroseconds(1600);
    }
    if(parser.read_ltog() == 0){
      light_toggle.writeMicroseconds(1100);
    }



   // int vert_pull = parser.read_thrusters(0);
    //Serial.println(vert_pull);

    //SAMPLER
    if(parser.read_stog()){
      digitalWrite(SAMPLER_TOGGLE, !digitalRead(SAMPLER_TOGGLE));
    }

    //VERTICAL THRUSTERS
    int VERT_signal = (int) parser.read_thrusters(0);
    //Serial.println(signal);   
    PORT_FWD_VERT.writeMicroseconds(VERT_signal);
    PORT_AFT_VERT.writeMicroseconds(VERT_signal);
    STBD_FWD_VERT.writeMicroseconds(VERT_signal);
    STBD_AFT_VERT.writeMicroseconds(VERT_signal);
    //Serial.println(thruster_convert(parser.read_thrusters(0)));
    
    //MANUEVERING THRUSTERS

//    Serial.print("0:");
//    Serial.println(parser.ltogop6);
//    Serial.print("1:");
//    Serial.println(parser.ltogop2);
//    Serial.print("2:");
//    Serial.println(parser.ltogop3);
//    Serial.print("3:");
//    Serial.println(parser.ltogop5);
    
//    Serial.print("1:");
//    Serial.println(parser.read_thrusters(1));
//    Serial.print("2:");
//    Serial.println(parser.read_thrusters(2));
//    Serial.print("3:");
//    Serial.println(parser.read_thrusters(3));
//    Serial.print("4:");
//    Serial.println(parser.read_thrusters(4));
//    Serial.println("BREAK");

//    int STBD_FWD_VECTOR_signal = (int) parser.read_thrusters(1);
//    int STBD_AFT_VECTOR_signal = (int) parser.read_thrusters(3);
//    int PORT_FWD_VECTOR_signal = (int) parser.read_thrusters(2);
//    int PORT_AFT_VECTOR_signal = (int) parser.read_thrusters(4); 
      
    int STBD_FWD_VECTOR_signal = (int) parser.read_thrusters(1);
    int STBD_AFT_VECTOR_signal = (int) parser.read_thrusters(3);
    int PORT_FWD_VECTOR_signal = (int) parser.read_thrusters(2);
    int PORT_AFT_VECTOR_signal = (int) parser.read_thrusters(4); 

//    Serial.print("1:");
//    Serial.println(STBD_FWD_VECTOR_signal);
//    Serial.print("2:");
//    Serial.println(STBD_AFT_VECTOR_signal);
//    Serial.print("3:");
//    Serial.println(PORT_FWD_VECTOR_signal);
//    Serial.print("4:");
//    Serial.println(PORT_AFT_VECTOR_signal);
//    Serial.println("BREAK");
    
    STBD_FWD_VECTOR.writeMicroseconds(STBD_FWD_VECTOR_signal);
    STBD_AFT_VECTOR.writeMicroseconds(STBD_AFT_VECTOR_signal);
    PORT_FWD_VECTOR.writeMicroseconds(PORT_FWD_VECTOR_signal);
    PORT_AFT_VECTOR.writeMicroseconds(PORT_AFT_VECTOR_signal);

//    Serial.println(parser.ltogop4);
//    Serial.print("X:");
//    Serial.println(parser.ltogop2);
//    Serial.print("Y:");
//    Serial.println(parser.ltogop3);
//    Serial.print("ROT:");
//    Serial.println(parser.ltogop4);
//    Serial.print("A:");
//    Serial.println(parser.read_thrusters(1));
//    Serial.print("B:");
//    Serial.println(parser.read_thrusters(2));
//    Serial.print("C:");
//    Serial.println(parser.read_thrusters(3));
//    Serial.print("D:");
//    Serial.println(parser.read_thrusters(4));
//    Serial.println("-------------");
    
    //NOT USED ANYMORE
    //FORWARD THRUSTERS
    //digitalWrite(T_FORWARD, thruster_convert(parser.read_thrusters(5)));

    
  }
 //digitalWrite(52, HIGH);
  // read sensor values
  pres_sens.read();
  tmpr_sens.read();
  
  ping.update();
//  float mDistance = ping.distance() / 1000;
    float mDistance = 0;
  //float ftDistance = 0;
  
  head_sens.getEvent(&event);
  float MagX = (((event.magnetic.x-(-70.82)) * 61.3) / 97.91) + (-38.04);
  float MagY = (((event.magnetic.y-(-72.73)) * 56.44) / 101.37) + (-27.36);

  //heading = (atan2(event.magnetic.y, event.magnetic.x) * 180) / Pi;
  heading = (atan2(MagY, MagX) * 180) / Pi;
  // Normalize to 0-360
  if (heading < 0) {
    heading = 360 + heading;
  }

  //read from voltage sensor
  voltage = ina260.readBusVoltage() / 1000;
  //voltage = 0;
  
  
 //generate nmea message and send back up serial
  //Serial.println("Sending Response");
  //Serial1.println("Response");`
  //Serial1.println(generator.generate(ack, tmpr_sens.temperature(), pres_sens.pressure(), heading, ftDistance));
  Serial.println(generator.generate(ack, tmpr_sens.temperature(), pres_sens.depth(), heading, mDistance, leak, voltage));
  ack++;

  first_loop_flag = true;

}


unsigned int thruster_convert(float p){
  //returns a PWM value based on the percentage given and the PWM ranges defined
  return round(PWM_MID + p * PWM_RANGE);
}

void parse(char* data){
  Serial.println();
  static char receive_buffer[200];
  static char token1[10];
  static char token2[10];
  static char token3[10];
  static char token4[10];
  static char token5[10];
  static char token6[10];
  static char token7[10];
  static char token8[10];
  static char token9[10];
  static char token10[10];
  static char token11[10];
  static char token12[10];
  

  strcpy(receive_buffer, data);
  static char* field_ptr;
  static char* receive_buffer_ptr;
  receive_buffer_ptr = receive_buffer;
 
  for (int i = 0; i < 12; i++) {

    field_ptr = strsep(&receive_buffer_ptr, ", ");

    switch (i){
      case 0: 
        strcpy(token1,field_ptr);
        if(strcmp(token1, "$") == 0){
          isValid = true;
        }
        Serial.println(token1);
        break;
      case 1:
        strcpy(token2,field_ptr);
        Serial.println(token2); 
        break;
      case 2:
        strcpy(token3,field_ptr);
        Serial.println(token3);
        break;
      case 3:
        strcpy(token4,field_ptr);
        Serial.println(token4);
        break;
      case 4:
        strcpy(token5,field_ptr);
        Serial.println(token5);
        break;
      case 5:
        strcpy(token6,field_ptr);
        Serial.println(token6);
        break;      
      case 6:
        strcpy(token7,field_ptr);
        Serial.println(token7);  
        break;
      case 7:
        strcpy(token8,field_ptr);
        Serial.println(token8);
        break;
      case 8:
        strcpy(token9,field_ptr);
        Serial.println(token9);
        break;
      case 9:
        strcpy(token10,field_ptr);
        Serial.println(token10); // ARM_UP
        break;
      case 10:
        strcpy(token11, field_ptr);
        Serial.println(token11); // ARM_DN
        break;
      case 11:
        strcpy(token12, field_ptr);
        Serial.println(token12);
        break;
      default:
         Serial.println("DEFAULT OOPS");
         break;
    }
    //Serial.println(field_ptr);
    
    delay(100);
  }

}
