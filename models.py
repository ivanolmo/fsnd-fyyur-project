from app import db
import datetime


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

    def update(self):
        db.session.update(self)
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
    genres = db.Column(db.ARRAY(db.String()))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    is_seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    upcoming_shows = db.relationship('Show', backref='venue', lazy=True)

    def add(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.update(self)
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
            Show.start_time > datetime.datetime.now()).filter(
            Show.venue_id == self.id).all()

    def venue_upcoming_shows_count(self):
        return len(self.venue_upcoming_shows())

    def venue_past_shows(self):
        return db.session.query(Show).filter(
            Show.start_time < datetime.datetime.now()).filter(
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
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    is_seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    upcoming_shows = db.relationship('Show', backref='artist', lazy=True)

    def add(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.update(self)
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
