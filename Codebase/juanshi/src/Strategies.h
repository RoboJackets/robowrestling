#ifndef Strategies_H
#define Strategies_H

#include "Movement.h"
#include <Servo.h>


class Strategies {
public: 
    Strategies(Movement& robot, Servo& servo);
    void Slowfight();
    void rightFight(); 
    void leftFight(); 
    void forwardFight();
private:
    Movement& robot;    
    Servo& servo;
};

#endif  