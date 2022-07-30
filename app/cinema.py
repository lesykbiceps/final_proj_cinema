import flask_login
from datetime import datetime

from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required

from app.models import UserModel, FilmModel, SessionModel, session, TicketModel
from .forms import RegisterForm, LoginForm, SeatForm

cinema_bp = Blueprint('cinema', __name__)


@cinema_bp.route('/', methods=['GET', 'POST'])
@cinema_bp.route('/home')
def index():
    """Demonstrates films and give opportunity
        to buy a movie ticket."""

    result = FilmModel.return_all()
    return render_template('index.html', title="Home page", result=result)


@cinema_bp.route('/schedule', methods=['GET', 'POST'])
@login_required
def schedule():
    """Demonstrates all available sessions and give opportunity
            to buy a ticket on some session. Only logged-in users can see this page.
            Otherwise, user redirects for logination. """
    sess = session.query(SessionModel, FilmModel).join(FilmModel, SessionModel.film_id == FilmModel.id)\
        .filter(SessionModel.started_at >= datetime.now()).all()
    sess_list = []
    for sess_, film in sess:
        sess_list.append({
            'sess_id': sess_.id,
            'started_at': sess_.started_at,
            'hall_id': sess_.hall_id,
            'number_seats': sess_.number_seats,
            'name': film.name,
            'genre': film.genre,
            'director': film.director
        })
    return render_template('schedule.html', title="Sessions page", sess_list=sess_list)


@cinema_bp.route("/schedule/<int:id_>", methods=["GET"])
@login_required
def get_schedule(id_):
    """
        Show all sessions for selected film.This function  accept id_ parameters.
        Only logged-in users can see this page.Otherwise, user redirects for logination.
            Args:
                id_: id of film what you want to get
            Returns:
                Sessions for film with selected id.
        """
    schedules = SessionModel.find_by_film_id(id_, offset=0, limit=100)
    return render_template('schedule_id.html', title="Sessions page", sess_list=schedules)


@cinema_bp.route("/buyticket/<int:id_>", methods=['GET', 'POST'])
@login_required
def buy_ticket(id_):
    """
        Page to purchase a ticket. Only authorized user can buy ticket.
            Args:
                id_: id of session which film you want to watch.
            Returns:
                Session's page with ability to buy ticket.
        """
    film = FilmModel.find_by_session_id(id_)

    blocked = session.query(TicketModel).filter(TicketModel.session_id == id_).all()
    lst = []
    lst_seats = []
    for s in blocked:
        lst.append(s.seat)
    session_ = session.query(SessionModel).filter(SessionModel.id == id_).first()
    count_seats = len(lst) + session_.number_seats
    for i in range(1, count_seats + 1):
        if i not in lst:
            lst_seats.append(i)
    available_seats = str(lst_seats)[1:-1]
    form = SeatForm()
    if form.validate_on_submit():
        user_id = flask_login.current_user.id
        if session_.number_seats > 0 and form.seat.data not in lst:
            ticket = TicketModel(
                seat=form.seat.data, user_id=user_id, session_id=id_)
            ticket.save_to_db()
            session_.number_seats -= 1
            session_.save_to_db()
            flash("Congratulations! You bought a ticket", category='success')
            return redirect(url_for('cinema.index'))
        if form.seat.data in lst:
            flash('Please, choose another seat.This place is already reserved', category='warning')
        else:
            flash('Error occurred. Maybe we have not available seat for this session', category='danger')
    return render_template('ticket.html', title='Purchase ticket', film=film, available_seats=available_seats,
                           form=form)


@cinema_bp.route('/purchased_tickets/<int:id_>', methods=['GET'])
@login_required
def get_my_tickets(id_):
    """
        Show all tickets for selected user_id.This function  accept id_ parameters.
        Only logged-in users can see this page.Otherwise, user redirects for logination.
            Args:
                id_: id of user what you want to get
            Returns:
                Ticket purchase history
        """
    tickets = TicketModel.find_by_user_id(id_, 0, 10)
    return render_template('mytickets.html', title="Purchase history", tickets=tickets)


@cinema_bp.route('/check_tickets', methods=['GET'])
@login_required
def check_my_tickets():
    """Secondary page to check user's tickets"""
    id_ = flask_login.current_user.id
    return render_template('check_stat.html', title="Purchase history", id_=id_)


@cinema_bp.route('/register', methods=['GET', 'POST'])
def register_page():
    """Method for adding a new user (registration)
           using form.
        """
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = UserModel(username=form.username.data, name=form.name.data,
                                   email=form.email.data, age=form.age.data, is_admin=form.checkbox.data,
                                   hashed_password=UserModel.generate_hash(form.password1.data))
        user_to_create.save_to_db()
        login_user(user_to_create)
        flash(f'Account created successfully! You are now logged in as: {user_to_create.username}', category='success')
        return redirect(url_for('cinema.index'))

    if form.errors != {}:  # If there are not errors from the validations
        for err_msg in form.errors.values():
            flash(f'There was an error with creating a user:{err_msg}', category='danger')
    return render_template('register.html', form=form, title='Register')


@cinema_bp.route('/login', methods=['GET', 'POST'])
def login_page():
    """Method for user to login using form."""
    form = LoginForm()
    current_user = UserModel.find_by_username(form.username.data, to_dict=False)
    if form.validate_on_submit():
        attempted_user = UserModel.find_by_username(form.username.data, to_dict=False)
        if attempted_user and UserModel.verify_hash(form.password.data, current_user.hashed_password):
            login_user(attempted_user)
            flash(f'Success! You are logged in as: {attempted_user.username}', category='success')
            return redirect(url_for('cinema.schedule'))
        else:
            flash('Username and password are not match!Please, try again', category='danger')
    return render_template('login.html', form=form, title='Sign in')


@cinema_bp.route('/logout')
def logout_page():
    """Method for user to logout  from account."""
    logout_user()
    flash('You have been logged out', category='info')
    return redirect(url_for('cinema.index'))


@cinema_bp.route('/about')
def about_page():
    """Method for user to look at page about cinema."""
    return render_template('about.html', title='About us')

@cinema_bp.route('/author')
def author_page():
    """Method for user to look at page about author."""
    return render_template('author.html', title='About author')

@cinema_bp.errorhandler(404)
def page_not_found(error):
    """Method for catching error 404"""
    return render_template('page404.html', title="Page not found"), 404
