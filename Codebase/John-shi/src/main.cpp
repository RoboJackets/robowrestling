#include <Arduino.h>
#include <Servo.h>

#include "Pins.h"
#include "Movement.h"
#include "Strategies.h"

Servo myservo;
Movement robot;
Strategies strat(robot, myservo);   // <-- strategies object uses robot + servo

enum RunMode {
  dashTurtleMode,
  leftMode,
  turtleMode,
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

  pinMode(lineLeft, INPUT);
  pinMode(lineRight, INPUT);

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
    mode = turtleMode;
  else if( a6 > 500 && a7 < 500)
    mode = leftMode;
  else if (a6 < 500 && a7 > 500)
    mode = rightMode;
  else if (a6 > 500 && a7 > 500)
    mode = dashTurtleMode;

  switch (mode) {
    case turtleMode:
      strat.turtle();      // 00
      break;
    case leftMode:            // 10
      strat.leftFight();
      break;
    case rightMode:           // 01
      strat.rightFight();
      break;
    case dashTurtleMode:           // 11
      strat.dashTurtle();
      break;
  }
}
