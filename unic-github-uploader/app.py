# from logging import log
from flask import render_template, redirect, Flask, session, request, url_for, jsonify
from flask_session import Session
import requests
# import requests
from datetime import datetime
from flask_wtf.csrf import CSRFProtect
from flask_simple_geoip import SimpleGeoIP
from mpu import haversine_distance
from werkzeug.utils import secure_filename
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from authlib.integrations.flask_client import OAuth

# this cuz relative imports are messed up
try:
    from helpers import getConnection, executeWriteQuery, executeReadQuery, login_required
except ImportError:
    from .helpers import getConnection, executeReadQuery, executeWriteQuery, login_required


# setup application secret key, config and csrf protection
app = Flask(__name__)
app.secret_key = '5yTuleqqRRdRwvCf'
app.config.from_object("config")
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# add csrf and geoip service
csrf = CSRFProtect(app)
app.config.update(GEOIPIFY_API_KEY='at_KIgYTxO7GSB26ukH0av9aCEC2IUCQ')
simple_geoip = SimpleGeoIP(app)


# add google oauth verification
Session(app)
GOOGLE_METADATA_URL = "https://accounts.google.com/.well-known/openid-configuration"
GOOGLE_USER_PROFILE_URL = "https://www.googleapis.com/oauth2/v1/userinfo"
oauth = OAuth(app)
google = oauth.register(
    name="google",
    server_metadata_url=GOOGLE_METADATA_URL,
    client_kwargs={'scope': 'openid email profile'},
)


# initialise important vars
names = ("Prakamya Singh", "Praneeth Suresh", "Pratyush Bansal", "Rahul Rajkumar",)
categories = ("Books", "Stationary", "Clothing", "Household", "Sports", "Electronics", "Toys", "Decorations", "Assorted",)
allowed_files = ("png", "jpg", "jpeg", "gif",)
db = getConnection("unic.db")


# login route
@app.route('/login')
def login():
    redirect_uri = url_for('authorize', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


# authorize google oauth access
@app.route('/authorize')
@csrf.exempt
def authorize():
    token = oauth.google.authorize_access_token()
    user_info = requests.get(f"{GOOGLE_USER_PROFILE_URL}?access_token={token['access_token']}").json()

    if len(executeReadQuery(db, "SELECT username FROM users WHERE user_id = ?;", (user_info["id"],))) == 0:
        authorize.user_storage_info = (user_info["id"], user_info["email"], f"{user_info['given_name']} {user_info['family_name']}", user_info["picture"])
        return redirect("/user_info")
    

    session["email"] = user_info["email"]
    session["user_id"] = user_info["id"]
    session["username"] = executeReadQuery(db, "SELECT username FROM users WHERE user_id = ?", (session["user_id"],))[0][0]
    return redirect('/')


# complete user profile(for first-time sign in)
@app.route("/user_info", methods=["GET", "POST"])
def user_info():
    if request.method == "GET":
        userinfo = authorize.user_storage_info
        return render_template("user_info.html", username=userinfo[2], id=userinfo[0], pic=userinfo[3], email=userinfo[1])

    username = request.form.get("username")
    bio = request.form.get("bio")
    email = request.form.get("email")
    phone_num = request.form.get("phone_num")
    location = request.form.get("location")
    long = request.form.get("long")
    lat = request.form.get("lat")
    pic = request.form.get("pic")
    user_id = request.form.get("user_id")

    query = "INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);"
    vals = (user_id, username, bio, email, pic, phone_num, lat, long, location)

    if executeWriteQuery(db, query, vals):
        session["email"] = email
        session["user_id"] = user_id
        session["username"] = username
        return redirect("/")


# user can check account information
@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    if request.method == "GET":
        query = "SELECT picture, phone_num, location, bio FROM users WHERE user_id = ?"
        xtra_info = executeReadQuery(db, query, (session["user_id"],))[0]
        account_info = (session["email"], session["username"], xtra_info[0], xtra_info[1], xtra_info[2], xtra_info[3])
        query = "SELECT * FROM mentors WHERE mentor = ?"
        mentorships = executeReadQuery(db, query, (session["user_id"],))
        query = "SELECT * FROM listings WHERE seller = ? AND availability = 1"
        listings_uploaded = executeReadQuery(db, query, (session["user_id"],))
        return render_template("account.html", info=account_info, mentorships=mentorships, listings=listings_uploaded)
    
    username = request.form.get("username")
    bio = request.form.get("bio")
    phone_num = request.form.get("phone_num")
    location = request.form.get("location")
    lat = request.form.get("lat")
    long = request.form.get("long")
    session["username"] = username
    query = "UPDATE users SET bio = ?, username = ?, phone_num = ?, location = ?, latitude = ?, longitude = ? WHERE user_id = ?"
    vals = (bio, username, phone_num, location, lat, long, session["user_id"])
    if executeWriteQuery(db, query, vals):
        return redirect("/account")


# home page
@app.route("/")
def homepage():
    if session.get("user_id", None):
        return render_template("home.html", logged_in=True)
    return render_template("home.html", logged_in=False)


# logout the user
@app.route('/logout')
@login_required
def logout():
    session.clear()
    return redirect('/')


# user can sell items
@app.route('/uni_shop/sell', methods=["GET", "POST"])
@login_required
def sell():
    if request.method == "GET":
        # render the form to sell an item
        return render_template("sell.html", categories=categories)

    # get the item details
    category = request.form.get("category")
    if not category or category not in categories:
        category = "Assorted"
    usage = request.form.get("usage")
    if not usage:
        usage = "old"
    item_name = request.form.get("item_name")
    proddesc = request.form.get("item_descr")
    timestamp = datetime.now().strftime("%B %d, %Y %H:%M:%S")
    price = float(request.form.get("price"))
    img = request.files.get("item_img")
    filename = img.filename
    file_type = filename.split(".")[-1]
    if file_type not in allowed_files:
        return render_template("sell.html", file_problem=True)
    item_id = executeReadQuery(db, "SELECT COUNT(listing_id) FROM listings;")[0][0]+1
    file_route = f"static/img/listings/listing-img-{item_id}.png"
    img.save(file_route)
    query = "INSERT INTO listings (seller, item_name, description, category, usage, availability, timestamp, price) VALUES (?, ?, ?, ?, ?, 1, ?, ?);"
    values = (session["user_id"], item_name, proddesc, category, usage, timestamp, price,)
    # insert the new item into db
    if executeWriteQuery(db, query, values):
        return render_template("sell.html", sold=True)


# show all available items
@app.route("/uni_shop")
@login_required
def uni_shop():
    query = "SELECT * FROM listings WHERE availability = 1 ORDER BY listing_id DESC;"
    listings_data = executeReadQuery(db, query)
    listings = []
    for l in listings_data:
        uploader = executeReadQuery(db, "SELECT username FROM users WHERE user_id = ?", (l[1],))[0]
        l += uploader
        listings.append(l)
    return render_template("shop.html", listings=listings)


# show details on particular item
@app.route("/uni_shop/item/<int:listing_id>")
@login_required
def see_item(listing_id):
    query = "SELECT * FROM listings WHERE listing_id = ?"
    listing = executeReadQuery(db, query, (listing_id,))[0]
    query = "SELECT username, phone_num, latitude, longitude, location FROM users WHERE user_id = ?"
    seller = executeReadQuery(db, query, (listing[1],))[0]
    user = executeReadQuery(db, "SELECT latitude, longitude FROM users WHERE user_id = ?", (session["user_id"],))[0]
    dist = haversine_distance((seller[2], seller[3],), (user[0], user[1],))
    if dist >= 1:
        display_dist = f"{dist:.1f} km"
    else:
        display_dist = f"{dist:.1f} meters"
    return render_template("see_item.html", listing=listing, seller=seller, dist=dist, display_dist=display_dist)


@app.route("/uni_shop/item/mark_sold/<int:listing_id>")
@login_required
def mark_as_sold(listing_id):
    query = "SELECT seller FROM listings WHERE listing_id = ?"
    seller = executeReadQuery(db, query, (listing_id,))[0][0]
    if seller != session["user_id"]:
        return render_template("nope.html")
    
    query = "UPDATE listings SET availability = 0 WHERE listing_id = ?"
    if executeWriteQuery(db, query, (listing_id,)):
        return redirect("/account")



# filter items in store by category and usage
@app.route("/uni_shop/filter", methods=["GET", "POST"])
@login_required
def choices():
    if request.method == "GET":
        # render form to filter out items in shop
        return render_template('shop_filter.html', categories=categories)

    # get the user's choices and make them available to other functions
    choices.category = request.form.get("category")
    choices.usage = request.form.get("usage")
    return redirect("/uni_shop/filter/results")


# show filtered items
@app.route("/uni_shop/filter/results")
@login_required
def findlistings():
    # filter items from db using user's choice
    if choices.usage == "any":
        query = "SELECT * FROM listings WHERE availability = 1 AND category = ? ORDER BY listing_id DESC;"
        listings_data = executeReadQuery(db, query, (choices.category,))
    else:
        query = "SELECT * FROM listings WHERE availability = 1 AND category = ? AND usage = ? ORDER BY listing_id DESC;"
        listings_data = executeReadQuery(db, query, (choices.category, choices.usage,))
    listings = []
    for l in listings_data:
        uploader = executeReadQuery(db, "SELECT username FROM users WHERE user_id = ?", (l[1],))[0]
        l += uploader
        listings.append(l)
    return render_template("shop.html", listings=listings)


# redirect to chat with mentor
@app.route("/uni_shop/item/chat/redirect", methods=["GET", "POST"])
@login_required
def processing():
    if request.method == "GET":
        return redirect("/uni_shop")
        
    phone_num = request.form.get("phone_num")
    x = phone_num.split()
    phone_num = "".join(x)
    return redirect(f"https://wa.me/{phone_num}")


# sign up as a mentor
@app.route('/mentor/signup', methods=["GET", "POST"])
@login_required
def signmentor():
    if request.method == "GET":
        # render form to sign up as mentor
        return render_template("sign_mentor.html")

    # get the user's area chosen and self-description
    area = request.form.get("expertin")
    descr = request.form.get("descr")
    query = "INSERT INTO mentors (mentor, description, area) VALUES (?, ?, ?);"
    values = (session["user_id"], descr, area,)
    # add user into db
    if executeWriteQuery(db, query, values):
        return render_template("sign_mentor.html", registered=True)


# resign a mentorship
@app.route("/mentor/resign/<int:mentor_id>")
@login_required
def resign(mentor_id):
    query = "SELECT mentor FROM mentors WHERE mentor_id = ?"
    mentor = executeReadQuery(db, query, (mentor_id,))[0][0]
    if mentor != session["user_id"]:
        return render_template("nope.html")
    
    query = "DELETE FROM mentors WHERE mentor_id = ?"
    if executeWriteQuery(db, query, (mentor_id,)):
        return redirect("/account")


# search for a mentor based on area of expertise
@app.route("/mentor/search", methods=["GET", "POST"])
@login_required
def mentorpreferences():
    if request.method == "GET":
        return render_template('mentor_search.html')

    mentorpreferences.area = request.form.get("expertin")
    return redirect("/mentor/search/results")


# filter out mentors based on chosen area of expertise
@app.route("/mentor/search/results")
@login_required
def mentorlistings():
    query = "SELECT * FROM mentors WHERE area = ? ORDER BY mentor_id DESC;"
    area = mentorpreferences.area
    mentors_data = executeReadQuery(db, query, (area,))
    mentors = []
    for m in mentors_data:
        uploader = executeReadQuery(db, "SELECT username FROM users WHERE user_id = ?", (m[1],))[0]
        m += uploader
        mentors.append(m)
    return render_template('mentor_results.html', mentors=mentors, area=area)


# see mentor details
@app.route("/mentor/mentor_id/<int:mentor_id>")
@login_required
def show_mentor(mentor_id):
    query = "SELECT * FROM mentors WHERE mentor_id = ?"
    mentor = executeReadQuery(db, query, (mentor_id,))[0]
    query = "SELECT username, phone_num, latitude, longitude, location FROM users WHERE user_id = ?"
    guy = executeReadQuery(db, query, (mentor[1],))[0]
    user = executeReadQuery(db, "SELECT latitude, longitude FROM users WHERE user_id = ?", (session["user_id"],))[0]
    dist = haversine_distance((guy[2], guy[3],), (user[0], user[1],))
    if dist >= 1:
        display_dist = f"{dist:.1f} km"
    else:
        display_dist = f"{dist:.1f} meters"
    return render_template("see_mentor.html", mentor=mentor, guy=guy, dist=dist, display_dist=display_dist)


# redirect to chat with mentor
@app.route("/mentor/mentor_id/chat/redirect", methods=["GET", "POST"])
@login_required
def processing1():
    if request.method == "GET":
        return redirect("/mentor/search")
    
    phone_num = request.form.get("phone_num")
    x = phone_num.split()
    phone_num = "".join(x)
    return redirect(f"https://wa.me/{phone_num}")


# error handling
def errorhandler(e):
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return render_template("error.html", name=e.name, code=e.code, description=e.description)

# listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

# show info about website(pretty useless but we'll keep it)
@app.route("/about")
@login_required
def about():
    return render_template('about.html', names=names)

if __name__ == "__main__":
    app.run()