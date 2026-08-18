#include "Strategies.h"
#include <Arduino.h>   
#include "Pins.h"      

Strategies::Strategies(Movement& robot, Servo& servo)
  : robot(robot), servo(servo) {}


bool state1 = false;
void Strategies::rightFight() {
  if(digitalRead(StartMod)) {
    servo.write(90);    
    if(state1 == false) {
      robot.turnRight(150);

      delay(100);
      unsigned long startTime = millis();
      robot.forward(200); 
      while (millis() - startTime < 160) {
          if (digitalRead(LSensor) || digitalRead(Lside)) 
              continue;  // EXIT immediately
      }  
      state1 = true; 
    }
    else {
      if (analogRead(A0) < 100 && !digitalRead(LSensor) && !digitalRead(RSensor))
        robot.lineRight();
      if (analogRead(A1) < 100 && !digitalRead(LSensor) && !digitalRead(RSensor))
        robot.lineLeft();
      if (digitalRead(LSensor) && digitalRead(RSensor)) {
        robot.attackRamp(200);
      } else if (digitalRead(Rside)) {
        robot.rotateRight(200);
        delay(10);
      } else if (digitalRead(Lside)) {
        robot.rotateLeft(200);
        delay(10);
      } else if (digitalRead(RSensor)) {
        robot.rotateRight(200);
      } else if (digitalRead(LSensor)) {
        robot.rotateLeft(200);
      } else {
        robot.forward(50);
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
      robot.turnLeft(150);
      delay(100);
      unsigned long startTime = millis();
      robot.forward(200); 
      while (millis() - startTime < 160) {
          if (digitalRead(RSensor) || digitalRead(Rside)) 
              continue;  // EXIT immediately
      }  
      state2 = true; 
    }
    else {
      if (analogRead(A0) < 100 && !digitalRead(LSensor) && !digitalRead(RSensor))
        robot.lineRight();
      if (analogRead(A1) < 100 && !digitalRead(LSensor) && !digitalRead(RSensor))
        robot.lineLeft();
      if (digitalRead(LSensor) && digitalRead(RSensor)) {
        robot.attackRamp(200);
      } else if (digitalRead(Rside)) {
        robot.rotateRight(200);
        delay(10);
      } else if (digitalRead(Lside)) {
        robot.rotateLeft(200);
        delay(10);
      } else if (digitalRead(RSensor)) {
        robot.rotateRight(200);
      } else if (digitalRead(LSensor)) {
        robot.rotateLeft(200);
      } else {
        robot.forward(50);
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
      robot.rampUp(170, 4);
      state3 = true; 
    } 
    else {
      if (analogRead(A0) < 100 && !digitalRead(LSensor) && !digitalRead(RSensor)) {
         robot.lineRight();
         delay(10);
      }
      if (analogRead(A1) < 100 && !digitalRead(LSensor) && !digitalRead(RSensor)) {
        robot.lineLeft();
        delay(10);
      }
      if (digitalRead(LSensor) && digitalRead(RSensor)) {
        robot.attackRamp(200);
      } else if (digitalRead(Rside)) {
        robot.rotateRight(200);
        delay(10);
      } else if (digitalRead(Lside)) {
        robot.rotateLeft(200);
        delay(10);
      } else if (digitalRead(RSensor)) {
        robot.rotateRight(200);
      } else if (digitalRead(LSensor)) {
        robot.rotateLeft(200);
      } else {
        robot.forward(52);
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
    if (analogRead(A0) < 100 && !digitalRead(LSensor) && !digitalRead(RSensor)) {
        robot.lineRight();
        delay(10);
    }
    else if (analogRead(A1) < 100 && !digitalRead(LSensor) && !digitalRead(RSensor)) {
      robot.lineLeft();
      delay(10);
    }

    if (digitalRead(LSensor) && digitalRead(RSensor)) {
      robot.waitSlam(200, 2);
    } else if (digitalRead(Rside)) {
      robot.rotateRight(200);
      delay(10);
    } else if (digitalRead(Lside)) {
      robot.rotateLeft(200);
      delay(10);
    } else if (digitalRead(RSensor)) {
      robot.rotateRight(200);
    } else if (digitalRead(LSensor)) {
      robot.rotateLeft(200);
    } else {
      robot.forward(0);
    }
  } else {  // If StartMod is disabled
    servo.write(180);
    robot.stop();
  }
}