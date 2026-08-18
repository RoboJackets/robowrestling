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
bool Movement::lineDetected() {
    return digitalRead(LSensor) ||
            digitalRead(RSensor) ||
            digitalRead(Lside)   ||
            digitalRead(Rside);
}
void Movement::lineRightt() {

    unsigned long startTime = millis();

    // Phase 1: Back up
    back(180);
    while (millis() - startTime < 300) {
        if (lineDetected()) {
            return;  // EXIT immediately
        }
    }

    // Phase 2: Rotate right
    startTime = millis();
    rotateRight(130);
    while (millis() - startTime < 220) {
        if (lineDetected()) {
            return;  // EXIT immediately
        }
    }
    stop();
}
void Movement::lineLeftt() {
    unsigned long startTime = millis();
    // Phase 1: Back up
    back(180);
    while (millis() - startTime < 300) {
        if (lineDetected()) {
            return;
        }
    }

    // Phase 2: Rotate left
    startTime = millis();
    rotateLeft(130);
    while (millis() - startTime < 150) {
        if (lineDetected()) {
            return;
        }
    }

    stop();
}
void Movement::lineRight() {

    // Phase 1: back up
    back(180);
    delay(300);
    // Phase 2: rotate right
    rotateLeft(130);
    delay(150);

    stop();
}
void Movement::lineLeft() {
    // Phase 1: back up
    back(180);
    delay(300);
    // Phase 2: rotate left
    rotateRight(130);
    delay(150);
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
}
void Movement::attackRamp(int targetSpeed) {
    int start = millis();
    analogWrite(Rpos, targetSpeed);
    analogWrite(Rneg, 0);
    analogWrite(Lpos, targetSpeed);
    analogWrite(Lneg, 0);

    while(millis() - start < 500){
        if (!digitalRead(LSensor) ||  !digitalRead(RSensor)|| analogRead(A0) < 100 || analogRead(A1) < 100) {
            return;
        }        
        delay(15);
    }
    
    analogWrite(Rpos, 100);
    analogWrite(Rneg, 0);
    analogWrite(Lpos, 100);
    analogWrite(Lneg, 0);
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

