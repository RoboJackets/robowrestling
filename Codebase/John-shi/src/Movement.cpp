#include "Movement.h"

// Line filter tuning
const float LINE_ALPHA = 0.4;              // 0-1: higher = reacts faster, lower = ignores more noise
const int LINE_THRESHOLD = 100;             // smoothed value below this = white line
const unsigned long LINE_UPDATE_US = 1000;  // filter update period (1 ms)

Movement::Movement() {
}

// Read twice and keep the second: the first read after switching ADC pins can be off
int Movement::readLinePin(uint8_t pin) {
    analogRead(pin);
    return analogRead(pin);
}

void Movement::updateLine() {
    unsigned long now = micros();
    if (lineSeeded && now - lastLineUpdate < LINE_UPDATE_US) {
        return;
    }
    lastLineUpdate = now;

    int right = readLinePin(A0);
    int left = readLinePin(A1);

    // First update: start the average at the current reading
    if (!lineSeeded) {
        smoothRight = right;
        smoothLeft = left;
        lineSeeded = true;
        return;
    }

    smoothRight += LINE_ALPHA * (right - smoothRight);
    smoothLeft += LINE_ALPHA * (left - smoothLeft);
}

bool Movement::lineSeenRight() {
    updateLine();
    return smoothRight < LINE_THRESHOLD;
}

bool Movement::lineSeenLeft() {
    updateLine();
    return smoothLeft < LINE_THRESHOLD;
}

void Movement::waitMs(unsigned long ms) {
    unsigned long startTime = millis();
    while (millis() - startTime < ms) {
        updateLine();
    }
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

bool Movement::botDetected() {
    return digitalRead(LSensor) ||
           digitalRead(RSensor) ||
           digitalRead(Lside)   ||
           digitalRead(Rside);
}

void Movement::lineRightt() {
    unsigned long startTime = millis();

    // Phase 1: Back up
    back(250);
    while (millis() - startTime < 150) {
        updateLine();
        if (botDetected()) {
            return;  // EXIT immediately
        }
    }

    // Phase 2: Rotate right
    unsigned long startTime1 = millis();
    rotateLeft(160);
    while (millis() - startTime1 < 150) {
        updateLine();
        if (botDetected()) {
            return;  // EXIT immediately
        }
    }

    stop();
}
void Movement::lineLeftt() {
    unsigned long startTime = millis();
    // Phase 1: Back up
    back(250);
    while (millis() - startTime < 150) {
        updateLine();
        if (botDetected()) {
            return;
        }
    }

    // Phase 2: Rotate left
    unsigned long startTime1 = millis();
    rotateRight(160);
    while (millis() - startTime1 < 150) {
        updateLine();
        if (botDetected()) {
            stop();
            return;
        }
    }

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

        waitMs(10);  // controls how fast ramping feels
    }
}

void Movement::waitSlam(int targetSpeed, int rampRate) {
    unsigned long startTime = millis();
    int currentSpeed = 20;

    // Soft touch: hold at speed 20 for 60 ms
    while (millis() - startTime < 60) {
        if (!digitalRead(RSensor) || !digitalRead(LSensor) || !digitalRead(StartMod) || digitalRead(Rside) || digitalRead(Lside)) {
            return;
        }
        if (lineSeenRight() || lineSeenLeft()) {
            return;
        }

        analogWrite(Rpos, currentSpeed);
        analogWrite(Rneg, 0);
        analogWrite(Lpos, currentSpeed);
        analogWrite(Lneg, 0);
    }

    // Ramp up: +rampRate every 10 ms until targetSpeed
    while (currentSpeed < targetSpeed) {
        if (!digitalRead(RSensor) || !digitalRead(LSensor) || !digitalRead(StartMod) || digitalRead(Rside) || digitalRead(Lside)) {
            return;
        }
        if (lineSeenRight() || lineSeenLeft()) {
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

        waitMs(10);
    }
    while(digitalRead(LSensor) && digitalRead(RSensor) && digitalRead(StartMod) && !digitalRead(Rside) && !digitalRead(Lside)) {
        if (lineSeenRight() || lineSeenLeft()) {
            return;
        }
    }
}