#include <Arduino.h>

#define directionPin 3
#define stepPin 2
#define enablePin 4
#define potPin A0

#define pulsesPerRevolution 800   // 200 steps = 360 degrees

int currentStepPosition = 0;

void stepMotor(int steps, bool direction);

void setup() {
  Serial.begin(9600);
  pinMode(directionPin, OUTPUT);
  pinMode(stepPin, OUTPUT);
  pinMode(enablePin, OUTPUT);
  pinMode(potPin, INPUT);

  digitalWrite(enablePin, LOW);   // Enable driver
  digitalWrite(directionPin, LOW);
}

void loop() {
  int sensorValue = analogRead(potPin);

  int angle = map(sensorValue, 0, 1023, 0, 360);
  int targetStepPosition = map(angle, 0, 360, 0, pulsesPerRevolution);

  Serial.print("  Angle: ");
  Serial.print(angle);
  Serial.print("  Target Steps: ");
  Serial.println(targetStepPosition);

  // Move only the difference
  if (targetStepPosition > currentStepPosition) {
    stepMotor(targetStepPosition - currentStepPosition, true);
    currentStepPosition = targetStepPosition;
  } 
  else if (targetStepPosition < currentStepPosition) {
    stepMotor(currentStepPosition - targetStepPosition, false);
    currentStepPosition = targetStepPosition;
  }
}
int stepDelay = 400;
void stepMotor(int steps, bool direction) {
  digitalWrite(directionPin, direction);
  for (int i = 0; i < steps; i++) {
    digitalWrite(stepPin, HIGH);
    delayMicroseconds(stepDelay);
    digitalWrite(stepPin, LOW);
    delayMicroseconds(stepDelay);
  }
}

// for (long i = 0; i < (long)pulsesPerRevolution * revolutions; i++) { // digitalWrite(stepPin, HIGH); // delayMicroseconds(450); // slower = safer // digitalWrite(stepPin, LOW); // delayMicroseconds(450); // } // digitalWrite(directionPin, HIGH); // Change direction // delay(1000); // for (long i = 0; i < (long)pulsesPerRevolution * revolutions; i++) { // digitalWrite(stepPin, HIGH); // delayMicroseconds(450); // slower = safer // digitalWrite(stepPin, LOW); // delayMicroseconds(450); // }