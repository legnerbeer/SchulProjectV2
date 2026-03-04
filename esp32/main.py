# Library imports
from machine import Pin, ADC, I2C
import ssd1306, dht20, bmp280
import time
from lis3dhtr import LIS3DHTR
import wifi
import mqtt
import json

# Pin-Zuordnung
LED_PIN = 27    #D6
BUZZER_PIN = 16   # D5
BUTTON_PIN = 17   # D4
LIGHT_PIN = 34     #ADC0
POTI_PIN = 2
SOUND_PIN = 35

#WLAN & MQTT
ssid = "Pixel_8523"
password = "24rubin!"
server = "broker.hivemq.com"
topic = b'est/efi224/group2'

#Variablen deklarieren
duration = 0
loc = "1"
status_Verbindung = 'OFF'
status_Übertragung = ''

#Verbindung per MQTT aufbauen & Festlegung KeepAlive für Last Will
client = mqtt.MQTTClient(server, keepalive=180)

#LED Blinken für zusätzliches visuelles Signal bei Standortwechsel
def LED_blink():
    led.value(1)
    time.sleep_ms(200)
    led.value(0)
    time.sleep_ms(200)
    
    
#Methode für WLAN- und MQTT Verbindung
def wlan_connect():
    global status_Verbindung
    try:
    #Connection
        wifi.wifiConnect(ssid, password)
        
        #Last Will offline
        lw_topic = topic
        lw_message = json.dumps({"lastwill":"offline"})
        client.set_last_will(lw_topic, lw_message, retain=True, qos=1)
        
        # Mit MQTT verbinden
        client.mqttConnect()
        
        #Online Status
        lw_message = {"lastwill":"online"}
        client.set_last_will(lw_topic, json.dumps(lw_message), retain=True, qos=1)
        status_Verbindung = 'ON'
        OLED_refresh()
        
        #Wenn keine Verbindung dann automatisch neu verbinden und Status festlegen
    except OSError as e:
        status_Verbindung = 'OFF'
        print('Failed to connect to Local Network or MQTT broker.')
        print('Reconnecting...')
        OLED_refresh()
        time.sleep(3)
        wlan_connect()
        
#Aktuelle Daten auf OLED-Display anzeigen
def OLED_refresh():
    oled.text('Connection: ' + status_Verbindung, 3, 5)
    oled.text('MQTT: ' + status_Übertragung, 3, 20)
    oled.text('Location: ' + loc, 3, 35)
    oled.show()

# Hardware initialisieren
led = Pin(LED_PIN, Pin.OUT)
buzzer = Pin(BUZZER_PIN, Pin.OUT)
button = Pin(BUTTON_PIN, Pin.IN, Pin.PULL_UP)
light_sensor = ADC(LIGHT_PIN)
poti = ADC(POTI_PIN)
poti.atten(ADC.ATTN_11DB)
sound_sensor = ADC(SOUND_PIN)
sound_sensor.atten(ADC.ATTN_11DB)

# OLED-Display initialisieren
i2c = I2C(0, scl=Pin(22), sda=Pin(21))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)
print("I2C devices found:", i2c.scan())
lis=LIS3DHTR(i2c)
dht=dht20.DHT20(0x38,i2c)
bmpSensor = bmp280.BMP280(i2c, 0x77, 101700)

OLED_refresh()
wlan_connect()

#Dauerschleife
while True:
    oled.fill(0)
    status_Übertragung = '...'
    
    #Messdaten abgreifen
    air_wet = dht.measurements['rh']# in %
    temp2 = bmpSensor.temperature   # in °C
    pres = bmpSensor.pressure      	# in hPa
    alt = bmpSensor.altitude		# in m
    
    #print(f"hoehe: {alt:.2f}")
    #print(f"temp: {temp2:.2f}")
    #print(f"pressure: {pres:.2f}")
    #print(f"measurements: {air_wet:.2f}")
    
    # Messdaten sammeln
    messwerte = {
        "pressure": pres,
        "altitude": alt,
        "temp": temp2,
        "humidity": air_wet,
        "location": loc,
        "lastwill" : None
    }
    
    #Button Logik
    if button.value() == 1:
        press_time = time.ticks_ms()
                 
        while button.value() == 1:
        
            duration = time.ticks_diff(time.ticks_ms(), press_time)   
       
        #Standortwechsel per Knopfdruckdauer
        if duration >= 3000:
            loc = "3"
            LED_blink()

        if duration >= 2000 and duration < 3000:
            loc = "2"
            LED_blink()

        if duration >= 1000 and duration < 2000:
            loc = "1"
            LED_blink()
            
        #Senden der Daten sowie Ausgabe des Sendestatus
        if duration >= 10 and duration < 1000:
            try:
                client.mqttPublish(topic, json.dumps(messwerte))
                print(messwerte)
                status_Übertragung = 'PUBLISHED'
                #Bei Fehlschlag in wlan_connect Funktion springen um Verbindung zu überprüfen
            except Exception as e:
                print('MQTT publish failed.')
                status_Übertragung = 'FAILED'
                wlan_connect()
    OLED_refresh()
    time.sleep_ms(50)