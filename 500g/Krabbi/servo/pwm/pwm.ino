int servo = 9;
double k = 30;
void setup() {
  // put your setup code here, to run once:
  pinMode(servo, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  servoWrite(servo, k);
  delay(300);
  k += 5;
  if (k > 180) {
    k = 30;
  }
}

double servoWrite(int pin, double deg) {
  double p = 2.038;
  if (deg > 179) {
    deg = 179;
  } 
  if (deg < 30.355) {
    deg = 30.355;
  }
  double ht = deg * p / 180;
  double dc = ht / p;
  double invertedDc = 1 - dc;
  analogWrite(pin, invertedDc * 255);
  return dc;
}
