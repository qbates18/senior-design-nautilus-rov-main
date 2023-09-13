
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
  #include "Adafruit_LIS2MDL.h"
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
  #define FLATILUS 0 // <---------------- IF USING FLATILUS SET TO 1, IF USING NAUTLIUS SET TO 0 | This is because there are a few minor differences in hardware

  byte PORT_AFT_VECTOR_PIN = 4;
  byte PORT_FWD_VECTOR_PIN = 5;
  byte PORT_AFT_VERT_PIN = 6;
  byte PORT_FWD_VERT_PIN = 7;
  byte STBD_FWD_VERT_PIN = 8;
  byte STBD_AFT_VERT_PIN = 9;
  byte STBD_FWD_VECTOR_PIN = 10;
  byte STBD_AFT_VECTOR_PIN = 11;

/*
  GLOBAL DEFINES
*/
  #define FLUID_DENSITY 997// kg/m^3 (997 freshwater, 1029 for seawater)
  #define accelLimit 20 // microseconds (limits how fast the specktrum brushless motors accelerate) [FLATILUS ONLY]

/*
  GLOBAL VARIABLES
*/
  MS5837 pres_sens;                  // pressure sensor
  TSYS01 tmpr_sens;                  // temperature sensor
  Adafruit_LSM303DLH_Mag_Unified head_sens = Adafruit_LSM303DLH_Mag_Unified(12345); // old imu, currently on nautilus
  Adafruit_LIS2MDL magnometer = Adafruit_LIS2MDL(54321); //new IMU, currently on flatilus
  Adafruit_INA260 ina260 = Adafruit_INA260(); //voltage sensor on nautilus
  HCPCA9685 HCPCA9685(0x41); // adafruit 16 channel servo driver on address 0x41 (default is 0x40, nautilus magnometer has same)
  Parser parser;
  Generator generator;
  Servo cam_tilt, light_toggle;
  int cam_pos = 90;
  float Pi = 3.14159;
  unsigned long ack; //variable for message ID
  String str;
  //char message1[100]; Q: believe this is depricated
  bool leak = false;
  bool isValid = false; //var for "is the recieved message in a valid format?"
  static Ping1D ping { Serial3 }; //sets the echosounder to the third serial port
  bool first_loop_flag = false; //
  unsigned long timeSinceLastMessage;
  int currentHorizontalSignal, goalHorizontalSignal, currentVerticalSignal, goalVerticalSignal;


//Thrusters
  Servo PORT_FWD_VERT;
  Servo PORT_AFT_VERT;
  Servo PORT_FWD_VECTOR;
  Servo PORT_AFT_VECTOR;
  Servo STBD_FWD_VERT;
  Servo STBD_AFT_VERT;
  Servo STBD_FWD_VECTOR;
  Servo STBD_AFT_VECTOR;



void setup(){
  Serial.begin(115200);
  Serial.setTimeout(5);
  Serial3.begin(115200); //Q: using for ping sensor
  Wire.begin(); //required for I2C communication

  // Initialize thrusters
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

    currentHorizontalSignal=1500;
    currentVerticalSignal=1500;

    delay(5000);

  // Initialize voltage Sensor
    if(!FLATILUS){
    if (!ina260.begin()) {
        Serial.println("Couldn't find INA260 chip");;
        while (1);
      }
      Serial.println("Found INA260 chip");
    } else {
      pinMode(A0,INPUT);
    }
   
  // Initialize pressure sensor
    while (!pres_sens.init()) {
      Serial.println("Pressure init failed!");
      Serial.println("\n");
      delay(3000);
    }
    Serial.println("Pressure init");
    pres_sens.setFluidDensity(FLUID_DENSITY); // kg/m^3 (freshwater, 1029 for seawater)
    
  // Initialize temperature sensor
    tmpr_sens.init();
    Serial.println("Temp init");

  // Initialize IMU (heading) sensor
    if(!FLATILUS){
      if (!head_sens.begin()) { 
        Serial.println("IMU init failed!");
      } else{
        Serial.println("IMU init");
      }
    } else {
      if(!magnometer.begin()){
        Serial.println("IMU init failed!");
      } else{
        Serial.println("IMU init");
      }
    }
    

  // Initialize echosounder (altimiter)
    while (!ping.initialize()) {
        Serial.println("\nPing device failed to initialize!");
        delay(1000); 
    }
    Serial.println("Ping init");
  
  // Initialize adafruit servo controller
    HCPCA9685.Init(SERVO_MODE);
    HCPCA9685.Sleep(false);
    Serial.println("Servo Controller initialized");

  // Initialize camera tilt servo
    cam_tilt.attach(CAM_TILT);
    cam_tilt.write(cam_pos); //should be initialized to midpoint 90
    light_toggle.attach(LIGHT_TOGGLE);
    light_toggle.writeMicroseconds(1100); //light set to off
    
  // Initialize leak sensor
    pinMode(17, OUTPUT); //Leak ground
    pinMode(18, OUTPUT); //Leak VCC
    pinMode(19, INPUT); //Leak data

    digitalWrite(17, LOW);
    digitalWrite(18, HIGH);

}

void loop() {
  float heading, voltage, adVoltage, mDistance;
  sensors_event_t event;

  // ------ READ MESSAGE FROM TOPSIDE ------
    // Wait for a message to be available
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
      }

    // Recieve the message from the serial buffer
      while(Serial.available() > 0){
        str = Serial.readString();
      }
      timeSinceLastMessage = millis();
      
    // Convert recieved string to char array in order for the message to be in the correct format for the parser
      int str_len = str.length() + 1;
      char message[str_len];
      str.toCharArray(message,str_len);
    
    // Parse recieved message
      parser.parse(message);

  // ASSIGN RECIEVED VALUES TO  (if message was valid)
    if(parser.is_valid() == 1){
      // Tilt Camera Servo 
        int cam_read = parser.read_camdir();
        if(cam_read == 2){
          cam_read = -1;
        }
        if(cam_pos + cam_read <= 180 && cam_pos + cam_read >= 0){
          cam_pos += cam_read;
          cam_tilt.write(cam_pos);
        }
      
      if(!FLATILUS){
        // Light Toggle
          if(parser.read_ltog() == 1){
            light_toggle.writeMicroseconds(1600);
          }
          if(parser.read_ltog() == 0){
            light_toggle.writeMicroseconds(1100);
          }

        // NAUTILUS MOTION
          // Vertical Thrusters
            int VERT_signal = (int) parser.read_thrusters(0);
    
            PORT_FWD_VERT.writeMicroseconds(VERT_signal);
            PORT_AFT_VERT.writeMicroseconds(VERT_signal);
            STBD_FWD_VERT.writeMicroseconds(VERT_signal);
            STBD_AFT_VERT.writeMicroseconds(VERT_signal);

          // Maneuvering Thrusters
            int STBD_FWD_VECTOR_signal = (int) parser.read_thrusters(1);
            int STBD_AFT_VECTOR_signal = (int) parser.read_thrusters(3);
            int PORT_FWD_VECTOR_signal = (int) parser.read_thrusters(2);
            int PORT_AFT_VECTOR_signal = (int) parser.read_thrusters(4); 

            STBD_FWD_VECTOR.writeMicroseconds(STBD_FWD_VECTOR_signal);
            STBD_AFT_VECTOR.writeMicroseconds(STBD_AFT_VECTOR_signal);
            PORT_FWD_VECTOR.writeMicroseconds(PORT_FWD_VECTOR_signal);
            PORT_AFT_VECTOR.writeMicroseconds(PORT_AFT_VECTOR_signal);

          // Manipulator Servos
            HCPCA9685.Servo(0, parser.read_servo1()); //mounted on frame
            HCPCA9685.Servo(2, parser.read_servo2()); //shortest arm link
            HCPCA9685.Servo(12, parser.read_servo3()); //longest arm link
            HCPCA9685.Servo(14, parser.read_servo4()); //claw
            //HCPCA9685.Servo(15, parser.read_servo5()); Q: currently no servo5

      } else {
        // FLATILUS MOTION
          // Brushless Motors
            // read incoming values
              goalHorizontalSignal=parser.read_thrusters(2); //motor is set as port_fwd_vector, arduino pin 5
              goalVerticalSignal=parser.read_thrusters(0); //set as port_fwd_vertical, arduino pin 7

            // limit acceleration of the motors as they work weird when throttled quickly
              if(abs(currentHorizontalSignal-1500) < abs(goalHorizontalSignal-1500)) { //if accelerating
                //limit acceleration
                if(goalHorizontalSignal > 1500) { //if going forward
                  currentHorizontalSignal += accelLimit; //increase speed slightly
                } else { //if going reverse
                  currentHorizontalSignal += -accelLimit; //decrease speed slightly
                }
              } else { //if not accelerating
                //don't limit deceleration
                currentHorizontalSignal = goalHorizontalSignal;
              }

              if(abs(currentVerticalSignal-1500) < abs(goalVerticalSignal-1500)) { //if accelerating
                //limit acceleration
                if(goalVerticalSignal > 1500) { //if going upward
                  currentVerticalSignal += accelLimit; //increase speed slightly
                } else { //if going down
                  currentVerticalSignal += -accelLimit; //decrease speed slightly
                }
              } else { //if not accelerating
                //don't limit deceleration
                currentVerticalSignal = goalVerticalSignal;
              }        
            // send signal
              PORT_FWD_VECTOR.writeMicroseconds(currentHorizontalSignal);
              PORT_FWD_VERT.writeMicroseconds(currentVerticalSignal);

          // Manipulator Servos
            HCPCA9685.Servo(12,parser.read_servo1());
            HCPCA9685.Servo(0,parser.read_servo2());
      }      
    }
  
  // READ SENSOR VALUES
    // leak sensor
      digitalWrite(17, LOW);
      digitalWrite(18, HIGH);
      leak = digitalRead(19);

    // pressure/depth
      pres_sens.read(); //can take about 40ms

    // temperature
      tmpr_sens.read(); //can take about 40ms

    // echosounder
      ping.update();
      mDistance = ping.distance() / 1000;

    // IMU Sensor (heading)
      if(!FLATILUS){
        head_sens.getEvent(&event);
      } else {
        magnometer.getEvent(&event);
      }
      float MagX = (((event.magnetic.x-(-70.82)) * 61.3) / 97.91) + (-38.04);
      float MagY = (((event.magnetic.y-(-72.73)) * 56.44) / 101.37) + (-27.36);
      heading = (atan2(MagY, MagX) * 180) / Pi;
      // Normalize to 0-360
        if (heading < 0) {
          heading = 360 + heading;
        }

    // voltage
      if(!FLATILUS){
        voltage = ina260.readBusVoltage() / 1000;
      } else {
        adVoltage = float(analogRead(A0)) * 5 / 1023; //convert from analog signal to voltage
        voltage = adVoltage * 37500 / 7500 ; // MH voltage sensor is a basic voltage divider circuit, 7500 and 30000 are resistances
      }


  // Generate NMEA message and send back up through serial to topside laptop
    Serial.println(generator.generate(ack, tmpr_sens.temperature(), pres_sens.depth(), heading, mDistance, leak, voltage));
    ack++;

  first_loop_flag = true;
}
