#include "Movement.h"

Movement::Movement() {
}

void Movement::stop() {
  analogWrite(Rpos, 0);
  analogWrite(Rneg, 0);
  analogWrite(Lpos, 0);
  analogWrite(Lneg, 0);
}

void Movement::forward(double speed) {
  analogWrite(Rpos, speed);
  analogWrite(Rneg, 0);
  analogWrite(Lpos, speed);
  analogWrite(Lneg, 0);
}

void Movement::back(double speed) {
  analogWrite(Rpos, 0);
  analogWrite(Rneg, speed);
  analogWrite(Lpos, 0);
  analogWrite(Lneg, speed);
}

void Movement::rotateRight(double speed) {
  analogWrite(Rpos, 0);
  analogWrite(Rneg, speed);
  analogWrite(Lpos, speed);
  analogWrite(Lneg, 0);
}

void Movement::rotateLeft(double speed) {
  analogWrite(Rpos, speed);
  analogWrite(Rneg, 0);
  analogWrite(Lpos, 0);
  analogWrite(Lneg, speed);
}

void Movement::turnRight(double speed) {
  analogWrite(Rpos, 0);
  analogWrite(Rneg, 0);
  analogWrite(Lpos, speed);
  analogWrite(Lneg, 0);
}

void Movement::turnLeft(double speed) {
  analogWrite(Rpos, speed);
  analogWrite(Rneg, 0);
  analogWrite(Lpos, 0);
  analogWrite(Lneg, 0);
}
void Movement::swerveRight(double speed) {
  analogWrite(Rpos, 0);
  analogWrite(Rneg, 30);
  analogWrite(Lpos, speed);
  analogWrite(Lneg, 0);
}

void Movement::swerveLeft(double speed) {
  analogWrite(Rpos, speed);
  analogWrite(Rneg, 0);
  analogWrite(Lpos, 0);
  analogWrite(Lneg, 30);
}
bool Movement::lineDetected() {
    return  digitalRead(RSensor) ||
            digitalRead(Lside)   ||
            digitalRead(LSensor) ||
            digitalRead(Rside);
}
void Movement::lineRightt() {

    unsigned long startTime = millis();

    // Phase 1: Back up
    back(220);
    while (millis() - startTime < 200) {
        if (lineDetected()) {
            return;  // EXIT immediately
        }
    }

    // Phase 2: Rotate right
    startTime = millis();
    rotateRight(130);
    while (millis() - startTime < 100) {
        if (lineDetected()) {
            return;  // EXIT immediately
        }
    }
    stop();
}
void Movement::lineLeftt() {
    unsigned long startTime = millis();
    // Phase 1: Back up
    back(220);
    while (millis() - startTime < 200) {
        if (lineDetected()) {
            return;
        }
    }

    // Phase 2: Rotate left
    startTime = millis();
    rotateLeft(130);
    while (millis() - startTime < 100) {
        if (lineDetected()) {
            return;
        }
    }

    stop();
}
void Movement::lineRight() {

    // Phase 1: back up
    back(150);
    delay(160);
    // Phase 2: rotate right
    if (lineDetected()) {
        return;
    }
    rotateLeft(130);
    delay(100);

    stop();
}
void Movement::lineLeft() {
    // Phase 1: back up
    back(150);
    delay(160);
    // Phase 2: rotate left
    if (lineDetected()) {
        return;
    }
    rotateRight(130);
    delay(100);
    stop();
}

void Movement::rampUp(int targetSpeed, int rampRate) {
    int currentSpeed = 0;

    while (currentSpeed < targetSpeed) {
        currentSpeed += rampRate;

        // Clamp so we don’t overshoot
        if (currentSpeed > targetSpeed) {
            currentSpeed = targetSpeed;
        }

        // Apply speed (forward motion)
        analogWrite(Rpos, currentSpeed);
        analogWrite(Rneg, 0);
        analogWrite(Lpos, currentSpeed);
        analogWrite(Lneg, 0);

        delay(10);  // controls how fast ramping feels
    }
    while(digitalRead(LSensor) && digitalRead(RSensor) && digitalRead(StartMod)) {
        if (analogRead(A0) < 100 || analogRead(A1) < 100) {
            return;
        }
    }
}

void Movement::slowRamp(int targetSpeed, int rampRate) {
    int currentSpeed = 0;

    // Ramp up to target speed
    while (currentSpeed < targetSpeed) {
        currentSpeed += rampRate;

        if (currentSpeed > targetSpeed) {
            currentSpeed = targetSpeed;
        }
        if (!digitalRead(LSensor) ||  !digitalRead(RSensor) || analogRead(A0) < 100 || analogRead(A1) < 100) {return;}
        analogWrite(Rpos, currentSpeed);
        analogWrite(Rneg, 0);
        analogWrite(Lpos, currentSpeed);
        analogWrite(Lneg, 0);
        delay(10);
    }
    while(digitalRead(LSensor) && digitalRead(RSensor) && digitalRead(StartMod)) {
        if (analogRead(A0) < 100 || analogRead(A1) < 100) {
            return;
        }
    }
    
}

void Movement::waitSlam(int targetSpeed, int rampRate) {
    unsigned long startTime = millis();
    int currentSpeed = 50;

    // Hold at speed 50 for 2 seconds
    while (millis() - startTime < 1000) {
        if (!digitalRead(RSensor) || !digitalRead(LSensor) || !digitalRead(StartMod)) {
             return;
            return;
        }

        analogWrite(Rpos, currentSpeed);
        analogWrite(Rneg, 0);
        analogWrite(Lpos, currentSpeed);
        analogWrite(Lneg, 0);
    }

    // After 2 seconds, ramp up
    while (currentSpeed < targetSpeed) {
        if (!digitalRead(RSensor) || !digitalRead(LSensor) || !digitalRead(StartMod)) {
            return;
        }

        currentSpeed += rampRate;
        if (currentSpeed > targetSpeed) {
            currentSpeed = targetSpeed;
        }

        analogWrite(Rpos, currentSpeed);
        analogWrite(Rneg, 0);
        analogWrite(Lpos, currentSpeed);
        analogWrite(Lneg, 0);

        delay(10);
    }
    while(digitalRead(LSensor) && digitalRead(RSensor) && digitalRead(StartMod)) {
        if (analogRead(A0) < 100 || analogRead(A1) < 100) {
            return;
        }
    }
}