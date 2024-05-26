from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
import pickle
import pandas as pd
import numpy as np
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import firebase_admin
from firebase_admin import credentials, auth
import json

pt = pickle.load(open('pt.pkl', 'rb'))
popular_df = pickle.load(open('popular.pkl', 'rb'))
books = pickle.load(open('books.pkl', 'rb'))
similarity_scores = pickle.load(open('similarity_scores.pkl', 'rb'))
ratings_csv = 'Ratings.csv'

app = Flask(__name__, template_folder='templates')


@app.route('/')
def index():
    return render_template('index.html',
                           book_name=popular_df['Book-Title'].to_list(),
                           author=popular_df['Book-Author'].to_list(),
                           image=popular_df['Image-URL-M'].to_list(),
                           votes=popular_df['num_ratings'].to_list(),
                           rating=popular_df['avg_rating'].to_list()
                           )


@app.route('/recommend')
def recommend_ui():
    return render_template('recommend.html')


@app.route('/recommend_books', methods=['post'])
def recommend():
    user_input = request.form.get('user_input')
    index = np.where(pt.index == user_input)[0][0]
    similar_items = sorted(list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True)[1:9]

    data = []
    for i in similar_items:
        item = []
        temp_df = books[books['Book-Title'] == pt.index[i[0]]]
        item.extend(temp_df.drop_duplicates('Book-Title')['Book-Title'].to_list())
        item.extend(temp_df.drop_duplicates('Book-Title')['Book-Author'].to_list())
        item.extend(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].to_list())

        data.append(item)

    print(data)

    return render_template('recommend.html', data=data)


@app.route('/rate_book/<book_id>', methods=['POST'])
def rate(book_id):
    data = request.get_json()
    if 'rating' not in data:
        return jsonify({"error": "No rating provided"}), 400

    try:
        rating = int(data['rating'])
    except ValueError:
        return jsonify({"error": "Rating must be an integer"}), 400

    user_id = 276724 # TODO: get authenticated user id

    old_rating = get_rating(user_id, book_id)
    if old_rating is not None:
        if old_rating == rating:
            return jsonify({"error": "This book has alreay been rated"}), 400
        else:
            update_rating(user_id, book_id, rating)
            return jsonify({"message": "Rating updated successfully", "User-ID": user_id, "ISBN": book_id, "New-Book-Rating": rating}), 200

    save_rating(user_id, book_id, rating)
    return jsonify({"message": "Rating saved successfully", "User-ID": user_id, "ISBN": book_id, "Book-Rating": rating}), 201


def save_rating(user_id, book_id, rating):
    new_rating = pd.DataFrame({'User-ID': [user_id], 'ISBN': [book_id], 'Book-Rating': [rating]})
    new_rating.to_csv(ratings_csv, mode='a', header=False, index=False)
    

def update_rating(user_id, book_id, rating):
    df = pd.read_csv(ratings_csv)
    df.loc[(df['User-ID'] == user_id) & (df['ISBN'] == book_id), 'Book-Rating'] = rating
    df.to_csv(ratings_csv, index=False)


def get_rating(user_id, book_id):
    try:
        df = pd.read_csv(ratings_csv)
        existing_rating = df.loc[(df['User-ID'] == user_id) & (df['ISBN'] == book_id), 'Book-Rating'].iloc[0]
        return existing_rating
    except FileNotFoundError:
        return None
    except IndexError:
        return None


if __name__ == '__main__':
    app.run(debug=True)
