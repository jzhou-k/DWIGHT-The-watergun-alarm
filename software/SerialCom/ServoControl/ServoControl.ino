#include <Servo.h> 

float x_angle = 0;
float y_angle = 0;
String angle_info = "";
Servo xservo;
Servo yservo;

/*
 * Description:
 * Example for setting the minimal and maximal angle.
 */ 

static const int yServoPin = 32;
static const int xServoPin = 33; 

float parseXinfo(String data);
float parseYinfo(String data);
void serialEvent();

void setup() {
    Serial.begin(115200);
    yservo.attach(
        yServoPin, 
        Servo::CHANNEL_NOT_ATTACHED, 
        45,
        120
    );
    xservo.attach(
      xServoPin, 
      Servo::CHANNEL_NOT_ATTACHED, 
      45, 
      120 
      
    );

    xservo.write(0);
    delay(1000);
    yservo.write(90);

}

void loop() {
//    for(int posDegrees = 0; posDegrees <= 90; posDegrees++) {
//        yservo.write(posDegrees);
//        // xservo.write(posDegrees);
//        Serial.println(posDegrees);
//        delay(10);
//    }
//
//    for(int posDegrees = 90; posDegrees >= 0; posDegrees--) {
//        yservo.write(posDegrees);
//        // xservo.write(posDegrees);
//        Serial.println(posDegrees);
//        delay(10);
//    }

  serialEvent(); 
  xservo.write(x_angle);
  yservo.write(y_angle); 


}


void serialEvent()
{
  if (Serial.available() > 0)
  {
    char data = Serial.read();
    angle_info += data;
    // Serial.println(data);




    //Serial.println(Serial.available());
    if (data == '#')
    {

      x_angle = parseXinfo(angle_info);
      y_angle = parseYinfo(angle_info);
      angle_info = ""; 
    }

    
  }
}

float parseXinfo(String data)
{
  // X25Y25#
  data.remove(data.indexOf("Y")); //removes Y25 since remove() gets rid of everything to the end of the string
  data.remove(data.indexOf("X"), 1); //removes X

  return data.toFloat();
}

float parseYinfo(String data)
{
  data.remove(data.indexOf("X"),data.indexOf("Y")+1);
  data.remove(data.indexOf("#")); 
  return data.toFloat();
}
