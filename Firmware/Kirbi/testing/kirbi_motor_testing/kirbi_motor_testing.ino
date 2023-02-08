double left_multi;
double right_multi;

void setup() {
    left_multi = 1;
    right_multi = 1;
    while(!ESC_SERIAL){delay(10);}
    ESC_SERIAL.setRX(34);
    ESC_SERIAL.setTX(33);
    ESC_SERIAL.begin(38400);
}

void drive(int left, int right) {
     if (left == 0 && right == 0) {
         ESC_SERIAL.write(0);
     } else {
        right = 64 + right;
        left = 192 + left;

        // 0: both motor stop
        // 1-63: motor 1 reverse, 64: motor 1 stop, 65-127: motor 1 forward
        // 128-191: motor 2 reverse, 192: motor 2 stop, 193-255 motor 2 forward
        ESC_SERIAL.write(left);
        ESC_SERIAL.write(right);
     }
}

void loop() {
  //-63 to +63 range
  Serial.print("Ramping both motors forwards...");
  for (int i = 0; i < 63; i++){
    drive(i,i);
    delay(8);
  }
  Serial.print("Waiting 2 seconds");
  drive(0,0);
  delay(2000);
  Serial.print("Ramping both motors backwards...");
  for (int i = 0; i < 63; i++){
    drive(-i,-i);
    delay(8);
  }
  Serial.print("Waiting 2 seconds");
  drive(0,0);
  delay(2000);
  Serial.print("Ramping left forwards and right backwards...");
  for (int i = 0; i < 63; i++){
    drive(i,-i);
    delay(8);
  }
  Serial.print("Waiting 2 seconds");
  drive(0,0);
  delay(2000);
  Serial.print("Ramping left backwards and right forwards...");
  for (int i = 0; i < 63; i++){
    drive(-i,i);
    delay(8);
  }
  Serial.print("Waiting 5 seconds");
  drive(0,0);
  delay(5000);
}
