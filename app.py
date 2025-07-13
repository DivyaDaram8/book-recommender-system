from flask import Flask, render_template, request
import pickle
import numpy as np
import pandas as pd

# ---------- Load data safely ----------
try:
    popular_df = pickle.load(open("popular.pkl", "rb"))
    pt = pickle.load(open("pt.pkl", "rb"))
    books = pickle.load(open("books.pkl", "rb"))
    sim_scores = pickle.load(open("similarity_scores.pkl", "rb"))
except Exception as e:
    raise RuntimeError(f"Failed to load pickle files → {e}")

# ---------- Fix column names if needed ----------
# Print once to confirm what's in popular_df
print("Columns in popular_df:", popular_df.columns)

# If 'num_ratings' or 'avg_rating' are missing, rename manually if needed
expected_columns = ['Book-Title', 'Book-Author', 'Image-URL-M', 'num_ratings', 'avg_rating']
if not all(col in popular_df.columns for col in expected_columns):
    # Try to flatten or rename columns if aggregation caused multi-index
    if isinstance(popular_df.columns, pd.MultiIndex):
        popular_df.columns = ['Book-Title', 'num_ratings', 'avg_rating']
    if 'Book-Author' not in popular_df.columns:
        popular_df = popular_df.merge(books[['Book-Title', 'Book-Author', 'Image-URL-M']], on='Book-Title', how='left')
    print("Updated columns:", popular_df.columns)

# ---------- Flask setup ----------
app = Flask(__name__)


@app.route("/")
def home():
    try:
        return render_template(
            "home.html",
            book_name=popular_df["Book-Title"].tolist(),
            author=popular_df["Book-Author"].tolist(),
            image=popular_df["Image-URL-M"].tolist(),
            votes=popular_df["num_ratings"].tolist(),
            rating=popular_df["avg_rating"].tolist(),
        )
    except KeyError as e:
        return f"Missing column in popular_df → {e}", 500
    except Exception as e:
        return f"Unexpected error → {e}", 500


@app.route("/recommend")
def recommend_ui():
    return render_template("recommend.html", data=None)


@app.route("/recommend_books", methods=["POST"])
def recommend():
    user_input = request.form.get("user_input", "").strip()

    if user_input not in pt.index:
        return render_template(
            "recommend.html",
            data=[],
            error=f"'{user_input}' not found. Check spelling and try again.",
        )

    idx = np.where(pt.index == user_input)[0][0]
    similar = sorted(
        list(enumerate(sim_scores[idx])), key=lambda x: x[1], reverse=True
    )[1:5]

    data = []
    for i, _ in similar:
        temp = books[books["Book-Title"] == pt.index[i]].drop_duplicates("Book-Title")
        if not temp.empty:
            data.append([
                temp.iloc[0]["Book-Title"],
                temp.iloc[0]["Book-Author"],
                temp.iloc[0]["Image-URL-M"],
            ])
        else:
            data.append(["Not Found", "Unknown", ""])

    return render_template("recommend.html", data=data, error=None)


if __name__ == "__main__":
    app.run(debug=True)
