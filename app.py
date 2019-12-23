# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#
import dateutil.parser
import babel
import logging

from flask import Flask, render_template, request, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from logging import Formatter, FileHandler
from sqlalchemy.exc import IntegrityError
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
# Models
# ----------------------------------------------------------------------------#

from models import *


# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime


# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#

@app.route('/')
def index():
    return render_template('pages/home.html')


# ----------------------------------------------------------------------------#
#  Venues
# ----------------------------------------------------------------------------#

@app.route('/venues')
def venues():
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

        # empty the list after we're done iterating over it or venues screen
        # will have duplicates
        all_venues = []

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


# ----------------------------------------------------------------------------#
#  Create Venue
# ----------------------------------------------------------------------------#

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


# ----------------------------------------------------------------------------#
#  Artists
# ----------------------------------------------------------------------------#
@app.route('/artists')
def artists():
    artists = Artist.query.all()
    data = []

    for artist in artists:
        data.append({
            'id': artist.id,
            'name': artist.name
        })

    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    search_term = request.form.get('search_term', '')
    search_results = Artist.query.filter(Artist.name.ilike
                                         (f'%{search_term}%')).all()
    response = {
        "count": len(search_results),
        "data": [artist for artist in search_results]
    }

    return render_template('pages/search_artists.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    artist = Artist.query.get(artist_id)
    data = artist.serialize()

    return render_template('pages/show_artist.html', artist=data)


# ----------------------------------------------------------------------------#
#  Update
# ----------------------------------------------------------------------------#
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    data = Artist.query.get(artist_id)
    form = ArtistForm(obj=data)

    return render_template('forms/edit_artist.html', form=form, artist=data)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    form = ArtistForm(request.form)

    try:
        artist = Artist.query.filter_by(id=artist_id).first()
        artist.name = form.name.data
        artist.city = form.city.data
        artist.state = form.state.data
        artist.phone = form.phone.data
        artist.genres = form.genres.data
        artist.image_link = form.image_link.data
        artist.facebook_link = form.facebook_link.data
        artist.website = form.website.data
        artist.is_seeking_venue = form.is_seeking_venue.data
        artist.seeking_description = form.seeking_description.data

        db.session.commit()
        flash(f"The artist '{artist.name}' has been successfully updated!")
    except Exception as e:
        db.session.rollback()
        flash(f"Error! The artist '{artist.name}' was not updated!")
    finally:
        db.session.close()

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    data = Venue.query.get(venue_id)
    form = VenueForm(obj=data)

    return render_template('forms/edit_venue.html', form=form, venue=data)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
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
        flash(f"The venue '{venue.name}' has been successfully updated!")
    except Exception as e:
        db.session.rollback()
        flash(f"Error! The venue '{venue.name}' was not updated!")
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
    artist_form = ArtistForm(request.form)

    try:
        new_artist = Artist(
            name=artist_form.name.data,
            city=artist_form.city.data,
            state=artist_form.state.data,
            phone=artist_form.phone.data,
            genres=artist_form.genres.data,
            image_link=artist_form.image_link.data,
            facebook_link=artist_form.facebook_link.data,
            website=artist_form.website.data,
            is_seeking_venue=artist_form.is_seeking_venue.data,
            seeking_description=artist_form.seeking_description.data
        )

        Artist.add(new_artist)
        flash("Artist '" + request.form['name'] + "' was successfully listed!")
    except:
        db.session.rollback()
        flash("Error! Artist '" + request.form['name'] + "' was NOT listed!")
    finally:
        db.session.close()

    return render_template('pages/home.html')


@app.route('/artists/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
    try:
        artist_to_delete = Artist.query.get(artist_id)
        Artist.delete(artist_to_delete)
        flash('Artist successfully deleted!')
    except:
        db.session.rollback()
        flash('Error! This artist could not be deleted.')
    finally:
        db.session.close()

    return redirect(url_for('index'))


# ----------------------------------------------------------------------------#
#  Shows
# ----------------------------------------------------------------------------#

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows
    #       per venue.
    shows = Show.query.all()
    data = []

    for show in shows:
        artist = Artist.query.get(show.artist_id)
        venue = Venue.query.get(show.venue_id)
        data.append({
            'show_id': show.id,
            'artist_id': artist.id,
            'artist_name': artist.name,
            'venue_id': venue.id,
            'venue_name': venue.name,
            'artist_image_link': artist.image_link,
            'start_time': show.start_time.strftime("%m-%d-%Y %H:%M")
        })

    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    show_form = ShowForm(request.form)

    try:
        new_show = Show(
            artist_id=show_form.artist_id.data,
            venue_id=show_form.venue_id.data,
            start_time=show_form.start_time.data
        )

        Show.add(new_show)
        flash("The show was successfully listed!")
    except IntegrityError:
        db.session.rollback()
        flash("Error! The show could not be listed because that venue or "
          "artist doesn't exist!")
    except:
        db.session.rollback()
        flash("Error! That show could not be listed!")
    finally:
        db.session.close()

    return render_template('pages/home.html')


# ----------------------------------------------------------------------------#
# Error handlers
# ----------------------------------------------------------------------------#

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
