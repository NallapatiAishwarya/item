from flask import Flask, render_template, url_for
from flask import request, redirect, flash, make_response, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from Data_Setup import Base,UniversityName,CollegeName, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import requests
import datetime

engine = create_engine('sqlite:///universities.db',
                       connect_args={'check_same_thread': False}, echo=True)
Base.metadata.create_all(engine)
DBSession = sessionmaker(bind=engine)
session = DBSession()
app = Flask(__name__)

CLIENT_ID = json.loads(open('client_secrets.json',
                            'r').read())['web']['client_id']
APPLICATION_NAME = "Universities"

DBSession = sessionmaker(bind=engine)
session = DBSession()
# Create anti-forgery state token
ish_zab = session.query(UniversityName).all()


# login
@app.route('/login')
def showLogin():
    
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    ish_zab = session.query(UniversityName).all()
    ishes = session.query(CollegeName).all()
    return render_template('login.html',
                           STATE=state, ish_zab=ish_zab, ishes=ishes)
    # return render_template('myhome.html', STATE=state
    # ish_zab=ish_zab,ishes=ishes)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print ("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px; border-radius: 150px;'
    '-webkit-border-radius: 150px; -moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print ("done!")
    return output


# User Helper Functions
def createUser(login_session):
    User1 = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(User1)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except Exception as error:
        print(error)
        return None

# DISCONNECT - Revoke a current user's token and reset their login_session

#####
# Home
@app.route('/')
@app.route('/home')
def home():
    ish_zab = session.query(UniversityName).all()
    return render_template('myhome.html', ish_zab=ish_zab)

#####
# University Category for admins
@app.route('/University')
def University():
    try:
        if login_session['username']:
            name = login_session['username']
            ish_zab = session.query(UniversityName).all()
            ishs = session.query(UniversityName).all()
            ishes = session.query(CollegeName).all()
            return render_template('myhome.html', ish_zab=ish_zab,
                                   ishs=ishs, ishes=ishes, uname=name)
    except:
        return redirect(url_for('showLogin'))

######
# Showing bykes based on byke category
@app.route('/University/<int:ishid>/AllUniversities')
def showColleges(ishid):
    ish_zab = session.query(UniversityName).all()
    ishs = session.query(UniversityName).filter_by(id=ishid).one()
    ishes = session.query(CollegeName).filter_by(universitynameid=ishid).all()
    try:
        if login_session['username']:
            return render_template('showColleges.html', ish_zab=ish_zab,
                                   ishs=ishs, ishes=ishes,
                                   uname=login_session['username'])
    except:
        return render_template('showColleges.html',
                               ish_zab=ish_zab, ishs=ishs, ishes=ishes)

#####
# Add New University
@app.route('/University/addUniversity', methods=['POST', 'GET'])
def addUniversity():
    if request.method == 'POST':
        company = UniversityName(name=request.form['name'],
                           user_id=login_session['user_id'])
        session.add(company)
        session.commit()
        return redirect(url_for('University'))
    else:
        return render_template('addUniversity.html', ish_zab=ish_zab)

########
# Edit College Category
@app.route('/University/<int:ishid>/edit', methods=['POST', 'GET'])
def editCollege(ishid):
    editedCollege = session.query(UniversityName).filter_by(id=ishid).one()
    creator = getUserInfo(editedCollege.user_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != login_session['user_id']:
        flash("You cannot edit this College Category."
              "This is belongs to %s" % creator.name)
        return redirect(url_for('University'))
    if request.method == "POST":
        if request.form['name']:
            editedCollege.name = request.form['name']
        session.add(editedCollege)
        session.commit()
        flash("College Category Edited Successfully")
        return redirect(url_for('University'))
    else:
        # ish_zab is global variable we can them in entire application
        return render_template('editCollege.html',
                               ish=editedCollege, ish_zab=ish_zab)

######
# Delete College Category
@app.route('/University/<int:ishid>/delete', methods=['POST', 'GET'])
def deleteCollege(ishid):
    ish = session.query(UniversityName).filter_by(id=ishid).one()
    creator = getUserInfo(ish.user_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != login_session['user_id']:
        flash("You cannot Delete this college Category."
              "This is belongs to %s" % creator.name)
        return redirect(url_for('University'))
    if request.method == "POST":
        session.delete(ish)
        session.commit()
        flash("college Category Deleted Successfully")
        return redirect(url_for('University'))
    else:
        return render_template('deleteCollege.html', ish=ish, ish_zab=ish_zab)

######
# Add New college Name Details
@app.route('/University/addUniversityName/addCollegeDetails/<string:ishname>/add',
           methods=['GET', 'POST'])
def addCollegeDetails(ishname):
    ishs = session.query(UniversityName).filter_by(name=ishname).one()
    # See if the logged in user is not the owner of byke
    creator = getUserInfo(ishs.user_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != login_session['user_id']:
        flash("You can't add new college edition"
              "This is belongs to %s" % creator.name)
        return redirect(url_for('showColleges', ishid=ishs.id))
    if request.method == 'POST':
        name = request.form['name']
        establishedyear = request.form['establishedyear']
        rating = request.form['rating']
        collegedetails = CollegeName(name=name, establishedyear=establishedyear,
                              rating=rating, 
                              universitynameid=ishs.id,
                              user_id=login_session['user_id'])
        session.add(collegedetails)
        session.commit()
        return redirect(url_for('showColleges', ishid=ishs.id))
    else:
        return render_template('addCollegeDetails.html',
                               ishname=ishs.name, ish_zab=ish_zab)

######
# Edit College details
@app.route('/University/<int:ishid>/<string:ishename>/edit',
           methods=['GET', 'POST'])
def editColleges(ishid, ishename):
    ish = session.query(UniversityName).filter_by(id=ishid).one()
    collegedetails = session.query(CollegeName).filter_by(name=ishename).one()
    # See if the logged in user is not the owner of byke
    creator = getUserInfo(ish.user_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != login_session['user_id']:
        flash("You can't edit this college edition"
              "This is belongs to %s" % creator.name)
        return redirect(url_for('showColleges', ishid=ish.id))
    # POST methods
    if request.method == 'POST':
        collegedetails.name = request.form['name']
        collegedetails.establishedyear = request.form['establishedyear']
        collegedetails.rating = request.form['rating']
        session.add(collegedetails)
        session.commit()
        flash("college Edited Successfully")
        return redirect(url_for('showColleges', ishid=ishid))
    else:
        return render_template('editColleges.html',
                               ishid=ishid, collegedetails=collegedetails, ish_zab=ish_zab)

#####
# Delete college Edit
@app.route('/University/<int:ishid>/<string:ishename>/delete',
           methods=['GET', 'POST'])
def deleteColleges(ishid, ishename):
    ish = session.query(UniversityName).filter_by(id=ishid).one()
    collegedetails = session.query(CollegeName).filter_by(name=ishename).one()
    # See if the logged in user is not the owner of byke
    creator = getUserInfo(ish.user_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != login_session['user_id']:
        flash("You can't delete this college edition"
              "This is belongs to %s" % creator.name)
        return redirect(url_for('showColleges', ishid=ish.id))
    if request.method == "POST":
        session.delete(collegedetails)
        session.commit()
        flash("Deleted college Successfully")
        return redirect(url_for('showColleges', ishid=ishid))
    else:
        return render_template('deleteColleges.html',
                               ishid=ishid, collegedetails=collegedetails, ish_zab=ish_zab)

####
# Logout from current user
@app.route('/logout')
def logout():
    access_token = login_session['access_token']
    print ('In gdisconnect access token is %s', access_token)
    print ('User name is: ')
    print (login_session['username'])
    if access_token is None:
        print ('Access Token is None')
        response = make_response(
            json.dumps('Current user not connected....'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = login_session['access_token']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = \
        h.request(uri=url, method='POST', body=None,
                  headers={'content-type': 'application/x-www-form-urlencoded'})[0]

    print (result['status'])
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected user..'), 200)
        response.headers['Content-Type'] = 'application/json'
        flash("Successful logged out")
        return redirect(url_for('showLogin'))
        # return response
    else:
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

#####
# Json
@app.route('/University/JSON')
def allUniversitiesJSON():
    universitynames = session.query(UniversityName).all()
    category_dict = [c.serialize for c in universitynames]
    for c in range(len(category_dict)):
        universities = [i.serialize for i in session.query(
                 CollegeName).filter_by(universitynameid=category_dict[c]["id"]).all()]
        if universities:
            category_dict[c]["universities"] = universities
    return jsonify(UniversityName=category_dict)

####
@app.route('/University/UniversityName/JSON')
def categoriesJSON():
    universities = session.query(UniversityName).all()
    return jsonify(UniversityName=[c.serialize for c in universities])

####
@app.route('/University/universities/JSON')
def itemsJSON():
    items = session.query(CollegeName).all()
    return jsonify(universities=[i.serialize for i in items])

#####
@app.route('/University/<path:college_name>/universities/JSON')
def categoryItemsJSON(college_name):
    universityName = session.query(UniversityName).filter_by(name=byke_name).one()
    universities = session.query(CollegeName).filter_by(collegename=universityName).all()
    return jsonify(universityName=[i.serialize for i in universities])

#####
@app.route('/University/<path:university_name>/<path:universitycollege_name>/JSON')
def ItemJSON(university_name, universitycollege_name):
    universityName = session.query(UniversityName).filter_by(name=universitycollege_name).one()
    universityCollegeName = session.query(CollegeName).filter_by(
           name=universitycollege_name, collegename=universityName).one()
    return jsonify(universityCollegeName=[universityCollegeName.serialize])

if __name__ == '__main__':
    app.secret_key = "super_secret_key"
    app.debug = True
    app.run(host='127.0.0.1', port=8000)
