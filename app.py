from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import os
import turicreate as tc
from flaskext.mysql import MySQL
import pandas
from math import*
import gc

app = Flask(__name__)
app.secret_key = os.urandom(24)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://ishanghanmode:Sameera$123@masterthesis.comthluimqpc.eu-central-1.rds.amazonaws.com/master_thesis'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Sameera$123@localhost/Master_Thesis'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'root' #ishanghanmode
app.config['MYSQL_DATABASE_PASSWORD'] = 'Sameera$123'
app.config['MYSQL_DATABASE_DB'] = 'Master_Thesis' #master_thesis
app.config['MYSQL_DATABASE_HOST'] = 'localhost' #masterthesis.comthluimqpc.eu-central-1.rds.amazonaws.com
mysql.init_app(app)
#conn = mysql.connect()


db = SQLAlchemy(app)

#DB model for collecting basic user information
class User_Demographics(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique = True)
    Unique_ID = db.Column(db.String(10), nullable=False, unique = True)
    Gender = db.Column(db.String(20), nullable=False)
    Age = db.Column(db.String(20), nullable=False)
    Movie_Consumption = db.Column(db.String(1000), nullable=False)
    Genre_Description = db.Column(db.String(1000), nullable=False)
    Genre_Description_Other = db.Column(db.String(1000))


#DB models for the movie_lens dataset.
class Movie_Lens_Ratings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    item_id = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.Integer, nullable=False)

class Movie_Lens_MovieData(db.Model):
    movieid = db.Column(db.Integer, primary_key=True, nullable=False)
    imdb_id = db.Column(db.String(20), nullable=False)
    movie_title = db.Column(db.String(500), nullable=False)
    movie_genre = db.Column(db.String(500), nullable=False)


#DB Models for Movie tweetings dataset information.
class MT_MovieData(db.Model): #imdbId	title	genre
    id = db.Column(db.Integer, primary_key=True)
    imdb_id = db.Column(db.String(30), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    genre = db.Column(db.String(200), nullable=False)

class ratings_final(db.Model):
    id = db.Column(db.Integer, primary_key=True) #user_id	imdbId	rating	title	genre	twitter_id	screen_name
    user_id = db.Column(db.Integer, nullable=False)
    imdb_id = db.Column(db.String(30), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    genre = db.Column(db.String(200), nullable=False)
    twitter_id = db.Column(db.Integer, nullable=False)
    screen_name = db.Column(db.String(200), nullable=False)

class MT_User_Details(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    twitter_id = db.Column(db.String(30), nullable=False)
    screen_name = db.Column(db.String(200), nullable=False)

#DB models for storing evaluation details.

#Novelty
class novelty_evaluation_lists(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    List_1_Movies = db.Column(db.String(500), nullable=False)
    List_2_Movies = db.Column(db.String(500), nullable=False)

class novelty_qa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    question_2 = db.Column(db.Integer, nullable=False)
    question_3 = db.Column(db.Integer, nullable=False)
    question_4 = db.Column(db.Integer, nullable=False)

#Diversity
class diversity_qa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    question_1 = db.Column(db.Integer, nullable=False)
    question_2 = db.Column(db.Integer, nullable=False)
    question_3 = db.Column(db.Integer, nullable=False)
    question_4 = db.Column(db.Integer, nullable=False)

#Precision_calculation

class precision_lists(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    List_1_Movies = db.Column(db.String(500), nullable=False)
    List_2_Movies = db.Column(db.String(500), nullable=False)

#User Satisfaction
class user_satisfaction_qa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    question_1 = db.Column(db.Integer, nullable=False)
    question_2 = db.Column(db.Integer, nullable=False)
    question_3 = db.Column(db.Integer, nullable=False)
    question_4 = db.Column(db.Integer, nullable=False)
    question_5 = db.Column(db.Integer, nullable=False)
    question_6 = db.Column(db.Integer, nullable=False)

#Other Details

class RS_Details(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    slider_value = db.Column(db.String(50), nullable=False)
    twitter_users_selected = db.Column(db.String(500), nullable=False)
    movies_first_panel = db.Column(db.String(500), nullable=False)
    R_List_1 = db.Column(db.String(500), nullable=False)
    R_List_2 = db.Column(db.String(500), nullable=False)


@app.route('/home')
def index():
    return render_template('home.html')

@app.route('/goodbye')
def goodbye():
    return render_template('goodbye.html')

@app.route('/demographics')
def demographics():
    return render_template('demographics.html')

@app.route('/initialseed', methods=['POST'])
def initialseed():

    Gender = request.form['gridRadios_Gender']
    Age = request.form['gridRadios_Age']
    Movie_Consumption = request.form['gridRadios_MC']
    Genre_Description = request.form.getlist('gridRadios_genre_desc')
    Genre_FreeText = request.form['gridRadios_genre_desc_freetext']
    Random_Value = request.form['random_value']

    Genre_Description_2 ='| '.join(Genre_Description)

    #print(Random_Value)

    #ADD TYPE OF GRAPHLAB MODEL BEING USED

    user_details = User_Demographics( Unique_ID = Random_Value, Gender = Gender, Age = Age, Movie_Consumption = Movie_Consumption, Genre_Description = Genre_Description_2, Genre_Description_Other = Genre_FreeText)
    db.session.add(user_details)
    db.session.commit()

    #print (Gender, Age, Movie_Consumption, Genre_Description, Genre_FreeText)

    User_ID = User_Demographics.query.filter_by(Unique_ID = Random_Value).all()
    User_ID_MovieLens = []
    for user in User_ID:
        User_ID_MovieLens.append(user.id)

    print ("USER_ID is {}".format(User_ID[0]))
    session['user_id_movielens'] = User_ID_MovieLens[0]
    print ("The current temporary movie_lens ID is : {}".format(session['user_id_movielens']))

    return render_template('initialseed.html', user_id_movielens = session['user_id_movielens'])


@app.route('/recommendations', methods=['POST'])
def recommendations():

    movielens_temp_id = session.get('user_id_movielens', None)
    print("The current temporary movie_lens ID is : {}".format(movielens_temp_id))

    Movie_Name_1 = request.form['id_1']
    Movie_IMDB_1 = request.form['imdb_1']
    Movie_Rating_1 = request.form['rating_1']
    Movie_Name_2 = request.form['id_2']
    Movie_IMDB_2 = request.form['imdb_2']
    Movie_Rating_2 = request.form['rating_2']
    Movie_Name_3 = request.form['id_3']
    Movie_IMDB_3 = request.form['imdb_3']
    Movie_Rating_3 = request.form['rating_3']
    Movie_Name_4 = request.form['id_4']
    Movie_IMDB_4 = request.form['imdb_4']
    Movie_Rating_4 = request.form['rating_4']
    Movie_Name_5 = request.form['id_5']
    Movie_IMDB_5 = request.form['imdb_5']
    Movie_Rating_5 = request.form['rating_5']
    Movie_Name_6 = request.form['id_6']
    Movie_IMDB_6 = request.form['imdb_6']
    Movie_Rating_6 = request.form['rating_6']
    Movie_Name_7 = request.form['id_7']
    Movie_IMDB_7 = request.form['imdb_7']
    Movie_Rating_7 = request.form['rating_7']
    Movie_Name_8 = request.form['id_8']
    Movie_IMDB_8 = request.form['imdb_8']
    Movie_Rating_8 = request.form['rating_8']
    Movie_Name_9 = request.form['id_9']
    Movie_IMDB_9 = request.form['imdb_9']
    Movie_Rating_9 = request.form['rating_9']
    Movie_Name_10 = request.form['id_10']
    Movie_IMDB_10 = request.form['imdb_10']
    Movie_Rating_10 = request.form['rating_10']
    Movie_Name_11 = request.form['id_11']
    Movie_IMDB_11 = request.form['imdb_11']
    Movie_Rating_11 = request.form['rating_11']
    Movie_Name_12 = request.form['id_12']
    Movie_IMDB_12 = request.form['imdb_12']
    Movie_Rating_12 = request.form['rating_12']
    Movie_Name_13 = request.form['id_13']
    Movie_IMDB_13 = request.form['imdb_13']
    Movie_Rating_13 = request.form['rating_13']
    Movie_Name_14 = request.form['id_14']
    Movie_IMDB_14 = request.form['imdb_14']
    Movie_Rating_14 = request.form['rating_14']
    Movie_Name_15 = request.form['id_15']
    Movie_IMDB_15 = request.form['imdb_15']
    Movie_Rating_15 = request.form['rating_15']
    Movie_Name_16 = request.form['id_16']
    Movie_IMDB_16 = request.form['imdb_16']
    Movie_Rating_16 = request.form['rating_16']
    Movie_Name_17 = request.form['id_17']
    Movie_IMDB_17 = request.form['imdb_17']
    Movie_Rating_17 = request.form['rating_17']
    Movie_Name_18 = request.form['id_18']
    Movie_IMDB_18 = request.form['imdb_18']
    Movie_Rating_18 = request.form['rating_18']
    Movie_Name_19 = request.form['id_19']
    Movie_IMDB_19 = request.form['imdb_19']
    Movie_Rating_19 = request.form['rating_19']
    Movie_Name_20 = request.form['id_20']
    Movie_IMDB_20 = request.form['imdb_20']
    Movie_Rating_20 = request.form['rating_20']
    Movie_Name_21 = request.form['id_21']
    Movie_IMDB_21 = request.form['imdb_21']
    Movie_Rating_21 = request.form['rating_21']
    Movie_Name_22 = request.form['id_22']
    Movie_IMDB_22 = request.form['imdb_22']
    Movie_Rating_22 = request.form['rating_22']
    Movie_Name_23 = request.form['id_23']
    Movie_IMDB_23 = request.form['imdb_23']
    Movie_Rating_23 = request.form['rating_23']
    Movie_Name_24 = request.form['id_24']
    Movie_IMDB_24 = request.form['imdb_24']
    Movie_Rating_24 = request.form['rating_24']
    Movie_Name_25 = request.form['id_25']
    Movie_IMDB_25 = request.form['imdb_25']
    Movie_Rating_25 = request.form['rating_25']
    Movie_Name_26 = request.form['id_26']
    Movie_IMDB_26 = request.form['imdb_26']
    Movie_Rating_26 = request.form['rating_26']
    Movie_Name_27 = request.form['id_27']
    Movie_IMDB_27 = request.form['imdb_27']
    Movie_Rating_27 = request.form['rating_27']
    Movie_Name_28 = request.form['id_28']
    Movie_IMDB_28 = request.form['imdb_28']
    Movie_Rating_28 = request.form['rating_28']
    Movie_Name_29 = request.form['id_29']
    Movie_IMDB_29 = request.form['imdb_29']
    Movie_Rating_29 = request.form['rating_29']
    Movie_Name_30 = request.form['id_30']
    Movie_IMDB_30 = request.form['imdb_30']
    Movie_Rating_30 = request.form['rating_30']
    Movie_Name_31 = request.form['id_31']
    Movie_IMDB_31 = request.form['imdb_31']
    Movie_Rating_31 = request.form['rating_31']
    Movie_Name_32 = request.form['id_32']
    Movie_IMDB_32 = request.form['imdb_32']
    Movie_Rating_32 = request.form['rating_32']
    Movie_Name_33 = request.form['id_33']
    Movie_IMDB_33 = request.form['imdb_33']
    Movie_Rating_33 = request.form['rating_33']
    Movie_Name_34 = request.form['id_34']
    Movie_IMDB_34 = request.form['imdb_34']
    Movie_Rating_34 = request.form['rating_34']
    Movie_Name_35 = request.form['id_35']
    Movie_IMDB_35 = request.form['imdb_35']
    Movie_Rating_35 = request.form['rating_35']
    Movie_Name_36 = request.form['id_36']
    Movie_IMDB_36 = request.form['imdb_36']
    Movie_Rating_36 = request.form['rating_36']
    Movie_Name_37 = request.form['id_37']
    Movie_IMDB_37 = request.form['imdb_37']
    Movie_Rating_37 = request.form['rating_37']
    Movie_Name_38 = request.form['id_38']
    Movie_IMDB_38 = request.form['imdb_38']
    Movie_Rating_38 = request.form['rating_38']
    Movie_Name_39 = request.form['id_39']
    Movie_IMDB_39 = request.form['imdb_39']
    Movie_Rating_39 = request.form['rating_39']
    Movie_Name_40 = request.form['id_40']
    Movie_IMDB_40 = request.form['imdb_40']
    Movie_Rating_40 = request.form['rating_40']

    U_1 = [movielens_temp_id, Movie_Name_1, Movie_IMDB_1, Movie_Rating_1]
    U_2 = [movielens_temp_id, Movie_Name_2, Movie_IMDB_2, Movie_Rating_2]
    U_3 = [movielens_temp_id, Movie_Name_3, Movie_IMDB_3, Movie_Rating_3]
    U_4 = [movielens_temp_id, Movie_Name_4, Movie_IMDB_4, Movie_Rating_4]
    U_5 = [movielens_temp_id, Movie_Name_5, Movie_IMDB_5, Movie_Rating_5]
    U_6 = [movielens_temp_id, Movie_Name_6, Movie_IMDB_6, Movie_Rating_6]
    U_7 = [movielens_temp_id, Movie_Name_7, Movie_IMDB_7, Movie_Rating_7]
    U_8 = [movielens_temp_id, Movie_Name_8, Movie_IMDB_8, Movie_Rating_8]
    U_9 = [movielens_temp_id, Movie_Name_9, Movie_IMDB_9, Movie_Rating_9]
    U_10 = [movielens_temp_id, Movie_Name_10, Movie_IMDB_10, Movie_Rating_10]
    U_11 = [movielens_temp_id, Movie_Name_11, Movie_IMDB_11, Movie_Rating_11]
    U_12 = [movielens_temp_id, Movie_Name_12, Movie_IMDB_12, Movie_Rating_12]
    U_13 = [movielens_temp_id, Movie_Name_13, Movie_IMDB_13, Movie_Rating_13]
    U_14 = [movielens_temp_id, Movie_Name_14, Movie_IMDB_14, Movie_Rating_14]
    U_15 = [movielens_temp_id, Movie_Name_15, Movie_IMDB_15, Movie_Rating_15]
    U_16 = [movielens_temp_id, Movie_Name_16, Movie_IMDB_16, Movie_Rating_16]
    U_17 = [movielens_temp_id, Movie_Name_17, Movie_IMDB_17, Movie_Rating_17]
    U_18 = [movielens_temp_id, Movie_Name_18, Movie_IMDB_18, Movie_Rating_18]
    U_19 = [movielens_temp_id, Movie_Name_19, Movie_IMDB_19, Movie_Rating_19]
    U_20 = [movielens_temp_id, Movie_Name_20, Movie_IMDB_20, Movie_Rating_20]
    U_21 = [movielens_temp_id, Movie_Name_21, Movie_IMDB_21, Movie_Rating_21]
    U_22 = [movielens_temp_id, Movie_Name_22, Movie_IMDB_22, Movie_Rating_22]
    U_23 = [movielens_temp_id, Movie_Name_23, Movie_IMDB_23, Movie_Rating_23]
    U_24 = [movielens_temp_id, Movie_Name_24, Movie_IMDB_24, Movie_Rating_24]
    U_25 = [movielens_temp_id, Movie_Name_25, Movie_IMDB_25, Movie_Rating_25]
    U_26 = [movielens_temp_id, Movie_Name_26, Movie_IMDB_26, Movie_Rating_26]
    U_27 = [movielens_temp_id, Movie_Name_27, Movie_IMDB_27, Movie_Rating_27]
    U_28 = [movielens_temp_id, Movie_Name_28, Movie_IMDB_28, Movie_Rating_28]
    U_29 = [movielens_temp_id, Movie_Name_29, Movie_IMDB_29, Movie_Rating_29]
    U_30 = [movielens_temp_id, Movie_Name_30, Movie_IMDB_30, Movie_Rating_30]
    U_31 = [movielens_temp_id, Movie_Name_31, Movie_IMDB_31, Movie_Rating_31]
    U_32 = [movielens_temp_id, Movie_Name_32, Movie_IMDB_32, Movie_Rating_32]
    U_33 = [movielens_temp_id, Movie_Name_33, Movie_IMDB_33, Movie_Rating_33]
    U_34 = [movielens_temp_id, Movie_Name_34, Movie_IMDB_34, Movie_Rating_34]
    U_35 = [movielens_temp_id, Movie_Name_35, Movie_IMDB_35, Movie_Rating_35]
    U_36 = [movielens_temp_id, Movie_Name_36, Movie_IMDB_36, Movie_Rating_36]
    U_37 = [movielens_temp_id, Movie_Name_37, Movie_IMDB_37, Movie_Rating_37]
    U_38 = [movielens_temp_id, Movie_Name_38, Movie_IMDB_38, Movie_Rating_38]
    U_39 = [movielens_temp_id, Movie_Name_39, Movie_IMDB_39, Movie_Rating_39]
    U_40 = [movielens_temp_id, Movie_Name_40, Movie_IMDB_40, Movie_Rating_40]

    data = [U_1, U_2, U_3, U_4, U_5, U_6, U_7, U_8, U_9, U_10, U_11, U_12, U_13, U_14, U_15, U_16, U_17, U_18, U_19, U_20, U_21, U_22, U_23, U_24, U_25, U_26, U_27, U_28, U_29, U_30, U_31, U_32, U_33, U_34, U_35, U_36, U_37, U_38, U_39, U_40]

    imdb_initial_list = []

    for x in data:
        if (x[3] == '0'):
            continue
        else:
            imdb_initial_list.append(x[2])
            y = [int(i) for i in x]
            user_rating = Movie_Lens_Ratings(user_id = y[0], item_id = y[1], rating = y[3])
            db.session.add(user_rating)
            db.session.commit()

    session['user_initial_movie_list'] = imdb_initial_list
    conn = mysql.connect()
    sf_sample = tc.SFrame.from_sql(conn, "SELECT user_id,item_id,rating FROM movie__lens__ratings")
    conn.close()
    gc.collect()
    print (sf_sample.num_rows())
    m = tc.item_similarity_recommender.create(sf_sample, user_id='user_id', item_id='item_id', target='rating', similarity_type='cosine') #pearson , jaccard , cosine
    #m = tc.factorization_recommender.create(sf_sample, target='rating')
    #m = tc.popularity_recommender.create(sf_sample, target='rating')
    recs = m.recommend()
    print (recs)

    print (movielens_temp_id)
    recommendations = recs[recs['user_id'] == movielens_temp_id]
    print (recommendations)

    recommendations_dataframe = recommendations.to_dataframe()
    my_movieid_list = recommendations_dataframe['item_id'].tolist()
    session['my_movieid_list_temp'] = my_movieid_list

    recommendation_details = db.session.query(Movie_Lens_MovieData).filter(Movie_Lens_MovieData.movieid.in_(my_movieid_list)).all()

    value = "panel_1"

    return render_template('recommendations.html', recommendation_details = recommendation_details, check = value)

@app.route('/recommendations_2', methods=['POST'])
def recommendations_2():

    movielens_temp_id = session.get('user_id_movielens', None) #Retrieve the current ID of the user using the system.
    my_movieid_list = session.get('my_movieid_list_temp', None) #The movies recommended in the first panel.

    imdb_values = request.form.getlist('imdb_detail') #The IMDB IDs of the movies clicked from the first panel.
    f=open('Panel_1_IDs.txt','w')
    s1='\n'.join(imdb_values)
    f.write(s1)
    f.close()

    #session['current_imdb_values'] = imdb_values
    print("The movies selected by the user are {}".format(imdb_values))
    recommendation_details = db.session.query(Movie_Lens_MovieData).filter(Movie_Lens_MovieData.movieid.in_(my_movieid_list)).all() #Retrive the details of the movies recommeneded in the first panel.
    MT_Users = db.session.query(ratings_final.user_id).filter(ratings_final.imdb_id.in_(imdb_values)).all() #Get IDs of MT users who have voted for the movies selected in the first panel.

    movie_tweeting_userid = []
    for user in MT_Users:
        movie_tweeting_userid.append(user.user_id) #Appended the user IDs.
    movie_tweeting_userid_temp = set(movie_tweeting_userid)
    movie_tweeting_userid_distinct = []
    movie_tweeting_userid_distinct = list(movie_tweeting_userid_temp) #Distinct user IDs are selected.
    #print("The distinct MT users who voted for this/these movie(s) are {}".format(movie_tweeting_userid_distinct))

    my_rated_movie_list = session.get('user_initial_movie_list', None)
    current_user_profile = []
    current_user_profile = my_rated_movie_list + imdb_values
    #print("The movies consumed by the current user are {}".format(current_user_profile))
    current_genres_consumed = []
    genres_consumed = db.session.query(MT_MovieData.genre).filter(MT_MovieData.imdb_id.in_(current_user_profile)).all() #Retrive all the genre information consumed by the current user.
    for current in genres_consumed:
        current_genres_consumed.append(current.genre)
    #print ("The current genres consumed by the user are {}".format(current_genres_consumed))
    a = ''
    for item in current_genres_consumed:
        a = a + "|" + item
    a = a[:0] + a[(0+1):]
    #print ("Current genres for comparison are {}".format(a))

    def square_rooted(x):
        return round(sqrt(sum([a*a for a in x])),3)

    def cosine_similarity(x,y):
        numerator = sum(a*b for a,b in zip(x,y))
        denominator = square_rooted(x)*square_rooted(y)
        return round(numerator/float(denominator),3)

    def word_count(str):
        counts = dict()
        words = str.split('|')
        for word in words:
            if word in counts:
                counts[word] += 1
            else:
                counts[word] = 1
        return counts

    user_1 = word_count(a)
    movie_genres = pandas.DataFrame(columns=['Action','Adult','Adventure','Animation','Biography','Comedy','Crime','Documentary','Drama','Family','Fantasy','Film-Noir','Game-Show','History','Horror','Music','Musical','Mystery','News','Reality-TV','Romance','Sci-Fi','Short','Sport','Talk-Show','Thriller','War','Western'])

    temp_dataframe_1 = pandas.DataFrame(user_1, index = [movielens_temp_id])
    frames = [movie_genres, temp_dataframe_1]
    final_result = pandas.concat(frames)
    final_result = final_result.fillna(0)
    for index,row in final_result.iterrows():
        a = row.values.tolist()

    #print (a)
    final_result = final_result[0:0]
    #print (len(final_result))

    MT_Users_Complete_Profiles = db.session.query(ratings_final).filter(ratings_final.user_id.in_(movie_tweeting_userid_distinct)).all()
    MT_Users_Complete_Profiles_userID = []
    MT_Users_Complete_Profiles_title = []
    MT_Users_Complete_Profiles_genre = []
    MT_Users_Complete_Profiles_screenname = []
    sample = pandas.DataFrame(columns=['user_id','title','genre','screenname'])
    for user in MT_Users_Complete_Profiles:
        MT_Users_Complete_Profiles_userID.append(user.user_id)
        MT_Users_Complete_Profiles_title.append(user.title)
        MT_Users_Complete_Profiles_genre.append(user.genre)
        MT_Users_Complete_Profiles_screenname.append(user.screen_name)
    sample['user_id'] = MT_Users_Complete_Profiles_userID
    sample['title'] = MT_Users_Complete_Profiles_title
    sample['genre'] = MT_Users_Complete_Profiles_genre
    sample['screenname'] = MT_Users_Complete_Profiles_screenname


    #movie_genres = pandas.DataFrame(columns=['Action','Adult','Adventure','Animation','Biography','Comedy','Crime','Documentary','Drama','Family','Fantasy','Film-Noir','Game-Show','History','Horror','Music','Musical','Mystery','News','Reality-TV','Romance','Sci-Fi','Short','Sport','Talk-Show','Thriller','War','Western'])
    similarity_score_dataframe = pandas.DataFrame(columns=['initial_user','movie_tweeting_user','similiarity_value', 'occurances'])

    for i in sample.user_id.unique():
        current_user = sample[(sample.user_id == i)]
        temp_list = current_user['genre'].tolist()
        current_list = ''
        for item in temp_list:
            current_list = current_list + "|" + item
            current_list = current_list[:0] + current_list[(0+1):]
            user_2 = word_count(current_list)
            #temp_dataframe_1 = pandas.DataFrame(user_1, index = [movielens_temp_id])
        temp_dataframe_2 = pandas.DataFrame(user_2, index = [i])
        frames = [final_result, temp_dataframe_2]
        final_result = pandas.concat(frames)

    #movie_genres = movie_genres.fillna(0)
    final_result_new = final_result[['Action','Adult','Adventure','Animation','Biography','Comedy','Crime','Documentary','Drama','Family','Fantasy','Film-Noir','Game-Show','History','Horror','Music','Musical','Mystery','News','Reality-TV','Romance','Sci-Fi','Short','Sport','Talk-Show','Thriller','War','Western']]
    final_result_new = final_result_new.fillna(0)
    final_result_new = final_result_new.astype(int)

    for index,row in final_result_new.iterrows():
        value = sample.loc[sample.user_id == index, 'user_id'].count()
        b = row.values.tolist()
        normed_a = [i/sum(a) for i in a]
        normed_b = [i/sum(b) for i in b]
        cosine_similarity_value = cosine_similarity(normed_a,normed_b)
        print ("Current User: {}, MT User: {}, Similarity Score: {}".format(movielens_temp_id, index, cosine_similarity_value))
        similarity_score_dataframe.loc[len(similarity_score_dataframe)] = [movielens_temp_id, index, cosine_similarity_value, value]

    similarity_score_dataframe['initial_user'] = similarity_score_dataframe['initial_user'].astype('int64')
    similarity_score_dataframe['movie_tweeting_user'] = similarity_score_dataframe['movie_tweeting_user'].astype('int64')
    similarity_score_dataframe['occurances'] = similarity_score_dataframe['occurances'].astype('int64')
    voted_users_details = similarity_score_dataframe.sort_values(by='similiarity_value', ascending=False)

    voted_users_MT = voted_users_details['movie_tweeting_user'].values.tolist()
    #print (voted_users_MT)


    def f(row):
        x = voted_users_details.nlargest(int(len(voted_users_details)*1/4), 'occurances')
        y = x['movie_tweeting_user'].tolist()
        if row['movie_tweeting_user'] in y:
            val = 'Super User'
        else:
            val = ''
        return val
    voted_users_details['user_type'] = voted_users_details.apply(f, axis=1)

    MT_Users_Twitter_Details = db.session.query(MT_User_Details).filter(MT_User_Details.user_id.in_(voted_users_MT)).all()
    MT_Users_Twitter_Details_userID = []
    MT_Users_Twitter_Details_twitterID = []
    MT_Users_Twitter_Details_screenname = []
    MT_Users_Twitter_DF = pandas.DataFrame(columns=['movie_tweeting_user','twitter_id','screen_name'])
    for user in MT_Users_Twitter_Details:
        MT_Users_Twitter_Details_userID.append(user.user_id)
        MT_Users_Twitter_Details_twitterID.append(user.twitter_id)
        MT_Users_Twitter_Details_screenname.append(user.screen_name)
    MT_Users_Twitter_DF['movie_tweeting_user'] = MT_Users_Twitter_Details_userID
    MT_Users_Twitter_DF['twitter_id'] = MT_Users_Twitter_Details_twitterID
    MT_Users_Twitter_DF['screen_name'] = MT_Users_Twitter_Details_screenname
    #print (MT_Users_Twitter_DF)

    voted_users = pandas.merge(voted_users_details, MT_Users_Twitter_DF, on = 'movie_tweeting_user')
    #print (voted_users)

    voted_users_details_dict = voted_users.astype(object).to_dict(orient='records')
    #session['voted_users_details_dict_session'] = voted_users_details_dict

    value = "panel_2"

    return render_template('recommendations.html', recommendation_details = recommendation_details, voter_details = voted_users_details_dict, check = value, current_imdb_values = imdb_values )

@app.route('/recommendations_3', methods=['POST'])
def recommendations_3():

    slider_value = request.form['slider_value']
    print ("Slider value is: {}".format(slider_value))


    #First panel
    movielens_temp_id = session.get('user_id_movielens', None) #Retrieve the current ID of the user using the system.
    my_movieid_list = session.get('my_movieid_list_temp', None) #The movies recommended in the first panel.
    recommendation_details = db.session.query(Movie_Lens_MovieData).filter(Movie_Lens_MovieData.movieid.in_(my_movieid_list)).all()

    #Second panel
    #voted_users_details_dict_session = session.get('voted_users_details_dict_session', None)
    #print (voted_users_details_dict_session)
    voter_detail_1 = request.form.getlist('voter_MT_User')
    voter_detail_2 = request.form.getlist('voter_screen_name')
    voter_detail_3 = request.form.getlist('voter_score')
    voted_users = pandas.DataFrame(columns=['movie_tweeting_user','screen_name','similiarity_value'])
    voted_users['movie_tweeting_user'] = voter_detail_1
    voted_users['screen_name'] = voter_detail_2
    voted_users['similiarity_value'] = voter_detail_3
    voted_users_details_dict = voted_users.astype(object).to_dict(orient='records')
    #print (voted_users_details_dict)


    #Third panel
    twitter_users = request.form.getlist('MT_User') #The user ID's of Twitter users selected from the second panel.
    print ("The twitter users involved are : {}".format(twitter_users))
    movies_rated_all = db.session.query(ratings_final).filter(ratings_final.user_id.in_(twitter_users)).all()
    movies_information_imdb_id = []
    movies_information_title = []
    movies_information_genre = []
    movies_information_DF = pandas.DataFrame(columns=['imdb_id','title','genre'])
    for item in movies_rated_all:
        movies_information_imdb_id.append(item.imdb_id)
        movies_information_title.append(item.title)
        movies_information_genre.append(item.genre)
    movies_information_DF['imdb_id'] = movies_information_imdb_id
    movies_information_DF['title'] = movies_information_title
    movies_information_DF['genre'] = movies_information_genre
    print ("The initial length of movies_information_DF is: {}".format(len(movies_information_DF)))
    movies_information_DF_dict = movies_information_DF.astype(object).to_dict(orient='records')

    movies_information_DF_new = pandas.DataFrame(columns=['imdb_id','occurances','title','genre'])
    for row in movies_information_DF.itertuples():
        if not row.imdb_id in movies_information_DF_new['imdb_id'].tolist():
            count = movies_information_DF.loc[movies_information_DF.imdb_id == row.imdb_id, 'imdb_id'].count()
            movies_information_DF_new.loc[len(movies_information_DF_new)] = [row.imdb_id, count, row.title, row.genre]
    print ("Done!")
    movies_information_DF_new = movies_information_DF_new.sort_values(by='occurances', ascending=0)
    print ("The length of movies_information_DF_new is: {}".format(len(movies_information_DF_new)))

    #MMR Formula implementation
    def square_rooted(x):
        return round(sqrt(sum([a*a for a in x])),3)

    def cosine_similarity(x,y):
        numerator = sum(a*b for a,b in zip(x,y))
        denominator = square_rooted(x)*square_rooted(y)
        return round(numerator/float(denominator),3)

    def word_count(str):
        counts = dict()
        words = str.split('|')
        for word in words:
            if word in counts:
                counts[word] += 1
            else:
                counts[word] = 1
        return counts

    movie_genres = pandas.DataFrame(columns=['Action','Adult','Adventure','Animation','Biography','Comedy','Crime','Documentary','Drama','Family','Fantasy','Film-Noir','Game-Show','History','Horror','Music','Musical','Mystery','News','Reality-TV','Romance','Sci-Fi','Short','Sport','Talk-Show','Thriller','War','Western'])

    #Calculation of Query for the MMR Equation
    #IMDB_CURRENT = request.form.getlist('current_imdb')
    #print ("Current IMDB values are: {}".format(IMDB_CURRENT))
    with open('Panel_1_IDs.txt') as f:
        IMDB_CURRENT = f.read().splitlines()
        f.close()

    current_Q = []
    current_Q = IMDB_CURRENT
    current_Q_genre = []
    genres_consumed_Q = db.session.query(MT_MovieData).filter(MT_MovieData.imdb_id.in_(current_Q)).all() #Retrive all the genre information consumed by the current user from only the first panel.
    for item in genres_consumed_Q:
        current_Q_genre.append(item.genre)
    print ("The current genres considered for Q are {}".format(current_Q_genre))
    q = ''
    for item in current_Q_genre:
        q = q + "|" + item
    q = q[:0] + q[(0+1):]
    print ("Current value for Q is {}".format(q))

    print ("q_value is: {}".format(q))
    q_count = word_count(q)
    temp_dataframe_q = pandas.DataFrame(q_count, index = [movielens_temp_id])
    frames_q = [movie_genres, temp_dataframe_q]
    q_result = pandas.concat(frames_q)
    q_result = q_result.fillna(0)
    print (q_result)
    q_result_list = q_result.loc[movielens_temp_id].tolist()
    q_result = q_result[0:0]

    pandas.options.mode.chained_assignment = None
    MMR_Final_List = pandas.DataFrame(columns=['imdb_id','title','genre'])
    x = movies_information_DF_new.iloc[0]
    MMR_Final_List.loc[len(MMR_Final_List)] = x
    movies_information_DF_new = movies_information_DF_new[movies_information_DF_new.imdb_id != x.imdb_id]
    print ("The initial length of MMR_Final_List is: {}".format(len(MMR_Final_List)))
    print ("The length after removal of first element of movies_information_DF_new is: {}".format(len(movies_information_DF_new)))

    temp_df = pandas.DataFrame(columns=['imdb_id','score'])
    temp_mmr_df = pandas.DataFrame(columns=['imdb_id','title','genre','mmr_score'])

    for row in MMR_Final_List.itertuples():
        a = word_count(row.genre)
        temp_dataframe_1 = pandas.DataFrame(a, index = [row.imdb_id])
    frames = [movie_genres, temp_dataframe_1]
    final_result = pandas.concat(frames)
    final_result = final_result.fillna(0)
    print ("The initial count for final_result is: {}".format(len(final_result)))

    for row in movies_information_DF_new.itertuples():
        b = word_count(row.genre)
        temp_dataframe_2 = pandas.DataFrame(b, index = [row.imdb_id])
        frames = [final_result, temp_dataframe_2]
        final_result = pandas.concat(frames)
    print ("The final count for final_result is: {}".format(len(final_result)))
    final_result_new = final_result[['Action','Adult','Adventure','Animation','Biography','Comedy','Crime','Documentary','Drama','Family','Fantasy','Film-Noir','Game-Show','History','Horror','Music','Musical','Mystery','News','Reality-TV','Romance','Sci-Fi','Short','Sport','Talk-Show','Thriller','War','Western']]
    final_result_new = final_result_new.fillna(0)
    final_result_new = final_result_new.astype(int)
    print ("The final count for final_result_new is: {}".format(len(final_result_new)))
    #print (final_result_new.head(n=5))

    if ((len(movies_information_DF_new)) > 10):
        max_length = 10
    else:
        max_length = len(movies_information_DF_new)

    while (len(MMR_Final_List) != max_length):
        for row in movies_information_DF_new.itertuples():
            if not row.imdb_id in MMR_Final_List['imdb_id'].tolist():
                print ("The item to be compared is: ",row.imdb_id,row.genre)
                for mmr_element in MMR_Final_List.itertuples():
                    index_1 = mmr_element.imdb_id
                    index_2 = row.imdb_id
                    x = final_result_new.loc[index_1].tolist()
                    y = final_result_new.loc[index_2].tolist()
                    similarity_score = cosine_similarity (x,y)
                    score = 1 - similarity_score
                    score = round(score,3)
                    temp_df.loc[len(temp_df)] = [row.imdb_id, score]
                    print (mmr_element.imdb_id,row.imdb_id,score)
                print ("Done")
                max_value_df = temp_df.loc[temp_df['imdb_id'] == row.imdb_id]
                max_value_score = max_value_df['score'].max()
                sim_q = cosine_similarity(final_result_new.loc[row.imdb_id].tolist(),q_result_list)
                sim_q = round(sim_q,3)
                print ("The similarity between Query and : ",row.imdb_id, sim_q)
                print ("Max value of (1 - sim) for Title: ", row.imdb_id, max_value_score)
                MMR_Final_value = (0.5*sim_q - 0.5*(max_value_score))
                MMR_Final_value = round(MMR_Final_value,3)
                print ("MMR_Final_value: ", MMR_Final_value)
                temp_mmr_df.loc[len(temp_mmr_df)] = [row.imdb_id, row.title, row.genre, MMR_Final_value]
                max_value_df = temp_mmr_df.loc[temp_mmr_df['mmr_score'] == temp_mmr_df["mmr_score"].max()]
                x = max_value_df["imdb_id"].tolist()
                print ("IMDB ID(s) with maximum MMR scores: ", x)
                for row in max_value_df.itertuples():
                    if (len(MMR_Final_List) != max_length):
                        details = row.imdb_id, row.title, row.genre
                        MMR_Final_List.loc[len(MMR_Final_List)] = details
                        print (len(MMR_Final_List))
                        movies_information_DF_new = movies_information_DF_new[movies_information_DF_new.imdb_id != row.imdb_id]
                        print (len(movies_information_DF_new))
                    else:
                        print ("MMR List Completed!")
                    temp_df = temp_df[0:0]
                    temp_mmr_df = temp_mmr_df[0:0]
            else:
                print ("MMR List Completed!")

    print ("The final length of MMR_Final_List is: {}".format(len(MMR_Final_List)))
    print ("The final length of movies_information_DF_new is: {}".format(len(movies_information_DF_new)))
    print ("The initial length of movies_information_DF is: {}".format(len(movies_information_DF)))

    MMR_Final_List_dict = MMR_Final_List.astype(object).to_dict(orient='records')

    movies_information_DF_new = movies_information_DF_new[0:0]
    print ("The final length of movies_information_DF_new is: {}".format(len(movies_information_DF_new)))
    session['final_mmr_movies'] = MMR_Final_List_dict

    return render_template('recommendations.html', recommendation_details = recommendation_details, voter_details = voted_users_details_dict, final_movies = MMR_Final_List_dict, current_movies_first_panel = IMDB_CURRENT, slider_value = slider_value, twitter_users = twitter_users )

@app.route('/evaluation_novelty', methods=['POST'])
def evaluation_novelty():

    #current_user_id = session.get('user_id_movielens', None)
    movies_first_panel = request.form['current_movies_first_panel']
    #current_first_panel_movies ='|'.join(movies_first_panel)
    slider_value = request.form['slider_value_selected']
    twitter_users = request.form['selected_twitter_users']
    movielens_temp_id = session.get('user_id_movielens', None) #Retrieve the current ID of the user using the system.

    print ("The final slider value is: {}".format(slider_value))
    print ("The Twitter users selected are : {}".format(twitter_users))
    print ("The movies selected in the first panel are: {}".format(movies_first_panel))
    print ("The current user using this system is: {}".format(movielens_temp_id))


    my_movieid_list = session.get('my_movieid_list_temp', None) #The movies recommended in the first panel.
    recommendation_details = db.session.query(Movie_Lens_MovieData).filter(Movie_Lens_MovieData.movieid.in_(my_movieid_list)).all()

    MMR_Final_List_dict = session.get('final_mmr_movies', None)

    return render_template('evaluation_novelty.html', recommendation_details = recommendation_details, final_movies = MMR_Final_List_dict, slider_value = slider_value, twitter_users = twitter_users, current_imdb_movies  = movies_first_panel )

@app.route('/evaluation_diversity', methods=['POST'])
def evaluation_diversity():

    slider_value = request.form['slider_value_selected']
    twitter_users = request.form['selected_twitter_users']
    movies_first_panel = request.form['current_imdb_movies']
    #current_first_panel_movies ='|'.join(movies_first_panel)

    movielens_temp_id = session.get('user_id_movielens', None) #Retrieve the current ID of the user using the system.
    novel_movies_RS_one = request.form.getlist('recommendations_1')
    Novel_Movies_1 ='|'.join(novel_movies_RS_one)
    novel_movies_RS_two = request.form.getlist('recommendations_2')
    Novel_Movies_2 ='|'.join(novel_movies_RS_two)
    Q_2 = request.form['q_1']
    Q_3 = request.form['q_2']
    Q_4 = request.form['q_3']

    print ("The current user using this system is: {}".format(movielens_temp_id))
    print ("The novel movies selected from the first panel are: {}".format(Novel_Movies_1))
    print ("The novel movies selected from the second panel are: {}".format(Novel_Movies_2))
    print (Q_2)
    print (Q_3)
    print (Q_4)
    print ("The final slider value is: {}".format(slider_value))
    print ("The Twitter users selected are : {}".format(twitter_users))
    print ("The movies selected in the first panel are: {}".format(movies_first_panel))

    novelty_lists = novelty_evaluation_lists( user_id = movielens_temp_id, List_1_Movies = Novel_Movies_1, List_2_Movies = Novel_Movies_2 )
    db.session.add(novelty_lists)
    db.session.commit()

    novelty_qa_answers = novelty_qa( user_id = movielens_temp_id, question_2 = Q_2, question_3 = Q_3, question_4 = Q_4 )
    db.session.add(novelty_qa_answers)
    db.session.commit()


    #movielens_temp_id = session.get('user_id_movielens', None) #Retrieve the current ID of the user using the system.
    my_movieid_list = session.get('my_movieid_list_temp', None) #The movies recommended in the first panel.
    recommendation_details = db.session.query(Movie_Lens_MovieData).filter(Movie_Lens_MovieData.movieid.in_(my_movieid_list)).all()

    MMR_Final_List_dict = session.get('final_mmr_movies', None)

    return render_template('evaluation_diversity.html', recommendation_details = recommendation_details, final_movies = MMR_Final_List_dict, slider_value = slider_value, twitter_users = twitter_users, current_imdb_movies  = movies_first_panel  )

@app.route('/evaluation_precision', methods=['POST'])
def evaluation_precision():

    slider_value = request.form['slider_value_selected']
    twitter_users = request.form['selected_twitter_users']
    movies_first_panel = request.form['current_imdb_movies']

    movielens_temp_id = session.get('user_id_movielens', None) #Retrieve the current ID of the user using the system.

    Q_1 = request.form['q_1']
    Q_2 = request.form['q_2']
    Q_3 = request.form['q_3']
    Q_4 = request.form['q_4']

    print ("The current user using this system is: {}".format(movielens_temp_id))
    print ("The final slider value is: {}".format(slider_value))
    print ("The Twitter users selected are : {}".format(twitter_users))
    print ("The movies selected in the first panel are: {}".format(movies_first_panel))
    print (Q_1)
    print (Q_2)
    print (Q_3)
    print (Q_4)

    diversity_qa_answers = diversity_qa( user_id = movielens_temp_id, question_1 = Q_1, question_2 = Q_2, question_3 = Q_3, question_4 = Q_4 )
    db.session.add(diversity_qa_answers)
    db.session.commit()

    #movielens_temp_id = session.get('user_id_movielens', None) #Retrieve the current ID of the user using the system.
    my_movieid_list = session.get('my_movieid_list_temp', None) #The movies recommended in the first panel.
    recommendation_details = db.session.query(Movie_Lens_MovieData).filter(Movie_Lens_MovieData.movieid.in_(my_movieid_list)).all()

    MMR_Final_List_dict = session.get('final_mmr_movies', None)

    return render_template('evaluation_precision.html', recommendation_details = recommendation_details, final_movies = MMR_Final_List_dict, slider_value = slider_value, twitter_users = twitter_users, current_imdb_movies  = movies_first_panel  )


@app.route('/user_satisfaction', methods=['POST'])
def user_satisfaction():

    #current_user_id = session.get('user_id_movielens', None)
    movielens_temp_id = session.get('user_id_movielens', None) #Retrieve the current ID of the user using the system.
    slider_value = request.form['slider_value_selected']
    twitter_users = request.form['selected_twitter_users']
    movies_first_panel = request.form['current_imdb_movies']
    #current_first_panel_movies ='|'.join(movies_first_panel)

    precision_list_1 = request.form.getlist('recommendations_1')
    Precision_1 ='|'.join(precision_list_1)
    precision_list_2 = request.form.getlist('recommendations_2')
    Precision_2 ='|'.join(precision_list_2)

    print ("The current user using this system is: {}".format(movielens_temp_id))
    print ("The final slider value is: {}".format(slider_value))
    print ("The Twitter users selected are : {}".format(twitter_users))
    print ("The movies selected in the first panel are: {}".format(movies_first_panel))
    print ("The relevant movies from Panel 1 are: {}".format(Precision_1))
    print ("The relevant movies from Panel 2 are: {}".format(Precision_2))

    prec_lists = precision_lists( user_id = movielens_temp_id, List_1_Movies = Precision_1, List_2_Movies = Precision_2 )
    db.session.add(prec_lists)
    db.session.commit()

    #movielens_temp_id = session.get('user_id_movielens', None) #Retrieve the current ID of the user using the system.
    my_movieid_list = session.get('my_movieid_list_temp', None) #The movies recommended in the first panel.
    recommendation_details = db.session.query(Movie_Lens_MovieData).filter(Movie_Lens_MovieData.movieid.in_(my_movieid_list)).all()

    MMR_Final_List_dict = session.get('final_mmr_movies', None)

    return render_template('user_satisfaction.html', recommendation_details = recommendation_details, final_movies = MMR_Final_List_dict, slider_value = slider_value, twitter_users = twitter_users, current_imdb_movies  = movies_first_panel )

@app.route('/thank_you', methods=['POST'])
def thank_you():

    movielens_temp_id = session.get('user_id_movielens', None) #Retrieve the current ID of the user using the system.
    slider_value = request.form['slider_value_selected']
    twitter_users = request.form['selected_twitter_users']
    movies_first_panel = request.form['current_imdb_movies']
    recommendation_list_1 = request.form.getlist('recommendations_1')
    All_Movies_1 ='|'.join(recommendation_list_1)
    recommendation_list_2 = request.form.getlist('recommendations_2')
    All_Movies_2 ='|'.join(recommendation_list_2)

    Q_1 = request.form['q_1']
    Q_2 = request.form['q_2']
    Q_3 = request.form['q_3']
    Q_4 = request.form['q_4']
    Q_5 = request.form['q_5']
    Q_6 = request.form['q_6']

    print ("The current user using this system is: {}".format(movielens_temp_id))
    print ("The final slider value is: {}".format(slider_value))
    print ("The Twitter users selected are : {}".format(twitter_users))
    print ("The movies selected in the first panel are: {}".format(movies_first_panel))
    print ("All movies from Panel 1 are: {}".format(All_Movies_1))
    print ("All movies from Panel 2 are: {}".format(All_Movies_2))
    print (Q_1)
    print (Q_2)
    print (Q_3)
    print (Q_4)
    print (Q_5)
    print (Q_6)

    user_satisfaction_answers = user_satisfaction_qa( user_id = movielens_temp_id, question_1 = Q_1, question_2 = Q_2, question_3 = Q_3, question_4 = Q_4, question_5 = Q_5, question_6 = Q_6 )
    db.session.add(user_satisfaction_answers)
    db.session.commit()

    other_RS_details = RS_Details( user_id = movielens_temp_id, slider_value = slider_value, twitter_users_selected = twitter_users, movies_first_panel = movies_first_panel, R_List_1 = All_Movies_1, R_List_2 = All_Movies_2 )
    db.session.add(other_RS_details)
    db.session.commit()

    #session.pop('user_id_movielens', None)
    #session.pop('user_initial_movie_list', None)
    #session.pop('my_movieid_list_temp', None)
    #session.pop('current_imdb_values', None)

    return render_template('thank_you.html')

@app.route('/user_information/<string:id>', methods=['GET'])
def user_information(id):

    MT_User_ID = id
    MT_Users_Complete_Profiles = ratings_final.query.filter_by(user_id = MT_User_ID)
    top_10_info_user_id = []
    top_10_info_imdb_id = []
    top_10_info_rating = []
    top_10_info_title = []
    top_10_info_genre = []
    top_10_info_screen_name = []
    top_information = pandas.DataFrame(columns=['user_id','imdb_id','rating','title','genre','screen_name'])
    for user in MT_Users_Complete_Profiles:
        top_10_info_user_id.append(user.user_id)
        top_10_info_imdb_id.append(user.imdb_id)
        top_10_info_rating.append(user.rating)
        top_10_info_title.append(user.title)
        top_10_info_genre.append(user.genre)
        top_10_info_screen_name.append(user.screen_name)
    top_information['user_id'] = top_10_info_user_id
    top_information['imdb_id'] = top_10_info_imdb_id
    top_information['rating'] = top_10_info_rating
    top_information['title'] = top_10_info_title
    top_information['genre'] = top_10_info_genre
    top_information['screen_name'] = top_10_info_screen_name

    top_n = top_information.sort_values(by=['rating'], ascending=[False])
    top_10 = top_n.groupby('user_id').head(10).reset_index(drop=True)
    top_n_records = top_10.astype(object).to_dict(orient='records')

    twitter_screen_id = top_10['screen_name'].iloc[0]

    print (MT_User_ID)

    return render_template('user_information.html', user_id = MT_User_ID, top_n_records = top_n_records, twitter_screen_id = twitter_screen_id)

if __name__ == '__main__':
    app.run(debug=True)
