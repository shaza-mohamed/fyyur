#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
#import flask_whooshalchemy as wa
from flask_migrate import Migrate
from datetime import datetime
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from sqlalchemy import func
from sqlalchemy import and_


#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)
# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_description = db.Column(db.String(300))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    seeking_talent = db.Column(db.Boolean, default=False)
    genres = db.Column(db.String(120))
    website = db.Column(db.String(120))
    #Artists = db.relationship('Artist', secondary=show, backref=db.backref('Artist', lazy=True))
    shows = db.relationship('Show', backref=db.backref("venue_show", uselist=False), lazy='dynamic') 

      


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_description = db.Column(db.String(300))
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    shows = db.relationship('Show', backref=db.backref("artist_show", uselist=False), lazy='dynamic') 


class Show(db.Model):
    __tablename__ = 'Show'
    id = db.Column(db.Integer, primary_key=True)
    #name = db.Column(db.String)
    start_time = db.Column(db.DateTime, nullable=False )

    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)






# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():

     
  cities = Venue.query.with_entities(Venue.city,Venue.state).group_by(Venue.city,Venue.state).all()
    #cities = Venue.query.with_entities(Venue.city,Venue.state).order_by(id).all()
  data_dic_org={"city":None,"state":None,"venues":[]}
  venue_dic_org={"id":0,"name":None,"num_upcoming_shows":0}
  data=[]
  cities=set(cities)
  for c in cities :
    data_dic=data_dic_org.copy()
    data_dic["city"]=c.city
    data_dic["state"]=c.state
    #data_dic["id"]=c.id

    venue_per_city=Venue.query.filter_by( city=c.city,state=c.state).all()
    data_dic["venues"]=[x for x in range (len(venue_per_city))]
    i=0
    for v in venue_per_city:
      
      venue_dic=venue_dic_org.copy()
      venue_dic["id"]=v.id
      venue_dic["name"]=v.name
      venue_dic["num_upcoming_shows"]=v.shows
      data_dic["venues"][i]=venue_dic
      i+=1
    data.append(data_dic)
    
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term=request.form.get('search_term','').lower()
  print(search_term)
  venue= Venue.query.filter(func.lower(Venue.name).contains(func.concat('%',search_term,'%'))).all()
  data_dic={"id":0,"name":0,"num_upcoming_shows":0}
  data=[]
  #show = Show.query.all()
  Now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  start_time= Show.query.with_entities(Show.start_time).all()
  for v in venue:
        data_dic["id"]=v.id
        data_dic["name"]=v.name
        data_dic["num_upcoming_shows"]=Show.query.filter_by(venue_id=v.id).filter( str(start_time) > Now).count()
        #data_dic["num_upcoming_shows"]= V.upcoming_shows_count = db.session.query(Venue).join(Show, Show.venue_id == V.id).filter( Show.start_time > now).count()
        data.append(data_dic)
  response = { "count": len(venue),"data": data }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))



@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  i = Venue.query.filter_by(id=venue_id).first()
  data_dic={"id":0,"name":0,"genres":[], "address":0, "city":0,"state":0,
   "phone":0, "website":0,"facebook_link":0,
  "seeking_talent":0,"seeking_description":0, "image_link":0,
   "past_shows":[], "upcoming_shows": [],"past_shows_count":0,"upcoming_shows_count":0 }  
  shows_dic_org={"artist_id":0,"artist_name":0,"artist_image_link": 0,"start_time": 0}
  
  now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  
  
  data_dic["id"]=i.id
  data_dic["name"]=i.name
  data_dic["genres"]=i.genres.split(",")
  data_dic["address"]=i.address
  data_dic["city"]=i.city
  data_dic["state"]=i.state
  data_dic["phone"]=i.phone
  data_dic["website"]=i.website
  data_dic["facebook_link"]=i.facebook_link
  data_dic["seeking_talent"]=i.seeking_talent
  data_dic["seeking_description"]=i.seeking_description
  data_dic["image_link"]=i.image_link
   
  past_shows=Show.query.filter(Show.venue_id==i.id).filter(Show.start_time < now).all()
  upcoming_shows=Show.query.filter(Show.venue_id==i.id).filter(Show.start_time >= now).all()

  for p in past_shows:
    shows_dic=shows_dic_org.copy()
    artists=Artist.query.filter_by(id=p.artist_id).first()
    shows_dic["artist_id"]= artists.id
    shows_dic["artist_name"]= artists.name
    shows_dic["artist_image_link"]= artists.image_link
    shows_dic["start_time"]= str(p.start_time)
    data_dic["past_shows"].append(shows_dic)

  for u in upcoming_shows:
    shows_dic=shows_dic_org.copy()
    artists=Artist.query.filter_by(id=u.artist_id).first()
    shows_dic["artist_id"]= artists.id
    shows_dic["artist_name"]= artists.name
    shows_dic["artist_image_link"]= artists.image_link
    shows_dic["start_time"]= str(u.start_time) 
    data_dic["upcoming_shows"].append(shows_dic)

    
  data_dic['past_shows_count']=len(past_shows)
  data_dic['upcoming_shows_count']=len(upcoming_shows)

  data=data_dic
  #shutdown_session()
  return render_template('pages/show_venue.html', venue=data)
#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
      
  venue = Venue(
  name = request.form['name'],
  city = request.form['city'],
  state = request.form['state'],
  phone = request.form['phone'],
  genres = ','.join(request.form.getlist('genres')),
  facebook_link = request.form['facebook_link']
  )


  try:
    db.session.add(venue)
    db.session.commit()     
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()  

    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()
  
  return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()    
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():    
  ids = Artist.query.order_by(Artist.id).all() 
  data=[]
  data_dic_org={"id":0,"name":0 }
  for i in ids:
    data_dic=data_dic_org.copy()  
    data_dic["id"]=i.id  
    data_dic["name"]=i.name
    data.append(data_dic)
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  term = request.form.get('search_term')
  search = "%{}%".format(term.lower())  

  res = Artist.query.filter(Artist.name.ilike(search)).all()

  data_dic={"id":0,"name":0,"num_upcoming_shows":0}
  data=[]
  Now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

  start_time= Show.query.with_entities(Show.start_time).all()

  for r in res:
        data_dic["id"]=r.id
        data_dic["name"]=r.name
        data_dic["num_upcoming_shows"]=Show.query.filter_by(artist_id=r.id).filter( str(start_time) > Now).count()
        data.append(data_dic)

  response = { "count": len(res),"data": data }

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))



@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  i = Artist.query.filter_by(id=artist_id).first()

  data_dic={"id":0,"name":0,"genres":[], "city":0,"state":0,
   "phone":0, "website":0,"facebook_link":0,
  "seeking_venue":0,"seeking_description":0, "image_link":0,
   "past_shows":[], "upcoming_shows": [],"past_shows_count":0,"upcoming_shows_count":0 }  

  shows_dic_org={"venue_id":0,"venue_name":0,"venue_image_link": 0,"start_time": 0}

  now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

  data_dic["id"]=i.id
  data_dic["name"]=i.name
  data_dic["genres"]=i.genres.split(",")
  data_dic["city"]=i.city
  data_dic["state"]=i.state
  data_dic["phone"]=i.phone
  data_dic["website"]=i.website
  data_dic["facebook_link"]=i.facebook_link
  data_dic["seeking_venue"]=i.seeking_venue
  data_dic["seeking_description"]=i.seeking_description
  data_dic["image_link"]=i.image_link
   
  past_shows=Show.query.filter(Show.artist_id==i.id).filter(Show.start_time < now).all()
  upcoming_shows=Show.query.filter(Show.artist_id==i.id).filter(Show.start_time >= now).all()

  for p in past_shows:
    shows_dic=shows_dic_org.copy()
    ven=Venue.query.filter_by(id=p.venue_id).first()
    shows_dic["venue_id"]= ven.id
    shows_dic["venue_name"]= ven.name
    shows_dic["venue_image_link"]= ven.image_link
    shows_dic["start_time"]= str(p.start_time)
    data_dic["past_shows"].append(shows_dic)

  for u in upcoming_shows:
    shows_dic=shows_dic_org.copy()
    ven=Venue.query.filter_by(id=u.venue_id).first()
    shows_dic["venue_id"]= ven.id
    shows_dic["venue_name"]= ven.name
    shows_dic["venue_image_link"]= ven.image_link
    shows_dic["start_time"]= str(u.start_time) 
    data_dic["upcoming_shows"].append(shows_dic)

    
  data_dic['past_shows_count']=len(past_shows)
  data_dic['upcoming_shows_count']=len(upcoming_shows)
  data=data_dic
  #shutdown_session()
  return render_template('pages/show_artist.html', artist=data)     
  

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm() 
  artist = Artist.query.filter_by(id=artist_id).first()

  artist = {"name":artist.name,
  "city":artist.city,
  "state":artist.state,
  "phone":artist.phone,
  "genres":artist.genres,
  "website":artist.website,
  "facebook_link":artist.facebook_link,
  "seeking_venue":artist.seeking_venue, 
  "seeking_description":artist.seeking_description,
  "image_link":artist.image_link}

  form.name.data=artist['name']
  form.city.data=artist['city']
  form.state.data=artist['state']
  form.phone.data=artist['phone']
  form.genres.data=artist['genres']
  form.facebook_link.data=artist['facebook_link']
  form.image_link.data=artist['image_link']

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  artist = Artist.query.filter_by(id=artist_id).first()  
  try:
    artist.name=request.form['name']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.genres = request.form['genres']
    #artist.address = request.form['address']
    artist.phone = request.form['phone']
    artist.facebook_link = request.form['facebook_link']
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return (url_for('show_artist', artist_id=artist_id))       
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes



@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.filter_by(id=venue_id).first()
  venue = {
  "name":venue.name,
  "city":venue.city,
  "state":venue.state,
  "phone":venue.phone,
  "genres":venue.genres,
  "facebook_link":venue.facebook_link,
  "image_link":venue.image_link}
  form.name.data=venue['name']
  form.city.data=venue['city']
  form.state.data=venue['state']
  form.phone.data=venue['phone']
  form.genres.data=venue['genres']
  form.facebook_link.data=venue['facebook_link']
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  venue = Venue.query.filter_by(id=venue_id).first()  
  try:
    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.genres = request.form['genres']
    venue.address = request.form['address']
    venue.phone = request.form['phone']
    venue.facebook_link = request.form['facebook_link']
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()    
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  artist = Artist(
  name = request.form['name'],
  city = request.form['city'],
  state = request.form['state'],
  phone = request.form['phone'],
  genres = ','.join(request.form.getlist('genres')),
  facebook_link = request.form['facebook_link']
  )

  try:
    db.session.add(artist)
    db.session.commit()     
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()  

    flash('An error occurred. Artist ' + request.form['name']+ ' could not be listed.')
  finally:
    db.session.close()
  
  return render_template('pages/home.html')      
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():      
  ids = Show.query.all()
  data=[]
  data_dic_org={"venue_id":0,"venue_name":0, "artist_id":0, "artist_name":0, "artist_image_link":0,
  "start_time":0 }
  for i in ids:
    data_dic=data_dic_org.copy()  
    data_dic["venue_id"]=i.venue_id  
    data_dic["venue_name"]=Venue.query.filter_by(id=i.venue_id).first().name
    data_dic["artist_id"]=i.artist_id
    art=Artist.query.filter_by(id=i.artist_id).first()
    data_dic["artist_name"]=art.name
    data_dic["artist_image_link"]=art.image_link
    data_dic["start_time"]=str(i.start_time)

    data.append(data_dic)
  return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  show = Show(
  venue_id = request.form['venue_id'],
  artist_id = request.form['artist_id'],
  start_time = request.form['start_time'],

  )
  try:
    db.session.add(show)
    db.session.commit()     
    flash('Show was successfully listed!')
  except:
    db.session.rollback()  

    flash('Show was successfully listed!')
  finally:
    db.session.close()
  
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
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
@app.teardown_appcontext
def shutdown_session(exception=None):
  db.session.remove()