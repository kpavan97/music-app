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

# Mock data for testing (comment out to use real Spotify)
MOCK_SONGS = {
    'Happy': [
        {'name': 'Good as Hell', 'artist': 'Lizzo', 'image': 'https://via.placeholder.com/200?text=Song1', 'external': 'https://open.spotify.com/track/1'},
        {'name': 'Walking on Sunshine', 'artist': 'Katrina & The Waves', 'image': 'https://via.placeholder.com/200?text=Song2', 'external': 'https://open.spotify.com/track/2'},
        {'name': 'Don\'t Stop Me Now', 'artist': 'Queen', 'image': 'https://via.placeholder.com/200?text=Song3', 'external': 'https://open.spotify.com/track/3'},
        {'name': 'Shut Up and Dance', 'artist': 'Walk the Moon', 'image': 'https://via.placeholder.com/200?text=Song4', 'external': 'https://open.spotify.com/track/4'},
        {'name': 'I Gotta Feeling', 'artist': 'Black Eyed Peas', 'image': 'https://via.placeholder.com/200?text=Song5', 'external': 'https://open.spotify.com/track/5'},
    ],
    'Sad': [
        {'name': 'Someone Like You', 'artist': 'Adele', 'image': 'https://via.placeholder.com/200?text=Sad1', 'external': 'https://open.spotify.com/track/6'},
        {'name': 'The Night We Met', 'artist': 'Lord Huron', 'image': 'https://via.placeholder.com/200?text=Sad2', 'external': 'https://open.spotify.com/track/7'},
        {'name': 'Hurt', 'artist': 'Johnny Cash', 'image': 'https://via.placeholder.com/200?text=Sad3', 'external': 'https://open.spotify.com/track/8'},
        {'name': 'Black', 'artist': 'Pearl Jam', 'image': 'https://via.placeholder.com/200?text=Sad4', 'external': 'https://open.spotify.com/track/9'},
        {'name': 'Mad World', 'artist': 'Gary Jules', 'image': 'https://via.placeholder.com/200?text=Sad5', 'external': 'https://open.spotify.com/track/10'},
    ],
    'Romantic': [
        {'name': 'Perfect', 'artist': 'Ed Sheeran', 'image': 'https://via.placeholder.com/200?text=Rom1', 'external': 'https://open.spotify.com/track/11'},
        {'name': 'All of Me', 'artist': 'John Legend', 'image': 'https://via.placeholder.com/200?text=Rom2', 'external': 'https://open.spotify.com/track/12'},
        {'name': 'Thinking Out Loud', 'artist': 'Ed Sheeran', 'image': 'https://via.placeholder.com/200?text=Rom3', 'external': 'https://open.spotify.com/track/13'},
        {'name': 'Make You Feel My Love', 'artist': 'Adele', 'image': 'https://via.placeholder.com/200?text=Rom4', 'external': 'https://open.spotify.com/track/14'},
        {'name': 'Lucky', 'artist': 'Jason Mraz', 'image': 'https://via.placeholder.com/200?text=Rom5', 'external': 'https://open.spotify.com/track/15'},
    ],
    'Energetic': [
        {'name': 'Uptown Funk', 'artist': 'Bruno Mars', 'image': 'https://via.placeholder.com/200?text=Ener1', 'external': 'https://open.spotify.com/track/16'},
        {'name': 'Blinding Lights', 'artist': 'The Weeknd', 'image': 'https://via.placeholder.com/200?text=Ener2', 'external': 'https://open.spotify.com/track/17'},
        {'name': 'Levitating', 'artist': 'Dua Lipa', 'image': 'https://via.placeholder.com/200?text=Ener3', 'external': 'https://open.spotify.com/track/18'},
        {'name': 'Pump It Up', 'artist': 'Endor', 'image': 'https://via.placeholder.com/200?text=Ener4', 'external': 'https://open.spotify.com/track/19'},
        {'name': 'Can\'t Hold Us', 'artist': 'Macklemore', 'image': 'https://via.placeholder.com/200?text=Ener5', 'external': 'https://open.spotify.com/track/20'},
    ],
    'Relaxing': [
        {'name': 'Weightless', 'artist': 'Marconi Union', 'image': 'https://via.placeholder.com/200?text=Relax1', 'external': 'https://open.spotify.com/track/21'},
        {'name': 'Breathe', 'artist': 'The Prodigy', 'image': 'https://via.placeholder.com/200?text=Relax2', 'external': 'https://open.spotify.com/track/22'},
        {'name': 'Strawberry Swing', 'artist': 'Coldplay', 'image': 'https://via.placeholder.com/200?text=Relax3', 'external': 'https://open.spotify.com/track/23'},
        {'name': 'Clair de Lune', 'artist': 'Claude Debussy', 'image': 'https://via.placeholder.com/200?text=Relax4', 'external': 'https://open.spotify.com/track/24'},
        {'name': 'Sunset', 'artist': 'The Midnight', 'image': 'https://via.placeholder.com/200?text=Relax5', 'external': 'https://open.spotify.com/track/25'},
    ]
}

def get_mock_songs(mood='Happy'):
    """Return mock song data for testing"""
    return MOCK_SONGS.get(mood, MOCK_SONGS['Happy'])[:5]

# Uncomment below to use REAL Spotify (requires valid API credentials)
# SPOTIFY_CLIENT_ID = "your_client_id_here"
# SPOTIFY_CLIENT_SECRET = "your_client_secret_here"
# sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
#     client_id=SPOTIFY_CLIENT_ID,
#     client_secret=SPOTIFY_CLIENT_SECRET
# ))

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

        # Use mock data (comment out to use real Spotify)
        songs = get_mock_songs(selected_mood)
        
        # Uncomment below to use REAL Spotify API
        # results = sp.search(q=query, type='track', limit=5, market="IN")
        # songs = [
        #     {
        #         'name': track['name'],
        #         'artist': track['artists'][0]['name'],
        #         'image': track['album']['images'][0]['url'],
        #         'external': track['external_urls']['spotify']
        #     }
        #     for track in results['tracks']['items']
        # ]

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
