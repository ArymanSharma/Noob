from flask import Flask, render_template, request, redirect, flash, g, session
from flask_mysqldb import MySQL
import yaml
import os


app = Flask(__name__)

app.secret_key = os.urandom(24)

db = yaml.load(open('db.yaml'))
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']

mysql = MySQL(app)


@app.route('/')
def start():
    return redirect('/signup')
    


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        userdetails = request.form
        name = userdetails['name']
        email = userdetails['email']
        usernames = userdetails['username']
        password = userdetails['password']
        repeatpass = userdetails['repeatpass']
        g.username = userdetails['username']

        cur = mysql.connection.cursor()
        check = cur.execute("SELECT username FROM userdata WHERE username = g.username ")
        mysql.connection.commit()
        cur.close()

        if check is None:

            if password == repeatpass:
                try:
                    cur = mysql.connection.cursor()
                    cur.execute("INSERT INTO userdata(name, email, username, password, repeatpass) VALUES(%s, %s, %s, %s, %s)",(name, email, usernames, password, repeatpass))
                    mysql.connection.commit()
                    
                finally:
                    cur.close()
                    flash('Successfully Registered')
                    return redirect('/login')

            else:

                flash('PASSWORDS MISMATCH, PLEASE TRY AGAIN')
                return redirect('/signup')

        else:

            flash('Username already exists , please choose another one !')
            return redirect('/signup.html')

    return render_template('signup.html')


@app.before_request
def before_request():
    g.loggedin = None
    if 'loggedin' in session:

        g.loggedin = session['loggedin']
            if g.loggedin:

                return render_template('User.html')

            else:
                return redirect('/login')

    else:
        return redirect('/login')



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':

        session.pop('loggedin', None)

        login = request.form
        usernames = login['username']
        password = login['password']
        g.usernames = login['username']

        cur = mysql.connection.cursor()
        checkpassword = cur.execute("SELECT password FROM userdata WHERE username = usernames ")
        mysql.connection.commit()
        cur.close()

        if checkpassword == password:
            session['loggedin'] = usernames
            return redirect('/user')

        else:
            flash('You have entered wrong username or password, please try again !')
            return redirect('/login')

    return render_template('index.html')


            

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    return redirect('/login')




@app.route('/user')
def user():
    render_template('User.html')




@app.route('/cab_sharing', methods=['POST' , 'GET'])
def cab_sharing():
    if g.loggedin:


        if request.method =='POST':
            cabdetails = request.form
            username = g.usernames
            source = cabdetails['source']
            destination = cabdetails['destination']
            start_date = cabdetails['start']
            start_time = cabdetails['starttime']
            stop_date = cabdetails['stop']
            stop_time = cabdetails['stoptime']
            vacancies = cabdetails['vacancies']
            fare = cabdetails['fare']
            contact = cabdetails['contact']

            if source!=destination:

                cur = mysql.connection.cursor()
                cur.execute("INSERT INTO cabsharing(username, source, destination, start_date, start_time, stop_date, stop_time, vacancies, fare, contact) VALUES(%s, %s, %s, %s, %s, %s, %s,%s ,%s ,%s)",(username, source, destination, start_date, start_time, stop_date, stop_time, vacancies, fare, contact))
                mysql.connection.commit()
                cur.close()
                return redirect('/my_cab_shares')

            else:
                flash('SOURCE AND DESTINATIO CANNOT BE SAME!')
                return redirect('/cab_sharing')
    else:
        return redirect('/login')

    return render_template('CAB_SHARING.html')



@app.route('/my_cab_shares', methods=['POST' , 'GET'])
def my_cab_shares():
    if g.loggedin:

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM cabsharing WHERE username = '" + g.loggedin + "' ")
        mycabshares = cur.fetchall()
        mysql.connection.commit()

            if method == 'POST':
                newseats = request.form
                seat = newseats['seat']
                cur.execute("UPDATE cabsharing SET vacancies = seat WHERE cabshareid = '" + cabshareid[0] + "' ")
                mysql.connection.commit()
                cur.close()

    else:
        return redirect('/login')


    return render_template('MY_CAB_SHARES.html')



@app.route('/cab_search')
def search():
    if g.loggedin:
        cur = mysql.connection.cursor()



    else:
        return redirect('/login')

    return render_template('CAB_SEARCH.html')




if __name__ == '__main__':
    app.run(debug=True)
