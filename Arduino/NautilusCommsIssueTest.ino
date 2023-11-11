  unsigned long i=0;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);

}

void loop() {
  // put your main code here, to run repeatedly:
    Serial.print("$,");
    Serial.print(i);
    Serial.println(", 21.21, 0.01, 333.33, 70, 1, 16.4, *");
    delay(50);
    i++;
  
  //Serial.println("$, 21, 21.21, 0.01, 333\xfc.33, 70, 1, 16.4, *");
}
