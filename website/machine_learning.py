import pandas as pd
import ast
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.stem.porter import PorterStemmer
import json

df1 = pd.read_csv('./website/static/data/not-cleaned-anime.csv')

### Preprocessing ###
# removed genres with null list (20%)
df1 = df1[df1['genres'] != '[]']

# 'type' has 49 null, 'start_date' has 391 null, 'episodes' has 316 null, dropped
df1.dropna(subset=['type', 'source', 'start_date', 'episodes', 'synopsis', 'main_picture'], inplace=True)

null_score = df1['score'].isnull().sum()
print((null_score/len(df1))*100)

# 'score' has 5775 null, replaced with median
df1['score'].fillna(df1['score'].median(), inplace=True)

# Extract data from dd/mm/yyyy format (start year, season)
df1['start_date'] = pd.to_datetime(df1['start_date'])
df1['start_year'] = df1['start_date'].dt.year
df1['start_month'] = df1['start_date'].dt.month
season_mapping = {1: 'winter', 2: 'winter', 3: 'spring', 4: 'spring', 5: 'spring', 6: 'summer', 7: 'summer', 8: 'summer', 9: 'fall', 10: 'fall', 11: 'fall', 12: 'winter'}
df1['start_season'] = df1['start_month'].map(season_mapping)

# Removing '' in genres
def remove_quotation_marks(genres_list):
    return [word.strip("''\"") for word in genres_list]
df1['genres'] = df1['genres'].apply(ast.literal_eval)
df1['genres'] = df1['genres'].apply(remove_quotation_marks)

# Remove start_date since not in format for ml
df1.drop(columns=['start_date'], inplace=True)

### Done preprocessing ###

df1.to_csv('./website/static/data/cleaned-anime.csv', index=False)

### Vectorization ###
df = pd.read_csv('./website/static/data/cleaned-anime.csv').head(5000)
cv = CountVectorizer(max_features=7000, stop_words='english')
vectors = cv.fit_transform(df['synopsis']).toarray()
ps = PorterStemmer()

def stem(text):
    y=[]
    for i in text.split():
        y.append(ps.stem(i))
    return " ".join(y)

df['synopsis'] = df['synopsis'].apply(stem)
similarity = cosine_similarity(vectors)

def recommend(anime):
    anime_index = df[df['title'] == anime].index[0]
    distances = sorted(list(enumerate(similarity[anime_index])), reverse=True, key=lambda x:x[1])
    recommend_anime = []
    print(f'Selected Anime: {anime}')
    print('-------------------------------------------------')
    for i in distances[1:6]:
        recommend_anime.append(df.iloc[i[0]])
    for i in distances[1:20]:
        print(f"{df.iloc[i[0]]['title']}: {i[1]:.2f}")
    return recommend_anime
