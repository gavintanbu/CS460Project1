######################################
# author ben lawson <balawson@bu.edu>
# Edited by: Craig Einstein <einstein@bu.edu>
######################################
# Some code adapted from
# CodeHandBook at http://codehandbook.org/python-web-application-development-using-flask-and-mysql/
# and MaxCountryMan at https://github.com/maxcountryman/flask-login/
# and Flask Offical Tutorial at  http://flask.pocoo.org/docs/0.10/patterns/fileuploads/
# see links for further understanding
###################################################

from email.mime import base
import flask
from flask import Flask, Response, request, render_template, redirect, url_for
from flaskext.mysql import MySQL
import flask_login
from datetime import datetime

#for image uploading
import os, base64

mysql = MySQL()
app = Flask(__name__)
app.secret_key = 'super secret string'  # Change this!

#These will need to be changed according to your creditionals
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = '1234'
app.config['MYSQL_DATABASE_DB'] = 'photoshare'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

#begin code used for login
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()
cursor.execute("SELECT email from Users")
users = cursor.fetchall()

def getUserList():
	cursor = conn.cursor()
	cursor.execute("SELECT email from Users")
	return cursor.fetchall()

class User(flask_login.UserMixin):
	pass

@login_manager.user_loader
def user_loader(email):
	users = getUserList()
	if not(email) or email not in str(users):
		return
	user = User()
	user.id = email
	return user

@login_manager.request_loader
def request_loader(request):
	users = getUserList()
	email = request.form.get('email')
	if not(email) or email not in str(users):
		return
	user = User()
	user.id = email
	cursor = mysql.connect().cursor()
	cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email))
	data = cursor.fetchall()
	pwd = str(data[0][0] )
	user.is_authenticated = request.form['password'] == pwd
	return user

'''
A new page looks like this:
@app.route('new_page_name')
def new_page_function():
	return new_page_html
'''

@app.route('/login', methods=['GET', 'POST'])
def login():
	if flask.request.method == 'GET':
		return '''
			   <form action='login' method='POST'>
				<input type='text' name='email' id='email' placeholder='email'></input>
				<input type='password' name='password' id='password' placeholder='password'></input>
				<input type='submit' name='submit'></input>
			   </form></br>
		   <a href='/'>Home</a>
			   '''
	#The request method is POST (page is recieving data)
	email = flask.request.form['email']
	cursor = conn.cursor()
	#check if email is registered
	if cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email)):
		data = cursor.fetchall()
		pwd = str(data[0][0] )
		if flask.request.form['password'] == pwd:
			user = User()
			user.id = email
			flask_login.login_user(user) #okay login in user
			return flask.redirect(flask.url_for('protected')) #protected is a function defined in this file

	#information did not match
	return "<a href='/login'>Try again</a>\
			</br><a href='/register'>or make an account</a>"

@app.route('/logout')
def logout():
	flask_login.logout_user()
	return render_template('hello.html', message='Logged out')

@login_manager.unauthorized_handler
def unauthorized_handler():
	return render_template('unauth.html')

#you can specify specific methods (GET/POST) in function header instead of inside the functions as seen earlier
@app.route("/register", methods=['GET'])
def register():
	return render_template('register.html', supress='True')

@app.route("/register", methods=['POST'])
def register_user():
	try:
		email=request.form.get('email')
		password=request.form.get('password')
		first=request.form.get('first')
		last=request.form.get('last')
		dob=request.form.get('dob')
		gender=request.form.get('gender')
	except:
		print("couldn't find all tokens") #this prints to shell, end users will not see this (all print statements go to shell)
		return flask.redirect(flask.url_for('register'))
	cursor = conn.cursor()
	test =  isEmailUnique(email)
	if test:
		print(cursor.execute("INSERT INTO Users (email, password,first_name,last_name,dob,gender) VALUES ('{0}', '{1}','{2}','{3}','{4}','{5}')".format(email, password,first,last,dob,gender)))
		conn.commit()
		#log user in
		user = User()
		user.id = email
		flask_login.login_user(user)
		return render_template('hello.html', name=email, message='Account Created!')
	else:
		print("couldn't find all tokens")
		return flask.redirect(flask.url_for('register'))

def getUsersPhotos(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT imgdata, picture_id, caption FROM Pictures WHERE user_id = '{0}'".format(uid))
	return cursor.fetchall() #NOTE list of tuples, [(imgdata, pid), ...]


###gavinbegin
def getUsersPhotoIds(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT picture_id FROM Pictures WHERE user_id = '{0}'".format(uid))
	return cursor.fetchall()

def getAllPhotos():
	cursor=conn.cursor()
	cursor.execute("SELECT imgdata, picture_id, caption FROM Pictures")
	return cursor.fetchall() #NOTE list of tuples, [(imgdata, pid), ...]

def getAllAlbumIds():
	cursor=conn.cursor()
	cursor.execute("SELECT album_id FROM Album")
	return cursor.fetchall() #NOTE list of tuples, [(imgdata, pid), ...]

def getAlbums(uid):
	cursor=conn.cursor()
	cursor.execute("SELECT album_id FROM Creates WHERE User_id = '{0}'".format(uid))
	return cursor.fetchall()

def getAlbumNameFromId(aid):
	cursor=conn.cursor()
	cursor.execute("SELECT album_name FROM Album WHERE album_id = '{0}'".format(aid))
	return cursor.fetchall() #NOTE list of tuples, [(imgdata, pid), ...]

def getAlbumIDandNameFromId(aid):
	cursor=conn.cursor()
	cursor.execute("SELECT album_id, album_name FROM Album WHERE album_id = '{0}'".format(aid))
	return cursor.fetchall() #NOTE list of tuples, [(imgdata, pid), ...]

def getAlbumIdFromDate(date):
	cursor=conn.cursor()
	cursor.execute("SELECT album_id  FROM Album WHERE dates = '{0}'".format(date))
	return cursor.fetchone()[0]

def getAlbumIdFromName(albumname):
	cursor=conn.cursor()
	cursor.execute("SELECT album_id  FROM Album WHERE album_name = '{0}'".format(albumname))
	return cursor.fetchone()[0]

def getAllPhotosFromAlbum(aid):
	cursor=conn.cursor()
	cursor.execute("SELECT picture_id FROM Contain WHERE album_id= '{0}'".format(aid))
	return cursor.fetchall() #NOTE list of tuples, [(imgdata, pid), ...]

def getPhotoFromPhotoId(pid):
	cursor=conn.cursor()
	cursor.execute("SELECT imgdata, picture_id, caption FROM Pictures WHERE picture_id= '{0}' ".format(pid))
	return cursor.fetchall() #NOTE list of tuples, [(imgdata, pid), ...]

def delteAlbumFromAlbumId(aid):
	cursor=conn.cursor()
	cursor.execute("DELETE FROM Contain WHERE album_id= '{0}' ".format(aid))
	cursor.execute("DELETE FROM Creates WHERE album_id= '{0}' ".format(aid))
	cursor.execute("DELETE FROM Album WHERE album_id= '{0}' ".format(aid))
	conn.commit()

def deletePhotofromPhotoId(pid):
	cursor=conn.cursor()
	cursor.execute("DELETE FROM Contain WHERE picture_id= '{0}' ".format(pid))
	cursor.execute("DELETE FROM Describes WHERE picture_id= '{0}' ".format(pid))
	cursor.execute("DELETE FROM Comments WHERE picture_id= '{0}' ".format(pid))
	cursor.execute("DELETE FROM Pictures WHERE picture_id= '{0}' ".format(pid))
	conn.commit()

def getAllTags():
	cursor=conn.cursor()
	cursor.execute("SELECT word_desc FROM Tag")
	return cursor.fetchall() #NOTE list of tuples, [(imgdata, pid), ...]

def getPhotoIdsFromTag(t):
	cursor=conn.cursor()
	cursor.execute("SELECT picture_id FROM Describes WHERE word_desc= '{0}' ".format(t))
	return cursor.fetchall()

def getallLikesFromUserId(uid):
	cursor=conn.cursor()
	cursor.execute("SELECT picture_id FROM Likes WHERE user_id= '{0}' ".format(uid))
	return cursor.fetchall()

def getTagsFromPhotoId(pid):
	cursor=conn.cursor()
	cursor.execute("SELECT word_desc FROM Describes WHERE picture_id= '{0}' ".format(pid))
	return cursor.fetchall()


###gavinend
###jonbegin
def getAllCommentswithId():					#pulling comments and id for matching with pictures
	cursor=conn.cursor()
	cursor.execute("SELECT picture_id, text,user_id FROM Comments")
	return cursor.fetchall() #NOTE list of tuples, [(imgdata, pid), ...]

def getFriends():
	cursor=conn.cursor()
	cursor.execute("SELECT friend_name FROM Friends WHERE user_id = '{0}'".format(getUserIdFromEmail(flask_login.current_user.id)))
	return cursor.fetchall() #NOTE list of tuples, [(imgdata, pid), ...]
def getFriendsID():								#gets the names from friends
	cursor=conn.cursor()
	x =4000
	cursor.execute("SELECT user_friend_id FROM Friends WHERE user_id = '{0}'".format(getUserIdFromEmail(flask_login.current_user.id)))
	return cursor.fetchall() #NOTE list of tuples, [(imgdata, pid), ...]
def getFriendsofFriends(idnum):						#getting friends of friends using ID
	cursor=conn.cursor()
	cursor.execute("SELECT friend_name,user_friend_id FROM Friends WHERE user_id = '{0}'".format(idnum))
	return cursor.fetchall() #NOTE list of tuples, [(imgdata, pid), ...]
def getNamefromID(idd):
	cursor=conn.cursor()
	cursor.execute("SELECT first_name,last_name FROM Users WHERE user_id = '{0}'".format(idd))
	return cursor.fetchall() #NOTE list of tuples, [(imgdata, pid), ...]

def getallLikesCounted():
	cursor= conn.cursor()
	cursor.execute("SELECT picture_id,COUNT(*) FROM Likes GROUP BY picture_id")
	return cursor.fetchall() #NOTE list of tuples, [(imgdata, pid), ...]

def getallLikesUserId():
	cursor= conn.cursor()
	cursor.execute("SELECT user_id,picture_id FROM Likes")
	return cursor.fetchall() #NOTE list of tuples, [(imgdata, pid), ...]

def getallPhotoId():
	cursor= conn.cursor()
	cursor.execute("SELECT picture_id FROM Pictures")
	return cursor.fetchall() #NOTE list of tuples, [(imgdata, pid), ...]
def getUserIdfromPictureId(phoid):
	cursor= conn.cursor()
	cursor.execute("SELECT user_id FROM Pictures WHERE picture_id = '{0}'".format(phoid))
	return cursor.fetchall() #NOTE list of tuples, [(imgdata, pid), ...]
def getUserIdfromComment(comment):
	cursor= conn.cursor()
	cursor.execute("SELECT user_id,Count(*) AS ccount FROM Comments WHERE text = '{0}' GROUP BY user_id ORDER BY ccount DESC".format(comment))
	return cursor.fetchall() #NOTE list of tuples, [(imgdata, pid), ...]
def getAllId():
	cursor= conn.cursor()
	cursor.execute("SELECT user_id FROM Users")
	return cursor.fetchall() #NOTE list of tuples, [(imgdata, pid), ...]
def getNumPhotos(id):
	cursor= conn.cursor()
	cursor.execute("SELECT Count(picture_id) FROM Pictures WHERE user_id = '{0}'".format(id))
	return cursor.fetchall() #NOTE list of tuples, [(imgdata, pid), ...]
def getNumComments(id):
	cursor= conn.cursor()
	cursor.execute("SELECT Count(comment_id) FROM Comments WHERE user_id = '{0}'".format(id))
	return cursor.fetchall() #NOTE list of tuples, [(imgdata, pid), ...]
###jonend
def getUserIdFromEmail(email):
	cursor = conn.cursor()
	cursor.execute("SELECT user_id  FROM Users WHERE email = '{0}'".format(email))
	return cursor.fetchone()[0]

def isEmailUnique(email):
	#use this to check if a email has already been registered
	cursor = conn.cursor()
	if cursor.execute("SELECT email  FROM Users WHERE email = '{0}'".format(email)):
		#this means there are greater than zero entries with that email
		return False
	else:
		return True
#end login code


@app.route('/profile')
@flask_login.login_required
def protected():
	return render_template('hello.html', name=flask_login.current_user.id, message="Here's your profile")

#begin photo uploading code
# photos uploaded using base64 encoding so they can be directly embeded in HTML
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
@flask_login.login_required
def upload_file():
	if request.method == 'POST':
		uid = getUserIdFromEmail(flask_login.current_user.id)
		imgfile = request.files['photo']
		caption = request.form.get('caption')
		aid=request.form.get('albumid')
		photo_data =imgfile.read()
		cursor = conn.cursor()
		cursor.execute('''INSERT INTO Pictures (imgdata, user_id, caption) VALUES (%s, %s, %s )''' ,(photo_data,uid, caption))
		pid=cursor.lastrowid

		cursor.execute('''INSERT INTO Contain (picture_id, album_id) VALUES (%s, %s)''' ,(pid,aid))
		conn.commit()
		return render_template('hello.html', name=flask_login.current_user.id, message='Photo uploaded!', photos=getUsersPhotos(uid),base64=base64)
	#The method is GET so we return a  HTML form to upload the a photo.
	else:
		uid = getUserIdFromEmail(flask_login.current_user.id)
		aids=getAlbums(uid)
		aids_and_anames=[]
		for a in aids:
			print(a)
			aids_and_anames+=getAlbumIDandNameFromId(a[0])

		return render_template('upload.html', albumids_and_albumnames=aids_and_anames)
#end photo uploading code


#default page
@app.route("/", methods=['GET'])
def hello():
	return render_template('hello.html', message='Welecome to Photoshare')


###gavinbegin
#jon begin
@app.route("/browse",methods=['GET','POST'])
def browse():
	if (request.method== "GET"):
		return render_template('browse.html',  photos=getAllPhotos(),comments=getAllCommentswithId() ,likes= getallLikesCounted(), base64=base64)
	if (request.method== 'POST'):
		if (flask_login.current_user.is_anonymous):
			return render_template('browse.html',  photos=getAllPhotos(),comments=getAllCommentswithId() ,likes= getallLikesCounted(),isanonm= True, base64=base64)
		uid = getUserIdFromEmail(flask_login.current_user.id)
		#photoids = getallPhotoId()									
		likescounted = getallLikesCounted()						#getting the number of likes for each photo

		#photoarray = []
		#for id in photoids:
		#	temptuple = [id[0],0]
		#	photoarray.append(temptuple)
		photoid = request.form.get('photo_id')					#pulling the comment that was submitted + photo_id
		comment= request.form.get('comment')
		userfromphoto= getUserIdfromPictureId(photoid)
		userfromphotoid=-1
		for u in userfromphoto:
			for user in u:
				userfromphotoid=user
		print(uid)
		print(userfromphoto)
		print("---------------")
		if userfromphotoid!=uid:
			cursor = conn.cursor()
			cursor.execute("INSERT INTO Comments (user_id,picture_id,text) VALUES ('{0}', '{1}','{2}')".format(uid,photoid,comment))
			aid=cursor.lastrowid
			conn.commit()
			return render_template('browse.html',  photos=getAllPhotos(),comments=getAllCommentswithId(),likes=likescounted,base64=base64)
		else: return render_template('browse.html',  photos=getAllPhotos(),comments=getAllCommentswithId(),likes=likescounted,isuserfromphoto=1,base64=base64)
@app.route("/browse2",methods=['GET','POST'])
def browse2():
	if (request.method== 'POST'):
		if (flask_login.current_user.is_anonymous):
			return render_template('browse.html',  photos=getAllPhotos(),comments=getAllCommentswithId() ,likes= getallLikesCounted(),isanon= True, base64=base64)
		uid = getUserIdFromEmail(flask_login.current_user.id)
		photoid = request.form.get('photo_id')
		alreadyliked = 0							#checking if a picture has already been liked
		likeids = getallLikesUserId()
		#print(likeids)
		for l in likeids:							#iterating through list to check if the same user is trying to like a post twice
			if (l[0]==uid ):

				strl = str(l[1])
				strp = str(photoid)
				if(strl==strp):
					print("what is going on?")
					alreadyliked+=1
		
		print(alreadyliked)
		print("alreadyliked")
		
		if alreadyliked==0:								#counter will not increase if post has been liked by one person
			cursor = conn.cursor()
			cursor.execute("INSERT INTO Likes (user_id,picture_id) VALUES ('{0}', '{1}')".format(uid,photoid))		
			aid=cursor.lastrowid
			conn.commit()

		return render_template('browse.html',  photos=getAllPhotos(),comments=getAllCommentswithId() ,likes= getallLikesCounted(),isliked=alreadyliked, base64=base64)
@app.route("/searchbycomment",methods=['GET','POST'])
def searchbycomment():
	if (request.method=='GET'):
		return render_template('commsearch.html',base64=base64)
	if (request.method=='POST'):

		comment= request.form.get('comment')				#getting user id from comment
		useridfromcomment = getUserIdfromComment(comment)	

		userarr = []
		idarr = []
		#for u in useridfromcomment:
		#	idarr.append(u[0])
		#print(idarr)
		for usertuple in useridfromcomment:				#iterating tuple of tuple to just get the id
				nametuple = getNamefromID(usertuple[0])
				for name in nametuple:
						userarr.append(name[0]+ " " + name[1])
		print(userarr)
		return render_template('commsearch.html',userl=userarr, base64=base64)
@app.route("/topten",methods=['GET','POST'])
def topten():
	#useractivity = number photos + comments - own comments
	ids = getAllId()
	activityarr= [] 			#calculating the activity arr, do not need to subtract comments on own posts because users cannot do that
	for id in ids:
		
		nametuple =getNamefromID(id[0])
		for name in nametuple:
						nameee = name[0]+ " " + name[1]
		numPhotos= getNumPhotos(id[0])[0][0]
		numComments = getNumComments(id[0])[0][0]
		activityarr.append((nameee,(numPhotos+numComments)))			#making a list of the names and that persons activity

	activityarr.sort(key = lambda x: x[1],reverse=True)		#sorting and truncating list to top ten
	del activityarr[10:]

	return render_template("topten.html",namesl=activityarr,base64=base64)
#jonend
@app.route("/createalbum",methods=['GET','POST'])
@flask_login.login_required
def createalbum():
	if request.method=='POST':
		uid = getUserIdFromEmail(flask_login.current_user.id)
		try:
			albumname=request.form.get('albumname')
		except:
			print("couldn't find all tokens") #this prints to shell, end users will not see this (all print statements go to shell)
			return flask.redirect(flask.url_for('createalbum'))
		currentdate=datetime.now()
		cursor = conn.cursor()
		print(cursor.execute("INSERT INTO Album (dates, album_name) VALUES ('{0}', '{1}')".format(currentdate,albumname)))

		aid=cursor.lastrowid

		print(cursor.execute("INSERT INTO Creates (user_id, album_id) VALUES ('{0}', '{1}')".format(uid,aid)))
		conn.commit()

		aids=getAlbums(uid)
		aids_and_anames=[]
		for a in aids:
			aids_and_anames+=getAlbumIDandNameFromId(a[0])

		return render_template('albumslist.html',albumids_and_albumnames=aids_and_anames)
	else:
		uid = getUserIdFromEmail(flask_login.current_user.id)
		return render_template('createalbum.html')
	

@app.route("/myalbums",methods=['GET'])
@flask_login.login_required
def myalbums():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	aids=getAlbums(uid)
	aids_and_anames=[]
	for a in aids:
		aids_and_anames+=getAlbumIDandNameFromId(a[0])

	return render_template('albumslist.html',albumids_and_albumnames=aids_and_anames)

@app.route("/addtoalbum",methods=['GET', 'POST'])
@flask_login.login_required
def addtoalbum():
	if (request.method=='GET'):
		uid = getUserIdFromEmail(flask_login.current_user.id)
		aids=getAlbums(uid)
		aids_and_anames=[]
		for a in aids:
			aids_and_anames+=getAlbumIDandNameFromId(a[0])
		return render_template('addtoalbum.html', photos=getUsersPhotos(uid), albumids_and_albumnames=aids_and_anames,base64=base64)
	elif (request.method=='POST'):
		uid = getUserIdFromEmail(flask_login.current_user.id)
		aids=getAlbums(uid)
		aids_and_anames=[]
		for a in aids:
			aids_and_anames+=getAlbumIDandNameFromId(a[0])
		aid=request.form.get('albumid')
		pid=request.form.get('photoid')
		cursor = conn.cursor()
		cursor.execute("UPDATE Contain SET album_id='{0}', picture_id='{1}' WHERE picture_id='{1}'".format(aid,pid))
		conn.commit()
		return render_template('albumslist.html',albumids_and_albumnames=aids_and_anames,base64=base64)

@app.route("/viewalbum",methods=['GET', 'POST'])
def viewalbum():
	if (request.method=='GET'):
		aids=getAllAlbumIds() #getting every album id
		aids_and_anames=[]
		for a in aids:
			aids_and_anames+=getAlbumIDandNameFromId(a[0])
		return render_template('viewalbum.html', albumids_and_albumnames=aids_and_anames)
	elif (request.method=='POST'):
		aid=request.form.get('albumid')
		aids=getAllAlbumIds() #getting every album id
		aids_and_anames=[]

		pids=getAllPhotosFromAlbum(aid)
		#print(pids)
		photoslist=[]

		for p in pids:
			#print(p[0])
			photoslist+=getPhotoFromPhotoId(p[0])
		for a in aids:
			aids_and_anames+=getAlbumIDandNameFromId(a[0])
		return render_template('viewalbum.html', photos=photoslist, base64=base64)

@app.route("/deletealbum",methods=['GET', 'POST'])
def deletealbum():
	if (request.method=='GET'):
		aids=getAllAlbumIds() #getting every album id
		aids_and_anames=[]
		for a in aids:
			aids_and_anames+=getAlbumIDandNameFromId(a[0])
		return render_template('deletealbum.html', albumids_and_albumnames=aids_and_anames)
	elif (request.method=='POST'):
		aid=request.form.get('albumid')
		
		aids=getAllAlbumIds() #getting every album id
		aids_and_anames=[]

		pids=getAllPhotosFromAlbum(aid)

		for p in pids: #deleting photos
			deletePhotofromPhotoId(p[0])
		delteAlbumFromAlbumId(aid) #delete album

		for a in aids:
			aids_and_anames+=getAlbumIDandNameFromId(a[0]) #getting the remaining albums


		

		return render_template('deletealbum.html', albumids_and_albumnames=aids_and_anames)		

@app.route("/deletephoto",methods=['GET', 'POST'])
@flask_login.login_required
def deletephoto():
	if (request.method=='GET'):
		uid = getUserIdFromEmail(flask_login.current_user.id)
		return render_template('deletephoto.html', photos=getUsersPhotos(uid), base64=base64)
	elif (request.method=='POST'):
		uid = getUserIdFromEmail(flask_login.current_user.id)
		pid=request.form.get("photoid")
		deletePhotofromPhotoId(pid)
		conn.commit()
		return render_template('deletephoto.html', photos=getUsersPhotos(uid), base64=base64)
		
@app.route("/createtag",methods=['GET','POST'])
@flask_login.login_required
def createtag():
	if request.method=='POST':
		tagname=request.form.get("tagname")
		cursor = conn.cursor()
		cursor.execute("INSERT INTO Tag (word_desc) VALUES ('{0}')".format(tagname))
		conn.commit()
		ts=getAllTags()
		return render_template('createtag.html',tags=ts)
	else:
		ts=getAllTags()
		return render_template('createtag.html', tags=ts)

@app.route("/viewtag",methods=['GET','POST'])
def viewtag():
	if (request.method=='GET'):
		ts=getAllTags()
		return render_template('viewtag.html', tags=ts, base64=base64)
	elif (request.method=='POST'):
		ts=getAllTags()
		tagname=request.form.get("tag")
		pid=request.form.get("photoid")
		photoslist=[]
		pids=getPhotoIdsFromTag(tagname)
		for p in pids:
			photoslist+=getPhotoFromPhotoId(p[0])
		
		return render_template('viewtag.html', tags=ts, phototag=photoslist, base64=base64)

@app.route("/viewowntag",methods=['GET','POST']) #shows only the photos you own with a certain tag
@flask_login.login_required
def viewowntag():
	if (request.method=='GET'):
		ts=getAllTags()
		return render_template('viewowntag.html', tags=ts, base64=base64)
	elif (request.method=='POST'):
		uid=getUserIdFromEmail(flask_login.current_user.id)
		ts=getAllTags()
		tagname=request.form.get("tag")
		pid=request.form.get("photoid")
		photoslist=[]

		#pids=getPhotoIdsFromTag(tagname)#
		pids=getPhotoIdsFromTag(tagname)
		newpids=[] #all the photo ids of the photos in the tag
		for p in pids:
			newpids+=[p[0]]
		#print(newpids)


		userspids=getUsersPhotoIds(uid)
		newuserspids=[] #all the photo ids of the photos the current user owns
		for up in userspids:
			newuserspids+=[up[0]]



		#print(newuserspids)
		#print(newpids)
		intersectionpids = [x for x in newuserspids if x in newpids]

		#print(intersectionpids)
		for p in intersectionpids:

			photoslist+=getPhotoFromPhotoId(p)#
		
		return render_template('viewowntag.html', tags=ts, phototag=photoslist, base64=base64)

@app.route("/viewpopulartags",methods=['GET','POST'])
def viewpopulartags():
	if (request.method=='GET'):
		ts=getAllTags() #tuple form
		tags=[] #string form
		tsizes=[]

		#### changes the tags into a dictionary where the key is the tag name and the value is the number of photos with that tag ex:{food:5, exercise:12}

		for t in ts:
			#print(t)
			#print(t[0])
			tags+=[t[0]]
			tsizes+=[getPhotoIdsFromTag(t[0])]
		#print(tsizes)

		lengths=[]
		for t in tsizes:
			lengths+=[len(t)]
		#print(lengths)

		
		dict = {tags[i]: lengths[i] for i in range(len(lengths))}
		#print(dict)

		####

		topten=sorted(dict, key=dict.get, reverse=True) #turns the dictionary into a sorted list of the tag names (sorted by how many pictures are tagged by a certain tag)
		#print(topten)
		if (len(topten)>10):
			topten=topten[:10]
		#print(topten)

		return render_template('viewpopulartags.html', mostpopular=topten, base64=base64)
	elif (request.method=='POST'):
		ts=getAllTags()
		tagname=request.form.get("tag")
		pid=request.form.get("photoid")
		photoslist=[]
		pids=getPhotoIdsFromTag(tagname)
		for p in pids:
			photoslist+=getPhotoFromPhotoId(p[0])
		
		return render_template('viewpopulartags.html', tags=ts, phototag=photoslist, base64=base64) #viewpopulartags submit currently sends a post to viewtag instead

@app.route("/viewmultipletags",methods=['GET','POST'])
def viewmultipletags():
	if (request.method=='GET'):
		ts=getAllTags()
		return render_template('viewmultipletags.html', tags=ts, base64=base64)
	elif (request.method=='POST'):
		ts=getAllTags()
		tagnames=(request.form.get("tag")).split()
		tagscount=len(tagnames) #how many tags there are
		photoslist=[]
		pidslist=[]
		for t in tagnames:

			pidslist+=list(getPhotoIdsFromTag(t))

		newpidslist=[]
		for i in pidslist:
			newpidslist+=[i[0]]

		taggedwithall=[]
		for i in newpidslist:
			if (newpidslist.count(i)==tagscount):
				taggedwithall+=[i]
		
		for p in taggedwithall:
			photoslist+=getPhotoFromPhotoId(p)

		return render_template('viewmultipletags.html', tags=ts, phototag=photoslist, base64=base64)

@app.route("/addtotag",methods=['GET','POST'])
@flask_login.login_required
def addtotag():
	if request.method=='POST':
		tagname=request.form.get("tag")
		pid=request.form.get("photoid")
		cursor = conn.cursor()
		cursor.execute("INSERT INTO Describes (word_desc, picture_id) VALUES ('{0}', '{1}')".format(tagname, pid))
		conn.commit()
		ts=getAllTags()
		photoslist=[]
		pids=getPhotoIdsFromTag(tagname)
		for p in pids:
			photoslist+=getPhotoFromPhotoId(p[0])
		return render_template('addtotag.html',tags=ts, phototag=photoslist,base64=base64)
	else:
		uid = getUserIdFromEmail(flask_login.current_user.id)
		ts=getAllTags()

		return render_template('addtotag.html', tags=ts, photos=getUsersPhotos(uid),base64=base64)

@app.route("/youmayalsolike",methods=['GET'])
@flask_login.login_required
def youmayalsolike():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	ulikes=getallLikesFromUserId(uid) #all the likes the current user has made
	#print(list(ulikes))
	newulikes=[]
	for ul in list(ulikes): #extracts the ids of the pictures the user liked
		newulikes+=[ul[0]]
	#print(newulikes)
	tags=[]
	for ul in newulikes:
		tags+=list(getTagsFromPhotoId(ul))
	#print(tags)

	newtags=[]
	for t in tags: #extracting the tag values from the tuple
		newtags+=[t[0]]
	#print(newtags)

	photoslist=[] #list of recs
	for t in newtags:
		pids=getPhotoIdsFromTag(t) #gets the photos from the tags
		for p in pids:
			photoslist+=getPhotoFromPhotoId(p[0]) #adds the photos

	return render_template('youmayalsolike.html', phototag=photoslist,base64=base64)

###gavinend
###jonbegin--------------------------------------
@app.route("/friends",methods=['GET','POST'])
@flask_login.login_required
def friends():
	if (request.method== 'GET'):
		uid = getUserIdFromEmail(flask_login.current_user.id)
		friendos=getFriends()
		idd = getFriendsID()
		recomendationarray = []
		for i in idd:
			for tupe in i:
				idvar = tupe
				recomendationarray += [getFriendsofFriends(idvar)]
		return render_template('friends.html',  friendos=getFriends(), arr = recomendationarray)
	if request.method=='POST':
		uid = getUserIdFromEmail(flask_login.current_user.id)
		try:
			newfriendid=request.form.get('user_id')
			print(newfriendid)
			neee= request.form.get('sadasdasd')
			print("--------------")
			print(neee)
			if (neee == None):
				print('ahahahahah')
			print("--------------")
			print(newfriendid)
			nametuple = getNamefromID(newfriendid)
			namestring = "-1"
			for names in nametuple:
				namestring = names[0] + " " + names[1]
				
			
			

					
		except:
			print("couldn't find all tokens") #this prints to shell, end users will not see this (all print statements go to shell)
		
		cursor = conn.cursor()
		if (namestring == "-1"):										#case where userid input it does not match database
			recomendationarray = []
			idd = getFriendsID()
			for i in idd:
				for tupe in i:
					idvar = tupe
					recomendationarray += [getFriendsofFriends(idvar)]			
			return render_template('friends.html',friendos = getFriends(),notfound = 1,arr=recomendationarray)
		usertuplename =getNamefromID(uid)								#getting the name of the current logged in user
		for firstandlast in usertuplename:
				username = firstandlast[0] + " " + firstandlast[1]

		print(cursor.execute("INSERT INTO Friends (user_id, user_friend_id, friend_name) VALUES ('{0}', '{1}','{2}')".format(uid,newfriendid,namestring)))
		print(cursor.execute("INSERT INTO Friends (user_id, user_friend_id, friend_name) VALUES ('{0}', '{1}','{2}')".format(newfriendid,uid,username)))
		aid=cursor.lastrowid

		conn.commit()
		recomendationarray = []
		idd = getFriendsID()
		for i in idd:
			for tupe in i:
				idvar = tupe
				recomendationarray += [getFriendsofFriends(idvar)]

		return render_template('friends.html',friendos = getFriends(),arr = recomendationarray)

	
###jonend---------------------------------------

if __name__ == "__main__":
	#this is invoked when in the shell  you run
	#$ python app.py
	app.run(port=5000, debug=True)
