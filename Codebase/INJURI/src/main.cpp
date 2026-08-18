#include <Arduino.h>

#define LPOS 38
#define LNEG 39

#define RPOS 11
#define RNEG 12
#define RPWM 36
#define LPWM 37

#define START 13
#define LINE1 14 
#define LINE2 15

#define SENSOR1 2
#define SENSOR2 3
#define SENSOR3 4
#define SENSOR4 5
#define SENSOR5 6
#define SENSOR6 9
#define SENSOR7 10
void driveForward(int);
void driveBackward(int);
void setup() {
  Serial.begin(9600);
  pinMode(LPOS, OUTPUT);
  pinMode(LNEG, OUTPUT);
  pinMode(RPOS, OUTPUT);
  pinMode(RNEG, OUTPUT);

  pinMode(LPWM, OUTPUT);
  pinMode(RPWM, OUTPUT);

  pinMode(START, INPUT);

  pinMode(LINE1, INPUT);
  pinMode(LINE2, INPUT);

  pinMode(SENSOR1, INPUT);
  pinMode(SENSOR2, INPUT);
  pinMode(SENSOR3, INPUT);
  pinMode(SENSOR4, INPUT);
  pinMode(SENSOR5, INPUT);
  pinMode(SENSOR6, INPUT);
  pinMode(SENSOR7, INPUT);
  Serial.println("Setup complete");
}


void loop() {
  Serial.println(analogRead(LINE1));
  delay(50);

  driveForward(200);
  delay(1000);
  driveBackward(200);
  delay(1000);
}
void driveForward(int speedVal) {
  analogWrite(RPWM, speedVal);
  analogWrite(LPWM, speedVal);

  digitalWrite(RPOS, HIGH);
  digitalWrite(RNEG, LOW);
  digitalWrite(LPOS, HIGH);
  digitalWrite(LNEG, LOW);
}

void driveBackward(int speedVal) {
  analogWrite(RPWM, speedVal);
  analogWrite(LPWM, speedVal);

  digitalWrite(RPOS, LOW);
  digitalWrite(RNEG, HIGH);
  digitalWrite(LPOS, LOW);
  digitalWrite(LNEG, HIGH);
}
