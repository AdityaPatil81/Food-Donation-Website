# IoT FeedBridge 🍱

IoT FeedBridge is an IoT and Machine Learning based system designed to monitor surplus food and help distribute safe and fresh food to people in need.

The system continuously monitors food-related environmental parameters, stores the sensor data in a cloud database, and uses Machine Learning to predict whether the selected food type is **Fresh or Spoiled**.

## 🎯 Objectives

- Reduce wastage of surplus food from restaurants, hotels, parties and social events.
- Continuously monitor the condition of stored surplus food.
- Detect possible food spoilage using sensor data.
- Connect safe surplus food with NGOs and volunteers for distribution.
- Prevent spoiled food from being distributed to people in need.

## ⚙️ How It Works

```text
Food / Surplus Food
        ↓
Sensors
        ↓
ESP32
        ↓
Wi-Fi
        ↓
Flask API (Render)
        ↓
TiDB Cloud
        ↓
Streamlit Dashboard
        ↓
Machine Learning Model
        ↓
Fresh / Spoiled Prediction
        ↓
NGO / Volunteer
        ↓
People in Need
