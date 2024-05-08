from flask_login import current_user, login_user, logout_user
from flask import render_template_string
from website.models import db, User
from website.views import get_anime_data, get_anime_details
from website.machine_learning import stem, recommend
import pandas as pd
from conftest import app
import random

data = pd.read_csv('./website/static/data/anime.csv')
size = len(data)
def get_random_id():
    i = random.randint(0, size)
    if i in data['anime_id'].values:
        return i
    else:
        return get_random_id()
random_id = get_random_id()
non_exist_id = ''
max_id = data['anime_id'].max()
for i in range(1, 99999999):
    if i not in data['anime_id'].values:
        non_exist_id = i
        break

# Without Authorisation
def test_home_page(client):
    response = client.get('/')
    assert response.status_code == 200

def test_music_page(client):
    response = client.get('/music')
    assert response.status_code == 200

def test_event_page(client):
    response = client.get('/events')
    assert response.status_code == 200

def test_events_post(client, monkeypatch):
    def mock_get_event(location):
        pass 
    monkeypatch.setattr('website.views.events', mock_get_event)
    form_data = {'location': 'Japan'} 
    response = client.post('/events', data=form_data, follow_redirects=True)
    assert response.status_code == 200

def test_anime_list_page(client):
    response = client.get('/anime_list')
    assert response.status_code == 200

def test_anime_details_page(client):
    anime_id = data['anime_id'].iloc[random_id]
    response = client.get(f'/anime_details/{anime_id}')
    assert response.status_code == 200

def test_anime_details_nonexistent_anime(client):
    response = client.get(f'/anime_details/{non_exist_id}')
    assert b'Error' in response.data

def test_discussion_page(client):
    response = client.get('/discussion')
    assert response.status_code == 200

def test_recommend_name_page(client):
    response = client.get('/recommend_name')
    assert response.status_code == 200

def test_analysis_page(client):
    response = client.get('/analysis')
    assert response.status_code == 200

def test_sign_up_page(client):
    response = client.get('/sign-up')
    assert response.status_code == 200

# With authorisation
def test_login_page(client):
    test_user = User(role='user', username='testuser', email='testuser@email.com', password='password', profile_picture='default.jpg')
    db.session.add(test_user)
    db.session.commit()

    response = client.post('/login', data={'email': 'testuser@example.com', 'password': 'password'}, follow_redirects=True)
    assert response.status_code == 200

    db.session.delete(test_user)
    db.session.commit()

def test_logout_page(client):
    test_user = User(role='user', username='testuser', email='testuser@email.com', password='password', profile_picture='default.jpg')
    db.session.add(test_user)
    db.session.commit()

    client.post('/login', data={'email': 'testuser@example.com', 'password': 'password'}, follow_redirects=True)
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200

    db.session.delete(test_user)
    db.session.commit()

def test_profile_page(client):
    test_user = User(role='user', username='testuser', email='testuser@email.com', password='password', profile_picture='default.jpg')
    db.session.add(test_user)
    db.session.commit()
    client.post('/login', data={'email': 'testuser@example.com', 'password': 'password'}, follow_redirects=True)
    response = client.get('/profile', follow_redirects=True)
    assert response.status_code == 200

    db.session.delete(test_user)
    db.session.commit()

def test_update_info_page(client):
    test_user = User(role='user', username='testuser', email='testuser@email.com', password='password', profile_picture='default.jpg')
    db.session.add(test_user)
    db.session.commit()
    client.post('/login', data={'email': 'testuser@example.com', 'password': 'password'}, follow_redirects=True)
    response = client.get('/update-info', follow_redirects=True)
    assert response.status_code == 200

    db.session.delete(test_user)
    db.session.commit()

def test_admin_page(client):
    test_user = User(role='admin', username='testadmin', email='testadmin@email.com', password='password', profile_picture='default.jpg')
    db.session.add(test_user)
    db.session.commit()
    client.post('/login', data={'email': 'testadmin@example.com', 'password': 'password'}, follow_redirects=True)
    response = client.get('/admin', follow_redirects=True)
    assert response.status_code == 200

    db.session.delete(test_user)
    db.session.commit()

def test_delete_user(client):
    admin_user = User.query.filter_by(role='admin').first()
    with client.application.test_request_context():
        login_user(admin_user)
        user_to_delete = User(role='user', username='user_to_delete', email='delete@example.com', password='password', profile_picture='default.jpg')
        db.session.add(user_to_delete)
        db.session.commit()
        response = client.post(f'/admin/{user_to_delete.id}/delete_user', follow_redirects=True)
        assert User.query.get(user_to_delete.id) is None
        assert response.status_code == 200
        logout_user()

# Test error pages
        
def test_bad_request_error_handler(client):
    response_400 = client.get('/error/400')
    assert response_400.status_code == 400

def test_forbidden_error_handler(client):
    response_403 = client.get('/error/403')
    assert response_403.status_code == 403

def test_not_found_error_handler(client):
    response = client.get('/random-page')
    assert response.status_code == 404
    
def test_internal_server_error_handler(client):
    response_500 = client.get('/error/500')
    assert response_500.status_code == 500

def test_service_unavilable_error_handler(client):
    response_503 = client.get('/error/503')
    assert response_503.status_code == 503

def test_anime_data_empty():
    data = get_anime_data()
    assert not data.empty

def test_get_anime_data_with_search_query():
    anime_title = data['title'].iloc[random_id]
    got_data = get_anime_data(search_query=anime_title)
    assert anime_title in got_data['title'].values

def test_get_anime_data_with_genre_filter():
    data = get_anime_data(selected_genre='Action')
    assert all('Action' in genres for genres in data['genres'])

def test_get_anime_data_with_year_filter():
    data = get_anime_data(selected_year='2023')
    years = [int(float(year)) for year in data['start_year']]
    assert all(year == 2023 for year in years)

def test_get_anime_details():
    data = pd.read_csv('./website/static/data/anime.csv')
    anime_id = data['anime_id'].iloc[random_id]
    anime_details = get_anime_details(anime_id)
    false_id = non_exist_id
    false_anime_details = get_anime_details(false_id)
    assert anime_details is not None
    assert false_anime_details is None

def test_stem():
    text = 'programming programs programmed'
    expected_result = 'program program program'
    assert stem(text) == expected_result

def test_recommender():
    data = pd.read_csv('./website/static/data/anime.csv')
    anime_title = data['title'].iloc[0]
    expected_length = 5
    recommended_anime = recommend(anime_title)
    assert len(recommended_anime) == expected_length

def test_jinja_max_filter(app):
    with app.test_request_context():
        rendered = render_template_string("{{ 5|jinja_max(3) }}")
        assert rendered.strip() == "5"
