#include "WifiCam.hpp"
#include <WiFi.h>
#include <Servo.h>

float x_angle = 90;
float y_angle = 0;
float rawx_angle = 90; 
float rawy_angle = 0; 
String angle_info = "";
Servo xservo;
Servo yservo;
static const int yServoPin = 32;
static const int xServoPin = 33;
float parseXinfo(String data);
float parseYinfo(String data);
void serialEvent();


static const char* WIFI_SSID = "BELL011";
static const char* WIFI_PASS = "69D19EFEA96F";
esp32cam::Resolution initialResolution;

WebServer server(80);

void
setup()
{
  Serial.begin(115200);
  Serial.println();
  delay(2000);

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

void loop()
{
  server.handleClient();
  
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

      rawx_angle =  parseXinfo(angle_info); 
      rawy_angle = parseYinfo(angle_info); 

      if (!((rawx_angle-x_angle)>-5 && (rawx_angle-x_angle) < 5)){
        x_angle = rawx_angle; 
      }
      if(!((rawy_angle-x_angle)>-5 && (rawy_angle-x_angle) < 5)){
        y_angle = rawy_angle; 
      }
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
