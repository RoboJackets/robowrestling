#include "Strategies.h"
#include <Arduino.h>   
#include "Pins.h"      

Strategies::Strategies(Movement& robot, Servo& servo)
  : robot(robot), servo(servo) {}


bool state1 = false;
void Strategies::rightFight() {
  if(digitalRead(StartMod)) {
    servo.write(95);    
    if(state1 == false) {
      robot.turnRight(230);
      delay(90);

      unsigned long startTime = millis();
      robot.forward(240); 
      while (millis() - startTime < 200) {
          if (digitalRead(LSensor) || digitalRead(Lside)) 
              continue;  // EXIT immediately
      } 
      state1 = true; 
    }
    else {
      if (analogRead(A0) < 100 && !digitalRead(LSensor) && !digitalRead(RSensor))
        robot.lineRightt();
      if (analogRead(A1) < 100 && !digitalRead(LSensor) && !digitalRead(RSensor))
        robot.lineLeftt();
      if (digitalRead(LSensor) && digitalRead(RSensor)) {
        robot.forward(250);
      } else if (digitalRead(Rside)) {
        robot.rotateRight(250);
      } else if (digitalRead(Lside)) {
        robot.rotateLeft(250);
      } else if (digitalRead(RSensor)) {
        robot.rotateRight(250);
      } else if (digitalRead(LSensor)) {
        robot.rotateLeft(250);
      } else {
        robot.forward(85);
      }
    }
  } else {
    servo.write(180);
    robot.stop(); 
  }
}
bool state2 = false;
void Strategies::leftFight() {
  if(digitalRead(StartMod)) {
    servo.write(90);    
    if(state2 == false) {
      robot.turnLeft(230);
      delay(90);

      unsigned long startTime = millis();
      robot.forward(240); 
      while (millis() - startTime < 200) {
          if (digitalRead(RSensor) || digitalRead(Rside)) 
              continue;  // EXIT immediately
      } 
      state2 = true; 
    }
    else {
      if (analogRead(A0) < 100 && !digitalRead(LSensor) && !digitalRead(RSensor))
        robot.lineRightt();
      if (analogRead(A1) < 100 && !digitalRead(LSensor) && !digitalRead(RSensor))
        robot.lineLeftt();
      if (digitalRead(LSensor) && digitalRead(RSensor)) {
        robot.forward(250);
      } else if (digitalRead(Rside)) {
        robot.rotateRight(250);
      } else if (digitalRead(Lside)) {
        robot.rotateLeft(250);
      } else if (digitalRead(RSensor)) {
        robot.rotateRight(250);
      } else if (digitalRead(LSensor)) {
        robot.rotateLeft(250);
      } else {
        robot.forward(85);
      }
    }
  } else {
    servo.write(180);
    robot.stop(); 
  }
}
bool state3 = false;
void Strategies::forwardFight() {
  if(digitalRead(StartMod)) {
    servo.write(90);    
    if(state3 == false) {
      unsigned long startTime = millis();
      robot.rampUp(220, 3);

      state3 = true; 
    }
    else {
      if (analogRead(A0) < 100 && !digitalRead(LSensor) && !digitalRead(RSensor))
        robot.lineRightt();
      if (analogRead(A1) < 100 && !digitalRead(LSensor) && !digitalRead(RSensor))
        robot.lineLeftt();
      if (digitalRead(LSensor) && digitalRead(RSensor)) {
        robot.forward(250);
      } else if (digitalRead(Rside)) {
        robot.rotateRight(250);
        delay(20);
      } else if (digitalRead(Lside)) {
        robot.rotateLeft(250);
        delay(20);
      } else if (digitalRead(RSensor)) {
        robot.rotateRight(250);
      } else if (digitalRead(LSensor)) {
        robot.rotateLeft(250);
      } else {
        robot.forward(85);
      }
    } 
  } else {
    servo.write(180);
    robot.stop(); 
  }
}
void Strategies::Slowfight() {
  if (digitalRead(StartMod)) {  // If StartMod is enabled
    servo.write(90);
    if (analogRead(A0) < 100)
      robot.lineRight();
    if (analogRead(A1) < 100)
      robot.lineLeft();

    if (digitalRead(LSensor) && digitalRead(RSensor)) {
      robot.waitSlam(220, 2);
    } else if (digitalRead(Rside)) {
      robot.rotateRight(250);
    } else if (digitalRead(Lside)) {
      robot.rotateLeft(250);
    } else if (digitalRead(RSensor)) {
      robot.rotateRight(220);
    } else if (digitalRead(LSensor)) {
      robot.rotateLeft(220);
    } else {
      robot.forward(0);
    }
  } else {  // If StartMod is disabled
    servo.write(180);
    robot.stop();
  }
}
