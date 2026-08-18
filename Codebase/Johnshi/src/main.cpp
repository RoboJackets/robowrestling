#include <Arduino.h>
#include <Servo.h>

#include "Pins.h"
#include "Movement.h"
#include "Strategies.h"

Servo myservo;
Movement robot;
Strategies strat(robot, myservo);   // <-- strategies object uses robot + servo

enum RunMode {
  frontMode,
  leftMode,
  slowMode,
  rightMode
};

void setup() {
  Serial.begin(9600);
  pinMode(Rpos, OUTPUT);
  pinMode(Rneg, OUTPUT);
  pinMode(Lpos, OUTPUT);
  pinMode(Lneg, OUTPUT);

  pinMode(StartMod, INPUT);
  pinMode(switch1, INPUT);
  pinMode(switch2, INPUT);

  pinMode(A0, INPUT);
  pinMode(A1, INPUT);

  pinMode(A6, INPUT);
  pinMode(A7, INPUT);
  randomSeed(analogRead(A5));

  myservo.attach(ServoPin);
  myservo.write(180); // 90 is deploy

}

void loop() {
  RunMode mode;
  int a6 = analogRead(A6);
  int a7 = analogRead(A7);

  if (a6 < 500 && a7 < 500)
    mode = slowMode;
  else if( a6 > 500 && a7 < 500)
    mode = leftMode;
  else if (a6 < 500 && a7 > 500)
    mode = rightMode;
  else if (a6 > 500 && a7 > 500)
    mode = frontMode;

  switch (mode) {
    case slowMode:
      strat.Slowfight();      // 00
      break;
    case leftMode:            // 10
      strat.leftFight();
      break;
    case rightMode:           // 01
      strat.rightFight();
      break;
    case frontMode:           // 11
      strat.forwardFight();
      break;
  }
}
