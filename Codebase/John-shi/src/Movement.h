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

  // Filtered line sensors (weighted average, updated every 1 ms)
  void updateLine();
  bool lineSeenRight();   // A0
  bool lineSeenLeft();    // A1
  void waitMs(unsigned long ms);  // like delay(), but keeps the line filter updated
private:
    bool botDetected();
    int readLinePin(uint8_t pin);
    float smoothRight = 0;
    float smoothLeft = 0;
    unsigned long lastLineUpdate = 0;
    bool lineSeeded = false;
};
#endif // MOVEMENT_H
