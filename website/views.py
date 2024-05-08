from flask import Blueprint, render_template, redirect, request, url_for
from flask_login import login_user, login_required, logout_user, current_user
from flask_paginate import Pagination
from .models import User, Discussion, Message, Review
from website.forms import CreateDiscussionForm
from . import db
import os
import pandas as pd
import ast
import altair as alt
from altair import Scale
from altair_saver import save
import altair_viewer
import re
import json
import numpy as np

views = Blueprint('views', __name__)

anime_data = pd.read_csv('./website/static/data/anime.csv')
data = pd.read_csv('./website/static/data/cleaned-anime.csv')

anime_data['start_year'] = anime_data['start_year'].fillna(0)
anime_data['start_year'] = anime_data['start_year'].astype(str)
anime_data['synopsis'] = anime_data['synopsis'].str.replace('[Written by MAL Rewrite]', '')

titles = data['title'].to_list()
json_path = './website/static/data/titles.json'
with open(json_path, 'w') as json_file:
    json.dump(titles, json_file)

@views.route('/')
def home():
    top_anime_data = pd.read_csv('./website/static/data/top_anime.csv')
    top_anime = top_anime_data.head(5).to_dict('records')
    return render_template('base.html', top_anime = top_anime)

@views.route('/music')
def music():
    musics = pd.read_csv('./website/static/data/music_list.csv').to_dict('records')
    return render_template('music.html', musics=musics)

@views.route('/events', methods=['GET', 'POST'])
def events():
    events = pd.read_csv('./website/static/data/event.csv').head(5).to_dict('records')
    if request.method == 'POST':
        from .web_crawling import get_event
        location = request.form.get('location')
        get_event(location=location)
        events_data = pd.read_csv('./website/static/data/event.csv')
        events = events_data.head(5).to_dict('records')

    return render_template('events.html', events=events)



# Find all unique genres
anime_data['genres'] = anime_data['genres'].apply(ast.literal_eval)
unique_genres = set(genre for genres_list in anime_data['genres'] for genre in genres_list)
unique_genres_list = list(unique_genres)

# Find all unique years
cleaned_years = [year for year in anime_data['start_year']]
unique_years = set(cleaned_years)
unique_years_list = list(unique_years)
unique_years_list = [int(float(year)) for year in unique_years_list if int(float(year)) != 0]
unique_years_list.sort()

PER_PAGE = 20

def get_anime_data(page=1, search_query='', selected_genre='', selected_year=''):
    start_idx = (page - 1) * PER_PAGE
    end_idx = start_idx + PER_PAGE
    filtered_data = anime_data
    if search_query:
        filtered_data = filtered_data[filtered_data['title'].str.contains(search_query, case=False)]
    if selected_genre:
        filtered_data = filtered_data[filtered_data['genres'].apply(lambda genres: selected_genre in genres)]
    if selected_year:
        filtered_data = filtered_data[filtered_data['start_year'].apply(lambda years: selected_year in years)]

    return filtered_data.iloc[start_idx:end_idx]

@views.route('/anime_list', methods=['GET'])
def anime_list():
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('search', '', type=str)
    selected_genre = request.args.get('genre', '', type=str)
    selected_year = request.args.get('year', '', type=str)
    anime_subset = get_anime_data(page, search_query, selected_genre, selected_year)
    total_pages = (len(anime_data) + PER_PAGE - 1) // PER_PAGE
    pages_to_display = 5
    start_page = max(1, min(page, total_pages - pages_to_display + 1))
    end_page = min(start_page + pages_to_display - 1, total_pages)
    display_range = range(start_page, end_page + 1)

    return render_template('anime_list.html', anime_data=anime_subset.to_dict(orient='records'),
                           page=page, total_pages=total_pages, display_range=display_range,
                           search_query=search_query, selected_genre=selected_genre,
                           unique_genres_list=unique_genres_list, unique_years_list=unique_years_list)

def get_anime_details(anime_id):
    anime = anime_data.loc[anime_data['anime_id'] == anime_id].squeeze()
    if anime.empty:
        return None
    return anime

@views.route('/anime_details/<int:anime_id>', methods=['GET'])
def anime_details(anime_id):
    anime = get_anime_details(anime_id)
    if anime is None:
        return render_template('errors/404.html')
    reviews = Review.query.filter_by(anime_title=anime.title).all()
    return render_template('anime_details.html', anime=anime, reviews=reviews, User=User)

@views.route('/leave_review/<int:anime_id>', methods=['POST'])
@login_required
def leave_review(anime_id):
    review_text = request.form.get('review')
    anime = get_anime_details(anime_id)

    if anime is None:
        return redirect(url_for('views.anime_details', anime_id=anime_id))

    new_review = Review(user_id=current_user.id, anime_title=anime.title, text=review_text)
    db.session.add(new_review)
    db.session.commit()

    return redirect(url_for('views.anime_details', anime_id=anime_id))

@views.route('/leave_review/<int:review_id>/delete_review', methods=['POST'])
@login_required
def delete_review(review_id):
    review = Review.query.get_or_404(review_id)

    if current_user.role == 'admin' or current_user.id == review.user_id:
        db.session.delete(review)
        db.session.commit()

    return redirect(url_for('views.anime_list'))


@views.route('/discussion')
def discussion():
    discussions = Discussion.query.all()
    return render_template('discussion.html', discussions=discussions)

@views.route('/discussion/<int:discussion_id>')
def view_discussion(discussion_id):
    discussion = Discussion.query.get_or_404(discussion_id)
    messages = discussion.messages
    return render_template('view_discussion.html', discussion=discussion, messages=messages)

@views.route('/create_discussion', methods=['GET', 'POST'])
@login_required
def create_discussion():
    form = CreateDiscussionForm()

    if form.validate_on_submit():
        new_discussion = Discussion(title=form.title.data, user_id=current_user.id)
        db.session.add(new_discussion)
        db.session.commit()

        new_message = Message(text=form.content.data, user_id=current_user.id, discussion_id=new_discussion.id)
        db.session.add(new_message)
        db.session.commit()

        return redirect(url_for('views.discussion'))

    return render_template('create_discussion.html', form=form)

@views.route('/discussion/<int:discussion_id>/submit_message', methods=['POST'])
@login_required
def submit_message(discussion_id):
    discussion = Discussion.query.get_or_404(discussion_id)

    if request.method == 'POST':
        text = request.form.get('message')
        if text:
            new_message = Message(text=text, user_id=current_user.id, discussion_id=discussion.id)
            db.session.add(new_message)
            db.session.commit()

    return redirect(url_for('views.view_discussion', discussion_id=discussion.id))


@views.route('/discussion/<int:discussion_id>/delete_message/<int:message_id>', methods=['POST'])
@login_required
def delete_message(discussion_id, message_id):
    discussion = Discussion.query.get_or_404(discussion_id)
    message = Message.query.get_or_404(message_id)

    # Check if the current user has permission to delete the message
    if current_user.is_authenticated and (current_user.role == 'admin' or current_user.id == message.user_id):
        db.session.delete(message)
        db.session.commit()

    return redirect(url_for('views.view_discussion', discussion_id=discussion.id))

@views.route('/discussion/<int:discussion_id>/delete_discussion', methods=['POST'])
@login_required
def delete_discussion(discussion_id):
    discussion = Discussion.query.get_or_404(discussion_id)

    if current_user.role == 'admin' or current_user.id == discussion.user_id:
        Message.query.filter_by(discussion_id=discussion_id).delete()
        db.session.delete(discussion)
        db.session.commit()

    return redirect(url_for('views.discussion'))

@views.route('/analysis')
def analysis():

    df = pd.read_csv('./website/static/data/anime.csv')
    df = df.head(5000)

    average_scores_df = df.groupby('start_year')['score'].mean().reset_index()

    chart_1 = alt.Chart(average_scores_df).mark_bar(clip=True).encode(
        x=alt.X('start_year:O', title='Start Year'),
        y=alt.Y('score:Q', title='Average Score', scale=Scale(domain=[6, 9])),
        tooltip=['start_year:O', 'score:Q'],
        color=alt.Color('start_year:O', legend=None)
    ).properties(width=1200, height=400, title='Average score by year')

    top_10 = df.nlargest(10, 'score')

    last_10 = df.nsmallest(10, 'score')

    chart_2 = alt.Chart(top_10).mark_bar(clip=True).encode(
        x=alt.X('title', sort=None, axis=alt.Axis(labelAngle=45, labelLimit=20)),
        y=alt.Y('score', scale=Scale(domain=[9, 10])),
        tooltip=['title', 'score'],
    ).properties(width=550, height=300, title='Top 10 popular anime')

    chart_3 = alt.Chart(last_10).mark_bar().encode(
        x=alt.X('title', sort=None, axis=alt.Axis(labelAngle=45, labelLimit=20)),
        y=alt.Y('score', scale=Scale(domain=[0, 10])),
        tooltip=['title', 'score'],
    ).properties(width=550, height=300, title='10 least popular anime')

    chart_2_3 = alt.hconcat(chart_2, chart_3)

    df_sorted = df.sort_values(by=['start_year', 'score'], ascending=[True, False])
    df_highest_score_per_year = df_sorted.groupby('start_year').first().reset_index()

    chart_4 = alt.Chart(df_highest_score_per_year).mark_line(point=True).encode(
        x='start_year:N',
        y=alt.Y('score:Q', scale=Scale(domain=[7, 10])),
        tooltip=['start_year:N', 'title:N', 'score:Q']
    ).properties(width=1200, height=400, title='Highest Scoring Anime per Year')

    def parse_genres(genre_string):
        genres = re.findall(r"'(.*?)'", genre_string)
        return genres

    df['genres'] = df['genres'].apply(parse_genres)

    df['genres'] = df['genres'].apply(lambda x: [genre.strip() for genre in x])
    tidy_df = df.explode('genres')

    average_scores = tidy_df.groupby('genres')['score'].mean().reset_index()

    chart_5 = alt.Chart(average_scores).mark_bar(clip=True).encode(
        x=alt.X('genres:N'),
        y=alt.Y('score:Q', scale=Scale(domain=[6, 8])),
        tooltip=['genres:N', 'score:Q']
    ).properties(width=1200, height=400, title='Average Score by Genre')

    save(chart_1, './website/templates/charts/chart_1.html')
    save(chart_2_3, './website/templates/charts/chart_2_3.html')
    save(chart_4, './website/templates/charts/chart_4.html')
    save(chart_5, './website/templates/charts/chart_5.html')


    return render_template('analysis.html', chart_1=chart_1.to_json(), chart_4=chart_4.to_json(), chart_2_3=chart_2_3.to_json(), chart_5=chart_5.to_json())


@views.route('/recommend_name', methods=['GET', 'POST'])
def recommend_name():
    anime_names = data['title']
    selected = None
    selected_anime = None
    recommend_anime_list = []

    if request.method == 'POST':
        from .machine_learning import recommend
        
        selected_anime_name = request.form.get('selected_anime')
        selected = f"You selected: {selected_anime_name}"

        selected_anime = anime_data[anime_data['title'] == selected_anime_name].squeeze()

        recommend_anime_list = recommend(selected_anime_name)

    return render_template('recommend_name.html', anime_names=anime_names, selected=selected, selected_anime=selected_anime, recommend_anime_list=recommend_anime_list)