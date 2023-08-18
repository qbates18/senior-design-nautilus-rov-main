#ifndef NEPTUNE_H
#define NEPTUNE_H

#include "Arduino.h"

class Parser{
public:
	Parser();
	void parse(char* data);
	int is_valid();
	uint32_t read_ackid();
	float read_thrusters(uint8_t index);
	int read_ltog();
	bool read_stog();
	int8_t read_camdir();
	char read_ltogop();
	int read_servo1();
	int read_servo2();
	int read_servo3();
	int read_servo4();
	int read_servo5();
	char ltogop1[10];
	float ltogop2,ltogop3, ltogop5, ltogop6;
	int ltogop4;
	float find_max(float,...);
	float find_max_thruster(float floatarray[], int start, int end);
	float find_max_thruster_closed(float floatarray[][1], int start, int end);
	float find_max_scaling(float float1, float float2, float float3);
	void multiply_matrices(float first[][3], float second[][1], float result[][1], int r1, int c1, int r2, int c2);

private:
	int _valid = 4;
	uint32_t _ackid = 0;
	float _thrusters[6];
	float _thrusters_signal[6];
		// [0] = VERTICAL
		// [1] = MANUEVERING_E
		// [2] = MANUEVERING_F
		// [3] = MANUEVERING_G
		// [4] = MANUEVERING_H
		// [5] = FORWARD
	bool _stog;
	int _ltog;
	int8_t _camdir;
	int servo1;
	int servo2;
	int servo3;
	int servo4;
	int servo5;
	float J45[4][3] = {
		{0.3536, -0.2537, -0.1667},
		{0.3536, 0.2537, 0.1667},
		{-0.3536, 0.2537, 0.1667},
		{-0.3536, -0.2537, -0.1667}
	};
	float J30[4][3] = {
		{0.2887, -0.2586, -0.25},
		{0.2887, 0.2586, 0.25},
		{-0.2887, -0.2586, -0.25},
		{-0.2887, -0.2586, -0.25}
	};
	float J60[4][3] = {
		{0.5, -0.2202, -0.1228},
		{0.5, 0.2202, 0.1228},
		{-0.5, 0.2202, 0.1228},
		{-0.5, -0.2202, -0.1228}
	};
	//char ltogop[10];
};


class Generator{
public:
	Generator();
	char* generate(uint32_t ackid, float pres, float temp, float head, float mDistance, bool leak, float voltage);

private:
	void add_next(char* input);
	void begin();
	void end();
	bool can_add(uint8_t size);
	static const uint8_t maxlen = 65;
	uint8_t _length;
	char _output[maxlen];
};

uint8_t count_digits(float num);

#endif