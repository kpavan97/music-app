from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

app = Flask(__name__)
app.secret_key = "supersecretkey"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

# Database model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

with app.app_context():
    db.create_all()
    if not User.query.first():
        db.session.add_all([User(username="venu", password="123"), User(username="vidya", password="123")])
        db.session.commit()

SPOTIFY_CLIENT_ID = "3f77d1e5abc646468005e90a6df0776d"
SPOTIFY_CLIENT_SECRET = "dd833d2e654a4d93a3b96b100011c39c"

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET
))

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['username'] = username
            return redirect(url_for('categories'))
        else:
            return "Invalid credentials"
    return render_template('login.html')

@app.route('/categories')
def categories():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('categories.html')

@app.route('/recommend', methods=['GET', 'POST'])
def recommend():
    if 'username' not in session:
        return redirect(url_for('login'))

    category = request.args.get('category', 'Mood')
    languages = ['Telugu', 'Kannada', 'Hindi']
    heroes = {
        'Telugu': [
            'Mahesh Babu', 'Allu Arjun', 'Pawan Kalyan', 'Prabhas', 'Ram Charan',
            'Nani', 'Naga Chaitanya', 'Ravi Teja', 'Vijay Deverakonda', 'Chiranjeevi',
            'Balakrishna', 'Venkatesh', 'Nithiin', 'Sai Dharam Tej', 'Varun Tej'
        ],
        'Kannada': [
            'Yash', 'Puneeth Rajkumar', 'Darshan', 'Sudeep', 'Ganesh',
            'Shiva Rajkumar', 'Rakshit Shetty', 'Dhananjay', 'Upendra', 'Vijay Raghavendra'
        ],
        'Hindi': [
            'Shahrukh Khan', 'Salman Khan', 'Aamir Khan', 'Akshay Kumar', 'Ajay Devgn',
            'Ranveer Singh', 'Ranbir Kapoor', 'Varun Dhawan', 'Hrithik Roshan', 'Tiger Shroff',
            'Sidharth Malhotra', 'Kartik Aaryan', 'Rajkummar Rao', 'Ayushmann Khurrana', 'Vicky Kaushal'
        ]
    }

    moods = ['Happy', 'Sad', 'Romantic', 'Energetic', 'Relaxing']
    songs = []

    if request.method == 'POST':
        selected_language = request.form.get('language', '')
        selected_year = request.form.get('year', '')
        selected_mood = request.form.get('mood', '')
        selected_hero = request.form.get('hero', '')

        if category == 'Mood':
            query = f"{selected_mood} {selected_language} {selected_year}"
        elif category == 'Hero':
            query = f"{selected_hero} {selected_language} songs"
        elif category == 'Trending':
            query = f"Trending {selected_language} songs"
        elif category == 'Janapada':
            query = f"Janapada {selected_language} songs"
        elif category == 'Item Songs':
            query = f"Item songs {selected_language}"
        elif category == 'Pop Songs':
            query = f"Pop songs {selected_language}"
        else:
            query = "Top songs"

        results = sp.search(q=query, type='track', limit=5, market="IN")
        songs = [
            {
                'name': track['name'],
                'artist': track['artists'][0]['name'],
                'image': track['album']['images'][0]['url'],
                'external': track['external_urls']['spotify']
            }
            for track in results['tracks']['items']
        ]

        # Store results and details in session for /player
        session['songs'] = songs
        session['category'] = category
        session['mood'] = selected_mood
        session['language'] = selected_language
        session['year'] = selected_year
        session['hero'] = selected_hero

        return redirect(url_for('player'))

    return render_template('recommend.html',
                           category=category,
                           languages=languages,
                           moods=moods,
                           heroes=heroes)

@app.route('/player')
def player():
    if 'username' not in session:
        return redirect(url_for('login'))

    songs = session.get('songs', [])
    category = session.get('category', '')
    mood = session.get('mood', '')
    language = session.get('language', '')
    year = session.get('year', '')
    hero = session.get('hero', '')

    return render_template('player.html',
                           songs=songs,
                           category=category,
                           mood=mood,
                           language=language,
                           year=year,
                           hero=hero)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
