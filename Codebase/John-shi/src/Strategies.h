#ifndef Strategies_H
#define Strategies_H

#include "Movement.h"
#include <Servo.h>


class Strategies {
public: 
    Strategies(Movement& robot, Servo& servo);
    void turtle();
    void rightFight(); 
    void leftFight(); 
    void forwardFight();
    void dashTurtle();
private:
    unsigned long turtleInchStart = 0;
    bool turtleInching = false;
    Movement& robot;    
    Servo& servo;
};

#endif
