from googleapiclient.discovery import build
import pandas as pd
from textblob import TextBlob

# Your API key
youtube_api_key = "AIzaSyBQRvP9qoTnCusaWVDT5UMJzu75TFdqDzk"

# Build YouTube service
youtube = build("youtube", "v3", developerKey=youtube_api_key)

# Search parameters
query = "smart fan"
max_results = 50  # you can increase this number up to 50 per request

# Perform search
search_response = youtube.search().list(
    q=query,
    part="id,snippet",
    type="video",
    maxResults=max_results
).execute()

# Collect video IDs
video_ids = [item["id"]["videoId"] for item in search_response["items"]]

# Get video statistics
video_response = youtube.videos().list(
    id=",".join(video_ids),
    part="snippet,statistics"
).execute()

# Define brands to track
brands = ["atomberg", "crompton", "orient", "havells", "usha"]

# Extract data
rows = []
for item in video_response["items"]:
    vid = item["id"]
    title = item["snippet"]["title"].lower()
    desc = item["snippet"]["description"].lower()
    views = int(item["statistics"].get("viewCount", 0))
    likes = int(item["statistics"].get("likeCount", 0))
    comments = int(item["statistics"].get("commentCount", 0))
    engagement = likes + comments

    # Detect brand mentions
    mentioned = [b for b in brands if b in title or b in desc]
    brand = mentioned[0] if mentioned else "other"

    # Sentiment analysis (on title + description)
    text = title + " " + desc
    polarity = TextBlob(text).sentiment.polarity
    if polarity > 0:
        sentiment = "positive"
    elif polarity < 0:
        sentiment = "negative"
    else:
        sentiment = "neutral"

    rows.append([vid, title, views, likes, comments, engagement, brand, sentiment])

# Create DataFrame
df = pd.DataFrame(rows, columns=["video_id", "title", "views", "likes", "comments", "engagement", "brand", "sentiment"])

# Basic Share of Voice (mentions)
sov_counts = df["brand"].value_counts(normalize=True) * 100

# Share of Positive Voice (only positive sentiment)
positive_df = df[df["sentiment"] == "positive"]
spv_counts = positive_df["brand"].value_counts(normalize=True) * 100

print("Video Data:")
print(df.head())
print("\nShare of Voice (% mentions):")
print(sov_counts)
print("\nShare of Positive Voice (% positive mentions):")
print(spv_counts)

# Save results
df.to_csv("youtube_smart_fan_sentiment.csv", index=False)
print("\nResults saved to youtube_smart_fan_sentiment.csv")
