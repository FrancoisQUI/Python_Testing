import json
from datetime import datetime
from pprint import pprint

from flask import Flask, render_template, request \
    , redirect, flash, url_for

TODAY = datetime.now()
MAX_PLACE_PER_CLUB = 12


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
def book(competition, club):
    found_club = [c for c in clubs if c['name'] == club][0]
    found_competition = [c for c in competitions if c['name'] == competition][0]
    if found_club and not found_competition["over"]:
        # define the max places can be purchased
        if found_club["points"] > found_competition["placeValue"] * MAX_PLACE_PER_CLUB:
            # test if club can take the allowed max places
            # if it can : max place is the minor between competition's number of place
            # and allowed max place per clun
            if found_competition["numberOfPlaces"] > MAX_PLACE_PER_CLUB:
                max_places = MAX_PLACE_PER_CLUB
            else:
                max_places = found_competition["numberOfPlaces"]
        else:
            # if not :  max place is the maximum place than the club
            # can purchase with the amount of points
            max_places = found_club["points"] / found_competition["placeValue"]
        return render_template('booking.html',
                               club=found_club,
                               competition=found_competition,
                               max_places=max_places)
    else:
        flash("Something went wrong-please try again")
        return render_template('welcome.html',
                               club=club,
                               competitions=competitions), 403


@app.route('/purchasePlaces', methods=['POST'])
def purchase_places():
    competition = [c for c in competitions if c['name'] == request.form['competition']][0]
    club = [c for c in clubs if c['name'] == request.form['club']][0]
    places_required = int(request.form['places'])
    if places_required <= club["points"] * competition["placeValue"] and \
            places_required <= competition["numberOfPlaces"]:
        # and \
        # places_required <= MAX_PLACE_PER_CLUB:
        competition['numberOfPlaces'] = int(competition['numberOfPlaces']) - places_required
        flash('Great-booking complete!')
    elif places_required > club["points"] * competition["placeValue"]:
        flash("Not enough points")
        return render_template('welcome.html', club=club, competitions=competitions), 403
    elif places_required > competition["numberOfPlaces"]:
        flash("Not enough place for this competition")
        return render_template('welcome.html', club=club, competitions=competitions), 403
    # elif places_required > MAX_PLACE_PER_CLUB:
    #     flash(f"Only {MAX_PLACE_PER_CLUB} places per club allowed")

    return render_template('welcome.html', club=club, competitions=competitions), 200


# TODO: Add route for points display


@app.route('/logout')
def logout():
    return redirect(url_for('index'))
