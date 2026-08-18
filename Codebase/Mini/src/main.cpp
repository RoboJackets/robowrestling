#include <Arduino.h>
#include <Servo.h>

#include "Pins.h"
#include "Movement.h"

Movement robot;

enum RunMode {
  fightMode,
  disabledMode,
  startMode,
  snakeMode
};
void snake();
void slow();
void fast();
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

  pinMode(9, INPUT);

  // delay(1000);
  // while (!digitalRead(StartMod)) {}
  // delay(5000);
}
bool state = false;

void slow() {
  if (digitalRead(StartMod)) {  // If StartMod is enabled
      if (analogRead(A0) < 100 && !digitalRead(LSensor) && !digitalRead(RSensor))
        robot.lineRight();
      if (analogRead(A1) < 100 && !digitalRead(LSensor) && !digitalRead(RSensor))
        robot.lineLeft();

      if (digitalRead(LSensor) && digitalRead(RSensor)) {
        robot.waitSlam(180, 2);
      } else if (digitalRead(Rside)) {
        robot.rotateRight(160);
        delay(20);
      } else if (digitalRead(Lside)) {
        robot.rotateLeft(160);
        delay(20);
      } else if (digitalRead(RSensor)) {
        robot.rotateRight(160);
      } else if (digitalRead(LSensor)) {
        robot.rotateLeft(160);
      } else {
        robot.forward(40);
      }
  }
  else {
    robot.forward(0);
  }
}

void fast() {
  if (digitalRead(StartMod)) {  // If StartMod is enabled
      if (analogRead(A0) < 100 && !digitalRead(LSensor) && !digitalRead(RSensor))
        robot.lineRight();
      if (analogRead(A1) < 100 && !digitalRead(LSensor) && !digitalRead(RSensor))
        robot.lineLeft();

      if (digitalRead(LSensor) && digitalRead(RSensor)) {
        robot.forward(160);
      } else if (digitalRead(Rside)) {
        robot.rotateRight(160);
        delay(20);
      } else if (digitalRead(Lside)) {
        robot.rotateLeft(160);
        delay(20);
      } else if (digitalRead(RSensor)) {
        robot.rotateRight(160);
      } else if (digitalRead(LSensor)) {
        robot.rotateLeft(160);
      } else {
        robot.forward(40);
      }
  }
  else {
    robot.forward(0);
  }
}

void snake() {
  if (digitalRead(StartMod)) {
    if (analogRead(A0) < 100)
        robot.lineRightt();
    if (analogRead(A1) < 100)
        robot.lineLeftt();



    if(millis() % 600 > 300)
        robot.swerveLeft(110); 
    else 
        robot.swerveRight(110);

    if (digitalRead(LSensor) && digitalRead(RSensor)) {
        robot.forward(200);
    } else if (digitalRead(Rside)) {
        robot.rotateRight(200);
        delay(20);
    } else if (digitalRead(Lside)) {
        robot.rotateLeft(200);
        delay(20);
    } else if (digitalRead(RSensor)) {
        robot.turnRight(200);
    } else if (digitalRead(LSensor)) {
        robot.turnLeft(200);
    } 
  } else {
    robot.stop();
  }
}
void loop() {
  if(digitalRead(9)) {
    fast();
  }
  else {
    slow(); 
  }
}



