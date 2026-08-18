#ifndef MOVEMENT_H
#define MOVEMENT_H

#include <Arduino.h>
#include "Pins.h"

class Movement {
public:
  Movement();
  void stop();
  void forward(double speed);
  void back(double speed);
  void rotateRight(double speed);
  void rotateLeft(double speed);
  void turnRight(double speed);
  void turnLeft(double speed);
  void lineLeftt();
  void lineRightt();
  void waitSlam(int targetSpeed, int rampRate);
  void rampUp(int targetSpeed, int rampRate);
  void Movement::attackRamp(int targetSpeed);
  void lineLeft();
  void slowRamp(int targetSpeed, int rampRate);
  void lineRight(); 

private:
    bool lineDetected();   // 👈 ADD THIS HERE
};
#endif // MOVEMENT_H
