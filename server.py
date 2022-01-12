import json
from datetime import datetime
from pprint import pprint

from flask import Flask, render_template, request\
    , redirect, flash, url_for


TODAY = datetime.now()


def load_clubs():
    with open('clubs.json') as c:
        list_of_clubs = json.load(c)['clubs']
        return list_of_clubs


def load_competitions():
    with open('competitions.json') as comps:
        list_of_competitions = json.load(comps)['competitions']
        """ Check if each competition is over """
        for competition in list_of_competitions:
            competition_date = datetime.strptime(competition['date'], "%Y-%m-%d %H:%M:%S")
            if competition_date < TODAY:
                competition["over"] = True
            else:
                competition["over"] = False
        return list_of_competitions


app = Flask(__name__)
app.secret_key = 'something_special'

competitions = load_competitions()
clubs = load_clubs()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/showSummary', methods=['POST'])
def show_summary():
    try:
        club = [club for club in clubs if club['email'] == request.form['email']][0]
    except IndexError:
        flash("Sorry, that email wasn't found.")
        return redirect(url_for('index'), 401), 301
    return render_template('welcome.html', club=club, competitions=competitions)


@app.route('/book/<competition>/<club>')
def book(competition,club):
    found_club = [c for c in clubs if c['name'] == club][0]
    found_competition = [c for c in competitions if c['name'] == competition][0]
    if found_club and not found_competition["over"]:
        return render_template('booking.html', club=found_club, competition=found_competition)
    else:
        flash("Something went wrong-please try again")
        return render_template('welcome.html', club=club, competitions=competitions), 404


@app.route('/purchasePlaces', methods=['POST'])
def purchase_places():
    competition = [c for c in competitions if c['name'] == request.form['competition']][0]
    club = [c for c in clubs if c['name'] == request.form['club']][0]
    places_required = int(request.form['places'])
    competition['numberOfPlaces'] = int(competition['numberOfPlaces'])-places_required
    flash('Great-booking complete!')
    return render_template('welcome.html', club=club, competitions=competitions)


# TODO: Add route for points display


@app.route('/logout')
def logout():
    return redirect(url_for('index'))
