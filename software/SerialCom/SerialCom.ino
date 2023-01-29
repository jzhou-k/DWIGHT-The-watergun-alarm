#include <Servo.h>

String sentence = "end of sentence";
float x_angle = 0;
float y_angle = 0;
String angle_info = "";
Servo xservo;
Servo yservo;


float parseXinfo(String data);
float parseYinfo(String data);
void serialEvent();

void setup() {

  // put your setup code here, to run once:
  Serial.begin(115200);
  pinMode(LED_BUILTIN, OUTPUT);
  xservo.attach(9);
  yservo.attach(8); 
}



void loop() {
  // put your main code here, to run repeatedly:
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
