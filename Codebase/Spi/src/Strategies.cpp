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

      delay(80);
      unsigned long startTime = millis();
      robot.forward(230); 
      while (millis() - startTime < 60) {
          if (digitalRead(LSensor) || digitalRead(Lside)) 
              continue;  // EXIT immediately
      }  
      state1 = true; 
    }
    else {
      if (analogRead(lnl) < 50 && !digitalRead(LSensor) && !digitalRead(RSensor))
        robot.lineRightt();
      if (analogRead(lnr) < 50 && !digitalRead(LSensor) && !digitalRead(RSensor))
        robot.lineLeftt();
      if (digitalRead(MSensor)) {
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
        robot.forward(55);
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
      delay(80);
      unsigned long startTime = millis();
      robot.forward(230); 
      while (millis() - startTime < 60) {
          if (digitalRead(RSensor) || digitalRead(Rside)) 
              continue;  // EXIT immediately
      }  
      state2 = true; 
    }
    else {
      if (analogRead(lnl) < 50 && !digitalRead(LSensor) && !digitalRead(RSensor))
        robot.lineRightt();
      if (analogRead(lnr) < 50 && !digitalRead(LSensor) && !digitalRead(RSensor))
        robot.lineLeftt();
      if (digitalRead(MSensor)) {
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
        robot.forward(55);
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
      if (analogRead(lnl) < 50 && !digitalRead(LSensor) && !digitalRead(RSensor)) {
         robot.lineRightt();
         delay(10);
      }
      if (analogRead(lnr) < 50 && !digitalRead(LSensor) && !digitalRead(RSensor)) {
        robot.lineLeftt();
        delay(10);
      }
      if (digitalRead(MSensor)) {
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
        robot.forward(55);
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
    if (analogRead(lnl) < 200) {
        robot.lineRightt();
        delay(10);
    }
    else if (analogRead(lnr) < 200) {
      robot.lineLeftt();
      delay(10);
    }

    if (digitalRead(MSensor)) {
      robot.forward(240);
    } else if (digitalRead(Rside)) {
      robot.rotateRight(240);
      delay(10);
    } else if (digitalRead(Lside)) {
      robot.rotateLeft(240);
      delay(10);
    } else if (digitalRead(RSensor)) {
      robot.rotateRight(240);
    } else if (digitalRead(LSensor)) {
      robot.rotateLeft(240);
    } else {
      robot.forward(50);
    }
  } else {  // If StartMod is disabled
    servo.write(180);
    robot.stop();
  }
}