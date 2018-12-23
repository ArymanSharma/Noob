from flask import Flask, render_template, request, redirect, flash, g, session, url_for
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
    return redirect(url_for('signup'))
    


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
        check = cur.execute("SELECT username FROM userdata WHERE username = %s", (usernames))
        mysql.connection.commit()
        cur.close()

        if check is None:

            if password == repeatpass:
                try:
                    cur = mysql.connection.cursor()
                    cur.execute("INSERT INTO userdata(name, email, username, password) VALUES(%s, %s, %s, %s, %s)",(name, email, usernames, password))
                    mysql.connection.commit()
                    
                finally:
                    cur.close()
                    flash('Successfully Registered')
                    return redirect(url_for('login'))

            else:

                flash('PASSWORDS MISMATCH, PLEASE TRY AGAIN')
                return redirect(url_for('signup'))

        else:

            flash('Username already exists , please choose another one !')
            return redirect(url_for('signup'))

    return render_template('signup.html')


@app.before_request
def before_request():

    g.loggedin = None

    if 'loggedin' in session:

        g.loggedin = session['loggedin']



@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        session.pop('loggedin', None)

        login = request.form
        usernames = login['username']
        password = login['password']
        g.usernames = login['username']

        cur = mysql.connection.cursor()
        checkpassword = cur.execute("SELECT password FROM userdata WHERE username = %s ", (username))
        mysql.connection.commit()
        cur.close()

        if checkpassword == password:

            session['loggedin'] = usernames
            return redirect(url_for('user'))

        else:

            flash('You have entered wrong username or password, please try again !')
            return redirect(url_for('login'))

    return render_template('index.html')


            

@app.route('/logout')
def logout():

    session.pop('loggedin', None)
    return redirect(url_for('login'))


#----------------------------------------------------------------------------------------------- HOME PAGE --------------------------------------------------------------------------------------------------------------

@app.route('/user')
def user():

    render_template('User.html')


#----------------------------------------------------------------------------------------------- CAB SHARING ------------------------------------------------------------------------------------------------------------


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

            if source != destination:

                cur = mysql.connection.cursor()
                cur.execute("INSERT INTO cabsharing(username, source, destination, start_date, start_time, stop_date, stop_time, vacancies, fare, contact) VALUES(%s, %s, %s, %s, %s, %s, %s,%s ,%s ,%s)",(username, source, destination, start_date, start_time, stop_date, stop_time, vacancies, fare, contact))
                mysql.connection.commit()
                cur.close()
                return redirect(url_for('my_cab_shares'))

            else:

                flash('SOURCE AND DESTINATIO CANNOT BE SAME!')
                return redirect(url_for('cab_sharing'))

    return render_template('CAB_SHARING.html')

    else:

        return redirect(url_for('login'))

    



@app.route('/my_cab_shares', methods=['POST' , 'GET'])
def my_cab_shares():

    if g.loggedin:

        cur = mysql.connection.cursor()
        ping = g.loggedin
        cur.execute("SELECT * FROM cabsharing WHERE username = %s", (ping))
        mycabshares = cur.fetchall()
        mysql.connection.commit()

            if method == 'POST':

                newseats = request.form
                seat = newseats['seat']
                cabid = newseats['cabid']
                cur.execute("UPDATE cabsharing SET vacancies = seat WHERE cabshareid = %s", (cabid))
                mysql.connection.commit()
                cur.close()
                return redirect(url_for('my_cab_shares'))

    return render_template('MY_CAB_SHARES.html', cabshares = mycabshares)

    else:

        return redirect(url_for('login'))




@app.route('/cab_search')
def cab_search():

    if g.loggedin:

        cur = mysql.connection.cursor()
        cur.execute("SELECT DISTINCT source FROM cabsharing")
        sources = cur.fetchall()
        cur.execute("SELECT DISTINCT destination FROM cabsharing")
        desinations = cur.fetchall()
        mysql.connection.commit()
        cur.close()

            if method == 'POST':

                search = request.form
                search_source = search['source']
                search_destination = search['destination']
                search_date = search['date']

                if search_source != search_destination

                    cur = mysql.connection.cursor()
                    cur.execute("SELECT * FROM cabsharing WHERE destination = %s AND source = %s AND start_date = %s",(search_destination, search_source, start_date))
                    search_result = cur.fetcall()
                    mysql.connection.commit()
                    cur.close()

                    if search_result is None:

                        flash('NO CAB SHARES FOUND, START A NEW ONE!')
                        return redirect(url_for('cab_sharing'))

                    else:

                        return render_template('CAB_SEARCH_RESULT.html', searchresult = search_result)

                else:

                    flash('SOURCE AND DESTINATIION CANNOT BE SAME!')
                    return redirect(url_for('cab_search'))

    return render_template('CAB_SEARCH.html')

    else:
        return redirect('/login')



@app.route('/my_account')
def my_account():

    if g.loggedin:

        cur = mysql.connection.cursor()
        ping = g.loggedin
        cur.execute("SELECT * FROM userdata WHERE username = %s", (ping))
        userdetails = cur.fetchall()

        email = userdetails[0]['email']
        name = userdetails[0]['name']

        mysql.connection.commit()
        cur.close()

    return render_template('MY_ACCOUNT.html', username = ping, email = email, name = name )
        
    else:

        return redirect(url_for('login'))



@app.route('/my_account_edit')
def my_acoount_edit():

    if g.loggedin:

        if method == 'POST':

            name = request.form
            name = name['newname']

            cur = mysql.connection.cursor()
            ping = g.loggedin 
            cur.execute("UPDATE userdata SET name = %s WHERE username = %s",(name, ping))
            connection.commit()
            cur.close()

            flash('Successfully changed your Name!')
            return redirect(url_for('my_account'))

    return render_template('MY_ACCOUNT_EDIT.html')

    else:

        return redirect(url_for('login'))


@app.route('/product_posting')
def product_posting():

    if g.loggedin:

        if method == 'POST'

            product = request.form
            username = g.loggedin
            product_name = product['name']
            product_category = product['category']
            product_details = product['details']
            product_price = product['price']
            city = product['city']
            contact_details = product['contact']

            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO sell_and_buy(username, product_name, category, price, details, city, contact_details) VALUES(%s, %s, %s, %s, %s, %s, %s)",(username, product_name, product_category, product_price, product_details, city, contact_details))
            connection.commit()
            cur.close()

            return redirect(url_for('user'))

    return render_template('PRODUCT_POSTING.html')

    else:

        return redirect(url_for('login'))




@app.route('/my_products')
def my_products():

    if g.loggedin:

        cur = mysql.connection.cursor()
        ping = g.loggedin
        cur.execute("SELECT * FROM sell_and_buy WHERE username = %s",(ping))
        myads = cur.fetchall()
        connection.commit()
        cur.close()

        if method == 'POST':
            productid = request.form['productid']
            cur = mysql.connection.cursor()
            cur.execute("DELETE FROM buy_and_sell WHERE product_id = %s", (productid))
            connection.commit()
            cur.close()

            return redirect(url_for('my_products'))

    return render_template('MY_PRODUCTS.html', myads = myads)

    else:

        return redirect(url_for('login'))






if __name__ == '__main__':
    app.run(debug=True)
