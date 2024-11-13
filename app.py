from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
import mysql.connector
import bcrypt
import logging

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Database connection function
def connect_to_database():
    return mysql.connector.connect(
        host='127.0.0.1',
        database='Bijli_bill',
        user='root',
        password='Kunal@2534'  # Ensure this is your actual MySQL password
    )

@app.route('/')
def welcome():
    return render_template('welcome.html')

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        db = None
        cursor = None
        try:
            db = connect_to_database()
            cursor = db.cursor()
            cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
            user = cursor.fetchone()

            if user and bcrypt.checkpw(password.encode('utf-8'), user[2].encode('utf-8')):
                session['user_id'] = user[0]
                return redirect('/dashboard')
            else:
                flash('Invalid username or password', 'error')

        except mysql.connector.Error as err:
            flash(f"Database error: {err}", "error")
        finally:
            if cursor:
                cursor.close()
            if db:
                db.close()
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    return render_template('dashboard.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/')

@app.route('/save_bill')
def save_bill():
    return render_template('save_bill.html')

@app.route('/Policies')
def policies():
    return render_template('Policies.html')

@app.route('/Tender_informations')
def tender_informations():
    return render_template('Tender_informations.html')

@app.route('/Right_informations')
def right_informations():
    return render_template('Right_informations.html')

@app.route('/FAQs')
def faqs():
    return render_template('FAQs.html')


# Route to display contact requests and category change options
@app.route('/contact')
def contact():
    db = connect_to_database()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM contact_requests")
    contact_requests = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('contact.html', contact_requests=contact_requests)

# Endpoint to update category
@app.route('/update_category/<int:request_id>', methods=['POST'])
def update_category(request_id):
    new_category = request.form['category']
    db = connect_to_database()
    cursor = db.cursor()
    cursor.execute("UPDATE contact_requests SET category = %s WHERE id = %s", (new_category, request_id))
    db.commit()
    cursor.close()
    db.close()
    flash("Category updated successfully!", "success")
    return redirect(url_for('contact'))



@app.route('/feedback')
def feedback():
    return render_template('feedback.html')


@app.route('/api/feedback_requests')
def get_feedback_requests():
    try:
        conn = connect_to_database()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM feedback")
        rows = cursor.fetchall()
        return jsonify(rows)  # Return feedback data as JSON
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return jsonify([])  # Return empty list if an error occurs
    finally:
        cursor.close()
        conn.close()



# Handling contact form submission
@app.route('/submit_contact', methods=['POST'])
def submit_contact():
    name = request.form['name']
    email = request.form['email']
    subject = request.form['subject']
    message = request.form['message']

    db = None
    cursor = None
    try:
        db = connect_to_database()
        cursor = db.cursor()
        query = '''
        INSERT INTO contact_requests (name, email, subject, message) VALUES (%s, %s, %s, %s)
        '''
        cursor.execute(query, (name, email, subject, message))
        db.commit()
        return redirect(url_for('thank_you'))
    except Exception as e:
        return jsonify({'error': str(e)})
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()

# Thank you page after form submission
@app.route('/thank_you')
def thank_you():
    return render_template('thank_you.html')

# Insert feedback into the database
@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']
    feedback = request.form['feedback']

    db = None
    cursor = None
    try:
        db = connect_to_database()
        cursor = db.cursor()
        query = '''
        INSERT INTO feedback (name, email, phone, feedback) VALUES (%s, %s, %s, %s)
        '''
        cursor.execute(query, (name, email, phone, feedback))
        db.commit()
        return redirect(url_for('thank_you'))
    except Exception as e:
        return jsonify({'error': str(e)})
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()

# Insert billing data into the database
@app.route('/insert_data', methods=['POST'])
def insert_data():
    data = request.get_json()

    db = None
    cursor = None
    try:
        db = connect_to_database()
        cursor = db.cursor()
        query = f'''
        INSERT INTO {data["table_name"]} (previous_date, previous_reading, date_upto, current_reading, cost_of_unit)
        VALUES (%s, %s, %s, %s, %s)
        '''
        cursor.execute(query, (data['previous_date'], data['previous_reading'], data['date_upto'], data['current_reading'], data['cost_of_unit']))
        db.commit()
        return jsonify({'message': 'Data inserted successfully!'})
    except Exception as e:
        return jsonify({'error': str(e)})
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()

@app.route('/insert_form', methods=['GET', 'POST'])
def insert_form():
    tables = ["rambha_bill", "muskan_bill", "sanjeev_bill", "shweta_bill"]
    months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

    db = None
    cursor = None
    if request.method == 'POST':
        table_name = request.form['table_name']
        bill_id = request.form['bill_id']
        month = request.form['month']
        pay_date = request.form['pay_date']
        home_rent = request.form['home_rent']
        bijli_bill = request.form['bijli_bill']
        status = request.form['status']

        try:
            db = connect_to_database()
            cursor = db.cursor()
            cursor.execute(f"INSERT INTO {table_name} (Bill_id, Month, Pay_Date, Home_Rent, Bijli_bill, Status) VALUES (%s, %s, %s, %s, %s, %s) ",
                           (bill_id, month, pay_date, home_rent, bijli_bill, status))
            db.commit()
            flash("Data inserted successfully!", "success")
        except mysql.connector.Error as err:
            flash(f"Database error: {err}", "error")
        finally:
            if cursor:
                cursor.close()
            if db:
                db.close()
        return redirect('/insert_form')

    return render_template('insert_form.html', tables=tables, months=months)

# Fetch billing data from the database
@app.route('/fetch_data', methods=['POST'])
def fetch_data():
    data = request.get_json()

    db = None
    cursor = None
    try:
        db = connect_to_database()
        cursor = db.cursor()
        query = f'''
        SELECT previous_date, previous_reading, date_upto, current_reading, cost_of_unit, (current_reading - previous_reading) * cost_of_unit AS total_bill
        FROM {data["table_name"]}
        '''
        cursor.execute(query)
        records = cursor.fetchall()

        result = ""
        total_bill = 0
        for row in records:
            total_bill += row[5]
            result += '|'.join(map(str, row)) + "\n"

        return jsonify({'data': {'records': result.strip(), 'total_bill': total_bill}})
    except Exception as e:
        return jsonify({'error': str(e)})
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()

def fetch_bills(table_name):
    """Fetch billing data from the specified table."""
    conn = None
    cursor = None
    try:
        conn = connect_to_database()
        cursor = conn.cursor(dictionary=True)
        query = f"SELECT * FROM {table_name}"
        cursor.execute(query)
        results = cursor.fetchall()
        return results
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return []
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/view_bills', methods=['POST'])
def view_bills():
    table_name = request.form.get('table_name')
    bills = fetch_bills(table_name)
    return render_template('bills.html', bills=bills, table_name=table_name)

@app.route('/bill_details/<string:table_name>/<int:bill_id>')
def bill_details(table_name, bill_id):
    bill = fetch_bill_details(table_name, bill_id)
    return render_template('bill_details.html', bill=bill)

@app.route('/update_status/<string:table_name>/<int:bill_id>', methods=['POST'])
def update_status(table_name, bill_id):
    current_status = request.form['current_status']
    new_status = 'paid' if current_status == 'unpaid' else 'unpaid'
    
    conn = None
    cursor = None
    try:
        conn = connect_to_database()
        cursor = conn.cursor()
        cursor.execute(f"UPDATE {table_name} SET Status = %s WHERE Bill_id = %s", (new_status, bill_id))
        conn.commit()
        flash('Status updated successfully!', "success")
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        flash('Error updating status.', "error")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    
    return redirect(url_for('watson'))  # Redirect to the watson view

@app.route('/watson')
def watson():
    return render_template('watson.html')  # Main page for the application

def fetch_bill_details(table_name, bill_id):
    """Fetch detailed billing data from the specified table for a given bill ID."""
    conn = None
    cursor = None
    try:
        conn = connect_to_database()
        cursor = conn.cursor(dictionary=True)
        query = f"SELECT * FROM {table_name} WHERE Bill_id = %s"
        cursor.execute(query, (bill_id,))
        result = cursor.fetchone()
        return result
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return {}
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == '__main__':
    app.run(debug=True)
