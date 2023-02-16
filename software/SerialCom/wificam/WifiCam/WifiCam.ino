#include "WifiCam.hpp"
#include <WiFi.h>
#include <Servo.h>

float x_angle = 90;
float y_angle = 90;
float rawx_angle = 90;
float rawy_angle = 90;
int triggerInfo = 0;
String angle_info = "";


Servo xservo;
Servo yservo;
Servo triggerServo;
static const int yServoPin = 32;
static const int xServoPin = 33;
static const int triggerServoPin = 12; //to be determined

boolean data_received = false ;


void calibrateXangle();
void calibrateYangle();
float parseXinfo(String data);
float parseYinfo(String data);
void serialEvent();
void trigger();


static const char* WIFI_SSID = "BELL011";
static const char* WIFI_PASS = "69D19EFEA96F";
esp32cam::Resolution initialResolution;


WebServer server(80);

void setup()
{
  Serial.begin(115200);
  Serial.println();
  delay(2000);

  Serial.begin(115200);
  yservo.attach(
    yServoPin,
    Servo::CHANNEL_NOT_ATTACHED,
    50,
    250 
  );
  xservo.attach(
    xServoPin,
    Servo::CHANNEL_NOT_ATTACHED,
    50,
    250

  );

  triggerServo.attach(
    triggerServoPin,
    Servo::CHANNEL_NOT_ATTACHED,
    //100, 200 no go 
    //15, 100 kinda?? 
    15,
    200
  );

  // triggerServo.write(0);



  WiFi.persistent(false);
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  if (WiFi.waitForConnectResult() != WL_CONNECTED) {
    Serial.println("WiFi failure");
    delay(5000);
    ESP.restart();
  }
  Serial.println("WiFi connected");

  {
    using namespace esp32cam;

    initialResolution = Resolution::find(1024, 768);

    Config cfg;
    cfg.setPins(pins::FreeNove);
    cfg.setResolution(initialResolution);
    cfg.setJpeg(80);

    bool ok = Camera.begin(cfg);
    if (!ok) {
      Serial.println("camera initialize failure");
      delay(5000);
      ESP.restart();
    }
    Serial.println("camera initialize success");
  }

  Serial.println("camera starting");
  Serial.print("http://");
  Serial.println(WiFi.localIP());

  addRequestHandlers();
  server.begin();
}
//***********************************************************
void loop()
{
  server.handleClient();

  
  serialEvent();
  if(data_received)
  {
    xservo.write(x_angle);
    yservo.write(y_angle);
  }
  
  //calibrateEvery();
  //if (triggerInfo) {
    //trigger();
  //}
  delay(1);

}
//***********************************************************

void tryingTrigger()
{
  yservo.write(20);
  delay(2000);
  yservo.write(90);
  delay(2000); 

 //45 
  triggerServo.write(50);
  delay(1500);
  triggerServo.write(18);
  delay(1000);
}

void calibrateEvery()
{
  calibrateYangle();
  delay(1000);
  calibrateZangle();
  delay(1000); 
  calibrateXangle();
}


void calibrateZangle()
{
  delay(100);
  triggerServo.write(45);
  delay(200);
  triggerServo.write(20);
  delay(500);
}

void calibrateXangle()
{
  delay(5000);
  xservo.write(45);
  delay(5000);
  xservo.write(90);
  delay(5000);
  xservo.write(135);
  delay(5000);
  xservo.write(90);

}


void calibrateYangle()
{
  delay(5000);
  yservo.write(85);
  delay(5000);
  yservo.write(90);
  delay(5000);
  yservo.write(95);
  delay(5000); 
  yservo.write(90);
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

      x_angle =  parseXinfo(angle_info);
      y_angle = parseYinfo(angle_info);
      triggerInfo = parseZinfo(angle_info);
      data_received = true; 
      angle_info = "";
    }else
    {
      data_received = false; 
    }
    

  }

}

float parseXinfo(String data)
{
  // X25Y25Z0#
  data.remove(data.indexOf("Y")); //removes Y25 since remove() gets rid of everything to the end of the string
  data.remove(data.indexOf("X"), 1); //removes X

  return data.toFloat();
}

float parseYinfo(String data)
{
  data.remove(data.indexOf("X"), data.indexOf("Y") + 1);
  data.remove(data.indexOf("Z"));
  return data.toFloat();
}

int parseZinfo(String data)
{
  // 1 to shoot 0 to not shoot
  data.remove(data.indexOf("X"), data.indexOf("Z") + 1);
  data.remove(data.indexOf("#"));
  return data.toInt();
}

void trigger()
{
  for (int i = 0; i < 3; i++)
  {
    triggerServo.write(90);
    delay(300);
    triggerServo.write(20);
    delay(300);
  }
}


//initial calibration of watergun -> lean back the watergun
//if trigger = true -> shooot
//if face stay in place for 5 sec (with tolerace) shoot
