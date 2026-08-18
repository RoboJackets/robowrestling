#include <Arduino.h>
#include <Servo.h>

#include "Pins.h"
#include "Movement.h"
#include "Strategies.h"

Servo myservo;
Movement robot;
Strategies strat(robot, myservo);   // <-- strategies object uses robot + servo
void printSensors();
enum RunMode {
  fightMode,
  leftMode,
  startMode,
  rightMode
};

void setup() {
  Serial.begin(9600);
  myservo.attach(ServoPin);
  pinMode(Rpos, OUTPUT);
  pinMode(Rneg, OUTPUT);
  pinMode(Lpos, OUTPUT);
  pinMode(Lneg, OUTPUT);

  pinMode(StartMod, INPUT);
  pinMode(switch1, INPUT);
  pinMode(switch2, INPUT);

  pinMode(lnl, INPUT);
  pinMode(lnr, INPUT);
  myservo.write(180);

}

void loop() {
  RunMode mode;
  int s1 = analogRead(switch1);
  int s2 = analogRead(switch2);

  if (s1 < 500 && s2 < 500)
    mode = startMode;
  else if( s1 > 500 && s2 < 500) //10
    mode = leftMode;
  else if (s1 < 500 && s2 > 500) //01
    mode = rightMode;
  else if (s1 > 500 && s2 > 500) //11
    mode = fightMode;

  switch (mode) {
    case startMode:
      strat.Slowfight();     // 00
      break;
    case leftMode:        // 10
      strat.leftFight();
      break;
    case rightMode:           // 01
      strat.rightFight();
      break;
    case fightMode:           // 11
      strat.forwardFight();
      break;
  }
}
