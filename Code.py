from googleapiclient.discovery import build
import pandas as pd
from textblob import TextBlob
import matplotlib.pyplot as plt
import os

# API key
youtube_api_key = "AIzaSyBQRvP9qoTnCusaWVDT5UMJzu75TFdqDzk"

# YouTube service
youtube = build("youtube", "v3", developerKey=youtube_api_key)

# Search queries
queries = ["smart fan", "best bldc fan", "ceiling fan review"]

# Brands to track
brands = ["atomberg", "crompton", "orient", "havells", "usha"]

# Store all results
all_results = []

# Loop through each query
for q in queries:
    print(f"Processing query: {q}\n")

    # Perform search
    search_response = youtube.search().list(q=q,part="id,snippet",type="video",maxResults=50).execute()

    # Collect video IDs
    video_ids = [item["id"]["videoId"] for item in search_response["items"]]

    # Get video statistics
    video_response = youtube.videos().list(id=",".join(video_ids),part="snippet,statistics").execute()

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

        # Sentiment analysis
        text = title + " " + desc
        polarity = TextBlob(text).sentiment.polarity
        if polarity > 0:
            sentiment = "positive"
        elif polarity < 0:
            sentiment = "negative"
        else:
            sentiment = "neutral"

        rows.append([vid, title, views, likes, comments, engagement, brand, sentiment, q])

    all_results.extend(rows)

# Final DataFrame
df = pd.DataFrame(all_results,columns=["video_id", "title", "views", "likes", "comments", "engagement", "brand", "sentiment", "query"])

# Share of Voice
sov_counts = df.groupby("query")["brand"].value_counts(normalize=True).mul(100).rename("SoV %").reset_index()

#Share of Positive Voice
positive_df = df[df["sentiment"] == "positive"]
spv_counts = positive_df.groupby("query")["brand"].value_counts(normalize=True).mul(100).rename("SPV %").reset_index()

#Visualization using matplotlib
for q in queries:
    plt.figure(figsize=(8,5))
    
    # SoV
    data = sov_counts[sov_counts["query"] == q]
    plt.bar(data["brand"], data["SoV %"])
    plt.title(f"Share of Voice (SoV) for '{q}'")
    plt.ylabel("Percentage (%)")
    plt.xlabel("Brand")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
 
    # SPV
    data = spv_counts[spv_counts["query"] == q]
    plt.figure(figsize=(8,5))
    plt.bar(data["brand"], data["SPV %"], color="green")
    plt.title(f"Share of Positive Voice (SPV) for '{q}'")
    plt.ylabel("Percentage (%)")
    plt.xlabel("Brand")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

# printing data of SOV 
print("Share of Voice (% mentions):")
print(sov_counts)

#printing data of SOPV
print("Share of Positive Voice (% positive mentions):")
print(spv_counts)

df.to_csv("Quantified data from SOV analysis .csv", index=False)
