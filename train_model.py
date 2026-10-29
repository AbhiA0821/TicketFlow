"""
TicketFlow - Model Training Script
Trains a Logistic Regression classifier with TF-IDF features
to categorize support tickets into Technical, Billing, Account, or Service.
"""

import os
import pickle
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report


def train_and_save_model():
    # Resolve paths relative to this script's directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    dataset_path = os.path.join(base_dir, "tickets_dataset.csv")
    model_path = os.path.join(base_dir, "model.pkl")
    vectorizer_path = os.path.join(base_dir, "tfidf_vectorizer.pkl")

    print("=" * 60)
    print("       TicketFlow: Support Ticket Classifier Training       ")
    print("=" * 60)

    # 1. Load dataset
    print(f"\n[1] Loading dataset from: {dataset_path}")
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"Dataset not found at: {dataset_path}")

    df = pd.read_csv(dataset_path)
    print(f"    Total records loaded: {len(df)}")
    print("    Class distribution:")
    for cat, count in df["category"].value_counts().items():
        print(f"      - {cat}: {count} tickets")

    # 2. Prepare features (X) and labels (y)
    X = df["complaint"]
    y = df["category"]

    # 3. Train-Test Split (80% Train, 20% Test, stratified)
    print("\n[2] Splitting dataset (80% train, 20% test)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"    Training samples: {len(X_train)}")
    print(f"    Testing samples:  {len(X_test)}")

    # 4. Feature Extraction using TF-IDF
    print("\n[3] Extracting features using TF-IDF Vectorizer...")
    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2),
        max_features=1000
    )
    X_train_tfidf = vectorizer.fit_transform(X_train)
    X_test_tfidf = vectorizer.transform(X_test)
    print(f"    TF-IDF Vocabulary size: {len(vectorizer.vocabulary_)} features")

    # 5. Train Logistic Regression Model
    print("\n[4] Training Logistic Regression model...")
    model = LogisticRegression(max_iter=1000, random_state=42)
    model.fit(X_train_tfidf, y_train)
    print("    Model training completed successfully.")

    # 6. Evaluate Model on Test Set
    print("\n[5] Evaluating model performance on test set:")
    y_pred = model.predict(X_test_tfidf)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"    Accuracy: {accuracy * 100:.2f}%\n")
    print("    Classification Report:")
    print(classification_report(y_test, y_pred))

    # 7. Save Model and Vectorizer to disk
    print("[6] Saving trained model and TF-IDF vectorizer...")
    with open(model_path, "wb") as f_model:
        pickle.dump(model, f_model)
    with open(vectorizer_path, "wb") as f_vec:
        pickle.dump(vectorizer, f_vec)

    print(f"    Saved model to:      {model_path}")
    print(f"    Saved vectorizer to: {vectorizer_path}")
    print("\n" + "=" * 60)
    print(" Training complete! You can now launch the app: streamlit run app.py")
    print("=" * 60)


if __name__ == "__main__":
    train_and_save_model()
