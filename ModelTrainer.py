import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report


youtube_urls = [
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "https://www.youtube.com/channel/UC-9-kyTW8ZkZNDHQJ6FgpwQ",
    "https://www.youtube.com/playlist?list=PL9tY0BWXOZFuSUzvEty6LRiEBGpLq1KAv",
    "https://www.youtube.com/shorts/a1b2c3d4e5f6",
    "https://www.youtube.com/live/abc123xyz",
    "https://music.youtube.com/watch?v=3tmd-ClpJxA",
    "https://gaming.youtube.com/channel/UCEz-WQj3Dh7s2xZfG5Sjtuw",
    "https://studio.youtube.com/channel/UCxyz-12345678-abcdefgh",
    "https://www.youtube.com/feed/subscriptions",
    "https://www.youtube.com/user/YouTube"
]


# Load the dataset
def read_csv(file_path) -> pd.DataFrame:
    """Reads a CSV file into a data structure that can be written to a new CSV file."""
    data = pd.read_csv(file_path)
    print(data.head())
    
    return data


# Preprocess the data set
def preprocess_data(data: pd.DataFrame) -> pd.DataFrame:
    """Preprocesses the data set"""
    # Remove any missing values
    data = data.dropna()

    # Remove any duplicates
    data = data.drop_duplicates()

    # Change the name of the 'type' column to 'label'
    data = data.rename(columns={'type': 'label'})

    # Convert values in the 'type' column to 1s and 0s where a 1 is any value that is not 'benign'
    data['label'] = data['label'].apply(lambda x: 1 if x != 'benign' else 0)

    # if the 'url' column contains 'youtube', set the 'label' column to 1
    data['label'] = data.apply(lambda x: 1 if x['url'].__contains__('youtube') else x['label'], axis=1)

    # Append 10 new rows to the data set using the YouTube URLs. The 'type' column should be set to 1 for all new rows.
    youtube_data = pd.DataFrame(youtube_urls, columns=['url'])
    youtube_data['label'] = 1
    data = pd.concat([data, youtube_data])

    print(data.tail())

    return data

# Extract features
def extract_features(url: str) -> list:
    """Extracts features from the data set"""
    features = []
    features.append(len(url))  # Length of URL
    features.append(url.count('.'))  # Number of dots
    features.append(int('http' in url or 'https' in url))  # Presence of http or https
    features.append(int('www' in url))  # Presence of www
    features.append(int('@' in url))  # Presence of @
    features.append(int(url.endswith('.html') or url.endswith('.htm')))  # Ends with .html or .htm
    features.append(int('youtube' in url))  # Presence of 'youtube'

    return features

# Split the data set into training and testing data
def split_data(data: pd.DataFrame, labels: pd.DataFrame) -> list:
    """Splits the data set into training and testing data"""

    X_train, X_test, y_train, y_test = train_test_split(data, labels, test_size=0.2, random_state=42)

    return X_train, X_test, y_train, y_test

if __name__ == "__main__":
    file_path = "/Users/uwemwilson/Desktop/projects/dns-proxy-server/malicious_phish.csv"
    data = read_csv(file_path)
    preprocessed_data = preprocess_data(data)

    # Extract features from the URLs
    features = preprocessed_data['url'].apply(extract_features)
    features_df = pd.DataFrame(features.tolist(), columns=['length', 'dot_count', 'has_http', 'has_www', 'has_at', 'ends_with_html', 'contains_youtube'])
    
    # Split the data set into training and testing data
    split_data = split_data(features_df, preprocessed_data['label'])
    print(f'split_data: {split_data}')
    X_train, X_test, y_train, y_test = split_data
    
    model = RandomForestClassifier()
    model.fit(X_train, y_train)

    # Save the model
    joblib.dump(model, 'random_forest_model.pkl')


    y_pred = model.predict(X_test)
    print(f'Predictions: {y_pred}')
    print(f'Classification Report: {classification_report(y_test, y_pred)}')
    print(f'Accuracy: {accuracy_score(y_test, y_pred)}')
