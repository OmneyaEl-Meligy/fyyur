#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for ,jsonify 
from flask_moment import Moment

import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
import sys
from forms import *
import json 
from enums import Genres
from models import Venue, Artist , Show
from config import db , app
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

moment = Moment(app)


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
  venuesList= Venue.query.order_by(Venue.city,Venue.state).all()
  today = datetime.today().date()
  current_city = ""
  current_state = ""
  data = []
  for venue in venuesList:
    upComingShows =  list(filter(lambda show: show.start_time.date() >= today , venue.shows))
    if venue.city != current_city or venue.state != current_state :
      data.append({
        "city": venue.city,
        "state": venue.state,
        "venues": []
      })
      current_city = venue.city
      current_state = venue.state

    data[-1]['venues'].append({
          "id": venue.id,
          "name": venue.name,
          "num_upcoming_shows": len(upComingShows)
        })

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  criteria = request.form.get('criteria')
  search_value = request.form.get('search_term')

  if criteria == 'city' :
    searchList = [x.strip() for x in search_value.split(',')] 
    if len(searchList) > 1:
     query = Venue.query.filter(Venue.city.ilike("%{}%".format(searchList[0]))).\
                  filter(Venue.state.ilike("%{}%".format(searchList[1])))
    else:
      query =  Venue.query.filter((Venue.city.ilike("%{}%".format(search_value))) | (Venue.state.ilike("%{}%".format(search_value))))
  else :
    search_value = "%{}%".format(search_value)
    query =  Venue.query.filter(Venue.name.ilike(search_value))
 
  result = query.all()
  response={
    "count": len(result),
    "data": result
  }
  print(criteria)
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term') , criteria=criteria)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  try:
    venueDetails=Venue.query.get(venue_id)
    today = datetime.today().date()
    venue_default_pic = "/static/img/front-splash.jpg"

    show_query = Show.query.with_entities(Show.start_time,Artist.id.label('artist_id'),Artist.name.label('artist_name'),Artist.image_link.label('artist_image_link')).\
                      join(Artist).filter(Show.venue_id == venue_id)

    past_shows = show_query.filter(Show.start_time <  today).order_by('start_time').all()
    upcoming_shows = show_query.filter(Show.start_time >=  today).order_by('start_time').all()
    gen_list = venueDetails.genres.split(",")
    gen_list_mapped = []
    for key in gen_list:    
      try:     
        gen_list_mapped.append(getattr(Genres, key).value)
      except:
        print(sys.exc_info())

    data={
      "id": venueDetails.id,
      "name": venueDetails.name,
      "genres": gen_list_mapped,
      "address": venueDetails.address,
      "city": venueDetails.city ,
      "state": venueDetails.state,
      "phone": venueDetails.phone,
      "website": venueDetails.website,
      "facebook_link": venueDetails.facebook_link,
      "seeking_talent": venueDetails.seeking_talent,
      "seeking_description":venueDetails.seeking_description,
      "image_link": venueDetails.image_link if venueDetails.image_link  != None else venue_default_pic,
      "past_shows" : past_shows ,
      "upcoming_shows" : upcoming_shows ,
      "past_shows_count": len(past_shows) ,
      "upcoming_shows_count" : len(upcoming_shows)
    }
    return render_template('pages/show_venue.html', venue=data)

  except:      
    flash('Something Went Wrong' , 'danger')
    return redirect(url_for('index'))


    
#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  genres=request.form.getlist('genres') 
  try:
      venue = Venue(name= request.form.get('name') ,city=  request.form.get('city')
                    ,state = request.form.get('state')  ,address= request.form.get('address') 
                    ,phone= request.form.get('phone') ,image_link= request.form.get('image_link') 
                    ,genres=  ','.join(genres) ,facebook_link=  request.form.get('facebook_link')
                    )
      
      db.session.add(venue)
      db.session.commit()

      # on successful db insert, flash success
      flash('Venue ' + venue.name  + ' was successfully listed!', 'info')
  except:
      # on unsuccessful db insert, flash an error
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.' , 'danger')
  finally:
      db.session.close()
      
  return render_template('pages/home.html')

@app.route('/delete_venue/<venue_id>', methods=['GET'])
def delete_venue(venue_id):
    try:
      Venue.query.filter_by(id=venue_id).delete()
      db.session.commit()
      flash('Venue was successfully Deleted!', 'info')
    except:
      db.session.rollback()
      flash('An error occurred. Venue could not be Deleted.' , 'danger')
    finally:
      db.session.close()  
     
    return redirect(url_for('index'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = Artist.query.with_entities(Artist.id, Artist.name)
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  criteria = request.form.get('criteria')
  search_value = request.form.get('search_term')

  if criteria == 'city' :
    searchList = [x.strip() for x in search_value.split(',')] 
    if len(searchList) > 1:
     query = Artist.query.filter(Artist.city.ilike("%{}%".format(searchList[0]))).\
                  filter(Artist.state.ilike("%{}%".format(searchList[1])))
    else:
      query =  Artist.query.filter((Artist.city.ilike("%{}%".format(search_value))) | (Artist.state.ilike("%{}%".format(search_value))))
  else :
    search_value = "%{}%".format(search_value)
    query =  Artist.query.filter(Artist.name.ilike(search_value))
 
  result = query.all()
  response={
    "count": len(result),
    "data": result
  }

 
  return render_template('pages/search_artists.html', results=response, search_term= request.form.get('search_term') , criteria=(criteria,''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  try:
    artistDetails=Artist.query.get(artist_id)
    today = datetime.today().date()
    default_pic = "/static/img/default-Artist.png" 
    show_query = Show.query.with_entities(Show.start_time,Venue.id.label('venue_id'),Venue.name.label('venue_name'),Venue.image_link.label('venue_image_link')).\
                      join(Venue).filter(Show.artist_id == artist_id)

    past_shows = show_query.filter(Show.start_time <  today).order_by('start_time').all()
    upcoming_shows = show_query.filter(Show.start_time >=  today).order_by('start_time').all()
    
    gen_list = artistDetails.genres.split(",")
    gen_list_mapped = []
    for key in gen_list:    
      try:     
        gen_list_mapped.append(getattr(Genres, key).value)
      except:
        print(sys.exc_info())

    data={
      "id": artistDetails.id,
      "name": artistDetails.name,
      "genres": gen_list_mapped ,
      "city": artistDetails.city ,
      "state": artistDetails.state,
      "phone": artistDetails.phone,
      "website": artistDetails.website,
      "facebook_link": artistDetails.facebook_link,
      "seeking_venue": artistDetails.seeking_venue,
      "seeking_description":artistDetails.seeking_description,
      "image_link": artistDetails.image_link if artistDetails.image_link  != None else default_pic,
      "past_shows" : past_shows ,
      "upcoming_shows" : upcoming_shows ,
      "past_shows_count": len(past_shows) ,
      "upcoming_shows_count" : len(upcoming_shows)
    }
    return render_template('pages/show_artist.html', artist=data)
 
  except:      
    flash('Something Went Wrong' , 'danger')
    return redirect(url_for('index'))

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist=Artist.query.get(artist_id)
  form.genres.default = artist.genres.split(",")
  form.process() 
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  
  try:
    genres=request.form.getlist('genres')
    artist = Artist.query.get(artist_id)
    artist.name= request.form.get('name')
    artist.city=  request.form.get('city')
    artist.state = request.form.get('state') 
    artist.phone= request.form.get('phone')
    artist.image_link= request.form.get('image_link')
    artist.genres= ','.join(genres)
    artist.seeking_description=  request.form.get('website')
    artist.seeking_venue=  True if request.form.get('seeking_venue') == 'on' else False
    artist.seeking_description=  request.form.get('seeking_description')

    db.session.commit()
    # on successful db update, flash success
    flash('Artist ' + artist.name  + ' was successfully Updated!', 'info')
  except:
    # on unsuccessful db update, flash an error
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be Updated.' , 'danger')
    print(sys.exc_info())
  finally:
      db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()  
  venue=Venue.query.get(venue_id)
  form.genres.default = venue.genres.split(",")
  form.process() 
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  try:
    genres=request.form.getlist('genres')
    venue = Venue.query.get(venue_id)
    venue.name= request.form.get('name')
    venue.city=  request.form.get('city')
    venue.state = request.form.get('state') 
    venue.phone= request.form.get('phone')
    venue.image_link= request.form.get('image_link')
    venue.genres= ','.join(genres)
    venue.seeking_description=  request.form.get('website')
    venue.seeking_talent=  True if request.form.get('seeking_talent') == 'on' else False
    venue.seeking_description=  request.form.get('seeking_description')

    db.session.commit()
    # on successful db update, flash success
    flash('Venue ' + venue.name  + ' was successfully Updated!', 'info')
  except:
    # on unsuccessful db update, flash an error
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be Updated.' , 'danger')
    print(sys.exc_info())
  finally:
      db.session.close()
      
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  genres=request.form.getlist('genres')  
  try:
      artist = Artist(name= request.form.get('name') ,city=  request.form.get('city')
                    ,state = request.form.get('state') ,phone= request.form.get('phone') 
                    ,image_link= request.form.get('image_link') ,genres= ','.join(genres)
                    ,facebook_link=  request.form.get('facebook_link')
                    )
      
      db.session.add(artist)
      db.session.commit()

      # on successful db insert, flash success
      flash('Artist ' + artist.name  + ' was successfully listed!', 'info')
  except:
      # on unsuccessful db insert, flash an error
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.' , 'danger')
      print(sys.exc_info())
  finally:
      db.session.close()
      
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows

  shows = Show.query.join(Venue).join(Artist).order_by(Show.start_time.desc()).all()
  print(shows[0].artist.name)
  data = []
  default_pic = "/static/img/default-Artist.png"
  # "https://www.freepngimg.com/thumb/google/66726-customer-account-google-service-button-search-logo.png"
  for show in shows:
    data.append({
      "venue_id": show.venue.id,
      "venue_name": show.venue.name,
      "artist_id": show.artist.id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link if show.artist.image_link != None else default_pic,
      "start_time": show.start_time.strftime("%Y-%m-%d, %H:%M:%S")
    })
   
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  try:
      show = Show(venue_id= request.form.get('venue_id') ,artist_id=  request.form.get('artist_id')
                    ,start_time = request.form.get('start_time')
                    )
      
      db.session.add(show)
      db.session.commit()

      # on successful db insert, flash success
      flash('Show was successfully listed!', 'info')
  except:
      # on unsuccessful db insert, flash an error
      flash('An error occurred. Show could not be listed' , 'danger')
      print(sys.exc_info())
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
