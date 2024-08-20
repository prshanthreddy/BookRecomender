from flask import Flask, render_template, request, flash, redirect, url_for
import pickle
import numpy as np

# Load the required data
popular_df = pickle.load(open('popular.pkl', 'rb'))
pt = pickle.load(open('pt.pkl', 'rb'))
books = pickle.load(open('books.pkl', 'rb'))
similarity_scores = pickle.load(open('similarity_scores.pkl', 'rb'))


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html',
                           book_name=list(popular_df['Book-Title'].values),
                           author=list(popular_df['Book-Author'].values),
                           image=list(popular_df['Image-URL-M'].values),
                           votes=list(popular_df['num_ratings'].values),
                           rating=list(popular_df['avg_rating'].values)
                           )

@app.route('/recommend')
def recommend_ui():
    return render_template('recommend.html')

@app.route('/recommend_books', methods=['POST'])
def recommend():
    user_input = request.form.get('user_input')

    try:
        # Check if the user input is valid
        if user_input not in pt.index:
            flash(f"No recommendations found for '{user_input}'. Please try another book.", 'danger')
            return redirect(url_for('recommend_ui'))
        index = np.where(pt.index == user_input)[0][0]
        similar_items = sorted(list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True)[1:5]

        data = []
        for i in similar_items:
            item = []
            temp_df = books[books['Book-Title'] == pt.index[i[0]]]
            popular_df1 = popular_df[popular_df['Book-Title'] == pt.index[i[0]]]
            item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values))
            item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))
            item.extend(list(temp_df.drop_duplicates('Book-Title')['Image-URL-L'].values))
            item.extend(list(popular_df1.drop_duplicates('Book-Title')['num_ratings'].values))
            item.extend(list(popular_df1.drop_duplicates('Book-Title')['avg_rating'].values.round(2)))

            data.append(item)

        return render_template('recommend.html', data=data)

    except IndexError:
        flash("An error occurred while finding recommendations. Please try again.", 'danger')
        return redirect(url_for('recommend_ui'))

    except Exception as e:
        flash(f"An unexpected error occurred: {str(e)}", 'danger')
        return redirect(url_for('recommend_ui'))

if __name__ == '__main__':
    app.run(debug=True)
