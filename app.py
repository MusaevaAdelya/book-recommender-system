from flask import Flask, render_template, request, jsonify
import pickle
import csv
import numpy as np

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
    similar_items = sorted(list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True)[1:5]

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
    
    if is_book_rated(276724, book_id):
        return jsonify({"error": "User has already rated this book"}), 400

    with open(ratings_csv, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([276724, book_id, rating])
    csvfile.close() 

    return jsonify({"message": "Rating saved successfully", "User-ID": 276724, "ISBN": book_id, "Book-Rating": rating}), 201

def is_book_rated(user_id, book_id):
    with open(ratings_csv, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if int(row['User-ID']) == user_id and row['ISBN'] == book_id:
                return True
    return False

if __name__ == '__main__':
    app.run(debug=True)
