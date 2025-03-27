# Digital Twin Brewing Control Dashboard

A Streamlit application that provides a dashboard to control a digital twin of a brewing system.

## Features

- Real-time monitoring of brewing parameters (temperature, pressure, pH, dissolved oxygen)
- Historical data visualization
- Control of non-critical parameters (data collection frequency)
- Safety thresholds for pressure control
- Critical operations requiring physical presence and verification

## Installation

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

Run the Streamlit application:
```
cd app
streamlit run app.py
```

## Safety Features

- The system incorporates safety thresholds for pressure control
- Critical operations require physical presence and manual confirmation
- Automatic prevention of unsafe commands