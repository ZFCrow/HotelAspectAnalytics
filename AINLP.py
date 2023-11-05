import os
import pandas as pd
from google.cloud import language_v1
from tqdm import tqdm
import concurrent.futures
from sklearn.metrics import confusion_matrix, accuracy_score
import chatgpt
import constants

def analyze_hotel_reviews(hotel_name):


    current_directory = os.getcwd()
    csv_file_path = os.path.join(current_directory, f'DatabyHotel/{hotel_name} ReviewData/hotelData.csv')

    try:
        df = pd.read_csv(csv_file_path, nrows=601)  # Limit to 601 lines due to NLP API limit
        reviews_ratings = df.iloc[:, [2, 3]].dropna()
        reviews = reviews_ratings.iloc[:, 0]
        ratings = reviews_ratings.iloc[:, 1].apply(lambda x: int(x.split()[0]))
        ratings = ratings.apply(lambda x: 0 if x <= 2 else (2 if x == 3 else 1))
    except FileNotFoundError:
        print('hotelData.csv not found!')

    # Initialize the Language Service client and set the API key and the quota project id.
    nlp_client = language_v1.LanguageServiceClient(
        client_options={"api_key": constants.googleNLPAPIKEY, "quota_project_id": "hotel-analysis-401203"}
    )

    entity_counts = {}


    # Initialize variables for confusion matrix
    y_true = []
    y_pred = []
    review_list = []
    rating_list = []
    avg_entity_sentiment_list = []  # List to store average entity sentiment scores

    # progress bar for the loop
    with tqdm(total=len(reviews), desc="Analyzing Reviews", unit=" review") as pbar:

        # This thing is the one that analyzes the review
        def analyze_review(review, rating):
            try:
                nonlocal y_true, y_pred, review_list, rating_list, entity_counts, avg_entity_sentiment_list

                # Call NLP to analyze the entity + sentiment of the review
                document = language_v1.Document(content=review, type_=language_v1.Document.Type.PLAIN_TEXT)
                entity_response = nlp_client.analyze_entity_sentiment(document=document)
                entities = entity_response.entities

                entity_sentiment_scores = []  # To store entity sentiment scores for this review

                # Calculate sentiment based on sentiment score (you can adjust this threshold)
                sentiment_score = sum([entity.sentiment.score for entity in entities]) / len(entities) if entities else 0
                if sentiment_score >= 0.2:
                    predicted_rating = 1
                elif sentiment_score <= -0.2:
                    predicted_rating = 0
                else:
                    predicted_rating = 2 #neutral

                # Process and count entities
                for entity in entities:
                    entity_name = entity.name.lower()  # Convert to lowercase
                    sentiment_score = entity.sentiment.score

                    # Check if the entity is purely numeric
                    if not entity_name.isnumeric():
                        if entity_name in entity_counts:
                            entity_counts[entity_name]["count"] += 1
                            entity_counts[entity_name]["sentiment_scores"].append(sentiment_score)
                        else:
                            entity_counts[entity_name] = {"count": 1, "sentiment_scores": [sentiment_score]}

                        entity_sentiment_scores.append(sentiment_score)

                # Calculate the average entity sentiment score for this review
                avg_entity_sentiment = sum(entity_sentiment_scores) / len(entity_sentiment_scores) if entity_sentiment_scores else 0
                avg_entity_sentiment_list.append(avg_entity_sentiment)

                y_true.append(rating)
                y_pred.append(predicted_rating)
                review_list.append(review)
                rating_list.append(rating)

            except Exception as e:
                print(f"Error analyzing review: {str(e)}")

            # Update the progress bar
            pbar.update(1)

        # Use multi-threading to parallelize the analysis
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            for review, rating in zip(reviews, ratings):
                executor.submit(analyze_review, review, rating)

    # Create a DataFrame to store the results
    results_df = pd.DataFrame({
        'Review': review_list,
        'Avg Entity Sentiment': avg_entity_sentiment_list,  # Add average entity sentiment as a new column
        'Actual': y_true,
        'Predicted': y_pred
    })

    # Save the results to a CSV file
    results_df.to_csv('sentiment_results.csv', index=False)

    # Save entity counts and sentiment scores to a CSV file
    entity_counts_df = pd.DataFrame(entity_counts).T.reset_index()
    entity_counts_df.columns = ['Entity', 'Count', 'Avg Sentiment']
    entity_counts_df['Avg Sentiment'] = entity_counts_df['Entity'].apply(lambda entity: sum(entity_counts[entity.lower()]['sentiment_scores']) / entity_counts[entity.lower()]['count'])

    # Save the updated DataFrame to a CSV file
    entity_counts_df.to_csv('entity_counts.csv', index=False)

    # Calculate the confusion matrix
    cm = confusion_matrix(y_true, y_pred)

    # Calculate accuracy of the Sentiment score against the ratings
    accuracy = accuracy_score(y_true, y_pred)
    accuracy = f"{accuracy * 100:.2f}%"

    try:
        tp = cm[1, 1]
        tn = cm[0, 0]
        fp = cm[0, 1]
        fn = cm[1, 0]
    except:
        print("Error calculating Confusion Matrix. Probably too little input.")

    try:
        average_sentiment_percentage = (sum(avg_entity_sentiment_list) / len(avg_entity_sentiment_list) + 1) * 50 
    except:
        print("Error calculating average sentiment. Probably too little input.")
    neutral = len(df)-(tp + tn + fp + fn) 
    try:
        print(f"Overall Average Sentiment by Google NLP: {average_sentiment_percentage:.2f}%")
        print(f"Accuracy: {accuracy}")
        print(f"Neutral: {neutral}")
        print(f"True Positives (TP): {tp}")
        print(f"True Negatives (TN): {tn}")
        print(f"False Positives (FP): {fp}")
        print(f"False Negatives (FN): {fn}")

    except:
        print("Error calculating Confusion Matrix. Probably too little input.")

    def send_hotel_review_report(hotel_name, avg_sentiment, top_entities, bottom_entities):
        # Generate the hotel review summary report
        report_template = f"Generate a comprehensive hotel review report to assist potential guests in making informed decisions with the following information and format:\n"
        report_template += f"**Information**\n"
        report_template += f"- Hotel Name: {hotel_name}\n"
        report_template += f"- Average Sentiment: {avg_sentiment:.2f}%\n\n"

        report_template += "**Top 10 Positive Entities**\n"
        for index, row in top_entities.iterrows():
            entity = row['Entity']
            sentiment = row['Avg Sentiment']
            report_template += f"{entity}: {sentiment:.2f}\n"

        report_template += "\n**Bottom 10 Negative Entities**\n"
        for index, row in bottom_entities.iterrows():
            entity = row['Entity']
            sentiment = row['Avg Sentiment']
            report_template += f"{entity}: {sentiment:.2f}\n"

        report_template += "\nFormat:\n"
        report_template += "\nSummary: [Provide a detailed summary of the hotel's overall sentiment and customer feedback]\n"
        report_template += "Recommendations for People Who Wish to Book: [Offer detailed recommendations based on the sentiment and entity analysis]\n"
        report_template += "Additional Notes: [Include any additional observations or comments]\n"

        # Send the report template to ChatGPT for generating the report
        response = chatgpt.chat_with_gpt(report_template)
    
        response_df = pd.DataFrame({
        'OpenAI Response': [response],
        'Accuracy': [accuracy]
        })
        
        return response_df

    avg_sentiment = average_sentiment_percentage

    # Sort the entities based on a weighted score (sentiment * count)
    entity_counts_df['Weighted Score'] = entity_counts_df['Count'] * entity_counts_df['Avg Sentiment']

    # Sort entities by the weighted score in descending order to get the top entities
    top_entities = entity_counts_df.sort_values(by='Weighted Score', ascending=False).head(10)

    # Sort entities by the weighted score in ascending order to get the bottom entities
    bottom_entities = entity_counts_df.sort_values(by='Weighted Score', ascending=True).head(10)

    response_df=send_hotel_review_report(hotel_name, avg_sentiment, top_entities, bottom_entities)
    return response_df


if __name__ == "__main__":
    hotel_name = "Aloft Singapore Novena"
    response_df=analyze_hotel_reviews(hotel_name)
    print(response_df.iloc[0,0])