from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from datetime import date, timedelta, datetime

app = Flask(__name__)

app.secret_key = '12345'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'ShYaM@4321'
app.config['MYSQL_DB'] = 'lms'
  
mysql = MySQL(app)

def update_fine():
        cur = mysql.connection.cursor()
        cur.execute('select U_ID, accession_number from Issue_Book')
        l1=cur.fetchall()
        for j in l1:
            cur.execute(
                'select due_date from Issue_Book where Issue_Book.U_Id=%s',
                ([j[0]]))
            list1 = cur.fetchall()
            sum = 0
            sums=0
            for i in list1:
                mdate1 = date.today()
                rdate1 = i[0]
                delta = (mdate1 - rdate1).days
                if delta >=0:
                    sums=(delta)*10
                    sum = sum + (delta)*10
                    cur.execute('update Issue_Book set fine=%s where U_Id=%s and accession_number=%s and due_date=%s', (sums, j[0],j[1],i[0],))
            cur.execute('update users set unpaid_fines=%s where U_Id=%s ', (sum, j[0],))
        mysql.connection.commit()
        cur.close()

def update_reserve():
        cur = mysql.connection.cursor()
        cur.execute('select accession_number,due_date from Reserve_Book')
        l1=cur.fetchall()
        for j in l1:
            tdate=date.today()
            if j[1] is not None:
                ddate = j[1]
                delta = (tdate-ddate).days
                if delta>0:
                    cur.execute('delete from Reserve_Book where accession_number=%s', (j[0],))
                    cur.execute('update book set book_reserve_status="no" where accession_number=%s ', (j[0],))
        mysql.connection.commit()
        cur.close()

@app.route('/',methods=['POST','GET'])
def home():
    update_fine()
    update_reserve()
    return render_template('home.html')

@app.route('/profile_lib',methods=['POST','GET'])
def profile_lib():
    update_fine()
    update_reserve()
    if 'loggedin' in session:
        e=session['email']
        p=session['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM librarian WHERE email = % s AND password = % s', (e, p,))
        account = cursor.fetchone()
        return render_template('profile_lib.html',lib_id=account['Lib_ID'], name=account['name'], email=account['email'], address=account['address'])


@app.route('/profile',methods=['POST','GET'])
def profile():
    update_fine()
    update_reserve()
    if 'loggedin' in session:
        e=session['email']
        p=session['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE email = % s AND password = % s', (e, p,))
        account = cursor.fetchone()
        return render_template('profile.html', U_ID=account['U_ID'], name=account['name'], email=account['email'], address=account['address'])

@app.route("/searchbook", methods=['GET', 'POST'])
def searchbook():
    update_fine()
    update_reserve()
    if request.method == 'POST':

        title = request.form.get("title")
        author = request.form['author']
        genre = request.form['genre']
        isbn = int(request.form['isbn'])
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if title == "" and author == "" and genre == "" and isbn == "":
            cur.execute(
                'SELECT ISBN, title, author, year_of_publication, genre, shelf_Id FROM book')
            result = cur.fetchall()

        elif title != "":
            if author == "" and genre == "" and isbn == "":
                query = "SELECT ISBN, title, author, year_of_publication, genre,shelf_Id FROM book where title LIKE '%{}%'".format(title)
                cur.execute(query)
                result = cur.fetchall()
            elif author == "" and genre == "" and isbn != "":
                query = "SELECT ISBN, title, author, year_of_publication, genre, shelf_Id FROM book where title LIKE '%{}%' and isbn <= '%{}%' ".format(title,isbn) 
                cur.execute(query)
                result = cur.fetchall()
            elif author == "" and genre != "" and isbn == "":
                query = "SELECT ISBN, title, author, year_of_publication, genre, shelf_Id FROM book where title LIKE '%{}%' and genre LIKE '%{}%' ".format(title,genre) 
                cur.execute(query)
                result = cur.fetchall()
            elif author == "" and genre != "" and isbn != "":
                query = "SELECT ISBN, title, author, year_of_publication, genre, shelf_Id FROM book where title LIKE '%{}%' and genre LIKE '%{}%' and isbn <= '%{}%' ".format(title,genre,isbn) 
                cur.execute(query)
                result = cur.fetchall()
            elif author != "" and genre == "" and isbn == "":
                query = "SELECT ISBN, title, author, year_of_publication, genre, shelf_Id FROM book where title LIKE '%{}%' and author LIKE '%{}%'".format(title,author)
                cur.execute(query)
                result = cur.fetchall()
            elif author != "" and genre == "" and isbn != "":
                query = "SELECT ISBN, title, author, year_of_publication, genre, shelf_Id FROM book where title LIKE '%{}%' and author LIKE '%{}%' and isbn <= '%{}%' ".format(title,author,isbn) 
                cur.execute(query)
                result = cur.fetchall()
            elif author != "" and genre != "" and isbn == "":
                query = "SELECT ISBN, title, author, year_of_publication, shelf_Id, genre FROM book where title LIKE '%{}%' and author LIKE '%{}%' and genre LIKE '%{}%' ".format(title,author,genre) 
                cur.execute(query)
                result = cur.fetchall()
            elif author != "" and genre != "" and isbn != "":
                query = "SELECT ISBN, title, author, year_of_publication, shelf_Id, genre FROM book where title LIKE '%{}%' and author LIKE '%{}%' and genre LIKE '%{}%' and isbn <= '%{}%' ".format(title,author,genre,isbn) 
                cur.execute(query)
                result = cur.fetchall()

        elif title == "" and author!="":
            if genre == "" and isbn == "":
                query = "SELECT ISBN, title, author, year_of_publication, genre, shelf_Id FROM book where author LIKE '%{}%'".format(author)
                cur.execute(query)
                result = cur.fetchall()
            elif genre == "" and isbn != "":
                query = "SELECT ISBN, title, author, year_of_publication, genre, shelf_Id FROM book where author LIKE '%{}%' and isbn <= '%{}%' ".format(author,isbn) 
                cur.execute(query)
                result = cur.fetchall()
            elif genre != "" and isbn == "":
                query = "SELECT ISBN, title, author, year_of_publication, genre, shelf_Id FROM book where author LIKE '%{}%' and genre LIKE '%{}%' ".format(author,genre) 
                cur.execute(query)
                result = cur.fetchall()
            elif genre != "" and isbn != "":
                query = "SELECT ISBN, title, author, year_of_publication, genre, shelf_Id FROM book where genre LIKE '%{}%' and author LIKE '%{}%' and isbn <= '%{}%' ".format(genre,author,isbn) 
                cur.execute(query)
                result = cur.fetchall()

        elif title == "" and author == "":
            if genre == "" and isbn != "":
                query = "SELECT ISBN, title, author, year_of_publication, genre, shelf_Id FROM book where isbn <= '%{}%'".format(isbn)
                cur.execute(query)
                result = cur.fetchall()
            elif genre != "" and isbn == "":
                query = "SELECT ISBN, title, author, year_of_publication, genre, shelf_Id FROM book where genre LIKE '%{}%'".format(genre)
                cur.execute(query)
                result = cur.fetchall()
            elif genre != "" and isbn != "":
                query = "SELECT ISBN, title, author, year_of_publication, genre, shelf_Id FROM book where isbn <= '%{}%' and genre LIKE '%{}%' ".format(isbn,genre) 
                cur.execute(query)
                result = cur.fetchall()
        mysql.connection.commit()
        cur.close()
        if result:
            return render_template('home.html', detail=result, msg="Result for the search", username="", email="")
        else:
            return render_template('home.html', detail="No records found", username="", email="")
    else:
        return render_template('home.html', username="", email="")


@app.route("/search_book_user", methods=['GET', 'POST'])
def search_book_user():
    update_fine()
    update_reserve()
    if request.method == 'POST':

        title = request.form.get("title")
        author = request.form['author']
        genre = request.form['genre']
        isbn = request.form['isbn']
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if title == "" and author == "" and genre == "" and isbn == "":
            cur.execute(
                'SELECT accession_number, ISBN, title, author, year_of_publication, genre,book_shelf_status, book_reserve_status FROM book')
            result = cur.fetchall()

        elif title != "":
            if author == "" and genre == "" and isbn == "":
                query = "SELECT accession_number, ISBN, title, author, year_of_publication, genre,book_shelf_status, book_reserve_status FROM book where title LIKE '%{}%'".format(title)
                cur.execute(query)
                result = cur.fetchall()
            elif author == "" and genre == "" and isbn != "":
                query = "SELECT accession_number, ISBN, title, author, year_of_publication, genre, book_shelf_status, book_reserve_status FROM book where title LIKE '%{}%' and isbn LIKE '%{}%' ".format(title,isbn) 
                cur.execute(query)
                result = cur.fetchall()
            elif author == "" and genre != "" and isbn == "":
                query = "SELECT accession_number, ISBN, title, author, year_of_publication, genre,book_shelf_status, book_reserve_status FROM book where title LIKE '%{}%' and genre LIKE '%{}%' ".format(title,genre) 
                cur.execute(query)
                result = cur.fetchall()
            elif author == "" and genre != "" and isbn != "":
                query = "SELECT accession_number, ISBN, title, author, year_of_publication, genre, book_shelf_status, book_reserve_status FROM book where title LIKE '%{}%' and genre LIKE '%{}%' and isbn LIKE '%{}%' ".format(title,genre,isbn) 
                cur.execute(query)
                result = cur.fetchall()
            elif author != "" and genre == "" and isbn == "":
                query = "SELECT accession_number, ISBN, title, author, year_of_publication, genre, book_shelf_status, book_reserve_status FROM book where title LIKE '%{}%' and author LIKE '%{}%'".format(title,author)
                cur.execute(query)
                result = cur.fetchall()
            elif author != "" and genre == "" and isbn != "":
                query = "SELECT accession_number, ISBN, title, author, year_of_publication, genre, book_shelf_status, book_reserve_status FROM book where title LIKE '%{}%' and author LIKE '%{}%' and isbn LIKE '%{}%' ".format(title,author,isbn) 
                cur.execute(query)
                result = cur.fetchall()
            elif author != "" and genre != "" and isbn == "":
                query = "SELECT accession_number, ISBN, title, author, year_of_publication, genre, book_shelf_status, book_reserve_status FROM book where title LIKE '%{}%' and author LIKE '%{}%' and genre LIKE '%{}%' ".format(title,author,genre) 
                cur.execute(query)
                result = cur.fetchall()
            elif author != "" and genre != "" and isbn != "":
                query = "SELECT accession_number, ISBN, title, author, year_of_publication, genre, book_shelf_status, book_reserve_status FROM book where title LIKE '%{}%' and author LIKE '%{}%' and genre LIKE '%{}%' and isbn LIKE '%{}%' ".format(title,author,genre,isbn) 
                cur.execute(query)
                result = cur.fetchall()

        elif title == "" and author!="":
            if genre == "" and isbn == "":
                query = "SELECT accession_number, ISBN, title, author, year_of_publication, genre,book_shelf_status, book_reserve_status FROM book where author LIKE '%{}%'".format(author)
                cur.execute(query)
                result = cur.fetchall()
            elif genre == "" and isbn != "":
                query = "SELECT accession_number, ISBN, title, author, year_of_publication, genre,book_shelf_status, book_reserve_status FROM book where author LIKE '%{}%' and isbn LIKE '%{}%' ".format(author,isbn) 
                cur.execute(query)
                result = cur.fetchall()
            elif genre != "" and isbn == "":
                query = "SELECT accession_number, ISBN, title, author, year_of_publication, genre,book_shelf_status, book_reserve_status FROM book where author LIKE '%{}%' and genre LIKE '%{}%' ".format(author,genre) 
                cur.execute(query)
                result = cur.fetchall()
            elif genre != "" and isbn != "":
                query = "SELECT accession_number, ISBN, title, author, year_of_publication, genre,book_shelf_status, book_reserve_status FROM book where genre LIKE '%{}%' and author LIKE '%{}%' and isbn LIKE '%{}%' ".format(genre,author,isbn) 
                cur.execute(query)
                result = cur.fetchall()

        elif title == "" and author == "":
            if genre == "" and isbn != "":
                query = "SELECT accession_number, ISBN, title, author, year_of_publication, genre,book_shelf_status, book_reserve_status FROM book where isbn LIKE '%{}%'".format(isbn)
                cur.execute(query)
                result = cur.fetchall()
            elif genre != "" and isbn == "":
                query = "SELECT accession_number, ISBN, title, author, year_of_publication, genre, book_shelf_status, book_reserve_status FROM book where genre LIKE '%{}%'".format(genre)
                cur.execute(query)
                result = cur.fetchall()
            elif genre != "" and isbn != "":
                query = "SELECT accession_number, ISBN, title, author, year_of_publication, genre,book_shelf_status, book_reserve_status FROM book where isbn LIKE '%{}%' and genre LIKE '%{}%' ".format(isbn,genre) 
                cur.execute(query)
                result = cur.fetchall()
        mysql.connection.commit()
        cur.close()
        if result:
            return render_template('search_book_user.html', detail=result, msg="Result for the search", username="", email="")
        else:
            return render_template('search_book_user.html', detail="No records found", username="", email="")
    else:
        return render_template('search_book_user.html')


@app.route("/search_book_lib", methods=['GET', 'POST'])
def search_book_lib():
    update_fine()
    update_reserve()
    if request.method == 'POST':

        title = request.form.get("title")
        author = request.form['author']
        genre = request.form['genre']
        isbn = request.form['isbn']
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if title == "" and author == "" and genre == "" and isbn == "":
            cur.execute(
                'SELECT accession_number, ISBN, title, author, year_of_publication, genre,book_shelf_status, shelf_Id, book_reserve_status FROM book')
            result = cur.fetchall()

        elif title != "":
            if author == "" and genre == "" and isbn == "":
                query = "SELECT accession_number, ISBN, title, author, year_of_publication, genre,book_shelf_status, shelf_Id, book_reserve_status FROM book where title LIKE '%{}%'".format(title)
                cur.execute(query)
                result = cur.fetchall()
            elif author == "" and genre == "" and isbn != "":
                query = "SELECT accession_number, ISBN, title, author, year_of_publication, genre, book_shelf_status, shelf_Id, book_reserve_status FROM book where title LIKE '%{}%' and isbn LIKE '%{}%' ".format(title,isbn) 
                cur.execute(query)
                result = cur.fetchall()
            elif author == "" and genre != "" and isbn == "":
                query = "SELECT accession_number, ISBN, title, author, year_of_publication, genre,book_shelf_status, shelf_Id, book_reserve_status FROM book where title LIKE '%{}%' and genre LIKE '%{}%' ".format(title,genre) 
                cur.execute(query)
                result = cur.fetchall()
            elif author == "" and genre != "" and isbn != "":
                query = "SELECT accession_number, ISBN, title, author, year_of_publication, genre, book_shelf_status, shelf_Id, book_reserve_status FROM book where title LIKE '%{}%' and genre LIKE '%{}%' and isbn LIKE '%{}%' ".format(title,genre,isbn) 
                cur.execute(query)
                result = cur.fetchall()
            elif author != "" and genre == "" and isbn == "":
                query = "SELECT accession_number, ISBN, title, author, year_of_publication, genre, book_shelf_status,shelf_Id, book_reserve_status FROM book where title LIKE '%{}%' and author LIKE '%{}%'".format(title,author)
                cur.execute(query)
                result = cur.fetchall()
            elif author != "" and genre == "" and isbn != "":
                query = "SELECT accession_number, ISBN, title, author, year_of_publication, genre, book_shelf_status,shelf_Id, book_reserve_status FROM book where title LIKE '%{}%' and author LIKE '%{}%' and isbn LIKE '%{}%' ".format(title,author,isbn) 
                cur.execute(query)
                result = cur.fetchall()
            elif author != "" and genre != "" and isbn == "":
                query = "SELECT accession_number, ISBN, title, author, year_of_publication, book_shelf_status,shelf_Id, genre, book_reserve_status FROM book where title LIKE '%{}%' and author LIKE '%{}%' and genre LIKE '%{}%' ".format(title,author,genre) 
                cur.execute(query)
                result = cur.fetchall()
            elif author != "" and genre != "" and isbn != "":
                query = "SELECT accession_number, ISBN, title, author, year_of_publication, shelf_Id, book_shelf_status, book_reserve_status,genre FROM book where title LIKE '%{}%' and author LIKE '%{}%' and genre LIKE '%{}%' and isbn LIKE '%{}%' ".format(title,author,genre,isbn) 
                cur.execute(query)
                result = cur.fetchall()

        elif title == "" and author!="":
            if genre == "" and isbn == "":
                query = "SELECT accession_number, ISBN, title, author, year_of_publication, genre,book_shelf_status, shelf_Id, book_reserve_status FROM book where author LIKE '%{}%'".format(author)
                cur.execute(query)
                result = cur.fetchall()
            elif genre == "" and isbn != "":
                query = "SELECT accession_number, ISBN, title, author, year_of_publication, genre,book_shelf_status, shelf_Id, book_reserve_status FROM book where author LIKE '%{}%' and isbn LIKE '%{}%' ".format(author,isbn) 
                cur.execute(query)
                result = cur.fetchall()
            elif genre != "" and isbn == "":
                query = "SELECT accession_number, ISBN, title, author, year_of_publication, genre,book_shelf_status, shelf_Id, book_reserve_status FROM book where author LIKE '%{}%' and genre LIKE '%{}%' ".format(author,genre) 
                cur.execute(query)
                result = cur.fetchall()
            elif genre != "" and isbn != "":
                query = "SELECT accession_number, ISBN, title, author, year_of_publication, genre,book_shelf_status, shelf_Id, book_reserve_status FROM book where genre LIKE '%{}%' and author LIKE '%{}%' and isbn LIKE '%{}%' ".format(genre,author,isbn) 
                cur.execute(query)
                result = cur.fetchall()

        elif title == "" and author == "":
            if genre == "" and isbn != "":
                query = "SELECT accession_number, ISBN, title, author, year_of_publication, genre,book_shelf_status, shelf_Id, book_reserve_status FROM book where isbn LIKE '%{}%'".format(isbn)
                cur.execute(query)
                result = cur.fetchall()
            elif genre != "" and isbn == "":
                query = "SELECT accession_number, ISBN, title, author, year_of_publication, genre,book_shelf_status, shelf_Id, book_reserve_status FROM book where genre LIKE '%{}%'".format(genre)
                cur.execute(query)
                result = cur.fetchall()
            elif genre != "" and isbn != "":
                query = "SELECT accession_number, ISBN, title, author, year_of_publication, genre,book_shelf_status, shelf_Id, book_reserve_status FROM book where isbn LIKE '%{}%' and genre LIKE '%{}%' ".format(isbn,genre) 
                cur.execute(query)
                result = cur.fetchall()
        mysql.connection.commit()
        cur.close()
        if result:
            return render_template('search_book_lib.html', detail=result, msg="Result for the search", username="", email="")
        else:
            return render_template('search_book_lib.html', detail="No records found", username="", email="")
    else:
        return render_template('search_book_lib.html', username="", email="")


@app.route('/signup',methods=['POST','GET'])
def signup():
    update_fine()
    update_reserve()
    msg=''
    if request.method=='POST':
        name = request.form['name']
        email = request.form['email']
        usertype = request.form['usertype']
        address = request.form['address']
        password = request.form['password']
        cpassword = request.form['cpassword']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if not name or not password or not email or not address or not cpassword or not address:
            msg = 'Please fill out the form !'
        if cpassword != password:
            msg = 'Confirm password does not match with password !'
        if usertype == 'choose user type':
            msg = 'Please select User Type'
        elif usertype == 'student' or usertype == 'faculty':
            cursor.execute('SELECT * FROM users WHERE email = % s', (email,))
            account = cursor.fetchone()
            cursor.execute('SELECT * FROM librarian WHERE email = % s', (email,))
            lib = cursor.fetchone()
            if account or lib:
                msg='Account already exist'
            elif cpassword != password:
                msg = 'Confirm password does not match with password !'
            else:
                status='deactivated'
                cursor.execute('INSERT INTO users VALUES(NULL, %s, %s, %s, %s, %s,%s,%s)', (name, password, email, address, usertype,0,status))
                mysql.connection.commit()
                cursor.close()
                msg = 'Your Request Has Been Successfully Registered !'
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('signup.html', msg = msg)



@app.route('/add_lib',methods=['POST','GET'])
def add_lib():
    update_fine()
    update_reserve()
    msg=''
    if request.method=='POST':
        name = request.form['name']
        email = request.form['email']
        address = request.form['address']
        password = request.form['password']
        cpassword = request.form['cpassword']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if not name or not password or not email or not address or not cpassword:
            msg = 'Please fill out the form !'
        elif cpassword != password:
            msg = 'Confirm password does not match with password !'
        else:
            cursor.execute('SELECT * FROM librarian WHERE email = % s', (email,))
            account = cursor.fetchone()
            cursor.execute('SELECT * FROM users WHERE email = % s', (email,))
            user = cursor.fetchone()
            if account or user:
                msg='Account already exist'
            elif cpassword != password:
                msg = 'Confirm password does not match with password !'
            else:
                cursor.execute('INSERT INTO librarian VALUES(NULL, %s, %s, %s, %s)', (name, password, email, address,))
                mysql.connection.commit()
                cursor.close()
                msg = 'Librarian Added Successfully !'
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('add_lib.html', msg = msg)

@app.route('/signin',methods=['POST','GET'])
def signin():
    update_fine()
    update_reserve()
    msg = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        usertype = request.form['usertype']
        if usertype == 'librarian':
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM librarian WHERE email = % s AND password = % s', (email, password,))
        
            account = cursor.fetchone()
            if account:
                session['loggedin'] = True
                session['password']=account['password']
                session['email'] = account['email']
                return render_template('profile_lib.html', lib_id=account['Lib_ID'],name=account['name'], email=email, address=account['address'])
            else:
                msg = 'Incorrect email / password !'
        if usertype == 'student' or usertype =='faculty':
            status='activated'
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM users WHERE email = % s AND password = % s AND usertype = %s AND status = %s', (email, password, usertype, status))
            account = cursor.fetchone()
            if account:
                session['loggedin'] = True
                session['password']=account['password']
                session['email'] = account['email']
                session['usertype'] = account['usertype']
                session['status'] = account['status']
                msg = usertype
                return render_template('profile.html',U_ID = account['U_ID'],name=account['name'], email=email, address=account['address'])
            else:
                msg = 'Incorrect email / password !'
    return render_template('signin.html', msg = msg)

@app.route('/requests',methods=['POST','GET'])
def requests():
    update_fine()
    update_reserve()
    status = 'deactivated'
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT U_ID, name, email, address, usertype FROM users WHERE status = %s",(status,))
    result = cur.fetchall()
    if result:
        return render_template('requests.html',detail=result)
    else:
        return render_template('requests.html',msg='No requests found')


@app.route('/add_user/<string:id>',methods=['POST','GET'])
def add_user(id):
    update_fine()
    update_reserve()
    status = 'activated'
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("UPDATE users SET status =%s WHERE U_ID =%s",(status,[id]))
    mysql.connection.commit()
    cur.close()
    return render_template('requests.html',msg='User Added Successfully')

@app.route('/delete_req/<string:id>',methods=['POST','GET'])
def delete_req(id):
    update_fine()
    update_reserve()
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("DELETE FROM users WHERE U_ID =%s",([id]))
    mysql.connection.commit()
    cur.close()
    return render_template('requests.html',msg='Request Delete Successfully')


@app.route('/delete_user',methods=['POST','GET'])
def delete_user():
    update_fine()
    update_reserve()
    msg =''
    if request.method=='POST':
        id = request.form['u_id']
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if not id:
            msg = "Please Fill Out Form !"
        else:
            cur.execute("SELECT U_ID, accession_number FROM Issue_Book where U_ID = %s",(id,))
            detail = cur.fetchall()
            if detail:
                msg = "Cannot Remove User As Book Is Issued By User"
            else:
                cur.execute("SELECT accession_number FROM Reserve_Book WHERE U_ID=%s",(id,))
                reserve = cur.fetchall()
                for j in reserve:
                    status = 'no'
                    cur.execute("UPDATE book SET book_reserve_status = %s WHERE accession_number = %s",(status,j[0],))
                cur.execute("DELETE FROM Reserve_Book WHERE U_ID = %s",(id,))
                cur.execute("DELETE FROM wishlist WHERE U_ID = %s",(id,))
                cur.execute("DELETE FROM users WHERE U_ID = %s",(id,))
                msg = "User Account Successfully Deleted"
        mysql.connection.commit()
        cur.close()
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template("delete_user.html", msg = msg)


@app.route('/delete_profile',methods=['POST','GET'])
def delete_profile():
    update_fine()
    update_reserve()
    msg =''
    email = session['email']
    password = session['password']
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT U_ID,name,address,email FROM users WHERE email=%s AND password=%s",(email, password,))
    aa = cur.fetchone()
    id = aa['U_ID']
    cur.execute("SELECT U_ID, accession_number FROM Issue_Book where U_ID = %s",(id,))
    detail = cur.fetchall()
    if detail:
        msg = "Cannot Delete Account As You Have Issued One Or More Than One Book"
        return render_template('profile.html',U_ID=aa['U_ID'],name=aa['name'],email=aa['email'],address=aa['address'],msg = msg)
    else:
        cur.execute("SELECT accession_number FROM Reserve_Book WHERE U_ID=%s",(id,))
        reserve = cur.fetchall()
        for j in reserve:
            status = 'no'
            cur.execute("UPDATE book SET book_reserve_status = %s WHERE accession_number = %s",(status,j[0],))
        cur.execute("DELETE FROM Reserve_Book WHERE U_ID = %s",(id,))
        cur.execute("DELETE FROM wishlist WHERE U_ID = %s",(id,))
        cur.execute("DELETE FROM users WHERE U_ID = %s",(id,))
        mysql.connection.commit()
        cur.close()
        msg = "User Account Successfully Deleted"
        return render_template('signin.html',msg = msg)



@app.route('/view_profile/<string:id>',methods=['POST','GET'])
def view_profile(id):
    update_fine()
    update_reserve()
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT U_ID, name, email, usertype, address, status,unpaid_fines FROM users WHERE U_ID=%s",([id],))
    profile = cursor.fetchone()
    cursor.execute("SELECT accession_number, start_date, due_date, fine FROM Issue_Book WHERE U_ID=%s",([id],))
    issue = cursor.fetchall()
    cursor.execute("SELECT accession_number, start_date, due_date FROM Reserve_Book WHERE U_ID=%s",([id],))
    reserve = cursor.fetchall()
    if issue and reserve:
        return render_template("view_profile.html", U_ID = profile['U_ID'], name = profile['name'], email = profile['email'], usertype = profile['usertype'], address = profile['address'],unpaid = profile['unpaid_fines'], detail = issue,reserve=reserve)
    elif issue and not reserve:
        return render_template("view_profile.html", U_ID = profile['U_ID'], name = profile['name'], email = profile['email'], usertype = profile['usertype'], address = profile['address'],unpaid = profile['unpaid_fines'], detail = issue,msg2="No Books Reserved")
    elif reserve and not issue:   
        return render_template("view_profile.html", U_ID = profile['U_ID'], name = profile['name'], email = profile['email'], usertype = profile['usertype'], address = profile['address'],unpaid = profile['unpaid_fines'],reserve=reserve, msg = "No Books Issued")
    else:
        return render_template("view_profile.html", U_ID = profile['U_ID'], name = profile['name'], email = profile['email'], usertype = profile['usertype'], address = profile['address'],unpaid = profile['unpaid_fines'], msg2="No Books Reserved", msg = "No Books Issued")




@app.route('/view_members',methods=['POST','GET'])
def view_members():
    update_fine()
    update_reserve()
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    status = 'activated'
    cursor.execute("SELECT U_ID, name, email,address, usertype FROM users WHERE status = %s",(status,))
    result = cursor.fetchall()
    if result:
        return render_template("view_members.html",detail = result)
    else:
        return render_template("view_members.html",msg = "No Active User Found")

@app.route("/search_user", methods=['GET', 'POST'])
def search_user():
    update_fine()
    update_reserve()
    if request.method == 'POST':

        U_ID = request.form['U_ID']
        name = request.form['name']
        email = request.form['email']
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if U_ID == "" and name == "" and email == "":
            cur.execute(
                'SELECT U_ID, name , email , address, usertype FROM users')
            result = cur.fetchall()

        elif U_ID != "":
            if name == "" and email == "":
                query = "SELECT U_ID, name , email , address, usertype FROM users where U_ID LIKE '%{}%'".format(U_ID)
                cur.execute(query)
                result = cur.fetchall()
            elif name == "" and email != "":
                query = "SELECT U_ID, name , email , address, usertype FROM users where U_ID LIKE '%{}%' and email LIKE '%{}%' ".format(U_ID,email) 
                cur.execute(query)
                result = cur.fetchall()
            elif name != "" and email == "":
                query = "SELECT U_ID, name , email , address, usertype FROM users where U_ID LIKE '%{}%' and name LIKE '%{}%'".format(U_ID,name)
                cur.execute(query)
                result = cur.fetchall()
            elif name != "" and email != "":
                query = "SELECT U_ID, name , email , address, usertype FROM users where U_ID LIKE '%{}%' and name LIKE '%{}%' and email LIKE '%{}%' ".format(U_ID,name,email) 
                cur.execute(query)
                result = cur.fetchall()
        elif U_ID == "" and name!="":
            if email == "":
                query = "SELECT U_ID, name , email , address, usertype FROM users where name LIKE '%{}%'".format(name)
                cur.execute(query)
                result = cur.fetchall()
            elif email != "":
                query = "SELECT U_ID, name , email , address, usertype FROM users where name LIKE '%{}%' and email LIKE '%{}%' ".format(name,email) 
                cur.execute(query)
                result = cur.fetchall()

        elif U_ID == "" and name == "":
            if email != "":
                query = "SELECT U_ID, name , email , address, usertype FROM users where email LIKE '%{}%'".format(email)
                cur.execute(query)
                result = cur.fetchall()

        mysql.connection.commit()
        cur.close()
        if result:
            if 'loggedin' in session:

                return render_template('view_members.html', detail=result, msg="Result for the search")
            else:
                return render_template('view_members.html', detail=result, msg="Result for the search", username="", email="")
        else:
            if 'loggedin' in session:

                return render_template('view_members.html', detail="No records found")
            else:
                return render_template('view_members.html', detail="No records found", username="", email="")
    else:
        if 'loggedin' in session:

            return render_template('view_members.html')
        else:
            return render_template('view_members.html', username="", email="")

@app.route('/update_profile_lib', methods= ['POST', 'GET'])
def update_profile_lib():
    update_fine()
    update_reserve()
    msg=''
    if request.method=='POST':
        name = request.form['name']
        email = request.form['email']
        address = request.form['address']
        password = request.form['password']
        cpassword = request.form['cpassword']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if 'loggedin' in session:
            e= session['email']
            p= session['password']
            if not name or not password or not email or not address or not cpassword:
                msg = 'Please fill out the form !'
            elif cpassword != password:
                msg = 'Confirm password does not match with password !'
            else:  
                cursor.execute('SELECT * FROM librarian WHERE email= % s AND password= % s', (e, p,))
                account= cursor.fetchone()
                if account and account['email']!=session['email']:
                    msg='Account Already Exist With This Email'
                elif cpassword != password:
                    msg = 'Confirm password does not match with password !'
                else:
                    id = account['Lib_ID']
                    if session['email']!=email:
                        session['email']=email
                    if session['password'] != password:
                        session['password'] = password
                    cursor.execute('UPDATE librarian SET name= % s, email= % s, address= % s, password= % s WHERE Lib_ID= % s', (name, email, address, password, id,))
                    msg='Your profile has been succesfully updated'
        mysql.connection.commit()
        cursor.close()
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('update_lib_profile.html', msg= msg)


@app.route('/update_profile', methods= ['POST', 'GET'])
def update_profile():
    update_fine()
    update_reserve()
    msg=''
    if request.method=='POST':
        name = request.form['name']
        email = request.form['email']
        address = request.form['address']
        password = request.form['password']
        cpassword = request.form['cpassword']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if 'loggedin' in session:
            e= session['email']
            p= session['password']
            if not name or not password or not email or not address or not cpassword:
                msg = 'Please fill out the form !'
            elif cpassword != password:
                msg = 'Confirm password does not match with password !'
            else:  
                cursor.execute('SELECT * FROM users WHERE email= % s AND password= % s', (e, p,))
                account= cursor.fetchone()
                if account and account['email']!=session['email']:
                    msg='Account Already Exist With This Email'
                elif cpassword != password:
                    msg = 'Confirm password does not match with password !'
                else:
                    id = account['U_ID']
                    if session['email']!=email:
                        session['email']=email
                    if session['password'] != password:
                        session['password'] = password
                    cursor.execute('UPDATE users SET name= % s, email= % s, address= % s, password= % s WHERE U_ID= % s', (name, email, address, password, id,))
                    msg='Your profile has been succesfully updated'
        mysql.connection.commit()
        cursor.close()
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('update_user_profile.html', msg= msg)


@app.route('/add_book',methods=['POST','GET'])
def add_book():
    update_fine()
    update_reserve()
    msg=''
    if request.method == 'POST':
        title = request.form.get("title")
        author = request.form['author']
        genre = request.form['genre']
        isbn = request.form['isbn']
        year_of_publication = request.form['year_of_publication']
        shelf_id = request.form['shelf_id']
        count = request.form['count']
        status = 'available'
        reserve='no'
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM shelf WHERE shelf_id=%s",(shelf_id,))
        s = cursor.fetchone()
        if not title or not author or not isbn or not genre or not year_of_publication or not shelf_id or not count:
            msg = 'Please fill out the form !'
        elif s:
            i=0
            x = int(count)
            y = int(s['capacity'])
            if x>y:
                msg='No Space Left In The Shelf. Available Space = ' + y
            else:
                while i < x:
                    cursor.execute('INSERT INTO book VALUES(NULL, %s, %s, %s, %s,%s,%s,%s,%s)', (isbn, title, author, year_of_publication,shelf_id,genre,status,reserve,))
                    i=i+1
                cursor.execute('UPDATE shelf SET capacity=%s WHERE shelf_id=%s',(y-x,shelf_id,))
                mysql.connection.commit()
                cursor.close()
                msg = 'Book Added Successfully !'
        else:
            msg = 'Please Enter a Valid Shelf ID'
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('add_book.html', msg = msg)


@app.route('/remove_book',methods=['POST','GET'])
def remove_book():
    update_fine()
    update_reserve()
    msg=''
    if request.method == 'POST':
        accession_number = request.form['accession_number']
        isbn = request.form['isbn']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if not accession_number or not isbn:
            msg='Please Fill Out Form !'
        else:
            cursor.execute('SELECT * FROM book WHERE accession_number = % s AND isbn = %s', (accession_number,isbn,))
            account = cursor.fetchone()
            if account:
                if account['book_shelf_status']=='available':
                    cursor.execute('SELECT * FROM shelf WHERE shelf_id=%s', (account['shelf_Id'],))
                    s = cursor.fetchone()
                    cursor.execute('DELETE FROM book WHERE accession_number = %s',(accession_number,))
                    cursor.execute('UPDATE shelf SET capacity=%s WHERE shelf_id=%s',(int(s['capacity']+1), account['shelf_Id']))
                    msg='Book Removed Successfully'
                else:
                    msg = 'Book Is Not On Shelf'
            else:
                msg = "Book Doesn't Exist Which Matches Given Records"
        mysql.connection.commit()
        cursor.close()
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('remove_book.html',msg=msg)


@app.route('/add_shelf',methods=['POST','GET'])
def add_shelf():
    update_fine()
    update_reserve()
    msg=''
    if request.method == 'POST':
        shelf_id = request.form['shelf_id']
        capacity = request.form['capacity']
        status = 'available'
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM shelf WHERE shelf_id = % s', (shelf_id,))
        account = cursor.fetchone()
        if not shelf_id or not capacity:
            msg = 'Please fill out the form !'
        elif account:
            msg='Shelf already exist'
        else:
            cursor.execute("INSERT INTO shelf VALUES(%s,%s,%s)",(shelf_id,capacity,status,))
            msg = 'Shelf added Successfully'
        mysql.connection.commit()
        cursor.close()
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('add_shelf.html',msg=msg)

@app.route('/edit_shelf',methods=['POST','GET'])
def edit_shelf():
    update_fine()
    update_reserve()
    msg=''
    if request.method == 'POST':
        shelf_id = request.form['shelf_id']
        accession_number = request.form['accession_number']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM book WHERE accession_number = %s",(accession_number,))
        b = cursor.fetchone()
        if not shelf_id or not accession_number:
            msg = 'Please Fill Out The Form !'
        elif b:
            cursor.execute("SELECT * FROM shelf WHERE shelf_id = %s",(shelf_id,))
            s = cursor.fetchone()
            if s:
                if int(s['capacity'])>=1:
                    cursor.execute("SELECT * FROM shelf WHERE shelf_id = %s",(b['shelf_Id'],))
                    s1 = cursor.fetchone()
                    cursor.execute("UPDATE book SET shelf_Id = %s WHERE accession_number = %s",(shelf_id, accession_number,))
                    cursor.execute("UPDATE shelf SET capacity = %s WHERE shelf_id = %s",(int(s['capacity'])-1, shelf_id,))
                    cursor.execute("UPDATE shelf SET capacity = %s WHERE shelf_id = %s",(int(s1['capacity'])+1, b['shelf_Id'],))
                    msg = "Shelf Editted Successfully"
                else:
                    msg = "Not Enough Space"
            else:
                msg = "Please Enter Valid Shelf ID"
        else:
            msg = "Please Enter Valid Accession Number"
        mysql.connection.commit()
        cursor.close()
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('edit_shelf.html',msg=msg)


@app.route('/view_shelf',methods=['POST','GET'])
def view_shelf():
    update_fine()
    update_reserve()
    msg=''
    if request.method == 'POST':
        shelf_id = request.form['shelf_id']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if shelf_id=="":
            msg = "Please Fill Out Form"
            return render_template("view_shelf.html",msg=msg)
        else:
            cursor.execute("SELECT * FROM shelf WHERE shelf_id =%s",(shelf_id,))
            shelf = cursor.fetchone()
            if shelf:
                cursor.execute("SELECT accession_number, isbn, title, author, year_of_publication, book_shelf_status FROM book WHERE shelf_Id = %s",(shelf_id,))
                result = cursor.fetchall()
                if result:
                    msg = "Shelf Details"
                else:
                    msg = "Shelf Is Empty"
            else:
                msg = "Please Enter Valid Shelf ID"
                return render_template('view_shelf.html',msg=msg)    
            mysql.connection.commit()
            cursor.close()
            return render_template('view_shelf.html',detail = result, msg = msg) 
    elif request.method == 'POST':
        msg = "Please Fill Out Form !"
        return render_template('view_shelf.html', msg = msg)     
    else:
        return render_template('view_shelf.html')  
    



@app.route("/issue_book",methods=['POST','GET'])
def issue_book():
    update_fine()
    update_reserve()
    msg=''
    if request.method=='POST':
        U_ID = request.form['User_ID']
        accession_number = request.form['accession number']        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if not U_ID or not accession_number :
            msg = 'Please fill out all the necessary information'
        else:    
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('select U_ID from users where U_Id=%s' , (U_ID,)) 
            aa = cursor.fetchone()
            cursor.execute('select accession_number from book where accession_number=%s' , (accession_number,)) 
            bb = cursor.fetchone()
            cursor.execute('select count(*) from Issue_Book where U_Id=%s' , (U_ID,)) 
            c=cursor.fetchone()
            cursor.execute('select unpaid_fines from users where U_Id=%s'  , (U_ID,))
            g = cursor.fetchone()
            cursor.execute('select usertype from users where U_ID=%s' , (U_ID,) ) 
            k= cursor.fetchone()
            cursor.execute('select book_shelf_status from book where accession_number=%s' , (accession_number,) ) 
            j= cursor.fetchone()
            cursor.execute('select U_ID from Reserve_Book where accession_number=%s' , (accession_number,) ) 
            jj= cursor.fetchone()
            cursor.execute('select U_ID from Reserve_Book where U_ID=%s and accession_number=%s ' , (U_ID , accession_number,) ) 
            rr= cursor.fetchone()
            cursor.execute('select title from book where accession_number=%s' , (accession_number,)) 
            titl = cursor.fetchone()
            cursor.execute('select author from book where accession_number=%s' , (accession_number,)) 
            auth = cursor.fetchone()
            if aa and bb:
                if j['book_shelf_status']=="Issued":
                    cursor.execute('select * from Issue_Book where U_Id=%s and accession_number=%s' , (U_ID , accession_number,))
                    flag=cursor.fetchone()
                    if flag:
                        msg='Oops!! you can issue a particular book only one time until you return the same!'
                    else:
                        msg='book is already Issued by someone else'
                elif rr:
                    if k['usertype']=="student":
                        if(c['count(*)']>=3):
                            msg='Oops!! you have already issued 3 books. You cannot issue more than 3 books.'
                        elif g['unpaid_fines']>1000:
                            msg = 'Oops!! first pay the unpaid fines :('
                        else:
                            start_date = date.today() 
                            due_date = start_date + timedelta(15)
                            cursor.execute('INSERT INTO Issue_Book VALUES (NULL,%s, %s, %s, %s,0)', (U_ID, accession_number, start_date, due_date,))
                            cursor.execute('INSERT INTO Transaction_History VALUES (NULL, %s, %s, %s, %s, %s)', (U_ID, accession_number, titl['title'], auth['author'],start_date,))
                            cursor.execute('update book set book_shelf_status="Issued" where accession_number=%s' , (accession_number,))
                            cursor.execute('update book set book_reserve_status="no" where accession_number=%s' , (accession_number,))  
                            cursor.execute('delete from Reserve_Book where accession_number=%s' , (accession_number,))
                            msg='Book got issued succesfully! :)'
                    else:
                        if g['unpaid_fines'] > 1000:
                            msg = 'Oops!! first pay the unpaid fines :('
                        else:
                            start_date = date.today() 
                            due_date = start_date + timedelta(15)
                            cursor.execute('INSERT INTO Issue_Book VALUES (NULL,%s, %s, %s, %s,0)', (U_ID, accession_number, start_date, due_date,))
                            cursor.execute('INSERT INTO Transaction_History VALUES (NULL, %s, %s, %s, %s, %s)', (U_ID, accession_number, titl['title'], auth['author'],start_date,))
                            cursor.execute('update book set book_shelf_status="Issued" where accession_number=%s' , (accession_number,))
                            cursor.execute('update book set book_reserve_status="no" where accession_number=%s' , (accession_number,))  
                            cursor.execute('delete from Reserve_Book where accession_number=%s' , (accession_number,))
                            msg='Book got issued succesfully! :)'
                elif jj:
                    msg='book alrady reserved by someone else'
                elif j['book_shelf_status']=="available":
                    if k['usertype']=="student":
                        if(c['count(*)']>=3):
                            msg='Oops!! you have already issued 3 books. You cannot issue more than 3 books.'
                        elif g['unpaid_fines']>1000:
                            msg = 'Oops!! first pay the unpaid fines :('
                        else:
                            start_date = date.today() 
                            due_date = start_date + timedelta(15)
                            cursor.execute('INSERT INTO Issue_Book VALUES(NULL,%s, %s, %s, %s,0)', (U_ID, accession_number, start_date, due_date,))
                            cursor.execute('INSERT INTO Transaction_History VALUES (NULL, %s, %s, %s, %s, %s)', (U_ID, accession_number, titl['title'], auth['author'],start_date,))
                            cursor.execute('update book set book_shelf_status="Issued" where accession_number=%s' , (accession_number,)) 
                            msg='Book got issued succesfully! :)'
                    else:
                        if g['unpaid_fines'] > 1000:
                            msg = 'Oops!! first pay the unpaid fines :('
                        else:
                            start_date = date.today()
                            due_date = start_date + timedelta(15)
                            cursor.execute('INSERT INTO Issue_Book VALUES(NULL,%s, %s, %s, %s,0)', (U_ID, accession_number, start_date, due_date,))
                            cursor.execute('INSERT INTO Transaction_History VALUES (NULL, %s, %s, %s, %s, %s)', (U_ID, accession_number, titl['title'], auth['author'],start_date,))
                            cursor.execute('update book set book_shelf_status="Issued" where accession_number=%s' , (accession_number,))
                            msg='Book got issued succesfully! :)'
                else:
                    msg='Sorry! this book is reserved for someone else'
                details = cursor.fetchall()
                mysql.connection.commit()    
            else:
                msg= 'invalid credentials'
    return render_template('issue_book.html',msg=msg)

@app.route("/return_book",methods=['POST','GET'])
def return_book():
    update_fine()
    update_reserve()
    msg=''
    if request.method=='POST':
        U_ID = request.form['User_ID']
        accession_number = request.form['accession number']        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if not U_ID or not accession_number :
            msg = 'Please fill out all the necessary information'
        else:    
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('select U_ID from users where U_Id=%s' , (U_ID,)) 
            aa = cursor.fetchone()
            cursor.execute('select accession_number from book where accession_number=%s' , (accession_number,)) 
            bb = cursor.fetchone()
            cursor.execute('select U_ID, accession_number from Issue_Book where accession_number=%s' , (accession_number,)) 
            cc = cursor.fetchone()
            if aa and bb and cc:
                cursor.execute('select fine from Issue_Book where accession_number=%s' , (accession_number,))
                pp=cursor.fetchone()
                cursor.execute('select book_reserve_status from book where accession_number=%s' , (accession_number,))
                qq=cursor.fetchone()
                if pp['fine']>0:
                    msg='please pay the unpaid fines first'
                    return render_template('manage_fines.html',detail = pp, msg = msg)
                elif qq['book_reserve_status']=="no":
                    cursor.execute('delete from Issue_Book where accession_number=%s' , (accession_number,))
                    cursor.execute('update book set book_shelf_status="available" where accession_number=%s' , (accession_number,))
                    msg='returned successfully'
                else:
                    cursor.execute('delete from Issue_Book where accession_number=%s' , (accession_number,))
                    cursor.execute('update book set book_shelf_status="available" where accession_number=%s' , (accession_number,))
                    start_date = date.today() 
                    due_date = start_date + timedelta(3)
                    cursor.execute('update Reserve_Book set start_date=%s , due_date=%s where accession_number=%s ', (start_date,due_date,accession_number,))
                    msg='returned sucessfully'
                details = cursor.fetchall()
                mysql.connection.commit()
                cursor.close()
            else:
                msg= 'invalid credentials'
    return render_template('return_book.html',msg=msg)


@app.route("/reserve_book/<string:id>",methods=['POST','GET'])
def reserve_book(id):
    update_fine()
    update_reserve()
    msg=''
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('select U_ID from users where email=%s AND password=%s' , (session['email'],session['password'],)) 
    aa = cursor.fetchone()
    cursor.execute('select accession_number from book where accession_number=%s' , (id,)) 
    bb = cursor.fetchone()
    if aa and bb:
        cursor.execute('select book_shelf_status from book where accession_number=%s' , (id,))
        j=cursor.fetchone()
        cursor.execute('select * from Reserve_Book where U_Id=%s and accession_number=%s' , (aa['U_ID'] , id,))
        flag=cursor.fetchone()
        if j['book_shelf_status']=="available":
            msg='The book is available for issue u can not reserve the book'
        elif flag:
            msg='u cannot reserve the same book twice'
        else:
            cursor.execute('select book_reserve_status from book where accession_number=%s' , (id,) ) 
            jj= cursor.fetchone()
            if jj['book_reserve_status']=="yes":
                msg='This book is already reserved by someone else'
            else:
                cursor.execute('select count(*) from Reserve_Book where U_Id=%s' , (aa['U_ID'],)) 
                c=cursor.fetchone()
                cursor.execute('select unpaid_fines from users where U_Id=%s'  , (aa['U_ID'],))
                g = cursor.fetchone()
                cursor.execute('select usertype from users where U_ID=%s' , (aa['U_ID'],) ) 
                k= cursor.fetchone()
                if k['usertype']=="student":
                    if(c['count(*)']>=2):
                        msg='Oops!! you have already reserved 2 books. You cannot reserve more than 2 books.'
                    elif g['unpaid_fines']>1000:
                        msg = 'Oops!! U first need to pay unpaid fines'
                    else:
                        cursor.execute('INSERT INTO Reserve_Book VALUES(NULL,%s, %s,NULL,NULL)', (aa['U_ID'], id,))
                        cursor.execute('update book set book_reserve_status="yes" where accession_number=%s' , (id,)) 
                        msg='Book got reserved succesfully! :)'
                else:
                    if g['unpaid_fines'] > 1000:
                        msg = 'Oops!! U first need to pay unpaid fines'
                    else:
                        cursor.execute('INSERT INTO Reserve_Book VALUES(NULL,%s, %s,NULL,NULL)', (aa['U_ID'], id,))
                        cursor.execute('update book set book_reserve_status="yes" where accession_number=%s' , (id,))
                        msg='Book got reserved succesfully! :)'
        details = cursor.fetchall()
        mysql.connection.commit()
        cursor.close()
    else:
        msg= 'invalid credentials'
    return render_template('search_book_user.html',msg=msg)


@app.route("/add_wishlist/<string:id>",methods=['POST','GET'])
def add_wishlist(id):
    update_fine()
    update_reserve()
    msg=''
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('select U_ID from users where email=%s AND password=%s' , (session['email'],session['password'],)) 
    aa = cursor.fetchone()
    cursor.execute("SELECT U_ID, accession_number FROM wishlist WHERE U_ID = %s AND accession_number = %s",(aa['U_ID'],id,))
    exist = cursor.fetchone()
    if exist:
        msg = "Book Already Wishlisted"
    else:
        cursor.execute("INSERT INTO wishlist VALUES(%s,%s)",(aa['U_ID'],id,))
        msg = "Book Added To Wishlist"
    mysql.connection.commit()
    cursor.close()
    return render_template('search_book_user.html',msg=msg)





@app.route("/manage_fines",methods=['POST','GET'])
def manage_fines():
    update_fine()
    update_reserve()
    msg=''
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT U_ID, accession_number, start_date, due_date, fine FROM Issue_Book")
    result = cursor.fetchall()
    if request.method=='POST':
        U_ID = request.form['u_id']
        if not U_ID:
            msg2 = 'Please Fill Out Form'
            return render_template('manage_fines.html', msg1 = msg2)
        cursor.execute("SELECT U_ID, accession_number, start_date, due_date, fine FROM Issue_Book WHERE U_ID=%s",(U_ID,))
        detail = cursor.fetchall()
        if detail:
            return render_template('manage_fines.html',detail = detail, msg = 'Fine Due For The User')
        else:
            return render_template('manage_fines.html',msg = "User Has No Dues")
    elif result:
        return render_template('manage_fines.html', detail =result, msg = "Dues For Each Book")
    else:
        return render_template("manage_fines.html", msg = "All Dues Are Cleared")


@app.route("/clear_fines/<string:uid>/<string:id>",methods=['POST','GET'])
def clear_fines(id,uid):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    fine = 0
    cursor.execute('Select fine from Issue_Book WHERE U_ID = %s AND accession_number = %s',( uid, id,))
    cc=cursor.fetchone()
    x = cc['fine']
    x = int(x)
    cursor.execute('Select unpaid_fines from users WHERE U_ID = %s',( uid, ))
    pp=cursor.fetchone()
    y = pp['unpaid_fines']
    y = int(y)
    new_unpaid_fines=(y-x)
    cursor.execute('UPDATE users SET unpaid_fines = %s WHERE U_ID = %s ',(new_unpaid_fines, uid,))
    cursor.execute('UPDATE Issue_Book SET fine = %s WHERE U_ID = %s AND accession_number = %s',(fine, uid, id,))
    datet=date.today()
    cursor.execute('UPDATE Issue_Book SET due_date = %s WHERE U_ID = %s AND accession_number = %s',(datet, uid, id,))
    mysql.connection.commit()
    cursor.close()
    msg = 'Fine Paid'
    return render_template('manage_fines.html', msg = msg)


@app.route("/book_issued",methods=['POST','GET'])
def books_issued():
    update_fine()
    update_reserve()
    msg=''
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT U_ID, unpaid_fines FROM users WHERE email = %s AND password = %s",(session['email'],session['password'],))
    user = cursor.fetchone()
    cursor.execute("SELECT accession_number, start_date, due_date, fine FROM Issue_Book WHERE U_ID = %s",(user['U_ID'],))
    issue = cursor.fetchall()
    if issue:
        msg = "Books Issued"
        return render_template('books_issued.html',detail = issue, msg= msg, unpaid = user['unpaid_fines'])
    else:
        msg = "No Books Issued"
        return render_template('books_issued.html',msg = msg, unpaid = user['unpaid_fines'])


@app.route("/book_reserved",methods=['POST','GET'])
def books_reserved():
    update_fine()
    update_reserve()
    msg=''
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT U_ID FROM users WHERE email = %s AND password = %s",(session['email'],session['password'],))
    user = cursor.fetchone()
    cursor.execute("SELECT accession_number, start_date, due_date FROM Reserve_Book WHERE U_ID = %s",(user['U_ID'],))
    reserve = cursor.fetchall()
    if reserve:
        msg = "Books Reserved"
        return render_template('books_reserved.html',detail = reserve, msg= msg)
    else:
        msg = "No Books Reserved"
        return render_template('books_reserved.html',msg = msg)



@app.route("/wishlist",methods=['POST','GET'])
def wishlist():
    update_fine()
    update_reserve()
    msg=''
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT U_ID FROM users WHERE email = %s AND password = %s",(session['email'],session['password'],))
    account = cursor.fetchone()
    cursor.execute("SELECT wishlist.accession_number, isbn, title, author, year_of_publication FROM book INNER JOIN wishlist on book.accession_number = wishlist.accession_number WHERE wishlist.U_ID = %s",(account['U_ID'],))
    wish = cursor.fetchall()
    if wish:
        msg = "Wishlisted Books"
        return render_template('wishlist.html',detail = wish, msg = msg)
    else:
        msg = "No Book in Wishlist"
        return render_template('wishlist.html',msg = msg)


@app.route("/remove_wishlist/<string:id>",methods=['POST','GET'])
def remove_wishlist(id):
    update_fine()
    update_reserve()
    msg=''
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('select U_ID from users where email=%s AND password=%s' , (session['email'],session['password'],)) 
    aa = cursor.fetchone()
    cursor.execute("DELETE FROM wishlist WHERE U_ID = %s AND accession_number = %s",(aa['U_ID'],id,))
    mysql.connection.commit()
    cursor.close()
    msg = "Book Removed From Wishlist"
    return render_template('wishlist.html',msg = msg)



@app.route("/issued_books",methods=['POST','GET'])
def issued_books():
    update_fine()
    update_reserve()
    msg=''
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT U_ID, accession_number, start_date, due_date, fine FROM Issue_Book")
    result = cursor.fetchall()
    if result:
        msg = 'Issued Books'
        return render_template('issued_books.html',detail = result, msg = msg)
    else:
        return render_template('issued_books.html', msg = "All Books Are In Shelf")




@app.route("/reserved_books",methods=['POST','GET'])
def reserved_books():
    update_fine()
    update_reserve()
    msg=''
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT U_ID, accession_number, start_date, due_date FROM Reserve_Book")
    result = cursor.fetchall()
    if result:
        msg = 'Reserved Books'
        return render_template('reserved_books.html',detail = result, msg = msg)
    else:
        return render_template('reserved_books.html', msg = "No Book Is Reserved")



@app.route("/transactions",methods=['POST','GET'])
def transactions():
    update_fine()
    update_reserve()
    msg = ''
    email = session['email']
    password = session['password']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT U_ID FROM users WHERE email=%s AND password=%s",(email,password,))
    ac=cursor.fetchone()
    cursor.execute("SELECT accession_number, title, author, date FROM Transaction_History WHERE U_ID=%s",(ac['U_ID'],))
    result = cursor.fetchall()
    msg = 'Transaction History'
    return render_template("transaction.html",detail = result, msg=msg)



@app.route("/transaction_records",methods=['POST','GET'])
def transaction_records():
    update_fine()
    update_reserve()
    msg = ''
    if request.method == "POST":
        uid = request.form['uid']
        if not uid:
            msg = "Please Fill Out The Form!"
        else:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT U_ID, accession_number, title, author, date FROM Transaction_History WHERE U_ID=%s",(uid,))
            result = cursor.fetchall()
            msg = 'Transaction History'
            return render_template("transaction_records.html",detail = result, msg=msg)
    return render_template("transaction_records.html",msg=msg)
    

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('name', None)
    session.pop('email', None)
    session.pop('address', None)
    return redirect(url_for('home'))

if __name__=="__main__":
    app.run(debug=True)