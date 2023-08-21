#include "Neptune.h"


using namespace std;

Parser::Parser(){
	for(int i = 0; i < 6; i++){
		this->_thrusters[i] = 0;
	}

	this->_valid = 4;
	this->_ackid = 0;
	this->_ltog = false;
	this->_stog = false;
	this->_camdir = 0;
	this->ltogop1;
	this->servo1 = 0;
	this->servo2 = 0;
	this->servo3 = 0;
	this->servo4 = 0;
	this->servo5 = 0;
}

void Parser::parse(char* data){
float angle, man_thrust, rot_thrust;
/* 	char *tokens[10];
	char *token;
	char *cstr;
	uint8_t i = 0;
	float angle, man_thrust, rot_thrust;

	cstr = new char [strlen(data)+1];
	strcpy(cstr, data);
	token = strtok(cstr, ",");
	
	while(token != NULL and i < 10){
		tokens[i] = token;
		ltogop[i] = token;
		token = strtok(NULL, ", ");
		i++;
		
	}
 */
  static char receive_buffer[200];
  char tokens0[10];
  char tokens1[10];
  char tokens2[10];
  char tokens3[10];
  char tokens4[10];
  char tokens5[10];
  char tokens6[10];
  char tokens7[10];
  char tokens8[10];
  char tokens9[10];
  char tokens10[10];
  char tokens11[10];
  char tokens12[10];
  char tokens13[10];
  char tokens14[10];
  char tokens15[10];
  char c = 'Q';


  strcpy(receive_buffer, data);
  static char* field_ptr;
  static char* receive_buffer_ptr;
  receive_buffer_ptr = receive_buffer;
 
  for (int i = 0; i < 16; i++) {

    field_ptr = strsep(&receive_buffer_ptr, ",");

    switch (i){
      case 0: 
        strcpy(tokens0,field_ptr);
        break;
      case 1:
        strcpy(tokens1,field_ptr);
		break;
      case 2:
        strcpy(tokens2,field_ptr);
        break;
      case 3:
        strcpy(tokens3,field_ptr);
        break;
      case 4:
        strcpy(tokens4,field_ptr);
        break;
      case 5:
        strcpy(tokens5,field_ptr);
        break;      
      case 6:
        strcpy(tokens6,field_ptr);
        break;
      case 7:
        strcpy(tokens7,field_ptr);
        break;
      case 8:
        strcpy(tokens8,field_ptr);
        break;
      case 9:
        strcpy(tokens9,field_ptr);
		this->ltogop4 = atoi(tokens9);
        break;
	  case 10:
	  	strcpy(tokens10, field_ptr);
		this->servo1 = atoi(tokens10); // Servo 1
		break;
	  case 11:
	  	strcpy(tokens11, field_ptr);
		this->servo2 = atoi(tokens11); // Servo 2
		break;
	  case 12:
	  	strcpy(tokens12, field_ptr);
		this->servo3 = atoi(tokens12); // Servo 3
		break;
      case 13:
	  	strcpy(tokens13, field_ptr);
		this->servo4 = atoi(tokens13); // Servo 4
		break;
      case 14:
	  	strcpy(tokens14, field_ptr);
		this->servo5 = atoi(tokens14); // Servo 5
		break;
	  case 15:
	    strcpy(tokens15, field_ptr);
		break;
      default:
         strcpy(tokens0,"DEFAULT OOPS");
         break;
    }

  } //end parsing for loop

	//FOR OLD VECTOR
	// tokens0 = begin message character $
	// tokens1 = ack_id
	// tokens2 = joystick magnitude
	// tokens3 = joystick angle
	// tokens4 = vertical thruster
	// tokens5 = rotation instructions
	// tokens6 = light toggle
	// tokens7 = sampler signal
	// tokens8 = camera tilt
	// tokens9 = end of message

	//FOR NICK's VECTOR
	// tokens0 = begin message character $
	// tokens1 = ack_id
	// tokens2 = L_joystick x
	// tokens3 = L_joystick y
	// tokens4 = vertical thruster
	// tokens5 = rotation instructions
	// tokens6 = light toggle
	// tokens7 = sampler signal
	// tokens8 = camera tilt
	// tokens9 = closed loop
	// toeksn10 = end of message

	//check for start string character 
	int x = strcmp(tokens0, "$");
	if(x == 0){
		//this->_ackid = 1;
		this->_valid = 1;
	}
	else{
		this->_valid = 24;
		//this->_ltogop = *tokens[1];
	}

	if(atoi(tokens1) >= 0)
		//this->_ackid = atoi(tokens1);

	//assign thruster values based on thruster mapping
	//thruster values are -1 < x < 1, a -100% to 100% range
	//values are scaled at arduino based on pwm range

	// VERTICAL THRUSTERS
	// thrusters[0] = A, B, C, D
	this->_thrusters[0] = ((atof(tokens4))*(-400)) + 1500;

	//this->ltogop2 = this->_thrusters[0];
	//this->ltogop2 = atof(tokens4);
	// MANUEVERING THRUSTERS
	//man = COS(angle in radians)*mag*sqrt(2)*0.5
	//rot = (rotation*(1-(sqrt(2)/2)))

	//angle = atof(tokens3) * M_PI/180;
	//man_thrust = cos(angle) * atof(tokens2) * sqrt(2) * 0.5;
	//rot_thrust = atof(tokens5) * (1 - sqrt(2) * 0.5);

	float x_axis = atof(tokens2);
	float y_axis = atof(tokens3);
	float rot = atof(tokens5);

	//add deazone for the joystick input
		if (abs(x_axis) < 0.1){ 
			x_axis=0;
		}
		if (abs(y_axis) < 0.1) {
			y_axis=0
		}
		if (abs(rot) < 0.1) {
			rot=0
		}

	this->ltogop2 = x_axis;
	this->ltogop3 = y_axis;
	this->ltogop5 = rot;
	//this->ltogop4 = rot;

	float C[3][1] = {
			{x_axis},
			{y_axis},
			{rot}
		};

	float result[4][1];


	switch (atoi(tokens9))
	{
	case 0:
			this->_thrusters[1] = 1500;
			this->_thrusters[2] = 1500;
			this->_thrusters[3] = 1500;
			this->_thrusters[4] = 1500;
			this->_thrusters[0] = 1500;
	break;	
	case 1: //if arm value is 1

		if(x_axis == 0 & y_axis == 0 & rot ==0){
			//if all values are zero, then set to zero
			this->_thrusters[1] = 1500;
			this->_thrusters[2] = 1500;
			this->_thrusters[3] = 1500;
			this->_thrusters[4] = 1500;
		}
		else{
			//combine vectored joystick inputs
			// thrusters[1] = Av
			this->_thrusters_signal[1] = (-1*x_axis) + y_axis + (-1*rot); 

			// thrusters[2] = Bv
			this->_thrusters_signal[2] = x_axis + y_axis + rot;

			// thrusters[3] = Cv
			this->_thrusters_signal[3] = (-1*x_axis) + (-1*y_axis) + rot;

			// thrusters[4] = Dv
			this->_thrusters_signal[4] = x_axis + (-1*y_axis) + (-1*rot);

			//Find normalizing and scaling factor
			float norm_factor = abs(find_max_thruster(this->_thrusters_signal, 1, 4));
			float scaling_factor = find_max_scaling(abs(x_axis), abs(y_axis), abs(rot));
			//this->ltogop2 = norm_factor;
		
			//Normalize and Scale for Gains
			float normalizedA = (scaling_factor*this->_thrusters_signal[1])/norm_factor;
			float normalizedB = (scaling_factor*this->_thrusters_signal[2])/norm_factor;
			float normalizedC = (scaling_factor*this->_thrusters_signal[3])/norm_factor;
			float normalizedD = (scaling_factor*this->_thrusters_signal[4])/norm_factor;

			// this->_thrusters[1] = normalizedA;
			// this->_thrusters[2] = normalizedB;
			// this->_thrusters[3] = normalizedC;
			// this->_thrusters[4] = normalizedD;

			//Convert to final ESC values
			this->_thrusters_signal[1] = round((400*normalizedA) + 1500);
			this->_thrusters_signal[2] = round((400*normalizedB) + 1500);
			this->_thrusters_signal[3] = round((400*normalizedC) + 1500);
			this->_thrusters_signal[4] = round((400*normalizedD) + 1500);

			if(this->_thrusters_signal[1] >= 1100 && this->_thrusters_signal[1] <=1900){
				this->_thrusters[1]	 = this->_thrusters_signal[1];
			}

			if(this->_thrusters_signal[2] >= 1100 && this->_thrusters_signal[2] <= 1900){
				this->_thrusters[2] = this->_thrusters_signal[2];
			}	

			if(this->_thrusters_signal[3] >= 1100 && this->_thrusters_signal[3] <= 1900){
				this->_thrusters[3]	 = this->_thrusters_signal[3];
			}

			if(this->_thrusters_signal[4] >= 1100 && this->_thrusters_signal[4] <= 1900){
				this->_thrusters[4] = this->_thrusters_signal[4];
			}	

			// this->_thrusters[1] = round((400*normalizedA) + 1500);
			// this->_thrusters[2] = round((400*normalizedB) + 1500); 
			// this->_thrusters[3] = round((400*normalizedC) + 1500);
			// this->_thrusters[4] = round((400*normalizedD) + 1500);

		}
		break;
	
	case 2: //heading lock is on
		{
			multiply_matrices(J45, C, result, 4, 3, 3, 1);
			//this->_thrusters[1] = 1465;
			//this->_thrusters[2] = 1465;
			//this->_thrusters[3] = 1465;
			//this->_thrusters[4] = 1465;
		
			float scaling_factor_closed = find_max_scaling(abs(x_axis), abs(y_axis), abs(rot));
			float norm_factor_closed = abs(find_max_thruster_closed(result, 0, 3));
		
			for(int i = 0; i < 4; i++){
				result[i][1] = result[i][1] * scaling_factor_closed * norm_factor_closed * 365;
			}
		
			for(int i = 0; i < 4; i++){
				result[i][1] = result[i][1] + 1465;
			}

			if(result[0][1] >= 1100 && result[0][1] <=1900){
				this->_thrusters[1]	 = result[0][1];
			}

			if(result[1][1] >= 1100 && result[1][1] <= 1900){
				this->_thrusters[2] = result[1][1];
			}	

			if(result[2][1] >= 1100 && result[2][1] <= 1900){
				this->_thrusters[3]	 = result[2][1];
			}

			if(result[3][1] >= 1100 && result[3][1] <= 1900){
				this->_thrusters[4] = result[3][1];
			}
		}
		break;
	
	default:
		this->_thrusters[1] = 1500;
		this->_thrusters[2] = 1500;
		this->_thrusters[3] = 1500;
		this->_thrusters[4] = 1500;
		break;
	}

//OLD VECTOR THRUST SWITCHING OUT FOR NICK'S METHOD
/*
	// thrusters[1] = E
	this->_thrusters[1] = man_thrust - rot_thrust; 

	// thrusters[2] = F
	this->_thrusters[2] = -man_thrust + rot_thrust;

	// thrusters[3] = G
	this->_thrusters[3] = man_thrust + rot_thrust;

	// thrusters[4] = H
	this->_thrusters[4] = -man_thrust - rot_thrust;

	//FORWARD THRUSTERS
	// thrusters[5] = I, J
	this->_thrusters[5] = sin(angle) * atof(tokens2);
*/

	// light toggle
	if(strcmp(tokens6, "T") == 0){
		if(this->_ltog == 0){
			this->_ltog = 1;
		}
		else{
			this->_ltog = 0;
		}
	}


	// sample toggle
	if(tokens7 == "T"){
		this->_stog = true;
	}
	else if(tokens7 == "F"){
		this->_stog = false;
	
	}
	else{
		//this->_valid = 16;
		this->_stog = false;
	}


	char token_8 = tokens8[0];
	ltogop1[0] = token_8;

	if(token_8 == 'U'){
		this->_camdir = 1;
	}

	if(token_8 == 'S'){
		this->_camdir = 0;
	}
	
	if(token_8 == 'D'){
		this->_camdir = 2;
	}

	// switch(token_8) {
	// 	case 'U' : {
	// 		this->_camdir = 1;
	// 		break;
	// 	} 
	// 	case 'S' : {
	// 		this->_camdir = 0;
	// 		break;
	// 	}
	// 	case 'D' : {
	// 		this->_camdir = -1;
	// 	}

	// 	default : {
	// 		this->_camdir = 0;
	// 	}
	// }


}

int Parser::is_valid(){
	return this->_valid;
}

uint32_t Parser::read_ackid(){
	return this->_ackid;
}

float Parser::read_thrusters(uint8_t index){
	if(index >= 0 && index <= 10)
		return this->_thrusters[index];
	return 0;	
}

int Parser::read_ltog(){
	return this->_ltog;
}

char Parser::read_ltogop(){
	return *this->ltogop1;
}

bool Parser::read_stog(){
	return this->_stog;
}

int8_t Parser::read_camdir(){
	return this->_camdir;
}

int Parser::read_servo1() {
	return this->servo1;
}

int Parser::read_servo2() {
	return this->servo2;
}

int Parser::read_servo3() {
	return this->servo3;
}

int Parser::read_servo4() {
	return this->servo4;
}

int Parser::read_servo5() {
	return this->servo5;
}

float Parser::find_max_thruster(float floatarray[], int start, int end){
	float num, max, min;

    num = floatarray[start];
	max = min = num;
	//i iterates from 1 to 5 because only thrusters[1-4] need to be accessed
    for (int i = start; i < end; i++)
    { 
        num = floatarray[i];
        if (max < num)
            max = num;
        else if (min > num)
            min = num;
    }
    return max;
}

float Parser::find_max_thruster_closed(float floatarray[][1], int start, int end){
	float num, max, min;

    num = floatarray[0][1];
	max = min = num;
	//i iterates from 1 to 5 because only thrusters[1-4] need to be accessed
    for (int i = start; i < end; i++)
    { 
        num = floatarray[i][1];
        if (max < num)
            max = num;
        else if (min > num)
            min = num;
    }
    return max;
}

float Parser::find_max_scaling(float float1, float float2, float float3){
	float floatarray[3] = {float1, float2, float3};
	float num, max, min;

    num = floatarray[0];
	max = min = num;
	
    for (int i = 0; i < 3; i++)
    { 
        num = floatarray[i];
        if (max < num)
            max = num;
        else if (min > num)
            min = num;
    }
    return max;
}

void Parser::multiply_matrices(
					  float first[][3],
                      float second[][1],
                      float result[4][1],
                      int r1, int c1, int r2, int c2){

   // Initializing elements of matrix mult to 0.
   for (int i = 0; i < r1; ++i) {
      for (int j = 0; j < c2; ++j) {
         result[i][j] = 0;
      }
   }

   // Multiplying first and second matrices and storing it in result
   for (int i = 0; i < r1; ++i) {
      for (int j = 0; j < c2; ++j) {
         for (int k = 0; k < c1; ++k) {
            result[i][j] += first[i][k] * second[k][j];
         }
      }
   }
}


Generator::Generator(){

}

char* Generator::generate(uint32_t ackid, float tmpr, float pres, float head, float mDistance, bool leak, float voltage){
	uint8_t length;	
	char buffer[65];

	this->begin();

	//0 < id < 4294967295
	//max 10 characters
	//sprintf(buffer, "%lu", ackid);
	itoa(ackid, buffer, 10);
	add_next(buffer);

	//-40 < t < 125, .00 precision, celsius
	//max 6 characters
	//sprintf(buffer, "%.2f", tmpr);
	dtostrf(tmpr, count_digits(tmpr) + 3, 2, buffer);
	add_next(buffer);

	//0 < p < 30000, .00 precision, mbar
	//max 8 characters
	//sprintf(buffer, "%.2f", pres);
	dtostrf(pres, count_digits(pres) + 3, 2, buffer);
	add_next(buffer);

	//0 < x < 360, .00 precision
	//max 6 characters
	//sprintf(buffer, "%.2f", head);
	dtostrf(head, count_digits(head) + 3, 2, buffer);
	add_next(buffer);

	dtostrf(mDistance, count_digits(mDistance) + 3, 2, buffer);
	add_next(buffer);

	dtostrf(leak, count_digits(leak) + 3, 2, buffer);
	add_next(buffer);

	dtostrf(voltage, count_digits(voltage) + 3, 2, buffer);
	add_next(buffer);

	end();

	return this->_output;

}

void Generator::add_next(char* input){
	

	if(can_add(2)){
		strcat(this->_output, ", ");
		this->_length += 2;
		if(can_add(strlen(input))){
			strncat(this->_output, input, strlen(input));
			this->_length += strlen(input);
		}
		//if input value is too large, don't add it
		

	}

}

void Generator::begin(){
	//resets the output string and the length counter
	//adds the start symbol and null character

	strcpy(this->_output, "$");
	this->_length = 1;
}


void Generator::end(){
	if(can_add(3)){
		strcat(this->_output, ", *");
		this->_length += 3;
	}
}

bool Generator::can_add(uint8_t size){
	return (strlen(this->_output) + size < this->maxlen); 	
}

uint8_t count_digits(float num){
	//counts how many whole digits are in the number
	uint8_t length = 1;

	if(abs(num) > 10000){
		length = 5;
	}

	else if(abs(num) > 1000){
		length = 4;
	}

	else if(abs(num) > 100){
		length = 3;
	}
	else if(abs(num) > 10){
		length++;
	}

	if(num < 0)
		length++;
}

