# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import json
import sys

import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, \
    url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text, func
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


app.jinja_env.filters['datetime'] = format_datetime


# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#

@app.route('/')
def index():
    return render_template('pages/home.html')


# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#

class Show(db.Model):
    __tablename__ = 'show'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'),
                          nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)

    def add(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def serialize(self):
        return {
            'id': self.id,
            'artist_id': self.artist_id,
            'venue_id': self.venue_id,
            'start_time': self.start_time
        }


class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    is_seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))

    def add(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'city': self.city,
            'state': self.state,
            'address': self.address,
            'phone': self.phone,
            'genres': self.genres,
            'image_link': self.image_link,
            'facebook_link': self.facebook_link,
            'website': self.website,
            'is_seeking_talent': self.is_seeking_talent,
            'seeking_description': self.seeking_description,
            'num_upcoming_shows': len(self.venue_upcoming_shows()),
            'upcoming_shows': self.venue_upcoming_shows(),
            'past_shows': self.venue_past_shows()
        }

    def venue_upcoming_shows(self):
        return db.session.query(Show).filter(
            Show.start_time > datetime.now()).filter(
            Show.venue_id == self.id).all()

    def venue_upcoming_shows_count(self):
        return len(self.venue_upcoming_shows())

    def venue_past_shows(self):
        return db.session.query(Show).filter(
            Show.start_time < datetime.now()).filter(
            Show.venue_id == self.id).all()

    def venue_past_shows_count(self):
        return len(self.venue_past_shows())


class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    is_seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))

    def add(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'city': self.city,
            'state': self.state,
            'address': self.address,
            'phone': self.phone,
            'genres': self.genres,
            'image_link': self.image_link,
            'facebook_link': self.facebook_link,
            'website': self.website,
            'is_seeking_venue': self.is_seeking_venue,
            'seeking_description': self.seeking_description,
            'num_upcoming_shows': len(self.artist_upcoming_shows()),
            'upcoming_shows': self.artist_upcoming_shows(),
            'past_shows': self.artist_past_shows()
        }

    def artist_upcoming_shows(self):
        return db.session.query().filter(
            Show.start_time > datetime.now(),
            Show.artist_id == self.id).all()

    def artist_upcoming_shows_count(self):
        return len(self.artist_upcoming_shows())

    def artist_past_shows(self):
        return db.session.query(Show).filter(
            Show.start_time < datetime.now(),
            Show.artist_id == self.id).all()

    def artist_past_shows_count(self):
        return len(self.artist_past_shows())


# ----------------------------------------------------------------------------#
#  Venues
# ----------------------------------------------------------------------------#

@app.route('/venues')
def venues():
    # locations = Venue.query.distinct(Venue.city, Venue.state).all()
    locations = Venue.query.with_entities(
        Venue.city, Venue.state).distinct(Venue.city, Venue.state).all()
    venues = Venue.query.all()
    data = []
    all_venues = []

    # remove duplicates from venues page without using set()
    for location in locations:
        for venue in venues:
            if venue.city == location[0] and venue.state == location[1]:
                all_venues.append({
                    'id': venue.id,
                    'name': venue.name,
                    'num_upcoming_shows': venue.venue_upcoming_shows_count()
                })
        data.append({
            'city': location.city,
            'state': location.state,
            'venues': all_venues
        })

    # for location in locations:
    #     location_venues = Venue.query.filter_by(
    #         state=location.state).filter_by(
    #         city=location.city).all()
    #     venues = []
    #     for venue in location_venues:
    #         venues.append({
    #             "id": venue.id,
    #             "name": venue.name,
    #             "upcoming_shows": venue.venue_upcoming_shows(),
    #             "num_upcoming_shows": venue.venue_upcoming_shows_count()
    #         })
    #         data.append({
    #             "city": venue.city,
    #             "state": venue.state,
    #             "venues": venues
    #         })

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    search_term = request.form.get('search_term', '')
    search_results = Venue.query.filter(Venue.name.ilike
                                        (f'%{search_term}%')).all()

    response = {
        "count": len(search_results),
        "data": [venue for venue in search_results]
    }

    return render_template('pages/search_venues.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    venue = Venue.query.get(venue_id)
    data = venue.serialize()

    return render_template('pages/show_venue.html', venue=data)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    venue_form = VenueForm(request.form)

    try:
        new_venue = Venue(
            name=venue_form.name.data,
            city=venue_form.city.data,
            state=venue_form.state.data,
            address=venue_form.address.data,
            phone=venue_form.phone.data,
            genres=venue_form.genres.data,
            image_link=venue_form.image_link.data,
            facebook_link=venue_form.facebook_link.data,
            website=venue_form.website.data,
            is_seeking_talent=venue_form.is_seeking_talent.data,
            seeking_description=venue_form.seeking_description.data
        )

        Venue.add(new_venue)
        flash("Venue '" + request.form['name'] + "' was successfully listed!")
    except:
        db.session.rollback()
        flash("Error! Venue '" + request.form['name'] + "' was NOT listed!")
    finally:
        db.session.close()

    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    try:
        venue_to_delete = Venue.query.get(venue_id)
        Venue.delete(venue_to_delete)
        flash('Venue successfully deleted!')
    except:
        db.session.rollback()
        flash('Error! This venue could not be deleted.')
    finally:
        db.session.close()

    return redirect(url_for('index'))


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    data = [{
        "id": 4,
        "name": "Guns N Petals",
    }, {
        "id": 5,
        "name": "Matt Quevedo",
    }, {
        "id": 6,
        "name": "The Wild Sax Band",
    }]
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it
    #  is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The
    # Wild Sax Band". search for "band" should return "The Wild Sax Band".
    response = {
        "count": 1,
        "data": [{
            "id": 4,
            "name": "Guns N Petals",
            "num_upcoming_shows": 0,
        }]
    }
    return render_template('pages/search_artists.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    data1 = {
        # fill this in
    }

    data2 = {
        # fill this in
    }

    data3 = {
        # fill this in
    }

    data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[
        0]
    return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = {
        # fill this in
    }
    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    data = Venue.query.get(venue_id)
    form = VenueForm(obj=data)
    return render_template('forms/edit_venue.html', form=form, venue=data)

    # form = VenueForm()
    # venue = Venue.query.filter_by(id=venue_id).first()
    #
    # form.name.data = venue.name
    # form.city.data = venue.city
    # form.state.data = venue.state
    # form.address.data = venue.address
    # form.phone.data = venue.phone
    # form.genres.data = venue.genres
    # form.image_link.data = venue.image_link
    # form.facebook_link.data = venue.facebook_link
    # form.website.data = venue.website
    # form.is_seeking_talent.data = venue.is_seeking_talent
    # form.seeking_description.data = venue.seeking_description
    #
    # return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    form = VenueForm(request.form)

    try:
        venue = Venue.query.filter_by(id=venue_id).first()
        venue.name = form.name.data
        venue.city = form.city.data
        venue.state = form.state.data
        venue.address = form.address.data
        venue.phone = form.phone.data
        venue.genres = form.genres.data
        venue.image_link = form.image_link.data
        venue.facebook_link = form.facebook_link.data
        venue.website = form.website.data
        venue.is_seeking_talent = form.is_seeking_talent.data
        venue.seeking_description = form.seeking_description.data

        db.session.commit()
        print('success maybe')
    except Exception as e:
        print(e)
        db.session.rollback()
        print('failure maybe')
    finally:
        db.session.close()

    return redirect(url_for('show_venue', venue_id=venue_id))


# ----------------------------------------------------------------------------#
#  Create Artist
# ----------------------------------------------------------------------------#

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion

    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be
    # listed.')
    return render_template('pages/home.html')


# ----------------------------------------------------------------------------#
#  Shows
# ----------------------------------------------------------------------------#

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows
    #       per venue.
    data = []
    # fill this in
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead

    # on successful db insert, flash success
    flash('Show was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')


# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
