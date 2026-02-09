# SustainAdvisor Elite | SGX

An interactive ESG stock recommendation engine built with Flask. Adjust your Environmental, Social, Governance, and Yield preferences to get personalized SGX stock matches.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open **http://127.0.0.1:5001** in your browser.

## Features

- **Interactive sliders** for E, S, G, and Yield preferences (0–100%)
- **Real-time analysis** via `/api/analyze` (POST)
- **Stock cards** with Match Logic, Risk Alert, Payouts, Growth Path, Fun Fact, Website, and Start Investing buttons
- **Loading states** and error handling
- **Responsive UI** with animations and hover effects
