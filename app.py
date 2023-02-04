 # Flask application

import psycopg2
import psycopg2.extras
from flask import Flask, request, render_template, g, current_app

# initialize Flask
app = Flask(__name__)

####################################################
# Routes


@app.route("/")
def homepage():
    return render_template('home.html')


@app.route("/browse_recipes", methods=['get', 'post'])
def browse_recipes():
    # Display all the recipes on the page
    if "step" not in request.form:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('select dishid, title from dish')
        rowlist = cursor.fetchall()
        return render_template('browse_recipes.html', step="display_recipes", recipes=rowlist)

    # Display information for the recipe selected by the user
    elif request.form["step"] == "display_recipe":
        conn = get_db()
        cursor = conn.cursor()
        dishid = str(request.form["dishid"])

        cursor.execute('select dishid, title, directions, time_amt from dish where dishid=%s', [dishid])
        recipe = cursor.fetchone()

        cursor.execute('select distinct(toolName) from uses where dishid=%s', [dishid])
        tools = cursor.fetchall()

        cursor.execute('select distinct(ingredientName) from contains where dishid=%s', [dishid])
        ingredients = cursor.fetchall()

        cursor.execute('select distinct(categoryName) from belongsto where dishid=%s', [dishid])
        categories = cursor.fetchall()

        return render_template('browse_recipes.html', step="display_recipe", recipe=recipe, tools=tools, ingredients=ingredients, categories=categories)


@app.route("/browse_categories", methods=['get', 'post'])
def browse_categories():
    # Display all the catgories of recipes
    if "step" not in request.form:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('select categoryName, categoryDescription from category')
        categories = cursor.fetchall()
        return render_template('browse_categories.html', step="display_categories", categories=categories)

    # Display recipes that are in the selected category
    elif request.form["step"] == "display_recipes":
        conn = get_db()
        cursor = conn.cursor()
        categoryname = request.form["categoryname"]

        cursor.execute('select distinct(title), dishid, categoryname from dish natural join belongsto where categoryname=%s', [categoryname])
        recipes = cursor.fetchall()

        return render_template("browse_categories.html", step="display_recipes", recipes=recipes, categoryname=categoryname)

    # Display the recipe selected by the user
    elif request.form["step"] == "display_recipe":
        conn = get_db()
        cursor = conn.cursor()
        dishid = str(request.form["dishid"])

        cursor.execute('select dishid, title, directions, time_amt from dish where dishid=%s', [dishid])
        recipe = cursor.fetchone()

        cursor.execute('select distinct(toolName) from uses where dishid=%s', [dishid])
        tools = cursor.fetchall()

        cursor.execute('select distinct(ingredientName) from contains where dishid=%s', [dishid])
        ingredients = cursor.fetchall()

        cursor.execute('select distinct(categoryName) from belongsto where dishid=%s', [dishid])
        categories = cursor.fetchall()

        return render_template('browse_categories.html', step="display_recipe", recipe=recipe, tools=tools, ingredients=ingredients, categories=categories)


@app.route("/edit_recipe", methods=['get', 'post'])
def edit_recipe():
    # Display all the recipes
    if "step" not in request.form:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('select dishid, title from dish')
        rowlist = cursor.fetchall()
        return render_template('edit_recipe.html', step="display_recipes", recipes=rowlist)

    # Allow user to make edits to the recipe
    elif request.form["step"] == "make_edits":
        conn = get_db()
        cursor = conn.cursor()
        dishid = str(request.form["dishid"])

        cursor.execute('select dishid, title, directions, time_amt from dish where dishid=%s', [dishid])
        recipe = cursor.fetchone()

        cursor.execute('select distinct(toolName) from uses where dishid=%s', [dishid])
        tools = cursor.fetchall()

        cursor.execute('select distinct(ingredientName) from contains where dishid=%s', [dishid])
        ingredients = cursor.fetchall()

        cursor.execute('select distinct(categoryName) from belongsto where dishid=%s', [dishid])
        categories = cursor.fetchall()

        cursor.execute('select toolname from tool')
        alltools = cursor.fetchall()

        cursor.execute('select categoryname from category')
        allcategories = cursor.fetchall()

        return render_template('edit_recipe.html', step="make_edits", recipe=recipe, tools=tools, ingredients=ingredients, categories=categories, alltools=alltools, allcategories=allcategories)

    # Update the database with the changes made by the user
    elif request.form["step"] == "update_database":
        conn = get_db()
        cursor = conn.cursor()
        dishid = str(request.form["dishid"])
                
        cursor.execute("update dish set title=%s, directions=%s, time_amt=%s where dishid=%s", 
                       [request.form['title'], request.form['directions'], request.form['time_amt'], dishid])

        cursor.execute('select distinct(toolName) from uses where dishid=%s', [dishid])
        tools = cursor.fetchall()

        for tool in tools:
            newtool = request.form[tool[0]]
            if newtool != tool[0]:
                cursor.execute('delete from uses where dishid=%s and toolname=%s', [dishid, tool[0]])
                cursor.execute('insert into uses (dishid, toolname) values (%s, %s)', [dishid, newtool])

        cursor.execute('select distinct(ingredientName) from contains where dishid=%s', [dishid])
        ingredients = cursor.fetchall()

        for ingredient in ingredients:
            newingredient = request.form[ingredient[0]]
            if newingredient != ingredient[0]:
                cursor.execute('delete from contains where dishid=%s and ingredientname=%s', [dishid, ingredient[0]])
                cursor.execute('insert into contains (dishid, ingredientname) values (%s, %s)', [dishid, newingredient])

        cursor.execute('select distinct(categoryName) from belongsto where dishid=%s', [dishid])
        categories = cursor.fetchall()

        for category in categories:
            newcategory = request.form[category[0]]
            if newtool != category[0]:
                cursor.execute('delete from belongsto where dishid=%s and categoryname=%s', [dishid, category[0]])
                cursor.execute('insert into belongsto (dishid, categoryname) values (%s, %s)', [dishid, newcategory])

        conn.commit()
        
        return render_template('edit_recipe.html', step="update_database") 

        
@app.route("/delete_recipe", methods=['get', 'post'])
def delete_recipe():
    # Display all the recipes
    if "step" not in request.form:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('select dishid, title from dish')
        recipes = cursor.fetchall()
        return render_template('delete_recipe.html', step="display_recipes", recipes=recipes)

    # Delete the recipe from the database
    elif request.form["step"] == "delete_recipe":
        conn = get_db()
        cursor = conn.cursor()
        
        dishid = request.form["dishid"]

        cursor.execute('delete from uses where dishid=%s', [dishid])
        cursor.execute('delete from contains where dishid=%s', [dishid])
        cursor.execute('delete from reviews where dishid=%s', [dishid])
        cursor.execute('delete from favorites where dishid=%s', [dishid])
        cursor.execute('delete from belongsto where dishid=%s', [dishid])
        cursor.execute("delete from dish where dishid=%s", [dishid])
        conn.commit()
        
        return render_template("delete_recipe.html", step="delete_recipe")


@app.route("/create_account", methods=['get', 'post'])
def create_account():
    # Prompt user to create new account
    if "step" not in request.form:     
        return render_template('create_account.html', step="create_new_user")

    # Add user to the database
    elif request.form["step"] == "add_user":
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("insert into users (email, firstname, lastname) values (%s, %s, %s)",
                   [request.form['email'], request.form['firstname'], request.form['lastname']])
        conn.commit()
        return render_template("create_account.html", step="add_user") 


@app.route("/edit_account", methods=['get', 'post'])
def edit_account():
    # Display all the users
    if "step" not in request.form:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('select userid, email, firstname, lastname from users')
        rowlist = cursor.fetchall()
        return render_template('edit_account.html', step="display_users", users=rowlist)

    # Display forms for user to be able to edit info
    elif request.form["step"] == "make_edits":
        conn = get_db()
        cursor = conn.cursor()
        userid = request.form["userid"]

        cursor.execute('select userid, email, firstname, lastname from users where userid=%s', [userid])
        row = cursor.fetchone()
        
        return render_template("edit_account.html", step="make_edits", user=row)

    # Update database with changes made
    elif request.form["step"] == "update_database":
        conn = get_db()
        cursor = conn.cursor()
        userid = request.form["userid"]
                
        cursor.execute("update users set email=%s, firstname=%s, lastname=%s where userid=%s", 
                       [request.form['email'], request.form['firstname'], request.form['lastname'], userid])
        conn.commit()
        return render_template("edit_account.html", step="update_database")


@app.route("/delete_account", methods=['get', 'post'])
def delete_account():
    # Display all the users 
    if "step" not in request.form:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('select userid, email, firstname, lastname from users')
        users = cursor.fetchall()
        return render_template('delete_account.html', step="display_users", users=users)

    # Delete the user from the database
    elif request.form["step"] == "delete_user":
        conn = get_db()
        cursor = conn.cursor()
        
        userid = int(request.form["userid"])

        cursor.execute('delete from reviews where userid=%s', [userid])
        cursor.execute('delete from favorites where userid=%s', [userid])
        cursor.execute("delete from users where userid=%s", [userid])
        conn.commit()
        return render_template("delete_account.html", step="delete_user")


@app.route("/fav_recipe", methods=['get', 'post'])
def fav_recipe():
    if "step" not in request.form:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('select userid, email, firstname, lastname from users')
        users = cursor.fetchall()
        cursor.execute('select dishid, title from dish')
        recipes = cursor.fetchall()
        return render_template("fav_recipe.html", step="display_users_recipes", users=users, recipes=recipes)
    elif request.form["step"] == "update_database":
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("insert into favorites (userid, dishid) values (%s, %s)",
                   [request.form['userid'], request.form['dishid']])
        conn.commit()
        return render_template("fav_recipe.html", step="update_database")


@app.route("/unfav_recipe", methods=['get', 'post'])
def unfav_recipe():
    if "step" not in request.form:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('select userid, firstname, lastname from users')
        users = cursor.fetchall()
        return render_template("unfav_recipe.html", step="display_users", users=users)
        
    elif request.form["step"] == "display_favorites":
        conn = get_db()
        cursor = conn.cursor()
        userid = int(request.form['userid'])
        cursor.execute('select userid, dishid, title from favorites natural join dish where userid=%s', [userid])
        favorites = cursor.fetchall()
        return render_template("unfav_recipe.html", step="display_favorites", favorites=favorites, userid=userid)
        
    elif request.form["step"] == "update_database":
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('delete from favorites where userid=%s and dishid=%s', [request.form['userid'], request.form['dishid']])
        conn.commit()
        return render_template("unfav_recipe.html", step="update_database")


@app.route("/browse_reviews", methods=['get', 'post'])
def browse_reviews():
    # Display all the recipes
    if "step" not in request.form:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('select dishid, title from dish')
        rowlist = cursor.fetchall()
        return render_template('browse_reviews.html', step="display_recipes", recipes=rowlist)

    # Display review for the selected recipe
    elif request.form["step"] == "display_reviews":
        conn = get_db()
        cursor = conn.cursor()
        dishid = str(request.form["dishid"])

        cursor.execute('select title, firstname, lastname, numstars, reviewtext, numupvote from reviews natural join dish natural join users where dishID=%s', [dishid])
        reviews = cursor.fetchall()

        cursor.execute('select trunc(avg(numstars), 2) from reviews where dishid=%s', [dishid])
        avgstars = cursor.fetchone()

        return render_template('browse_reviews.html', step="display_reviews", reviews=reviews, avgstars=avgstars)


@app.route("/write_review", methods=['get', 'post'])
def write_review():
    # Display form for user to select user and recipe to review
    if "step" not in request.form:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('select userid, firstname, lastname from users')
        users = cursor.fetchall()

        cursor.execute('select dishid, title from dish')
        dishes = cursor.fetchall()
        
        return render_template("write_review.html", step="compose_review", users=users, dishes=dishes) 

    # Display form to add information for the review
    elif request.form["step"] == "add_review":
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("insert into reviews (userid, dishid, numstars, reviewtext, numupvote) values (%s, %s, %s, %s, 0)",
                   [request.form['userid'], request.form['dishid'], request.form['numstars'], request.form['reviewtext']])
        conn.commit()
        return render_template("write_review.html", step="add_review")


@app.route("/edit_review", methods=['get', 'post'])
def edit_review():
    if "step" not in request.form:
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute('select userid, firstname, lastname from users')
        users = cursor.fetchall()
    
        return render_template("edit_review.html", step="display_users", users=users)

    elif request.form["step"] == "display_reviews":
        conn = get_db()
        cursor = conn.cursor()
        userid = int(request.form['userid'])
        cursor.execute('select userID, dishID, title from reviews natural join dish where userID=%s', [userid])
        reviews = cursor.fetchall()
        
        return render_template("edit_review.html", step="display_reviews", reviews=reviews, userid=userid)

    elif request.form["step"] == "make_edits":
        conn = get_db()
        cursor = conn.cursor()
        dishid = request.form['dishid']
        userid = request.form['userid']
        cursor.execute('select userid, dishid, numStars, reviewText, numUpvote from reviews where userid=%s and dishid=%s', [userid, dishid])
        review = cursor.fetchone()
        
        return render_template("edit_review.html", step="make_edits", review=review, userid=userid, dishid=dishid)

    elif request.form['step'] == "update_database":
        conn = get_db()
        cursor = conn.cursor()
        dishid = request.form['dishid']
        userid = request.form['userid']
        cursor.execute("update reviews set numstars=%s, reviewtext=%s where userid=%s and dishid=%s",
                       [request.form['numstars'], request.form['reviewtext'], request.form['userid'], request.form['dishid']])
        conn.commit()
        
        return render_template("edit_review.html", step="update_database")


@app.route("/delete_review", methods=['get', 'post'])
def delete_review():
    if "step" not in request.form:
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute('select userid, firstname, lastname from users')
        users = cursor.fetchall()
    
        return render_template("delete_review.html", step="display_users", users=users)

    elif request.form["step"] == "display_reviews":
        conn = get_db()
        cursor = conn.cursor()
        userid = int(request.form['userid'])
        cursor.execute('select userID, dishID, title from reviews natural join dish where userID=%s', [userid])
        reviews = cursor.fetchall()
        
        return render_template("delete_review.html", step="display_reviews", reviews=reviews, userid=userid)

    elif request.form['step'] == "update_database":
        conn = get_db()
        cursor = conn.cursor()
        dishid = request.form['dishid']
        userid = request.form['userid']
        cursor.execute('delete from reviews where userid=%s and dishid=%s', [userid, dishid])
        conn.commit()
        return render_template("delete_review.html", step="update_database")


####################################################
# Database handling


def connect_db():
    """Connects to the database."""
    debug("Connecting to DB.")
    conn = psycopg2.connect(host="database.rhodescs.org",
                            user="fosjm-22",
                            password="fosjm-22",
                            dbname="practice",
                            cursor_factory=psycopg2.extras.DictCursor)
    return conn


def get_db():
    """Retrieve the database connection or initialize it. The connection
    is unique for each request and will be reused if this is called again.
    """
    if "db" not in g:
        g.db = connect_db()

    return g.db


@app.teardown_appcontext
def close_db(e=None):
    """If this request connected to the database, close the
    connection.
    """
    db = g.pop("db", None)

    if db is not None:
        db.close()
        debug("Closing DB")


@app.cli.command("initdb")
def init_db():
    """Clear existing data and create new tables."""
    conn = get_db()
    cur = conn.cursor()
    with current_app.open_resource("schema.sql") as file:  # open the file
        alltext = file.read()  # read all the text
        cur.execute(alltext)  # execute all the SQL in the file
    conn.commit()
    print("Initialized the database.")


@app.cli.command('populate')
def populate_db():
    conn = psycopg2.connect(host="database.rhodescs.org",
                            user="fosjm-22",
                            password="fosjm-22",
                            dbname="practice")
    cur = conn.cursor()

    with open('csvfiles/users.csv', 'r') as file:
        next(file)  # Skip the header row.
        cur.copy_from(file, 'users', sep=',')
    conn.commit()

    with open('csvfiles/category.csv', 'r') as file:
        next(file)  # Skip the header row.
        cur.copy_from(file, 'category', sep=',')
    conn.commit()

    with open('csvfiles/dish.csv', 'r') as file:
        next(file)  # Skip the header row.
        cur.copy_from(file, 'dish', sep=',')
    conn.commit()

    with open('csvfiles/favorites.csv', 'r') as file:
        next(file)  # Skip the header row.
        cur.copy_from(file, 'favorites', sep=',')
    conn.commit()

    with open('csvfiles/reviews.csv', 'r') as file:
        next(file)  # Skip the header row.
        cur.copy_from(file, 'reviews', sep=',')
    conn.commit()

    with open('csvfiles/tool.csv', 'r') as file:
        next(file)  # Skip the header row.
        cur.copy_from(file, 'tool', sep=',')
    conn.commit()

    with open('csvfiles/uses.csv', 'r') as file:
        next(file)  # Skip the header row.
        cur.copy_from(file, 'uses', sep=',')
    conn.commit()

    with open('csvfiles/belongsto.csv', 'r') as file:
        next(file)  # Skip the header row.
        cur.copy_from(file, 'belongsto', sep=',')
    conn.commit()

    with open('csvfiles/contains.csv', 'r') as file:
        next(file)  # Skip the header row.
        cur.copy_from(file, 'contains', sep=',')
    conn.commit()

    print("Populated DB with data.")


#####################################################
# Debugging


def debug(s):
    """Prints a message to the screen (not web browser) 
    if debugging is turned on."""
    if app.config['DEBUG']:
        print(s)


#####################################################
# App begins running here:

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080,
            debug=True)  # can turn off debugging with False
