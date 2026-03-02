import json
from pathlib import Path

import paho.mqtt.client as mqtt
import sqlite3

def on_connect(client, userdata, flags, reason_code, properties):
    """
    Handles actions taken when the client connects to the MQTT broker.

    This callback function is triggered once the client successfully
    establishes a connection with the MQTT broker. It logs the reason
    code for the connection and subscribes the client to a specific
    topic.

    :param client: The MQTT client instance that establishes the
        connection.
    :param userdata: User-defined data passed to the client
        on instantiation.
    :param flags: Response flags sent by the MQTT broker during
        connection.
    :param reason_code: The integer result code returned by the
        broker indicating the status of the connection attempt.
    :param properties: Additional connection properties returned
        by the broker in MQTT v5.0. May be None for earlier protocol
        versions.
    :return: None
    """
    print(f"Connected with result code {reason_code}")
    #subscribing to the Chanel
    client.subscribe("est/efi224/group2")


def on_message(client, userdata, msg):
    """
    Handles the MQTT message event, processes the data, and stores it in a local SQLite database.
    This function manages the creation of necessary database tables if they do not exist, decodes
    the incoming MQTT message, and inserts the data into the relevant database tables.

    :param client: Represents the MQTT client instance invoking the callback.
    :type client: Any
    :param userdata: Arbitrary user-defined data passed to the MQTT client for callback use.
    :type userdata: Any
    :param msg: Contains information about the message, including the payload.
    :type msg: Any
    :return: None
    """
    try:
        #try to get the Data from MQTT and connecting to the DB
        data = msg.payload.decode("utf-8")
        path_to_DB = Path(__file__).parent / ".auth"
        if not path_to_DB.exists():
            path_to_DB.mkdir(parents=True)
        path_to_DB_file = path_to_DB / "mqtt_metadata.db"
        conn = sqlite3.connect(path_to_DB_file)
        cursor = conn.cursor()
        #create the Table
        cursor.execute("""CREATE TABLE IF NOT EXISTS mqtt_metadata
                          (
                              temperature       VARCHAR(20),
                              pressure          VARCHAR(20),
                              altitude          VARCHAR(20),
                              humidity          VARCHAR(20),
                              location_id          VARCHAR(20),
                              capture_timestamp timestamp default (CURRENT_TIMESTAMP)
                          )""")
        cursor.execute("DROP TABLE IF EXISTS mqtt_lastwill")
        cursor.execute("""CREATE TABLE IF NOT EXISTS mqtt_lastwill
                          (
                              status VARCHAR(20)
                          )""")

        #Loads the data into the DB
        data_json = json.loads(data)
        if data_json["lastwill"] is not None:
            sql_statement = "INSERT INTO mqtt_lastwill (status) VALUES (?)"
            cursor.execute(sql_statement, (data_json["lastwill"],))
            conn.commit()
            conn.close()
            return
        pressure = str(data_json["pressure"])
        altitude = str(data_json["altitude"])
        temp = str(data_json["temp"])
        humidity = str(data_json["humidity"])
        location = str(data_json["location"])
        sql_statement = "INSERT INTO mqtt_metadata (temperature, pressure, altitude, humidity, location_id) VALUES (?, ?, ?, ?, ?)"
        cursor.execute(sql_statement, (temp, pressure, altitude, humidity, location))
        sql_statement = "INSERT INTO mqtt_lastwill (status) VALUES (?)"
        cursor.execute(sql_statement, ('online', ))
        conn.commit()
        #cursor.execute("DELETE FROM mqtt_metadata WHERE capture_timestamp < datetime('now', '-20 minutes')")
        #conn.commit()
        conn.close()
        print(f"Message received: {data}")
    except Exception as e:
        print(f"Error: {e}")

mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqttc.on_connect = on_connect
mqttc.on_message = on_message


#Connecting to the Broker
mqttc.connect("broker.hivemq.com", 1883, 60)

mqttc.loop_forever()
