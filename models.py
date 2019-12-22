import datetime
from app import db


# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#

class Show(db.Model):
    __tablename__ = 'show'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'),
                          nullable=False)

    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)

    start_time = db.Column(db.DateTime, nullable=False,
                           default=datetime.datetime.now)

    def __repr__(self):
        return f'Artist ID: {self.artist_id}, Venue ' \
               f'ID:' \
               f' {self.venue_id}, ' \
               f'Start Time: {self.start_time}'

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
    shows = db.relationship('Show', backref='venue', lazy=True)

    def __repr__(self):
        return f'<Venue ID: {self.id}, Name: {self.name}, Location: ' \
               f'{self.city}, {self.state}'

    def add(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def serialize(self):
        past_shows = self.venue_past_shows()
        upcoming_shows = self.venue_upcoming_shows()
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
            'venue_upcoming_shows_count': self.venue_upcoming_shows_count(),
            'venue_upcoming_shows': [{
                'artist_id': show.artist.id,
                'artist_name': show.artist.name,
                'artist_image_link': show.artist.image_link,
                'start_time': show.start_time.strftime("%m-%d-%Y %H:%M")
            } for show in upcoming_shows],
            'venue_past_shows': [{
                'artist_id': show.artist.id,
                'artist_name': show.artist.name,
                'artist_image_link': show.artist.image_link,
                'start_time': show.start_time.strftime("%m-%d-%Y %H:%M")
            } for show in past_shows],
            'venue_past_shows_count': self.venue_past_shows_count()
        }

    def venue_shows(self):
        return Show.query.filter_by(venue_id=self.id).all()

    def venue_upcoming_shows(self):
        return db.session.query(Show).filter(
            Show.start_time > datetime.datetime.now(),
            Show.venue_id == self.id).all()

    def venue_upcoming_shows_count(self):
        return len(self.venue_upcoming_shows())

    def venue_past_shows(self):
        return db.session.query(Show).filter(
            Show.start_time < datetime.datetime.now(),
            Show.venue_id == self.id).all()

    def venue_past_shows_count(self):
        return len(self.venue_past_shows())


class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    is_seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref='artist', lazy=True)

    def __repr__(self):
        return f'<Artist ID: {self.id}, Name: {self.name}>'

    def add(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def serialize(self):
        past_shows = self.artist_past_shows()
        upcoming_shows = self.artist_upcoming_shows()
        return {
            'id': self.id,
            'name': self.name,
            'city': self.city,
            'state': self.state,
            'phone': self.phone,
            'genres': self.genres,
            'image_link': self.image_link,
            'facebook_link': self.facebook_link,
            'website': self.website,
            'is_seeking_venue': self.is_seeking_venue,
            'seeking_description': self.seeking_description,
            'artist_upcoming_shows_count': self.artist_upcoming_shows_count(),
            'artist_upcoming_shows': [{
                'venue_id': show.venue.id,
                'venue_name': show.venue.name,
                'venue_image_link': show.venue.image_link,
                'start_time': show.start_time.strftime("%m-%d-%Y %H:%M")
            } for show in upcoming_shows],
            'artist_past_shows': [{
                'venue_id': show.venue.id,
                'venue_name': show.venue.name,
                'venue_image_link': show.venue.image_link,
                'start_time': show.start_time.strftime("%m-%d-%Y %H:%M")
            } for show in past_shows],
            'artist_past_shows_count': self.artist_past_shows_count()
        }

    def artist_upcoming_shows(self):
        return db.session.query(Show).filter(
            Show.start_time > datetime.datetime.now(),
            Show.artist_id == self.id).all()

    def artist_upcoming_shows_count(self):
        return len(self.artist_upcoming_shows())

    def artist_past_shows(self):
        return db.session.query(Show).filter(
            Show.start_time < datetime.datetime.now(),
            Show.artist_id == self.id).all()

    def artist_past_shows_count(self):
        return len(self.artist_past_shows())
