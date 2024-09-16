#include "kirbi.h"

ICM20948 icm(Wire2, (uint8_t)0x68);

int dist[6];

volatile bool left_line_hit;
volatile bool right_line_hit;

/* acceleration timing variables */
int curr_time;
int prev_time_accel;
int check_accel;

/* encoder counts */
volatile int right_encoder;
volatile int left_encoder;

double left_multi;
double right_multi;


/* Current sensing stuff */
double r1 = 2.3;
double r2 = 7.28;
double nominal_current = 4.12;
const double precalc = 2.01873; //nominal_current*(sqrt(r1/(r1+r2)))
const double tw = 42.2;
int total_currentxtime_left;
int total_currentxtime_right;
double percent_overloaded_left;
double percent_overloaded_right;
int prev_time_current; //for use with curr_time
int last_read_current;
int check_overload;
const double voltage_to_current = .01611328;

/* configurations */
//lidar serial configs
byte configOutput [5] = {0x5A, 0x05, 0x07, 0x01, 0x11};
byte configUART [5] = {0x5A, 0x05, 0x0A, 0x00, 0x11};
byte factoryReset[5] = {0x5A, 0x04, 0x10, 0x6E}


State state_machine() {
    curr_time = micros();
    get_distances();
//    get_current();
//    if (percent_overloaded_left > 1 || percent_overloaded_right > 1) {
//        return PANIC_FIRE;
//    }
//    if (curr_time - prev_time_accel > check_accel) {
//        prev_time_accel = micros();
//        get_accel();
//        //if (y_acceleration > ouch || y_acceleration < -ouch) {
//            // return PANIC_HIT;
//        // }
//    }

    Location curr_opponent_location = get_opponent();
//    Serial.println(curr_opponent_location);
    switch(curr_opponent_location) {
        case FRONT_CLOSE:
            return MEGA_SLAMMY_WHAMMY;

        case FRONT_FAR:
            return SLAMMY_WHAMMY;

        case LEFT_CORNER_FRONT:
            return ADJUST_1_LEFT;

        case RIGHT_CORNER_FRONT:
            return ADJUST_1_RIGHT;

        case LEFT_CORNER:
            return ADJUST_2_LEFT;

        case RIGHT_CORNER:
            return ADJUST_2_RIGHT;
        case LEFT_CORNER_SIDE:
            return ADJUST_3_LEFT;

        case RIGHT_CORNER_SIDE:
            return ADJUST_3_RIGHT;

        case LEFT_SIDE:
            return ADJUST_4_LEFT;

        case RIGHT_SIDE:
            return ADJUST_4_RIGHT;

        case BEHIND:
            return SEARCH;
    }
    return SEARCH;
}

// void drive(int left, int right) {
//     bool left_reverse = left < 0;
//     bool right_reverse = right < 0;
//     left = abs(left);
//     right = abs(right);

//     left = left*left_multi;
//     right = right*right_multi;
//     ESC_SERIAL.write(ESC_ADDRESS);
//     ESC_SERIAL.write(!left_reverse);
//     ESC_SERIAL.write(left);
//     ESC_SERIAL.write((ESC_ADDRESS+(unsigned int)left_reverse+(unsigned int)left)&ESC_CHECKSUM);
//     ESC_SERIAL.write(ESC_ADDRESS);
//     ESC_SERIAL.write(right_reverse);
//     ESC_SERIAL.write(right);
//     ESC_SERIAL.write((ESC_ADDRESS+(unsigned int)right_reverse+(unsigned int)right)&ESC_CHECKSUM);
// }

/**
 * using simple serial. valid input range is 0-63 for left and right
**/
void drive(int left, int right) {
     if (left == 0 && right == 0) {
         ESC_SERIAL.write(0);
     } else {
        right = 64 - right;
        left = 192 - left;

        // 0: both motor stop
        // 1-63: motor 1 reverse, 64: motor 1 stop, 65-127: motor 1 forward
        // 128-191: motor 2 reverse, 192: motor 2 stop, 193-255 motor 2 forward
        ESC_SERIAL.write(left);
        ESC_SERIAL.write(right);
     }
}

/**
 * INTERRUPT METHODS
**/
void left_line_int() {
    left_line_hit = !digitalReadFast(LEFT_INT_LINE);
}
void right_line_int() {
    right_line_hit = !digitalReadFast(RIGHT_INT_LINE);
}

// void left_off_line_int() {
//     left_line_hit = false;
// }
// void right_off_line_int() {
//     right_line_hit = false;
// }

void increment_encoder_right() {
    if (digitalReadFast(RIGHT_B_ENCODER)) {
        right_encoder--;
    }
    else {
        right_encoder++;
    }
}

void increment_encoder_left() {
    if (digitalReadFast(LEFT_B_ENCODER)) {
        left_encoder++;
    }
    else {
        left_encoder--;
    }
}

/**
 * Method for startup action
**/
void do_startup_action() {
    delay(5000);
}

/**
 * SETUP METHODS
**/
 void setup_imu() {
    pinMode(IMU_ADDRESS_PIN, OUTPUT);
    digitalWrite(IMU_ADDRESS_PIN, LOW); //Don't ever set this high
    Wire2.begin();
    Wire2.setSDA(IMU_SDA);
    Wire2.setSCL(IMU_SCL);
    icm.begin();
    icm.disableDataReadyInterrupt();
    icm.configAccel(ICM20948::ACCEL_RANGE_2G, ICM20948::ACCEL_DLPF_BANDWIDTH_6HZ);
    icm.configGyro(ICM20948::GYRO_RANGE_250DPS, ICM20948::GYRO_DLPF_BANDWIDTH_6HZ);
 }

 void setup_distance() {
     /* lidar setup */
     LEFT_LIDAR_SERIAL.setRX(31);
     LEFT_LIDAR_SERIAL.setTX(32);
     while(!LEFT_LIDAR_SERIAL){delay(10);}
     LEFT_LIDAR_SERIAL.begin(115200);
     LEFT_LIDAR_SERIAL.write(configUART, 5);
     LEFT_LIDAR_SERIAL.write(configOutput, 5);
     RIGHT_LIDAR_SERIAL.setRX(0);
     RIGHT_LIDAR_SERIAL.setTX(1);
     while(!RIGHT_LIDAR_SERIAL){delay(10);}
     RIGHT_LIDAR_SERIAL.begin(115200);
     RIGHT_LIDAR_SERIAL.write(configUART, 5);
     RIGHT_LIDAR_SERIAL.write(configOutput, 5);
     pinMode(DIST_L, INPUT);
     pinMode(DIST_L_45, INPUT);
     pinMode(DIST_R, INPUT);
     pinMode(DIST_R_45, INPUT);
 }

void setup_current() {
    analogReadResolution(13);
    pinMode(LEFT_CURRENT, INPUT);
    pinMode(RIGHT_CURRENT, INPUT);
    percent_overloaded_left = 0;
    percent_overloaded_right = 0;
    check_overload = 0;
 }

 void setup_motors(){
    left_multi = 1;
    right_multi = 1;
    while(!ESC_SERIAL){delay(10);}
    ESC_SERIAL.setRX(34);
    ESC_SERIAL.setTX(33);
    ESC_SERIAL.begin(38400);
 }

 void setup_encoders(){
    pinMode(LEFT_A_ENCODER, INPUT);
    pinMode(RIGHT_A_ENCODER, INPUT);

    attachInterrupt(digitalPinToInterrupt(LEFT_A_ENCODER), increment_encoder_left, RISING);
    attachInterrupt(digitalPinToInterrupt(RIGHT_A_ENCODER), increment_encoder_right, RISING);
}

void setup_line(){
    left_line_hit = 0;
    right_line_hit = 0;

    pinMode(LINE_REF, OUTPUT);
    analogWrite(LINE_REF, LINE_THRES);

    pinMode(LEFT_INT_LINE, INPUT);
    pinMode(RIGHT_INT_LINE, INPUT);

    attachInterrupt(digitalPinToInterrupt(LEFT_INT_LINE), left_line_int, CHANGE);
    attachInterrupt(digitalPinToInterrupt(RIGHT_INT_LINE), right_line_int, CHANGE);
}

void setup_remote(){
    pinMode(REMOTE_PIN, INPUT);
}

/**
 * SENSOR READ METHODS
**/
bool get_line_flag() {
  return (left_line_hit || right_line_hit);
}

void get_accel() {
//    x_accel.add(icm.getAccelX_mss());
//    y_accel.add(icm.getAccelY_mss());
}
void get_gyro() {
    //TODO: implement?
}
void get_distances() {
    dist[0] = digitalReadFast(DIST_L);
    dist[1] = digitalReadFast(DIST_L_45);
    dist[2] = read_lidar(LEFT_LIDAR);
    if (dist[2] == 65535) { digitalWrite(13, HIGH); } else { digitalWrite(13, LOW); }
    dist[3] = read_lidar(RIGHT_LIDAR);
    dist[4] = digitalReadFast(DIST_R_45);
    dist[5] = digitalReadFast(DIST_R);
    Serial.println(String(dist[0]) + " " + String(dist[1]) + " " + String(dist[2]) + " " + String(dist[3]) + " " + String(dist[4]) + " " + String(dist[5]));
}
int read_lidar(int serial_port) {
    byte bytes[9];
    if (serial_port == 4) {
      LEFT_LIDAR_SERIAL.readBytes(bytes, 9);
    } else {
      RIGHT_LIDAR_SERIAL.readBytes(bytes, 9);
    }
//    Serial.println(String(bytes[0]) + " " + String(bytes[1]) + " " + String(bytes[2]) + " " + String(bytes[3]) + " " + String(bytes[4]) + " " + String(bytes[5]) + " " + String(bytes[6]) + " " + String(bytes[7]) + " " + String(bytes[8]));
    int dist_low = 0;
    int value = -1;
    while (dist_low < 9 && value == -1) {
        if (bytes[dist_low] == 0x59) {
            if (dist_low == 0) {
                if (bytes[8] == 0x59) {
                    value = (int)bytes[1] + ((int)bytes[2] << 8);
                } else if (bytes[1] == 0x59) {
                    value = (int)bytes[2] + (((int)bytes[3]) << 8);
                }
            } else if (dist_low == 7) {
                if (bytes[8] == 0x59) {
                    value = (int)bytes[0] + ((int)bytes[1] << 8);
                }
            } else {
                if (bytes[++dist_low] == 0x59) {
                    value = (int)bytes[++dist_low] + (((int)bytes[++dist_low]) << 8);
                }
            }
        }
        dist_low++;
    }
    if (value == 0 || value == -1) {
        return MAX_DIST+1;
    }
    return value;
}
void get_current() {
    int time_at_current = curr_time - last_read_current;
    last_read_current = curr_time;
    int current = analogRead(LEFT_CURRENT)*voltage_to_current; //read in voltage then change to current using magic number
    total_currentxtime_left += time_at_current*current; //Keep track of current*time over the interval to average later
    current = analogRead(RIGHT_CURRENT)*voltage_to_current;
    total_currentxtime_right += time_at_current*current;
    int time_since_check = curr_time - prev_time_current;
    if (time_since_check > check_overload) { //is it time to check the overload?
        prev_time_current = curr_time;
        current = total_currentxtime_left/(time_since_check);
        double k_left = current/precalc;
        total_currentxtime_left = 0;
        current = total_currentxtime_right/(time_since_check);
        double k_right = current/precalc;
        total_currentxtime_right = 0;
        if (k_left > 1) { //are we overloading?
            double k2 = pow(k_left, 2);
            double ton = tw * log(k2/(k2-1));
            percent_overloaded_left += time_since_check/ton; //add the time that we were overloading/time we can
                                                             //overload for at that at that amperage to our percent overloaded
        }
        if (k_right > 1) {
            double k2 = pow(k_right, 2);
            double ton = tw * log(k2/(k2-1));
            percent_overloaded_right += time_since_check/ton;
        }
    }
}

Location get_opponent(){

    bool left_side_valid = DIST_LEFT_SIDE == 1; //Is the distance on the sensor a resonable number
    bool left_corner_valid = DIST_LEFT_CORNER == 1;
    bool left_front_valid = DIST_LEFT_CENTER < MAX_DIST;
    bool left_front_close_valid = DIST_LEFT_CENTER < CLOSE_DIST;
    bool right_front_close_valid = DIST_RIGHT_CENTER < CLOSE_DIST;
    bool right_front_valid = DIST_RIGHT_CENTER < MAX_DIST;
    bool right_corner_valid = DIST_RIGHT_CORNER == 1;
    bool right_side_valid = DIST_RIGHT_SIDE == 1;
    if((left_front_close_valid || right_front_close_valid)
        && !(right_corner_valid || left_corner_valid || left_side_valid || right_side_valid)){
        return FRONT_CLOSE;
    }

    if((left_front_valid || right_front_valid)
            && !(right_corner_valid || left_corner_valid || left_side_valid || right_side_valid)){
        return FRONT_FAR;
    }

    if(left_front_valid && left_corner_valid
            && !(right_corner_valid || right_front_valid || left_side_valid || right_side_valid)){
        return LEFT_CORNER_FRONT;
    }

    if(right_front_valid && right_corner_valid
            && !(left_corner_valid || left_front_valid || left_side_valid || right_side_valid)){
        return RIGHT_CORNER_FRONT;
    }

    if(left_corner_valid
            && !(right_corner_valid || right_front_valid || left_side_valid || right_side_valid || left_front_valid)){
        return LEFT_CORNER;
    }

    if(right_corner_valid
            && !(left_corner_valid || right_front_valid || left_side_valid || right_side_valid || left_front_valid)){
        return RIGHT_CORNER;
    }

    if(left_side_valid && left_corner_valid
            && !(right_corner_valid || right_front_valid || left_front_valid || right_side_valid)){
        return LEFT_CORNER_SIDE;
    }

    if(right_side_valid && right_corner_valid
            && !(left_corner_valid || left_front_valid || left_side_valid || right_front_valid)){
        return RIGHT_CORNER_SIDE;
    }

    if(left_side_valid
            && !(right_corner_valid || right_front_valid || left_corner_valid || right_side_valid || left_front_valid)){
        return LEFT_SIDE;
    }

    if(right_side_valid
            && !(left_corner_valid || right_front_valid || left_side_valid || right_corner_valid || left_front_valid)){
        return RIGHT_SIDE;
    }
    return BEHIND;
}

/**
 * OTHER
**/
void balance_motors() {
    if (left_encoder > right_encoder) {
        left_multi = right_encoder/left_encoder;
        right_multi = 1;
    } else {
        right_multi = left_encoder/right_encoder;
        left_multi = 1;
    }
}
