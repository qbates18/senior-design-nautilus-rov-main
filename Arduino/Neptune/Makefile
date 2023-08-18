output: test.o Neptune.o
	g++ test.o Neptune.o -o output

test.o: test.cpp
	g++ -c test.cpp

Neptune.o: Neptune.cpp Neptune.h
	g++ -c Neptune.cpp

target: dependencies
	action

clean:
	del *.o output.exe