#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
from os import name
import dateutil.parser
import babel
from flask import (
		render_template, 
		request, 
		flash, 
		redirect, 
		url_for
	)
from models import app, db, Venue, Artist, Shows
from flask_moment import Moment
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

moment = Moment(app)
app.config.from_object('config')


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
	date = dateutil.parser.parse(value)
	if format == 'full':
		format="EEEE MMMM, d, y 'at' h:mma"
	elif format == 'medium':
		format="EE MM, dd, y h:mma"
	return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
	venues = Venue.query.order_by(Venue.id.desc()).limit(10).all()
	artists = Artist.query.order_by(Artist.id.desc()).limit(10).all()

	return render_template('pages/home.html', venues=venues, artists=artists)


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
	venues = Venue.query.order_by('id').all()
	# state_city = db.session.query(Venue.city, Venue.state).distinct().all()
	# print(state_city)
	
	return render_template('pages/venues.html', venues=venues)

@app.route('/venues/search', methods=['POST'])
def search_venues():
	search_term = request.form.get('search_term')
	result = Venue.query.filter(Venue.name.ilike('%' + search_term + '%')).all()
	response = {
		"count": len(result),
		"data": result
	}

	return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
	venue = Venue.query.filter_by(id=venue_id).first()
	# past_shows_venue = Shows.query.filter_by(venue_id=venue_id).filter(Shows.start_time < datetime.today()).all()
	# upcoming_shows_venue = Shows.query.filter_by(venue_id=venue_id).filter(Shows.start_time > datetime.today()).all()

	# I noticed the venue image was no longer showing, what could be the cause
	past_shows_query = db.session.query(Shows).join(Artist, Shows.artist_id==Artist.id).filter(Shows.venue_id==venue_id).filter(Shows.start_time < datetime.today()).all()
	upcoming_shows_query = db.session.query(Shows).join(Artist, Shows.artist_id==Artist.id).filter(Shows.venue_id==venue_id).filter(Shows.start_time > datetime.today()).all()
	
	# I'm converting the start_time property to string here because of the error I'm getting when trying to render date
	for show in past_shows_query:
		show.start_time = str(show.start_time)
		# show['artist_name'] = Artist.name
		# show['image_link'] = Artist.image_link
	
	for show in upcoming_shows_query:
		show.start_time = str(show.start_time)

	remove_curly_braces = venue.genres[1:len(venue.genres)-1]
	genres = remove_curly_braces.split(',')

	# 

	data = {
		"id": venue.id,
		"name": venue.name,
		"genres": genres,
		"address": venue.address,
		"city": venue.city,
		"state": venue.state,
		"phone": venue.phone,
		"website": venue.website_link,
		"facebook_link": venue.facebook_link,
		"seeking_talent": venue.seeking_talent,
		"seeking_description": venue.seeking_description,
		"image_link": venue.image_link,
	}

	# I'm leaving the old code below just to note the differences in using join and not using join.
	
	# for show in past_shows_venue:
	# 	venue_artist_info = {
	# 		'artist_id': show.artist_id,
	# 		'artist_name': show.artist.name,
	# 		'artist_image_link': show.artist.image_link,
	# 		'start_time': str(show.start_time)
	# 	}	
	# 	past_shows.append(venue_artist_info)

	# for show in upcoming_shows_venue:
	# 	venue_artist_info = {
	# 		'artist_id': show.artist_id,
	# 		'artist_name': show.artist.name,
	# 		'artist_image_link': show.artist.image_link,
	# 		'start_time': str(show.start_time)
	# 	}	
	# 	past_shows.append(venue_artist_info)
	
	data['past_shows'] = past_shows_query
	data['upcoming_shows'] = upcoming_shows_query
	data['past_shows_count'] = len(past_shows_query)
	data['upcoming_shows_count'] = len(upcoming_shows_query)

	return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
	form = VenueForm()
	return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
	error = False
	
	try:
		form = VenueForm()
		venue_name = form.name.data
		venue_city = form.city.data
		venue_state = form.state.data
		venue_address = form.address.data
		venue_genres = form.genres.data
		venue_phone = form.phone.data
		venue_facebook_link = form.facebook_link.data
		venue_image_link = form.image_link.data
		venue_website_link = form.website_link.data
		venue_seeking_talent = form.seeking_talent.data
		venue_seeking_description = form.seeking_description.data

		if form.validate():
			newVenue = Venue(
				name=venue_name, city=venue_city, state=venue_state, address=venue_address, phone=venue_phone,
				facebook_link=venue_facebook_link, image_link=venue_image_link, website_link=venue_website_link,
				seeking_talent=venue_seeking_talent, seeking_description=venue_seeking_description, genres=venue_genres
			)
			if bool(Venue.query.filter_by(name=venue_name).first()):
				flash('Venue ' + form.name.data + ' already exist!')
				return render_template('forms/new_venue.html', form=form) 

			db.session.add(newVenue)
			db.session.commit()
			# on successful db insert, flash success
			flash('Venue ' + form.name.data + ' was successfully listed!')
	except:
		db.session.rollback()
		error = True
	finally:
		db.session.close()

	if error:
		flash('An error occurred. Venue ' + form.name.data + ' could not be listed.')
	
	
	return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
	error = False

	try:
		Venue.query.filter_by(id=venue_id).delete()
		db.session.commit()
		flash('Venue deleted Successfully')
	except:
		error = True
		db.session.rollback()
	finally:
		db.session.close()

	if error:
		flash('Error occured while Deleting Venue! Try again')
	return redirect(url_for('index'))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
	form = VenueForm()
	venue = Venue.query.filter_by(id=venue_id).first()
		
	form.name.data = venue.name
	form.city.data = venue.city
	form.state.data = venue.state
	form.phone.data = venue.phone
	form.address.data = venue.address
	form.genres.data = venue.genres
	form.facebook_link.data = venue.facebook_link
	form.image_link.data = venue.image_link
	form.website_link.data = venue.website_link
	form.seeking_talent.data = venue.seeking_talent
	form.seeking_description.data = venue.seeking_description

	return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
	form = VenueForm()
	error = False
	venue = Venue.query.filter_by(id=venue_id).first()
	
	try:
		venue.name = form.name.data
		venue.city = form.city.data
		venue.state = form.state.data
		venue.address = form.address.data
		venue.phone = form.phone.data
		venue.genres = form.genres.data
		venue.facebook_link = form.facebook_link.data
		venue.image_link = form.image_link.data
		venue.website_link = form.website_link.data
		venue.seeking_talent = form.seeking_talent.data
		venue.seeking_description = form.seeking_description.data

		if form.validate():
			db.session.add(venue)
			db.session.commit()
		flash('Venue ' + form.name.data + ' was successfully edited!')
	except:
		db.session.rollback()
		error = True
	finally:
		db.session.close()

	if error:
		flash('An error occurred. Venue ' + form.name.data + ' could not be edited.')

	return redirect(url_for('show_venue', venue_id=venue_id))


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
	artistes = Artist.query.order_by('id').all()
	
	return render_template('pages/artists.html', artists=artistes)

@app.route('/artists/search', methods=['POST'])
def search_artists():
	search_term = request.form.get('search_term')

	result = Artist.query.filter(Artist.name.ilike('%' + search_term + '%')).all()
	response = {
		"count": len(result),
		"data": result
	}

	return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
	artist = Artist.query.filter_by(id=artist_id).first()
	# past_shows_artist = Shows.query.filter_by(artist_id=artist_id).filter(Shows.start_time < datetime.today()).all()
	# upcoming_shows_artist = Shows.query.filter_by(artist_id=artist_id).filter(Shows.start_time > datetime.today()).all()

	# I noticed the venue image was no longer showing, what could be the cause
	past_shows_query = db.session.query(Shows).join(Venue, Shows.venue_id==Venue.id).filter(Shows.artist_id==artist_id).filter(Shows.start_time < datetime.today()).all()
	upcoming_shows_query = db.session.query(Shows).join(Venue, Shows.venue_id==Venue.id).filter(Shows.artist_id==artist_id).filter(Shows.start_time > datetime.today()).all()
	print(past_shows_query)
	# I'm converting the start_time property to string here because of the error I'm getting when trying to render date
	for show in past_shows_query:
		show.start_time = str(show.start_time)

	for show in upcoming_shows_query:
		show.start_time = str(show.start_time)

	remove_curly_braces = artist.genres[1:len(artist.genres)-1]
	genres = remove_curly_braces.split(',')

	data = {
		"id": artist.id,
		"name": artist.name,
		"genres": genres,
		"city": artist.city,
		"state": artist.state,
		"phone": artist.phone,
		"website": artist.website_link,
		"facebook_link": artist.facebook_link,
		"seeking_venue": artist.seeking_venue,
		"seeking_description": artist.seeking_description,
		"image_link": artist.image_link,
	}

	# I'm still leaving my code below just to always note the differences in both methods (that is using join)
	
	# for show in past_shows_artist:
	# 	artist_venue_info = {
	# 		'venue_id': show.venue_id,
	# 		'venue_name': show.venue.name,
	# 		'venue_image_link': show.venue.image_link,
	# 		'start_time': str(show.start_time)
	# 	}	
	# 	past_shows.append(artist_venue_info)

	# for show in upcoming_shows_artist:
	# 	artist_venue_info = {
	# 		'venue_id': show.venue_id,
	# 		'venue_name': show.venue.name,
	# 		'venue_image_link': show.venue.image_link,
	# 		'start_time': str(show.start_time)
	# 	}	
	# 	past_shows.append(artist_venue_info)
	
	data['past_shows'] = past_shows_query
	data['upcoming_shows'] = upcoming_shows_query
	data['past_shows_count'] = len(past_shows_query)
	data['upcoming_shows_count'] = len(upcoming_shows_query)

	return render_template('pages/show_artist.html', artist=data)

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
	form = ArtistForm()
	return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
	error = False

	try:
		form = ArtistForm()
		artist_name = form.name.data
		artist_city = form.city.data
		artist_state = form.state.data
		artist_phone = form.phone.data
		artist_genres = form.genres.data
		artist_facebook_link = form.facebook_link.data
		artist_image_link = form.image_link.data
		artist_website_link = form.website_link.data
		artist_seeking_venue = form.seeking_venue.data
		artist_seeking_description = form.seeking_description.data

		if form.validate():
			newArtist = Artist(
				name=artist_name, city=artist_city, state=artist_state, phone=artist_phone, genres=artist_genres,
				facebook_link=artist_facebook_link, image_link=artist_image_link, website_link=artist_website_link,
				seeking_venue=artist_seeking_venue, seeking_description=artist_seeking_description
			)

			if bool(Artist.query.filter_by(name=artist_name).first()):
				flash('Artiste ' + form.name.data + ' already exist!')
				return render_template('forms/new_artist.html', form=form) 

			db.session.add(newArtist)
			db.session.commit()
		else: 
			flash('Please fill the form fields correctly!')
	except Exception as e:
		error = True
		err = str(e)
		db.session.rollback()	
	finally:
		db.session.close()

	if error:
		flash('An error occurred. Artist ' + form.name.data + ' could not be listed.' + err)

	if error == False:
		flash('Artist ' + form.name.data + ' was successfully listed!')
	return render_template('pages/home.html')

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
	form = ArtistForm()
	
	artist = Artist.query.filter_by(id=artist_id).first()
	form.name.data = artist.name
	form.city.data = artist.city
	form.state.data = artist.state
	form.genres.data = artist.genres
	form.phone.data = artist.phone
	form.facebook_link.data = artist.facebook_link
	form.image_link.data = artist.image_link
	form.website_link.data = artist.website_link
	form.seeking_venue.data = artist.seeking_venue
	form.seeking_description.data = artist.seeking_description

	return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
	form = ArtistForm()
	error = False

	artist = Artist.query.filter_by(id=artist_id).first()
	try:
		artist.name = form.name.data
		artist.city = form.city.data
		artist.state = form.state.data
		artist.genres = form.genres.data
		artist.phone = form.phone.data
		artist.facebook_link = form.facebook_link.data
		artist.image_link = form.image_link.data
		artist.website_link = form.website_link.data
		artist.seeking_venue = form.seeking_venue.data
		artist.seeking_description = form.seeking_description.data 

		if form.validate():
			db.session.add(artist)
			db.session.commit()
			flash('Artist ' + form.name.data + ' was successfully edited!')
	except:
		db.session.rollback()
		error = True
	finally:
		db.session.close()

	if error:
		flash('An error occurred. Artist ' + form.name.data + ' could not be edited.')

	return redirect(url_for('show_artist', artist_id=artist_id))


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
	query_result = Shows.query.all()

	shows = []

	for show in query_result:
		show_info = {
			'venue_id': show.venue_id,
			'artist_id': show.artist_id,
			'start_time': str(show.start_time),
			'venue_name': show.venue.name,
			'artist_name': show.artist.name,
			'artist_image_link': show.artist.image_link
		}

		shows.append(show_info)
		
	return render_template('pages/shows.html', shows=shows)

@app.route('/shows/search', methods=['POST'])
def search_shows():
	search_term = request.form.get('search_term')

	result = Shows.query.filter(Shows.venue_id.ilike('%' + search_term + '%')).all()
	response = {
		"count": len(result),
		"data": result
	}

	return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/shows/create')
def create_shows():
	# renders form. do not touch.
	form = ShowForm()
	return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():

	error = False
	errMsg = ''
	form = ShowForm()

	try:
		show_artist_id = form.artist_id.data
		show_venue_id = form.venue_id.data
		show_start_time = form.start_time.data

		venue = Venue.query.get(show_venue_id)
		artist = Artist.query.get(show_artist_id)

		if form.validate():
			# venue.artists.append(artist)
			newShow = Shows(venue_id=show_venue_id, artist_id=show_artist_id, start_time=show_start_time)

			db.session.add(newShow)
			db.session.commit()
			# on successful db insert, flash success
			flash('Show was successfully listed!')
		else: 
			flash('Please fill the form fields correctly!')
	except Exception as e:
		error = True
		errMsg = str(e)
		db.session.rollback()
		flash('An error occurred. Show could not be listed.' + errMsg)
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
    app.debug = True
    app.run(host='0.0.0.0', port=3000)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
