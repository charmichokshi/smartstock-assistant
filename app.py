import streamlit as st
import google.generativeai as genai
import yfinance as yf
import feedparser
import datetime
import re
import os
from PIL import Image
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import tempfile

# Configure Gemini API
try:
    if not os.getenv("GEMINI_API_KEY"):
        raise ValueError("GEMINI_API_KEY environment variable is not set.")
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
except Exception as e:
    st.error(
        f"Failed to configure Gemini API: {e}. Please set GEMINI_API_KEY in your Cloud Run environment variables.")
    st.stop()


# Helper Functions
def analyze_image(image_data, prompt):
    """Analyze an uploaded financial chart or screenshot using Gemini 2.5 Pro."""
    try:
        model = genai.GenerativeModel("gemini-2.5-pro")
        response = model.generate_content([prompt, image_data])
        return response.text
    except Exception as e:
        return f"Error analyzing image: {str(e)}"


def fetch_stock_data(ticker):
    """Fetch stock data and news headlines for the given ticker."""
    try:
        today = datetime.datetime.now().date()
        seven_days_ago = today - datetime.timedelta(days=6)
        ticker_obj = yf.Ticker(ticker)
        data = ticker_obj.history(start=seven_days_ago, end=today + datetime.timedelta(days=1))
        data = data["Close"].dropna().round(2)

        if len(data) < 2:
            return {"error": f"Not enough data for {ticker}."}

        price = data.iloc[-1]
        change = (data.iloc[-1] - data.iloc[-2]) / data.iloc[-2] * 100
        week_change = (data.iloc[-1] - data.iloc[0]) / data.iloc[0] * 100
        closing_prices = data.tolist()
        dates = [seven_days_ago + datetime.timedelta(days=i) for i in range(7)]
        trend_data = "\n".join([f"{d.strftime('%Y-%m-%d')}: ${p}" for d, p in zip(dates, closing_prices)])

        # Fetch news
        rss_url = f"https://news.google.com/rss/search?q={ticker}+stock"
        feed = feedparser.parse(rss_url)
        headlines = [entry.title for entry in feed.entries[:20]]

        return {
            "price": price,
            "change": change,
            "week_change": week_change,
            "trend_data": trend_data,
            "headlines": headlines
        }
    except Exception as e:
        return {"error": str(e)}


def analyze_sentiment(headlines):
    """Analyze sentiment of news headlines using Gemini 2.5 Pro."""
    try:
        model = genai.GenerativeModel("gemini-2.5-pro")
        headlines_text = '\n'.join(f'- {h}' for h in headlines)
        prompt = f"""
        Analyze the sentiment of the following news headlines for a stock:
        Headlines:
        {headlines_text}

        Provide a sentiment summary (Bullish, Slightly Bullish, Neutral, Slightly Bearish, Bearish) and a brief explanation (1-2 sentences).
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error analyzing sentiment: {str(e)}"


def generate_pdf_report(data):
    """Generate a PDF report summarizing stock analysis with dynamic text wrapping."""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            doc = SimpleDocTemplate(tmp_file.name, pagesize=letter)
            styles = getSampleStyleSheet()
            style_normal = styles["Normal"]
            style_heading = styles["Heading1"]
            style_subheading = styles["Heading2"]

            # Build PDF content
            story = []

            # Title
            story.append(Paragraph(f"Stock Analysis Report: {data['ticker']}", style_heading))
            story.append(Spacer(1, 12))

            # Metadata
            story.append(Paragraph(f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d')}", style_normal))
            story.append(Paragraph(f"Current Price: ${data['price']:.2f} ({data['change']:+.2f}% today)", style_normal))
            story.append(Paragraph(
                f"Weekly Change: {'gained' if data['week_change'] > 0 else 'lost'} {abs(data['week_change']):.2f}%",
                style_normal))
            story.append(Spacer(1, 12))

            # Trend Analysis
            story.append(Paragraph("Trend Analysis", style_subheading))
            story.append(Paragraph(data["trend_analysis"].replace('\n', '<br/>'), style_normal))
            story.append(Spacer(1, 12))

            # Sentiment Analysis
            story.append(Paragraph("Sentiment Analysis", style_subheading))
            story.append(Paragraph(data["sentiment_analysis"].replace('\n', '<br/>'), style_normal))
            story.append(Spacer(1, 12))

            # Chart Analysis (if available)
            if "image_analysis" in data and data["image_analysis"]:
                story.append(Paragraph("Chart Analysis", style_subheading))
                story.append(Paragraph(data["image_analysis"].replace('\n', '<br/>'), style_normal))
                story.append(Spacer(1, 12))

            # Build the PDF
            doc.build(story)
            return tmp_file.name
    except Exception as e:
        return f"Error generating report: {str(e)}"


# Streamlit App
st.set_page_config(page_title="SmartStock Analyst", layout="centered")
st.title("📈 SmartStock Analyst")
st.caption("Analyze stocks with price trends, news, sentiment, chart analysis, and downloadable reports.")

# User input
question = st.text_input("Ask about a stock (e.g., 'What's happening with AAPL or TSLA?'):").strip()
uploaded_file = st.file_uploader("Upload a financial chart or screenshot (optional)", type=["png", "jpg", "jpeg"])

# Button to trigger analysis
if st.button("Analyze"):
    # Validate ticker input
    ticker_input = ""
    if question:
        possible_tickers = re.findall(r"\b[A-Z]{1,5}\b", question)
        for word in possible_tickers:
            try:
                ticker = yf.Ticker(word)
                info = ticker.info
                if info and 'symbol' in info:
                    ticker_input = word
                    break
            except Exception as e:
                st.warning(f"Error validating ticker '{word}': {e}")

    if not ticker_input:
        st.warning("Please enter a valid stock symbol (e.g., AAPL, TSLA, or MSFT).")
        st.stop()

    # Orchestrate tasks
    with st.spinner(f"Analyzing {ticker_input}..."):
        # Step 1: Fetch stock data
        stock_data = fetch_stock_data(ticker_input)
        if "error" in stock_data:
            st.error(stock_data["error"])
            st.stop()

        # Step 2: Perform sentiment analysis
        sentiment_result = analyze_sentiment(stock_data["headlines"])
        if "Error" in sentiment_result:
            st.error(sentiment_result)
            st.stop()

        # Step 3: Perform image analysis if uploaded
        image_analysis = ""
        if uploaded_file:
            try:
                image = Image.open(uploaded_file)
                st.image(image, caption="Uploaded Chart", use_container_width=True)
                image_prompt = f"""
                Analyze this financial chart or screenshot for {ticker_input}. Identify key patterns such as moving averages, trends, or indicators (e.g., 50-day vs. 200-day moving average, RSI, MACD). Provide a concise insight, such as whether the chart indicates a bullish or bearish trend.
                """
                image_analysis = analyze_image(image_data=image, prompt=image_prompt)
                if "Error" in image_analysis:
                    st.error(image_analysis)
                    st.stop()
            except Exception as e:
                st.error(f"Error processing image: {e}")
                st.stop()

        # Step 4: Perform trend analysis
        trend_prompt = f"""
        You are a financial analyst AI.
        Analyze the stock performance of {ticker_input} over the past week based on:
        {stock_data['trend_data']}
        Recent headlines:
        {'-'.join(f'- {h}' for h in stock_data['headlines'])}
        Provide in short:
        1. Full name of stock and main highlight
        2. Overall trend (rising, falling, flat)
        3. Connection with relevant news
        4. Investor insight (1-2 sentences)

        Do NOT make up news or events. Only use what’s above. Avoid repetitions and any extra or filler words. 
        """
        try:
            trend_analysis = genai.GenerativeModel("gemini-2.5-pro").generate_content(trend_prompt).text
        except Exception as e:
            st.error(f"Error in trend analysis: {e}")
            st.stop()

        # Step 5: Generate report
        report_data = {
            "ticker": ticker_input,
            "price": stock_data["price"],
            "change": stock_data["change"],
            "week_change": stock_data["week_change"],
            "trend_analysis": trend_analysis,
            "sentiment_analysis": sentiment_result,
            "image_analysis": image_analysis if uploaded_file else ""
        }
        report_file = generate_pdf_report(report_data)
        if "Error" in report_file:
            st.error(report_file)
            st.stop()

        # Display results
        st.subheader("🧾 Stock Summary")
        st.write(f"📌  {ticker_input} current price: ${stock_data['price']:.2f} ({stock_data['change']:+.2f}% today)."
                 f" Over the past week, the stock has {'gained' if stock_data['week_change'] > 0 else 'lost'} {abs(stock_data['week_change']):.2f}%")

        st.markdown("<h3 style='font-size: 24px;'>📈 Trend Analysis</h3>", unsafe_allow_html=True)
        st.write(trend_analysis)

        st.markdown("<h3 style='font-size: 24px;'>😊 Sentiment Analysis</h3>", unsafe_allow_html=True)
        st.write(sentiment_result)

        if image_analysis:
            st.markdown("<h3 style='font-size: 24px;'>📊 Chart Analysis:</h3>", unsafe_allow_html=True)
            st.write(image_analysis)

        # Provide downloadable report
        try:
            with open(report_file, "rb") as file:
                st.download_button(
                    label="Download Analysis Report (PDF)",
                    data=file,
                    file_name=f"{ticker_input}_analysis_report.pdf",
                    mime="application/pdf"
                )
        except Exception as e:
            st.error(f"Error providing report download: {e}")

        st.markdown(
            "> ⚠️ *This app uses AI-generated responses. They may be inaccurate or incorrect — use with caution.*")
