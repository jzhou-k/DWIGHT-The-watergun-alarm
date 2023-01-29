#include <Servo.h>

String sentence = "end of sentence";
float x_angle = 0;
float y_angle = 0;
String angle_info = "";
Servo myservo;


float parseXinfo(String data);
void serialEvent();

void setup() {

  // put your setup code here, to run once:
  Serial.begin(115200);
  pinMode(LED_BUILTIN, OUTPUT);
  myservo.attach(9);

}



void loop() {
  // put your main code here, to run repeatedly:
  serialEvent();
  myservo.write(x_angle);

}

void serialEvent()
{
  if (Serial.available() > 0)
  {
    char data = Serial.read();
    angle_info += data;
    Serial.println(data);




    //Serial.println(Serial.available());
    if (data == '#')
    {

      x_angle = parseXinfo(angle_info);
      Serial.println(x_angle);
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

double parseYinfo()
{
  //lol
}
