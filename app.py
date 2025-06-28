from flask import Flask, render_template, request, jsonify
from textblob import TextBlob
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import os

app = Flask(__name__)

# Ensure the static folder exists
os.makedirs('static', exist_ok=True)

def analyze_sentiment(text):
    analysis = TextBlob(text)
    polarity = analysis.sentiment.polarity
    
    if polarity > 0:
        return 'positive', polarity
    elif polarity == 0:
        return 'neutral', polarity
    else:
        return 'negative', polarity

def create_sentiment_chart(sentiment_data):
    labels = ['Positive', 'Neutral', 'Negative']
    values = [
        sentiment_data.count('positive'),
        sentiment_data.count('neutral'),
        sentiment_data.count('negative')
    ]
    
    colors = ['#4CAF50', '#FFC107', '#F44336']
    
    plt.figure(figsize=(6, 6))
    plt.pie(values, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
    plt.axis('equal')
    plt.title('Sentiment Distribution')
    
    # Save plot to a BytesIO object
    img = BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight', transparent=True)
    img.seek(0)
    plt.close()
    
    # Convert to base64 for embedding in HTML
    plot_url = base64.b64encode(img.getvalue()).decode('utf8')
    return plot_url

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analye():
    text = request.form.get('text')
    
    if not text:
        return jsonify({'error': 'Please enter some text to analyze'})
    
    # Analyze sentiment
    sentiment, polarity = analyze_sentiment(text)
    
    # Generate emoji based on sentiment
    emoji = ""
    if sentiment == 'positive':
        emoji = "😊"
    elif sentiment == 'neutral':
        emoji = "😐"
    else:
        emoji = "😞"
    
    # Prepare response
    response = {
        'sentiment': sentiment,
        'polarity': round(polarity, 2),
        'emoji': emoji,
        'text': text
    }
    
    return jsonify(response)

@app.route('/analyze_batch', methods=['POST'])
def analyze_batch():
    texts = request.form.getlist('texts[]')
    
    if not texts or len(texts) == 0:
        return jsonify({'error': 'Please enter some texts to analyze'})
    
    results = []
    sentiment_data = []
    
    for text in texts:
        if text.strip():  # Skip empty texts
            sentiment, polarity = analyze_sentiment(text)
            results.append({
                'text': text,
                'sentiment': sentiment,
                'polarity': round(polarity, 2)
            })
            sentiment_data.append(sentiment)
    
    if not results:
        return jsonify({'error': 'No valid texts to analyze'})
    
    # Generate chart
    chart_url = create_sentiment_chart(sentiment_data)
    
    return jsonify({
        'results': results,
        'chart': chart_url
    })

if __name__ == '__main__':
    app.run(debug=True)