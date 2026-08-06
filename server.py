from flask import Flask, request, jsonify
import mysql.connector

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload():

    data = request.json

    print("\n===== SENSOR DATA RECEIVED =====")

    print("Temperature:", data["temperature"])
    print("Humidity:", data["humidity"])
    print("CO2:", data["CO2"])
    print("VOC:", data["VOC"])
    print("Ethanol:", data["ethanol"])
    print("Ethylene:", data["ethylene"])
    print("NH3:", data["NH3"])
    print("H2S:", data["H2S"])

    print("================================")

    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="iotfeedbridge"
    )

    cursor = conn.cursor()

    sql = """
    INSERT INTO iotparameters
    (temperature, humidity, CO2, VOC, ethanol, ethylene, NH3, H2S)
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
    """

    values = (
        data["temperature"],
        data["humidity"],
        data["CO2"],
        data["VOC"],
        data["ethanol"],
        data["ethylene"],
        data["NH3"],
        data["H2S"]
    )

    cursor.execute(sql, values)

    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({"status":"success"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4000)