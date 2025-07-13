import pandas as pd
import pickle

# Load CSVs
ratings = pd.read_csv("ratings.csv")
books = pd.read_csv("books.csv", low_memory=False)

# Merge on ISBN to get Book-Title with Book-Rating
merged = ratings.merge(books, on='ISBN')

# Now group by Book-Title
rating_stats = merged.groupby('Book-Title').agg({'Book-Rating': ['count', 'mean']}).reset_index()
rating_stats.columns = ['Book-Title', 'num_ratings', 'avg_rating']

# Filter popular books
popular_df = rating_stats[rating_stats['num_ratings'] >= 50]

# Add metadata from books
popular_df = popular_df.merge(
    books[['Book-Title', 'Book-Author', 'Image-URL-M']],
    on='Book-Title',
    how='left'
).drop_duplicates('Book-Title')

# Save it
with open("popular.pkl", "wb") as f:
    pickle.dump(popular_df, f)

print("✅ popular.pkl built successfully.")
