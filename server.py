"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import (Flask, render_template, redirect, request, 
                   flash, session)

from flask_debugtoolbar import DebugToolbarExtension

from model import User, Rating, Movie, connect_to_db, db


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""

    return render_template("homepage.html")


@app.route("/users")
def user_list():
    """Show list of users."""

    users = User.query.all()
    return render_template("users_list.html", users=users)


@app.route("/users/<int:user_id>")
def user(user_id):
    """Shows info about a user."""

    user = User.query.get(user_id)
    return render_template("user.html", user=user)


@app.route("/movies")
def movie_list():
    """Show list of movies."""

    movies = Movie.query.order_by(Movie.title).all()

    return render_template("movies_list.html", movies=movies)


@app.route("/movies/<int:movie_id>")
def movie(movie_id):

    movie = Movie.query.get(movie_id)
    return render_template("movie.html", movie=movie)


@app.route("/register", methods=["GET"])
def register_form():

    email = request.args.get("email")
    password = request.args.get("password")

    return render_template("register_form.html",
                           email=email,
                           password=password)


@app.route("/register", methods=["POST"])
def register_process():

    email = request.form.get("email")
    password = request.form.get("password")

    if User.query.filter(User.email == email).all():
        flash("This email address is already registered.")
        return render_template("register_form.html")
    else:
        sql = """INSERT INTO users (email, password)
                 VALUES (:email, :password)
              """

        db.session.execute(sql,
                           {'email': email,
                            'password': password})

        db.session.commit()
        flash("Thank you for registering!")
        return redirect("/")


@app.route("/login", methods=["GET"])
def login_form():

    email = request.args.get("email")
    password = request.args.get("password")

    return render_template("login_form.html",
                           email=email,
                           password=password)


@app.route("/login", methods=["POST"])
def login_process():

    email = request.form.get("email")
    password = request.form.get("password")

    if User.query.filter(User.email == email).all():

        if User.query.filter(User.email == email).one().password == password:
            
            # query for user id on existing email, add to session
            user_id = User.query.filter(User.email == email).one().user_id 
            session["user_id"] = user_id

            flash("Login successful!")
            return redirect("/")

    flash("Your email and password don't match. Please try again!")
    return render_template("login_form.html")


@app.route("/logged_out", methods=["POST"])
def log_out():

    # print "/logged out working!!!"
    # session.clear()
    print session
    del session["user_id"]
    print session
    return redirect("/")


@app.route("/rate", methods=["POST"])
def rate_movie():

    score = request.form.get("rating")
    movie_id = request.form.get("movie_id")
    user_id = session["user_id"]

    rating = Rating.query.filter(Rating.user_id == user_id, Rating.movie_id==movie_id).first()
    if rating:    

        rating.score = score
        flash("Thank you for updating your rating!")

    else:
       
        rating = Rating(score=score,
                        movie_id=movie_id,
                        user_id=user_id
                        )

        db.session.add(rating)
        flash("Thank you for rating!")

    db.session.commit()
    
    return redirect("/movies")



if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    app.jinja_env.auto_reload = app.debug  # make sure templates, etc. are not cached in debug mode

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)



    app.run(port=5000, host='0.0.0.0')
