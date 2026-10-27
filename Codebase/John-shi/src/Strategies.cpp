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
      robot.waitMs(90);

      unsigned long startTime = millis();
      robot.forward(240); 
      while (millis() - startTime < 200) {
          if (digitalRead(LSensor) || digitalRead(Lside)) 
              continue;  // EXIT immediately
      } 
      state1 = true; 
    }
    else {
      if (robot.lineSeenRight() && !digitalRead(LSensor) && !digitalRead(RSensor))
        robot.lineRightt();
      if (robot.lineSeenLeft() && !digitalRead(LSensor) && !digitalRead(RSensor))
        robot.lineLeftt();
      // Side sensors win over the front: front + side means the front is likely a flag
      if (digitalRead(Rside)) {
        robot.rotateRight(150);
      } else if (digitalRead(Lside)) {
        robot.rotateLeft(150);
      } else if (digitalRead(LSensor) && digitalRead(RSensor)) {
        robot.forward(250);
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
      robot.turnLeft(230);
      robot.waitMs(90);

      unsigned long startTime = millis();
      robot.forward(240); 
      while (millis() - startTime < 200) {
          if (digitalRead(RSensor) || digitalRead(Rside)) 
              continue;  // EXIT immediately
      } 
      state2 = true; 
    }
    else {
      if (robot.lineSeenRight() && !digitalRead(LSensor) && !digitalRead(RSensor))
        robot.lineRightt();
      if (robot.lineSeenLeft() && !digitalRead(LSensor) && !digitalRead(RSensor))
        robot.lineLeftt();
      // Side sensors win over the front: front + side means the front is likely a flag
      if (digitalRead(Rside)) {
        robot.rotateRight(150);
      } else if (digitalRead(Lside)) {
        robot.rotateLeft(150);
      } else if (digitalRead(LSensor) && digitalRead(RSensor)) {
        robot.forward(250);
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
      unsigned long startTime = millis();
      robot.rampUp(220, 5);

      state3 = true; 
    }
    else {
      if (robot.lineSeenRight() && !digitalRead(LSensor) && !digitalRead(RSensor))
        robot.lineRightt();
      if (robot.lineSeenLeft() && !digitalRead(LSensor) && !digitalRead(RSensor))
        robot.lineLeftt();
      // Side sensors win over the front: front + side means the front is likely a flag
      if (digitalRead(Rside)) {
        robot.rotateRight(150);
        robot.waitMs(20);
      } else if (digitalRead(Lside)) {
        robot.rotateLeft(150);
        robot.waitMs(20);
      } else if (digitalRead(LSensor) && digitalRead(RSensor)) {
        robot.forward(250);
      } else if (digitalRead(RSensor)) {
        robot.rotateRight(200);
      } else if (digitalRead(LSensor)) {
        robot.rotateLeft(200);
      } else {
        robot.forward(85);
      }
    } 
  } else {
    servo.write(180);
    robot.stop(); 
  }
}
void Strategies::turtle() {
  if (digitalRead(StartMod)) {  // If StartMod is enabled
    servo.write(90);
    if (robot.lineSeenRight()) {
      turtleInching = false;
      robot.lineRightt();
      return;
    }
    if (robot.lineSeenLeft()) {
      turtleInching = false;
      robot.lineLeftt();
      return;
    }

    if (digitalRead(Rside) || digitalRead(Lside) ||
        digitalRead(RSensor) || digitalRead(LSensor)) {
      turtleInching = false;
    }

    // Side sensors win over the front: front + side means the front is likely a flag
    if (digitalRead(Rside)) {
      robot.rotateRight(150);
    } else if (digitalRead(Lside)) {
      robot.rotateLeft(150);
    } else if (digitalRead(LSensor) && digitalRead(RSensor)) {
      robot.waitSlam(250, 4);
    } else if (digitalRead(RSensor)) {
      robot.rotateRight(180);
    } else if (digitalRead(LSensor)) {
      robot.rotateLeft(180);
    } else {
      // Start a short inch immediately, then repeat once per second.
      const unsigned long inchPeriodMs = 1000;
      const unsigned long inchDurationMs = 100;
      const int inchSpeed = 85;
      unsigned long now = millis();
      if (!turtleInching) {
        turtleInchStart = now;
        turtleInching = true;
      }
      unsigned long elapsed = now - turtleInchStart;
      if (elapsed >= inchPeriodMs) {
        turtleInchStart = now;
        elapsed = 0;
      }
      if (elapsed < inchDurationMs)
        robot.forward(inchSpeed);
      else
        robot.stop();
    }
  } else {  // If StartMod is disabled
    turtleInching = false;
    servo.write(180);
    robot.stop();
  }
}
bool state4 = false;
void Strategies::dashTurtle() {
  if (digitalRead(StartMod)) {
    servo.write(90);
    if (state4 == false) {
      // Opening: short forward dash, then fall into normal turtle
      unsigned long startTime = millis();
      robot.forward(200);
      while (millis() - startTime < 200) {
        if (!digitalRead(StartMod) || robot.lineSeenRight() || robot.lineSeenLeft())
          break;
      }
      robot.stop();
      state4 = true;
    }
    else {
      turtle();
    }
  } else {
    turtleInching = false;
    servo.write(180);
    robot.stop();
  }
}
