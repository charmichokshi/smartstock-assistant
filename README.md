# SmartStock Analyst

A Streamlit-based web application that analyzes stock performance using real-time data, news sentiment, and optional chart analysis, powered by Gemini 2.5 Pro and an agent development framework. The app autonomously fetches stock data, performs sentiment and trend analysis, and generates downloadable PDF reports. Deployable on Google Cloud Run using Docker.

## Features

- **Stock Data Analysis**: Fetches real-time stock prices and weekly trends using `yfinance`.
- **News Sentiment Analysis**: Analyzes recent news headlines to determine bullish or bearish sentiment using Gemini 2.5 Pro.
- **Chart Analysis**: Optionally uploads financial charts or screenshots for technical analysis (e.g., moving averages, RSI).
- **PDF Reports**: Generates downloadable PDF reports summarizing stock data, trends, sentiment, and chart analysis.
- **User-Friendly Interface**: Built with Streamlit for an intuitive web experience.
- **Agentic Capabilities**: Leverages an agent development framework to enable autonomous task execution, including:
  - Extracting and validating stock tickers from user input.
  - Decision-making for error handling (e.g., invalid tickers or API failures).
  - Orchestrating multi-step workflows (data fetching, AI analysis, report generation).
  - The app does not require advanced agentic features like iterative reasoning, memory management, or multi-agent collaboration, keeping the implementation lightweight and focused.
- **Cloud Deployment**: Deployed on Google Cloud Run using a Docker container for scalability and reliability.

## Tech Stack

- **Frontend**: Streamlit (`1.39.0`)
- **Backend**: Python (`3.11`), Google Generative AI SDK (`google-generativeai==0.8.3`), Agent Development Framework
- **Data Sources**: Yahoo Finance (`yfinance==0.2.44`), Google News RSS (`feedparser==6.0.11`)
- **Image Processing**: Pillow (`10.4.0`)
- **PDF Generation**: ReportLab (`4.2.2`)
- **Deployment**: Google Cloud Run, Docker

## Prerequisites

- Python 3.11
- Docker (for containerization)
- Google Cloud SDK (for Cloud Run deployment)
- Gemini API Key (from [Google AI Studio](https://aistudio.google.com/))

## Installation

```bash
Clone the Repository
git clone https://github.com/charmichokshi/smartstock-assistant.git
cd smartstock-assistant

Set Up a Virtual Environment (optional, for local development):
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

Install Dependencies:
pip install -r requirements.txt


Set the Gemini API Key:
Export the key locally:export GEMINI_API_KEY=your-api-key-from-aistudio
On Windows:set GEMINI_API_KEY=your-api-key-from-aistudio

Run the App Locally:
streamlit run app.py

Access at http://localhost:8501.
Test by entering a stock ticker (e.g., "PLTR") and optionally uploading a chart.

Project Structure
smartstock-assistant/
├── app.py                # Main Streamlit application
├── Dockerfile            # Docker configuration for Cloud Run
├── requirements.txt      # Python dependencies
└── .dockerignore         # Files to exclude from Docker image

Deploying to Google Cloud Run

Set Up Google Cloud:

Create a project in the Google Cloud Console.
Enable Cloud Run and Container Registry APIs:gcloud services enable run.googleapis.com containerregistry.googleapis.com

Authenticate Google Cloud SDK:gcloud init

Build the Docker Image:
docker build -t gcr.io/[PROJECT-ID]/smartstock-assistant .

Push to Google Container Registry:
gcloud auth configure-docker
docker push gcr.io/[PROJECT-ID]/smartstock-assistant

Deploy to Cloud Run:
gcloud run deploy smartstock-analyst \
  --image gcr.io/[PROJECT-ID]/smartstock-assistant \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GEMINI_API_KEY=your-api-key-from-aistudio

Replace [PROJECT-ID] with your Google Cloud project ID and your-api-key-from-aistudio with your Gemini API key.
Access the app via the provided Cloud Run URL (e.g., https://smartstock-analyst-XXXX.a.run.app).
```


## Usage

Open the app in a browser (local: http://localhost:8501, Cloud Run: provided URL).
Enter a stock ticker (e.g., "What's happening with PLTR?") in the text input.
Optionally upload a financial chart (PNG/JPG).
Click "Analyze" to view:
Stock summary (current price, daily/weekly change).
Trend analysis (full name, trend, news connection, investor insight).
Sentiment analysis (bullish/bearish based on news).
Chart analysis (if uploaded).
Download the PDF report for a summary.


## Limitations

AI Accuracy: The app uses AI-generated responses (Gemini 2.5 Pro), which may be inaccurate. Use with caution.
Data Sources: Relies on Yahoo Finance and Google News RSS, which may have delays or limitations.
Agentic Scope: The app leverages an agent development framework for autonomous task execution, ticker validation, and error handling but does not implement advanced agentic features like iterative reasoning, memory management, or multi-agent collaboration.


## Future Improvements

Enhance agentic capabilities with iterative reasoning or user feedback loops.
Integrate additional data sources (e.g., X posts for sentiment).
Implement user authentication for private access.
Optimize Docker image size for faster deployments.


## License
MIT License. See LICENSE for details.

## Contributing
Contributions are welcome! Please open an issue or submit a pull request for bug fixes, features, or improvements.

## Contact
For questions, contact [charmichokshi@gmail.com] or open an issue on GitHub.

Built with ❤️ by [Charmi Chokshi]
