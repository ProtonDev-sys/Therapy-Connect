from flask import Flask, render_template, request, redirect, make_response, jsonify, url_for, send_from_directory
from account import Account
from therapist import Therapist
from database import Database
import re
from utilities import is_strong_password
import os
### todo ###
# booking page
# only allow booking if the date is not taken, display only available dates/times
# user accounts ->
# store details in user table
# hash passwords + salt (maybe pepper too)
# session tokens that lasts 300 seconds per keep-alive request, max of 1 request / second
# admin page ->
# admin accounts for admin page
# view databases update - remove


class Website():
    def __init__(self) -> None:
        self.app = Flask(__name__)
        self.database = Database()

    def run(self) -> None:
        self.defineUrls()
        self.app.run(host="127.0.0.1", port=8080)

    def defineUrls(self) -> None:
        self.app.add_url_rule("/", "Index", self.index, methods=['GET'])
        self.app.add_url_rule("/search", "Search", self.search, methods=['GET'])
        self.app.add_url_rule("/previewSearch", "PreviewSearch",
                              self.previewSearch, methods=['GET'])
        self.app.add_url_rule("/book", "book", self.book, methods=['GET'])
        self.app.add_url_rule("/login", "Login", self.login, methods=['GET'])
        self.app.add_url_rule("/login", "authorizeLogin",
                              self.login_post, methods=['POST'])
        self.app.add_url_rule("/logout", "logout",
                              self.logout, methods=['POST'])
        self.app.add_url_rule("/signup", "SignUpPage",
                              self.signup_get, methods=['GET'])
        self.app.add_url_rule("/register", "register",
                              self.signup_get, methods=['GET'])

        self.app.add_url_rule("/signup", "AuthorizeSignup",
                              self.signup_post, methods=['POST'])
        self.app.add_url_rule("/profile", "GetProfile",
                              self.get_profile, methods=['GET'])
        self.app.add_url_rule(
            "/admin", "admin", self.admin_page, methods=['GET'])
        self.app.add_url_rule(
            "/get_database", "get_database", self.get_database, methods=['GET'])
        self.app.add_url_rule(
            "/update_database", "update_database", self.update_database, methods=['POST'])
        self.app.register_error_handler(404, self.handle_404)

        # self.app.add_url_rule("/favicon.ico", "/favicon.ico", self.favicon, methods=['GET'])
    def handle_404(self, error):
        return make_response(render_template('404.html', error=error))

    def favicon(self) -> None:
        pass
    #    return send_from_directory(os.path.join(app.root_path, 'static'),
    #                           'favicon.ico', mimetype='image/vnd.microsoft.icon')

    def is_admin(self, request) -> bool:
        session_token = request.cookies.get("SESSION-TOKEN")
        if not session_token:
            return False,"",
        account = Account()
        id = None
        if request.args.get('username'):
            username = request.args.get('username')
        elif request.args.get('id'):
            id = request.args.get('id')
        else:
            username = request.cookies.get("USERNAME")

        account.username = request.cookies.get("USERNAME")
        valid = account.set_session_token(session_token)
        if not valid:
            return False,"",
        print(self.database.get_account_by_username(username))
        if int(self.database.get_account_by_username(username)[4]) == 1:
            return True,valid,


    def get_database(self) -> dict:
        #valid, token = self.is_admin(request)
        #print(token )
        valid = True
        token = "admin-testing"
        if not valid:
            response = make_response(jsonify([["nice", "try", "you", "are", "not", "admin", "get out bozo"]]))
            return response 
        else:
            response = make_response(jsonify(self.database.get_account_database()))
            response.set_cookie("SESSION-TOKEN", token)
        return response
    
    def update_database(self) -> dict:
        #valid, token = self.is_admin(request)  
        #print(valid, token)
        valid = True
        token = "admin-testing"
        if not valid:
            response = make_response(jsonify(["go away."]))
            response.set_cookie("SESSION-TOKEN", token)
            return response 
        else:
            request_type = request.args.get('type')
            database = request.args.get('database')
            if database == "account" and request_type == "edit":
                record = request.get_json()['record']
                self.database.update_account_from_id(record)
                response = make_response(jsonify([True]))
                response.set_cookie("SESSION-TOKEN", token)
                return response

    def index(self) -> dict:
        session_token = request.cookies.get("SESSION-TOKEN")
        
        if not session_token:
            return redirect(url_for('Login'))
        account = Account()
        id = None
        if request.args.get('username'):
            username = request.args.get('username')
        elif request.args.get('id'):
            id = request.args.get('id')
        else:
            username = request.cookies.get("USERNAME")

        account.username = request.cookies.get("USERNAME")
        valid = account.set_session_token(session_token)
        if not valid:
            return redirect(url_for('Login'))
        response = make_response(render_template('index.html'))
        response.set_cookie('SESSION-TOKEN', valid)
        return response

    def search(self) -> dict:
        query = request.args.get('search')
        if not query:
            return redirect('/')
        results = []
        therapists = self.database.get_therapists()
        for therapist in therapists:
            if query.lower() in therapist['name'].lower() or query.lower() in therapist['speciality'].lower() or query.lower() in therapist['location'].lower():
                results.append(therapist)
        return render_template('search_results.html', query=query, therapists=results)

    def previewSearch(self) -> dict:
        query = request.args.get('search')
        if not query:
            return redirect('/')
        results = []
        therapists = self.database.get_therapists()
        for therapist in therapists:
            if query.lower() in therapist['name'].lower() or query.lower() in therapist['speciality'].lower() or query.lower() in therapist['location'].lower():
                if len(results) < 4:
                    results.append(therapist)
        return jsonify(results)

    def book(self) -> dict:
        account = Account()
        account.username = request.cookies.get("USERNAME")
        session_token = request.cookies.get("SESSION-TOKEN")
        if not account.validate_session_token(session_token):
            return redirect(url_for('Login'))
        id = request.args.get('id')
        therapist = self.database.get_therapist_by_id(id)
        if not therapist:
            return redirect('/')
        return render_template('booking.html', therapist=therapist)

    def login(self) -> dict:
        return render_template("login.html")

    def login_post(self) -> dict:
        username = request.form['username']
        password = request.form['password']
        if not username or not password:
            return make_response(jsonify({"LOGIN-SUCCESS": False, "ERROR": "Invalid username or password"}))
        account = Account()
        account.username = username
        valid_login = account.login(username, password)
        if not valid_login:
            return make_response(jsonify({"LOGIN-SUCCESS": False, "ERROR": "Invalid username or password"}))
        session_token = account.get_session_token()
        response_data = {"LOGIN-SUCCESS": True}
        response = make_response(jsonify(response_data))
        response.set_cookie("SESSION-TOKEN", value=session_token, max_age=1200)
        response.set_cookie("USERNAME", value=username)
        return response

    def signup_get(self) -> dict:
        return render_template('signup.html')

    def signup_post(self) -> dict:
        username = request.form['username']
        email = request.form['email']
        phone_number = request.form['phone']
        full_name = request.form['full_name']
        password = request.form['password']
        try:
            first_part = request.form['first-part']
        except:
            first_part = False
        error = None

        new_account = Account()

        if not re.match("^[a-zA-Z0-9_]{3,20}$", username):
            error = "Invalid username, ensure your username uses only alphanumeric characters and is between 3 and 20 characters."

        # Check email validity
        if not re.match("^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email) and not first_part and not error:
            error = "Invalid email, ensure your email address contains only alphanumeric characters and has the @xxx.xxx."

        # Check phone number validity
        if not re.match("^[0-9]{10}$", phone_number) and not first_part and not error:
            error = "Invalid phone number."

        # Check full name validity
        if not re.match("^[A-Za-z ]{3,50}$", full_name) and not first_part and not error:
            error = "Invalid name, ensure you've only input alphanumeric characters, if you believe this is an issue contact support."

        # Check password strength
        if not is_strong_password(password) and not error:
            error = "Weak password, your password must be at least 8 characters, contain at least 1 uppercase and lowercase character and symbols."

        if not error:
            account_exists = new_account.account_exists(username, phone_number)
            if account_exists:
                error = f"Account with that {account_exists == 1 and 'username' or 'phone number'} already exists."
            elif first_part:
                response = make_response(jsonify({"success": True}))
                return response

        # All fields are valid
        if error:
            return jsonify({"error": error})
        else:
            new_account = Account()
            new_account.username = username
            new_account.signup(username, password, "user")
            account = self.database.get_account_by_username(username)
            self.database.add_customer_to_database(
                account[0], full_name, email, phone_number)
            response = make_response(jsonify({"success": True}))
            response.set_cookie(
                "SESSION-TOKEN", value=new_account.get_session_token(), max_age=1200)
            response.set_cookie("USERNAME", value=username, max_age=1200)

            return response

    def get_profile(self) -> dict:
        session_token = request.cookies.get("SESSION-TOKEN")
        if not session_token:
            return redirect(url_for('Login'))
        account = Account()
        id = None
        if request.args.get('username'):
            username = request.args.get('username')
        elif request.args.get('id'):
            id = request.args.get('id')
        else:
            username = request.cookies.get("USERNAME")

        account.username = request.cookies.get("USERNAME")
        valid = account.set_session_token(session_token)
        print(valid)
        if not valid:
            return redirect(url_for('Login'))
        if not id:
            profile_account = self.database.get_account_by_username(username)
        else:
            profile_account = self.database.get_account_by_id(id)

        if not profile_account:
            response = jsonify({"error": "Account does not exist."})
            response.set_cookie("SESSION-TOKEN", value=valid, max_age=1200)
            return response

        if profile_account[5] == "therapist":
            other_database = self.database.get_therapist_by_account_id(
                profile_account[0])
            response = make_response(render_template('profile.html', user={
                "username": profile_account[1],
                "creation_date": profile_account[3],
                "type": profile_account[5],
                "name": other_database.name,
                "speciality": other_database.speciality,
            }))
        else:
            other_database = self.database.get_customer_by_account_id(
                profile_account[0])
            response = make_response(render_template('profile.html', user={
                "username": profile_account[1],
                "creation_date": profile_account[3],
                "type": profile_account[5],
                "name": other_database.name,
                "speciality": "Customer",
            }))
        response.set_cookie("SESSION-TOKEN", value=valid, max_age=1200)
        return response

    def logout(self) -> dict:
        response = make_response(jsonify({"success": True}))
        response.delete_cookie("USERNAME")
        response.delete_cookie("SESSION-TOKEN")

        return response

    def admin_page(self) -> dict:
        return render_template("admin.html")


if __name__ == '__main__':
    website = Website()
    website.run()
