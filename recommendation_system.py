# -*- coding: utf-8 -*-
"""recommendation-system.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1f8yO--PoUCrVd8KNd-1zhxZYOdJt3Nfj

# Proyek Machine Learning-Sistem Rekomendasi Film

## Latar Belakang
Pada era digital dimana arus informasi dan data bergerak dengan sangat cepat, pengguna internet kerap kali dihadapkan pada banuaknya pilihan konten dalam hal hiburan seperti film. Dengan banyaknya film yang tersedia, kerap kali pengguna merasa kesulitan dalam menentukan film yang cocok dengannya.

Pengalaman pengguna menjadi faktor yang sangat penting untuk menarik pelanggan agar mereka dapat menemukan informasi yang mereka inginkan dengan mudah. Ketika pengguna tidak menemukan informasi atau produk yang dimaksud, mereka akan beralih pada aplikasi lain atau bahkan menceritakan pengalaman buruk mereka kepada orang lain.

Melalui proyek ini, dikembangkan sistem rekomendasi film dengan pendekatan content based filtering yang melibatkan preferensi pengguna berdasarkan genre dan collaboratife filtering yang memanfaatkan data rating untuk memprediksi preferensi pengguna terhadap film lain.

## Problem statement
Berdasarkan latar belakang yang sudah disampaikan, terdapat beberapa rumusan masalah yang akan diselesaikan pada proyek ini:
1. Bagaimana cara membangun sistem rekomendasi dengan algoritma content-based filtering berdasarkan genre?
2. Bagaimana cara membangun sistem rekomendasi dengan algoritma collaborative filtering berdasarkan?
3. Bagaimana kinerja dari algoritma content-based filtering dan collaborative filtering yang dibuat?

## Goals
1. Mengetahui cara membangun sistem rekomendasi dengan algoritma content-based filtering berdasarkan genre.
2. Mengetahui cara membangun sistem rekomendasi dengan algoritma collaborative filtering berdasarkan aktivitas rating yang diberikan pengguna.
3. Mengetahui kinerja dari algoritma content-based filtering dan collaborative filtering yang dibuat

## Solution Statement
1. Membangun sistem rekomendasi dengan algoritma content-based filtering, dalam proyek ini akan memanfaatkan informasi fitur genre. Setiap film akan direpresentasikan dengan vektor fitur TF-IDF, dan rekomendasi diberikan berdasarkan kemiripan antara film yang dipilih menggunakan metrik mesamaan cosine similarity.
2. Membangun sistem rekomendasi dengan algoritma collaborative filtering menggunakan pendekatab berbasis model machine learning dengan memanfaatkan data rating pengguna terhadap film.
3. Melakukan pengujian menggunakan metrik Precision untuk menguji kinerja alogritma content-based filtering dan menggunakan metrik Root Mean Square Error (RMSE) pada collaborative filtering.

# Import Library yang Digunakan
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import tensorflow as tf

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics.pairwise import linear_kernel

from tensorflow import keras
from tensorflow.keras import layers

"""# Load kaggle api"""

# Upload kaggle.json
from google.colab import files
files.upload()

!mkdir -p ~/.kaggle
!mv kaggle.json ~/.kaggle/
!chmod 600 ~/.kaggle/kaggle.json

"""# Data Understanding

## Load Dataset
"""

!kaggle datasets download -d nicoletacilibiu/movies-and-ratings-for-recommendation-system -p /kaggle

!unzip /kaggle/movies-and-ratings-for-recommendation-system.zip -d /kaggle

# konversi data movies ke dalam dataframe
movies_df = pd.read_csv('/kaggle/movies.csv', on_bad_lines='skip')
movies_df.head()

"""insight :
- Setiap film dikategorikan ke dalam beberapa genre sekaligus.
"""

# konversi data ratings ke dalam dataframe
ratings_df = pd.read_csv('/kaggle/ratings.csv', on_bad_lines='skip')
ratings_df.head()

# cek jumlah data
print('Jumlah data movies: ',len(movies_df.movieId.unique()))
print('Jumlah data user: ',len(ratings_df.userId.unique()))

"""## Exploratory Data Analysis

### Deskripsi Variabel
"""

movies_df.info()

"""insight :
- terdapat 9742 baris data di dalam dataset
- data terdiri dari 3 kolom yaitu : movieId, title, dan genres.
- terdapat 1 data bertipe int64 yaitu kolom movieId, dan 2 kolom bertipe object yaitu kolom title dan genres
"""

ratings_df.info()

"""insight
Data Movies terdiri dari 100.836 baris data dan 4 kolom, yang merepresentasikan beberapa informasi mengenai rating film.
- userId : menyimpan data id unik pengguna.
- movieId : menyimpan data id unik film.
- rating : 	Nilai rating yang diberikan pengguna terhadap film (dalam skala 0.5 – 5.0).
- timestamp :Menyimpan waktu (dalam format UNIX timestamp) saat rating diberikan.
"""

movies_df.describe()

"""insight
- fitur movieId memiliki rentang antara 1-193609, ini menunjukkan bahwa id film tidak berurutan dan memiliki banyak celah di dalam penomoran id.
- Data memiliki nilai median= 7300 dan nilai mean= 42200 yang menandakan distribusi data movieId cenderong ke kanan(right-skewed)
"""

ratings_df.describe()

"""insight
- Nilai movieId memiliki sebaran yang sangat luas, dari 1 hingga 193.609, dengan rata-rata sekitar 19.435 dan standar deviasi yang besar. Hal ini menunjukkan bahwa penomoran ID film tidak berurutan secara padat.
- Data rating, memiliki nilai dalam rentang 0.5 hingga 5, dengan rata-rata 3.5 dan distribusi yang hampir simetris.

### Missing Value, Outlier, Data Duplikat

#### Missing Value
"""

missing_values_movie = movies_df.isnull().sum()
print('jumlah missing value pada data movie: ', missing_values_movie)

missing_values_rating = ratings_df.isnull().sum()
print('jumlah missing value pada data rating: ', missing_values_rating)

"""insight :
- tidak ditemukan missing value di dalam data

#### Memeriksa Outlier

melakukan visualisasi data ratings dengan boxplot
"""

cols = ['userId', 'movieId', 'rating']

# Set gaya visual
sns.set(style="whitegrid")

# Buat subplot 1 baris 3 kolom
fig, axes = plt.subplots(1, 3, figsize=(18, 6))

# Loop setiap kolom dan buat boxplot-nya
for i, col in enumerate(cols):
    sns.boxplot(y=ratings_df[col], ax=axes[i], color='skyblue')
    axes[i].set_title(f'Distribusi {col}', fontsize=12)
    axes[i].set_ylabel(col)

# Atur layout agar tidak saling tumpang tindih
plt.tight_layout()
plt.show()

"""melakukan visualisasi data ratings dengan histogram"""

sns.set(style="whitegrid")

# Buat subplot 1 baris 3 kolom
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

# Loop setiap kolom dan buat histogram-nya
for i, col in enumerate(cols):
    sns.histplot(data=ratings_df, x=col, bins=30, kde=True, ax=axes[i], color='skyblue')
    axes[i].set_title(f'Distribusi {col}', fontsize=12)
    axes[i].set_xlabel(col)
    axes[i].set_ylabel('Frekuensi')

# Tata letak agar rapi
plt.tight_layout()
plt.show()

"""insight
- data movieId memiliki persebaran yang tidak merata dan sangat right-skewed, namun tidak dapat dikatakan bahwa data tersebut memiliki outlier

### Memeriksa data duplikat
"""

# jumlah data duplikat pada data movie
jumlah_duplikat_movie = movies_df.duplicated().sum()
print('Jumlah data duplikat pada data movie: ', jumlah_duplikat_movie)

# jumlah data duplikat pada data rating
jumlah_duplikat_rating = ratings_df.duplicated().sum()
print('Jumlah data duplikat pada data rating', jumlah_duplikat_rating)

"""memeriksa keunikan data"""

# Jumlah data unik di kolom title
unique_titles = movies_df['title'].nunique()
print('Jumlah judul unik:', unique_titles)

# Jumlah data unik di kolom movieId
unique_movieIds = movies_df['movieId'].nunique()
print('Jumlah movieId unik:', unique_movieIds)

"""melihat letak data duplikat"""

duplicates = movies_df.groupby('title')['movieId'].nunique()
duplicates = duplicates[duplicates > 1]
print(duplicates)

"""insight :
- ditemukan data duplikat dimana sebuah judul film memiliki id yang berbeda

## Univariate Analysis
"""

movies_df

"""### Analisis Persebaran Genre Film"""

# cek daftar genre
all_genres = movies_df['genres'].str.split('|').explode()

unique_genres = all_genres.unique()
print('Jumlah genre unik:', len(unique_genres))
print('Daftar genre unik:')
for genre in unique_genres:
    print('-', genre)

"""menampilkan jumlah judul berdasarkan genre"""

# Visualisasi jumlah genre
genre_counts = all_genres.value_counts()

# Tampilkan  genre terbanyak
print("Genre terbanyak:\n")
print(genre_counts)
# Visualisasi dengan barplot
plt.figure(figsize=(12, 6))
sns.barplot(x=genre_counts.values, y=genre_counts.index, palette='viridis')

plt.title('Genre dalam Dataset')
plt.xlabel('Jumlah Film')
plt.ylabel('Genre')
plt.tight_layout()
plt.show()

"""insight :
- terdapat 20 genre unik di dalam dataset.
- Drama adalah genre yang paling banyak muncul, diikuti oleh Comedy dan Thriller.
- Genre seperti Film-Noir dan Western tergolong langka.
- Terdapat 34 film tanpa genre yang tercantum, sehingga perlu dilakukan penghapusan karena model content based filtering yang akan dibangun berdasarkan genre.

### Analisis Persebaran Ratings Rating yang Diberikan Pengguna
"""

# visualisasi persebaran ratings
sns.set(style="whitegrid")

# Ukuran figure
plt.figure(figsize=(8, 5))

# Plot distribusi rating
sns.countplot(x='rating', data=ratings_df, palette='viridis')

# Tambahkan judul dan label
plt.title('Distribusi Rating Film')
plt.xlabel('Rating')
plt.ylabel('Jumlah')
plt.xticks(rotation=45)  # Rotasi label jika perlu

# Tampilkan plot
plt.tight_layout()
plt.show()

"""insight :
- Mayoritas pengguna cenderung memberikan rating moderat (antara 3.0 hingga 4.0), dengan 4.0 sebagai rating terbanyak.
- Rating sempurna (5.0) cukup sering diberikan pengguna jika dibandingkan dengan rating-rating rendah.

### Analisis Film yang Mendapatkan Rating Terbanyak
"""

# Hitung jumlah rating per film
rating_counts = ratings_df.groupby('movieId').size().reset_index(name='rating_count')

# Gabungkan dengan movies_df agar dapat judul film
movie_rating_counts = rating_counts.merge(movies_df[['movieId', 'title']], on='movieId')

# Urutkan berdasarkan rating_count terbesar dan ambil 20 teratas
top20_most_rated = movie_rating_counts.sort_values(by='rating_count', ascending=False).head(20)

print(top20_most_rated[['title', 'rating_count']])

# Visualisasi dengan bar chart
plt.figure(figsize=(14,8))
plt.barh(top20_most_rated['title'][::-1], top20_most_rated['rating_count'][::-1], color='skyblue')
plt.xlabel('Jumlah Rating')
plt.title('20 Film dengan Jumlah Rating Terbanyak')
plt.grid(axis='x', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()

"""insight :
- sebagian besar film yang mendapatkan rating terbanyak dirilis pada tahun 1990-an.
"""

print('Jumlah userId unik: ', len(ratings_df.userId.unique()))
print('Jumlah movieId unik yang tersedia: ', len(movies_df.movieId.unique()))
print('Jumlah movieId unik yang dirating: ', len(ratings_df.movieId.unique()))
print('Jumlah data ratings: ', len(ratings_df))

"""# Data Preparation

## Data movie

Hapus baris yang kolom 'genres' berisi '(no genres listed)'
"""

# Hapus baris yang kolom 'genres' berisi '(no genres listed)'
fix_movie = movies_df[movies_df['genres'] != '(no genres listed)'].copy()

# Cek hasil
print(f"Sebelum: {len(movies_df)} baris")
print(f"Setelah: {len(fix_movie)} baris")

"""menghapus judul film yang duplikat"""

fix_movie = fix_movie.drop_duplicates(subset='title', keep='first')
duplicates = fix_movie.groupby('title')['movieId'].nunique()
duplicates = duplicates[duplicates > 1]
print(duplicates)

"""menggabungkan data movies dan ratings untuk mendapatkan informasi mengenai film dan ratings"""

merged_df = pd.merge(
    ratings_df,
    movies_df,
    on='movieId',
    how='left'
    )
merged_df.head()

"""## Data Preparation untuk algoritma Content-based Filtering"""

# mengonversi setiap data series 'movieId' menjadi bentuk list
moviesId = fix_movie['movieId'].tolist()

# mengonversi data 'title' menjadi bentuk list
title = fix_movie['title'].tolist()

# mengonversi data 'genres' menjadi bentuk list
genres = fix_movie['genres'].tolist()

print(len(moviesId))
print(len(title))
print(len(genres))

# Membuat dictionary untuk data ‘moviesId’, ‘title’, dan ‘genres’
movies_new = pd.DataFrame({
    'moviesId': moviesId,
    'title': title,
    'genres': genres
})
movies_new

"""insight
- membuat dictionary untuk menentukan pasangan key-value pada data movies_id, title, dan genres
"""

# membuat salinan dari data movies
data_movies = movies_new

"""### TF_IDF Vectorizer"""

# Inisialisasi TfidfVectorizer
tfidf = TfidfVectorizer(stop_words='english')

tfidf_matrix = tfidf.fit_transform(data_movies['genres'])

tfidf.get_feature_names_out()

"""insight
- Mengubah teks genre menjadi vektor numerik untuk mengubah setiap kumpulan genre (contohnya "Action|Adventure|Fantasy") menjadi vektor berdasarkan bobot TF-IDF (Term Frequency-Inverse Document Frequency).
"""

tfidf_matrix.shape

"""Konversi Sparse Matrix ke Dense Matrix"""

tfidf_matrix.todense()

"""insight
- Mengubah matrix TF-IDF dari format sparse menjadi format dense agar dapat diproses atau ditampilkan secara lengkap.








"""

pd.DataFrame(
    tfidf_matrix.todense(),
    columns=tfidf.get_feature_names_out(),
    index=data_movies['title']
).sample(21, axis=1).sample(10, axis=0)

"""## Data preparation untuk Collaborative Filtering

copy data ratings ke dalam dataframe baru
"""

ratings_new = ratings_df.drop(columns=['timestamp'])
ratings_new.head()

"""insight
- menghapus kolom timestamp karena tidak relevan untuk membangun sistem rekomendasi

Data Encoding dilakukan untuk mengubah nilai asli dari userId dan movieId menjadi bentuk numerik yang terurut (dari 0
hingga N-1), agar dapat digunakan sebagai input dalam model machine learning seperti embedding layer pada collaborative
filtering.
"""

# Encoding data userId
userIds = ratings_new['userId'].unique().tolist()
print('list userIds:', userIds)

user_to_user_encoded = {x: i for i, x in enumerate(userIds)}
print('encoded userIds : ', user_to_user_encoded)

user_encoded_to_user = {i: x for i, x in enumerate(userIds)}
print('encoded angka ke userIds: ', user_encoded_to_user)

# encoding data movie
movieIds = ratings_new['movieId'].unique().tolist()
print('list movieIds:', movieIds)

movie_to_movie_encoded = {x: i for i, x in enumerate(movieIds)}
print('encoded movieID : ', movie_to_movie_encoded)

movie_encoded_to_movie = {i: x for i, x in enumerate(movieIds)}
print('encoded angka ke movieID: ', movie_encoded_to_movie)

# menentukan jumlah user di dalam data ratings
num_users = len(userIds)
print('jumlah user:', num_users)

# menentukan jumlah film di dalam data ratings
num_movies = len(movieIds)
print('jumlah movie:', num_movies)

ratings_df['rating'] = ratings_df['rating'].values.astype(np.float32)

# Nilai minimum rating
min_rating = min(ratings_new['rating'])
max_rating = max(ratings_new['rating'])

print('Number of User: {}, Number of Movie: {}, Min Rating: {}, Max Rating: {}'.format(
    num_users, num_movies, min_rating, max_rating
))

"""alasan
- Kode ini berfungsi untuk menghitung jumlah user dan film unik serta menentukan rentang nilai rating, yang penting untuk mengatur ukuran embedding layer dan memastikan data rating memiliki tipe yang konsisten agar model rekomendasi dapat dilatih dengan benar. Informasi ini juga membantu dalam preprocessing seperti normalisasi agar model lebih stabil saat training.
"""

# mengacak kolom ratings
ratings_new = ratings_new.sample(frac=1, random_state=42)
ratings_new

"""alasan
- pengacakan data dilakukan agar model tidak memelajari data secara berurutan agar dapat memelajari data baru lebih baik
"""

# Mapping userID ke dataframe user
ratings_new['user'] = ratings_new['userId'].map(user_to_user_encoded)

# Mapping movieId ke dataframe movie
ratings_new['movie'] = ratings_new['movieId'].map(movie_to_movie_encoded)

X = ratings_new[['user', 'movie']]
y = ratings_new['rating'].apply(lambda x: (x - min_rating) / (max_rating - min_rating)).values

train_indices = int(0.8 * ratings_new.shape[0])
X_train, X_val, y_train, y_val = (
    X[:train_indices],
    X[train_indices:],
    y[:train_indices],
    y[train_indices:]
)

print(X, y)

"""insight
- mendefinisikan kolom fitur dan terget
- melakukan spliting data dengan perbandingan 80 : 20. 80 digunakan untuk melakukan training model, dan 20 untuk evaluasi model.

# Model Deployment

## Model Content Based Filtering

### Cek Cosine Similarity
"""

# menggunakan subset 1000 film pertama untuk menghemat ram
cosine_sim = cosine_similarity(tfidf_matrix)
cosine_sim.shape

"""insight

- Menghitung similarity antar film berdasarkan fitur TF-IDF dari deskripsi atau metadata film.

- Mengurangi penggunaan memori dan mempercepat perhitungan dengan membatasi data hanya pada 1000 film pertama, karena menghitung similarity untuk seluruh dataset bisa sangat berat dan lambat jika dataset besar.
"""

cosine_sim_df = pd.DataFrame(
    cosine_sim,
    index=data_movies['title'],
    columns=data_movies['title']
)

print('Shape:', cosine_sim_df.shape)

cosine_sim_df.sample(5, axis=1).sample(10, axis=0)

# Fungsi rekomendasi film berdasarkan cosine similarity
def movie_recommendations(title, similarity_data=cosine_sim_df, items=data_movies[['title', 'genres']], k=5):
    index = similarity_data.loc[:, title].to_numpy().argpartition(range(-1, -k, -1))
    closest = similarity_data.columns[index[-1:-(k+2):-1]]
    closest = closest.drop(title, errors='ignore')
    return pd.DataFrame(closest).merge(items).head(k)

"""membangun fungsi untuk melakukan rekomendasi content based filtering"""

data_movies[data_movies.title.eq('Jumanji (1995)')]

movie_recommendations('Jumanji (1995)')

"""mencoba melihat rekomendasi berdasarkan film 'Jumanji (1995)'

## Model Collaborative Filtering
"""

class RecommenderNet(tf.keras.Model):

    # Inisialisasi fungsi
    def __init__(self, num_users, num_movies, embedding_size, **kwargs):
        super(RecommenderNet, self).__init__(**kwargs)
        self.num_users = num_users
        self.num_movies = num_movies
        self.embedding_size = embedding_size

        # Embedding untuk pengguna
        self.user_embedding = layers.Embedding(
            input_dim=num_users,
            output_dim=embedding_size,
            embeddings_initializer='he_normal',
            embeddings_regularizer=keras.regularizers.l2(1e-6)
        )
        self.user_bias = layers.Embedding(num_users, 1)

        # Embedding untuk film
        self.movie_embedding = layers.Embedding(
            input_dim=num_movies,
            output_dim=embedding_size,
            embeddings_initializer='he_normal',
            embeddings_regularizer=keras.regularizers.l2(1e-6)
        )
        self.movie_bias = layers.Embedding(num_movies, 1)

    def call(self, inputs):
        user_vector = self.user_embedding(inputs[:, 0])
        user_bias = self.user_bias(inputs[:, 0])
        movie_vector = self.movie_embedding(inputs[:, 1])
        movie_bias = self.movie_bias(inputs[:, 1])

        dot_user_movie = tf.tensordot(user_vector, movie_vector, 2)

        x = dot_user_movie + user_bias + movie_bias

        return tf.nn.sigmoid(x)

"""membangun model collaborative filtering dan mengcompile model"""

model = RecommenderNet(num_users, num_movies, embedding_size=50)

model.compile(
    loss=tf.keras.losses.BinaryCrossentropy(),
    optimizer=keras.optimizers.Adam(learning_rate=0.001),
    metrics=[tf.keras.metrics.RootMeanSquaredError()]
)

history = model.fit(
    x=X_train,
    y=y_train,
    batch_size=8,
    epochs=60,
    validation_data=(X_val, y_val)
)

"""melatih model"""

plt.plot(history.history['root_mean_squared_error'])
plt.plot(history.history['val_root_mean_squared_error'])
plt.title('model_metrics')
plt.ylabel('root_mean_squared_error')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()

"""visualisasi grafik root mean square error"""

# Mengambil satu userId secara acak dari merged_df
user_id = merged_df['userId'].sample(1).iloc[0]

# Ambil semua movie yang sudah dirating oleh user ini
movies_watched_by_user = merged_df[merged_df.userId == user_id]

# Ambil semua movie yang belum ditonton oleh user ini
movies_not_watched = merged_df[~merged_df['movieId'].isin(movies_watched_by_user['movieId'].values)][['movieId']].drop_duplicates()

# Filter movieId yang ada di kamus encoding
movies_not_watched = movies_not_watched[movies_not_watched['movieId'].isin(movie_to_movie_encoded.keys())]

# Encoding movieId
movies_not_watched_encoded = [[movie_to_movie_encoded[x]] for x in movies_not_watched['movieId'].values]

# Encoding userId
user_encoded = user_to_user_encoded.get(user_id)

# Membuat array pasangan user dan semua film yang belum ditonton
user_movie_array = np.hstack((
    np.array([[user_encoded]] * len(movies_not_watched_encoded)),
    np.array(movies_not_watched_encoded)
))

# Prediksi rating
ratings = model.predict(user_movie_array).flatten()

# Ambil indeks top-10 prediksi tertinggi
top_indices = ratings.argsort()[-10:][::-1]

# Ambil movieId dari encoded
recommended_movie_ids = [
    movie_encoded_to_movie[i[0]] for i in np.array(movies_not_watched_encoded)[top_indices]
]

# Ambil judul dan genre film dari movieId rekomendasi
recommended_movies = merged_df[merged_df['movieId'].isin(recommended_movie_ids)][['movieId', 'title', 'genres']].drop_duplicates()
print(recommended_movies)

"""mencoba melihat rekomendasi berdasarkan film

# Evauation

## Model Content Based Filtering

** Precision**
**Precision** adalah matriks evaluasi kinerja model sistem rekomendasi yang mengukur seberapa banyak rekomendasi yang diberikan oleh sistem benar-benar relevan atau sesuai dengan preferensi pengguna. Secara matematis :

$$
\text{Precision} = \frac{\text{Jumlah item relevan yang direkomendasikan}}{\text{Jumlah total item yang direkomendasikan}}
$$

#### Alasan Memilih Precision sebagai Metrik Evaluasi

1. Fokus pada kualitas rekomendasi yang diberikan

   Precision menilai seberapa tepat rekomendasi yang muncul. Dalam konteks content-based filtering, rekomendasi yang akurat sangat penting agar pengguna merasa puas dan sistem dianggap bermanfaat.

2. Mudah dipahami dan diinterpretasikan

   Precision memberikan gambaran langsung berapa banyak rekomendasi yang benar-benar relevan dibanding total rekomendasi yang diberikan. Nilai precision yang tinggi menunjukkan kualitas rekomendasi yang baik.

3. Relevan untuk kasus rekomendasi dengan daftar terbatas

   Dalam banyak kasus, sistem rekomendasi hanya menampilkan sejumlah kecil item (misal top 5 atau top 10). Precision cocok digunakan untuk menilai performa dalam skala kecil tersebut.

4. Tidak bergantung pada total jumlah item relevan di database

   Berbeda dengan recall yang membutuhkan data lengkap tentang semua item relevan, precision hanya fokus pada hasil rekomendasi yang muncul. Ini memudahkan evaluasi terutama ketika data lengkap sulit diketahui.

#### Kesimpulan

Precision adalah metrik yang tepat digunakan untuk mengevaluasi sistem rekomendasi content-based filtering karena memberikan informasi jelas tentang proporsi rekomendasi yang benar-benar relevan bagi pengguna. Dengan memaksimalkan precision, kita dapat meningkatkan kepuasan pengguna terhadap rekomendasi yang diberikan.

---
"""

target_genres = set(['Adventure', 'Children', 'Fantasy']) # target genre ganti berdasarkan genre film yang dicari

# mengambil rekomendasi
recommendations = movie_recommendations('Jumanji (1995)')

# Fungsi cek relevansi
def is_relevant(genre_str, target_genres):
    genres = set(genre_str.split('|'))
    return target_genres.issubset(genres)

# menghitung precision
total_recs = len(recommendations)
relevant_recs = recommendations['genres'].apply(lambda x: is_relevant(x, target_genres)).sum()

precision = relevant_recs / total_recs if total_recs > 0 else 0

print(f"Precision: {precision:.2f}")

"""insight :
- sistem rekomendasi dengan Content-based filtering mencapai metric evaluasi precision sebesar 100%  
- nilai precision yang mencapai 100% menunjukkan bahwa algoitma yang dibangun berhasil merekomendasikan film berdasarkan genre dangan sangat akurat.

## Model Collaborative Filtering

**Root Mean Squared Error (RMSE)** dipilih sebagai metrik evaluasi untukmodel collaborative filtering ini. RMSE memberikan gambaran seberapa besar rata-rata kesalahan prediksi model dibandingkan rating asli dari pengguna, dengan satuan yang sama seperti rating.

Rumus RMSE:

$$
\text{RMSE} = \sqrt{\frac{1}{N} \sum_{i=1}^N (y_i - \hat{y}_i)^2}
$$

di mana:

- $y_i$ adalah rating asli,
- $\hat{y}_i$ adalah rating prediksi,
- $N$ adalah jumlah data.
"""

plt.plot(history.history['root_mean_squared_error'])
plt.plot(history.history['val_root_mean_squared_error'])
plt.title('model_metrics')
plt.ylabel('root_mean_squared_error')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()

final_rmse_train = history.history['root_mean_squared_error'][-1]
final_rmse_val = history.history['val_root_mean_squared_error'][-1]

print(f"Final RMSE (Train): {final_rmse_train:.4f}")
print(f"Final RMSE (Validation): {final_rmse_val:.4f}")

"""Insight
- Nilai Final RMSE (Train) sebesar 0.1766 menunjukkan bahwa model mampu memprediksi rating film dengan kesalahan rata-rata sekitar 0.18 poin pada data pelatihan. Ini menandakan model sudah belajar dengan baik dari data training.

- Nilai Final RMSE (Validation) sebesar 0.2031 menunjukkan performa model pada data yang belum pernah dilihat selama pelatihan. Nilai ini hanya sedikit lebih tinggi dibandingkan RMSE training, yang berarti model mampu melakukan generalisasi dengan baik dan tidak mengalami overfitting yang signifikan.

- Secara keseluruhan, nilai RMSE di bawah 0.3 pada skala rating 1–5 menunjukkan model memberikan prediksi yang cukup akurat dan dapat diandalkan untuk merekomendasikan film sesuai preferensi pengguna.
"""

!pip freeze > requirements.txt