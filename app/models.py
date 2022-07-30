from datetime import datetime

from passlib.hash import pbkdf2_sha256 as sha256
from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship
from flask_login import UserMixin

from app.database.database import base, session

"""All models used: TicketModel, SessionModel, FilmModel, ActorModel, HallModel, UserModel, RevokedTokenModel"""


class TicketModel(base):
    __tablename__ = "tickets"
    id = Column(Integer, primary_key=True)
    seat = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    session_id = Column(Integer, ForeignKey('sessions.id'))
    user = relationship("UserModel", back_populates='tickets')
    session = relationship("SessionModel", back_populates='tickets')

    @classmethod
    def find_by_id(cls, id_, to_dict=True):
        """Method for finding selected ticket by id"""
        ticket = session.query(cls).filter_by(id=id_).first()
        if not ticket:
            return {}
        if to_dict:
            return cls.to_dict(ticket)
        else:
            return ticket

    @classmethod
    def find_by_user_id(cls, user_id, offset, limit):
        """
            Method for finding selected ticket by user_id
            Returns list of dictionaries
        """
        tickets = session.query(cls).filter_by(user_id=user_id) \
            .order_by(cls.id).offset(offset).limit(limit).all()
        return [cls.to_dict(s) for s in tickets]

    @classmethod
    def find_by_session_id(cls, session_id, offset, limit):
        """
            Method for finding selected ticket by session_id
            Returns list of dictionaries
        """
        tickets = session.query(cls).filter_by(session_id=session_id) \
            .order_by(cls.id).offset(offset).limit(limit).all()
        return [cls.to_dict(s) for s in tickets]

    @classmethod
    def return_all(cls):
        """Method to return all tickets"""
        tickets = session.query(cls).order_by(cls.id).all()
        return [cls.to_dict(ticket) for ticket in tickets]

    @classmethod
    def delete_by_id(cls, id_):
        """Method to delete ticket by id"""
        ticket = session.query(cls).filter_by(id=id_).first()
        if ticket:
            session.delete(ticket)
            session.commit()
            return 200
        else:
            return 404

    def save_to_db(self):
        """Method to save changes into DB"""
        session.add(self)
        session.commit()

    @staticmethod
    def to_dict(ticket):
        """Method to get a dict with fields"""
        return {
            "id": ticket.id,
            "seat": ticket.seat,
            "user_id": ticket.user_id,
            "session_id": ticket.session_id
        }


class SessionModel(base):
    __tablename__ = "sessions"
    id = Column(Integer, primary_key=True)
    started_at = Column(DateTime())
    number_seats = Column(Integer)
    hall_id = Column(Integer, ForeignKey('halls.id'))
    film_id = Column(Integer, ForeignKey('films.id'))
    film = relationship("FilmModel", back_populates='sessions')
    hall = relationship("HallModel", back_populates='sessions')
    tickets = relationship(TicketModel, lazy='dynamic',
                           cascade="all, delete-orphan",
                           foreign_keys="TicketModel.session_id")

    @classmethod
    def find_by_id(cls, id_, to_dict=True):
        """Method for finding selected session by id"""
        sess = session.query(cls).filter_by(id=id_).first()
        if not sess:
            return {}
        if to_dict:
            return cls.to_dict(sess)
        else:
            return sess

    @classmethod
    def find_by_film_id(cls, film_id, offset, limit):
        """
            Method for finding sessions by film_id
            Returns list of dictionaries
        """
        from_date = datetime(year=datetime.now().year, month=datetime.now().month, day=datetime.now().day,
                             hour=datetime.now().hour, minute=datetime.now().minute, second=datetime.now().second)
        sessions = session.query(cls).filter(SessionModel.started_at >= from_date).filter_by(film_id=film_id) \
            .order_by(cls.id).offset(offset).limit(limit).all()
        return [cls.to_dict(s) for s in sessions]

    @classmethod
    def delete_by_id(cls, id_):
        """Method to delete session by id"""
        session_ = session.query(cls).filter_by(id=id_).first()
        if session_:
            session.delete(session_)
            session.commit()
            return 200
        else:
            return 404

    @classmethod
    def return_all(cls):
        """Method to return all sessions"""
        from_date = datetime(year=datetime.now().year, month=datetime.now().month, day=datetime.now().day,
                             hour=datetime.now().hour, minute=datetime.now().minute, second=datetime.now().second)
        sessions = session.query(cls).filter(SessionModel.started_at >= from_date).order_by(cls.id).all()
        return [cls.to_dict(sess) for sess in sessions]

    @classmethod
    def find_by_genre(cls, genre):
        """
            Method for finding sessions by genre
            Returns list of dictionaries
        """
        if genre:
            sessions = session.query(cls).join(FilmModel).filter(FilmModel.genre == genre).all()
        else:
            sessions = cls.return_all()
        return [cls.to_dict(sess) for sess in sessions]

    @classmethod
    def find_by_name(cls, name):
        """
            Method for finding sessions by film name
            Returns list of dictionaries
        """
        if name:
            sessions = session.query(cls).join(FilmModel).filter(FilmModel.name == name).all()
        else:
            sessions = cls.return_all()
        return [cls.to_dict(sess) for sess in sessions]

    @classmethod
    def find_by_actor(cls, actor_name):
        """
            Method for finding sessions by actor
            Returns list of dictionaries
        """
        if actor_name:
            sessions = session.query(SessionModel).join(FilmModel).join(film_actor).join(ActorModel).filter(
                ActorModel.name == actor_name).all()
        else:
            sessions = cls.return_all()
        return [cls.to_dict(sess) for sess in sessions]

    @classmethod
    def find_by_director(cls, director):
        """
            Method for finding sessions by director
            Returns list of dictionaries
        """
        if director:
            sessions = session.query(cls).join(FilmModel).filter(FilmModel.director == director).all()
        else:
            sessions = cls.return_all()
        return [cls.to_dict(sess) for sess in sessions]

    @classmethod
    def find_by_date(cls, started_at):
        """
            Method for finding sessions by date
            Returns list of dictionaries
        """
        if started_at:
            from_date = datetime(year=datetime.now().year, month=datetime.now().month, day=datetime.now().day,
                                 hour=datetime.now().hour, minute=datetime.now().minute, second=datetime.now().second)
            sessions = session.query(SessionModel).filter(SessionModel.started_at == started_at) \
                .filter(SessionModel.started_at >= from_date).all()
        else:
            sessions = cls.return_all()
        return [cls.to_dict(sess) for sess in sessions]

    def save_to_db(self):
        """Method to save changes into DB"""
        session.add(self)
        session.commit()

    @staticmethod
    def to_dict(session_):
        """Method to get a dict with fields"""
        return {
            "id": session_.id,
            "started_at": session_.started_at,
            "film_id": session_.film_id,
            "hall_id": session_.hall_id,
            "number_seats": session_.number_seats
        }


film_actor = Table('association', base.metadata,
                   Column('films_id', Integer, ForeignKey('films.id'), primary_key=True),
                   Column('actors_id', Integer, ForeignKey('actors.id'), primary_key=True)
                   )


class FilmModel(base):
    __tablename__ = "films"
    id = Column(Integer, primary_key=True)
    name = Column(String(30), nullable=False)
    genre = Column(String(30), nullable=False)
    director = Column(String(30), nullable=False)
    image = Column(String(30), nullable=False)
    rating = Column(Float, nullable=False)
    sessions = relationship(SessionModel, lazy='dynamic',
                            cascade="all, delete-orphan",
                            foreign_keys="SessionModel.film_id")
    actors = relationship(
        "ActorModel",
        secondary=film_actor,
        back_populates="films")

    @classmethod
    def find_by_id(cls, id_, to_dict=True):
        """Method for finding selected film by id"""
        film = session.query(cls).filter_by(id=id_).first()
        if not film:
            return {}
        if to_dict:
            return cls.to_dict(film)
        else:
            return film

    @classmethod
    def find_by_session_id(cls, id_):
        """
            Method for finding film by session id
            Returns list of dictionaries
        """
        if id_:
            films = session.query(cls).join(SessionModel).filter(SessionModel.id == id_).all()
        else:
            films = cls.return_all()
        return [cls.to_dict(sess) for sess in films]

    @classmethod
    def return_all(cls):
        """Method to return all films"""
        films = session.query(cls).order_by(cls.id).all()
        return [cls.to_dict(film) for film in films]

    @classmethod
    def delete_by_id(cls, id_):
        """Method to delete film by id"""
        film = session.query(cls).filter_by(id=id_).first()
        if film:
            session.delete(film)
            session.commit()
            return 200
        else:
            return 404

    def save_to_db(self):
        """Method to save changes into DB"""
        session.add(self)
        session.commit()

    @staticmethod
    def to_dict(film):
        """Method to get a dict with fields"""
        return {
            "id": film.id,
            "name": film.name,
            "genre": film.genre,
            "director": film.director,
            "image": film.image,
            "rating": film.rating
        }


class ActorModel(base):
    __tablename__ = "actors"
    id = Column(Integer, primary_key=True)
    name = Column(String(30), nullable=False)
    surname = Column(String(30), nullable=False)
    films = relationship(
        "FilmModel",
        secondary=film_actor,
        back_populates="actors")

    @classmethod
    def find_by_film_id(cls, film_id, offset, limit):
        """
            Method for finding actors by film_id
            Returns list of dictionaries
        """
        actors = session.query(cls).filter_by(film_id=film_id) \
            .order_by(cls.id).offset(offset).limit(limit).all()
        return [cls.to_dict(s) for s in actors]

    @classmethod
    def return_all(cls):
        """Method to return all actors"""
        actors = session.query(cls).order_by(cls.id).all()
        return [cls.to_dict(actor) for actor in actors]

    @classmethod
    def delete_by_id(cls, id_):
        """Method to delete actor by id"""
        actor = session.query(cls).filter_by(id=id_).first()
        if actor:
            session.delete(actor)
            session.commit()
            return 200
        else:
            return 404

    def save_to_db(self):
        """Method to save changes into DB"""
        session.add(self)
        session.commit()

    @staticmethod
    def to_dict(actor):
        """Method to get a dict with fields"""
        return {
            "id": actor.id,
            "name": actor.name,
            "surname": actor.surname,
        }


class HallModel(base):
    __tablename__ = "halls"
    id = Column(Integer, primary_key=True)
    name = Column(String(30), nullable=False)
    capacity = Column(Integer, nullable=False)
    sessions = relationship(SessionModel, lazy='dynamic',
                            cascade="all, delete-orphan",
                            foreign_keys="SessionModel.hall_id")

    @classmethod
    def find_by_id(cls, id_, to_dict=True):
        """Method for finding selected hall by id"""
        hall = session.query(cls).filter_by(id=id_).first()
        if not hall:
            return {}
        if to_dict:
            return cls.to_dict(hall)
        else:
            return hall

    @classmethod
    def return_all(cls):
        """Method to return all halls"""
        halls = session.query(cls).order_by(cls.id).all()
        return [cls.to_dict(hall) for hall in halls]

    @classmethod
    def delete_by_id(cls, id_):
        """Method to delete hall by id"""
        hall = session.query(cls).filter_by(id=id_).first()
        if hall:
            session.delete(hall)
            session.commit()
            return 200
        else:
            return 404

    def save_to_db(self):
        """Method to save changes into DB"""
        session.add(self)
        session.commit()

    @staticmethod
    def to_dict(hall):
        """Method to get a dict with fields"""
        return {
            "id": hall.id,
            "name": hall.name,
            "capacity": hall.capacity,

        }


class UserModel(base, UserMixin):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(30), nullable=False)
    age = Column(Integer, nullable=False)
    username = Column(String(30), nullable=False)
    email = Column(String(30), nullable=False)
    hashed_password = Column(String(50), nullable=False)
    is_admin = Column(Boolean(), default=False)
    tickets = relationship(TicketModel, lazy='dynamic',
                           cascade="all, delete-orphan",
                           foreign_keys="TicketModel.user_id")

    @classmethod
    def find_by_id(cls, id_, to_dict=True):
        """Method for finding selected user by id"""
        user = session.query(cls).filter_by(id=id_).first()
        if not user:
            return {}
        if to_dict:
            return cls.to_dict(user)
        else:
            return user

    @classmethod
    def find_by_username(cls, username, to_dict=True):
        """Method for finding selected user by username"""
        user = session.query(cls).filter_by(username=username).first()
        if not user:
            return {}
        if to_dict:
            return cls.to_dict(user)
        else:
            return user

    @classmethod
    def find_by_email(cls, email, to_dict=True):
        """Method for finding selected user by email"""
        user = session.query(cls).filter_by(email=email).first()
        if not user:
            return {}
        if to_dict:
            return cls.to_dict(user)
        else:
            return user

    @classmethod
    def return_all(cls):
        """Method to return all users"""
        users = session.query(cls).order_by(cls.id).all()
        return [cls.to_dict(user) for user in users]

    @classmethod
    def delete_by_id(cls, id_):
        """Method to delete user by id"""
        user = session.query(cls).filter_by(id=id_).first()
        if user:
            session.delete(user)
            session.commit()
            return 200
        else:
            return 404

    def save_to_db(self):
        """Method to save changes into DB"""
        session.add(self)
        session.commit()

    @staticmethod
    def to_dict(user):
        """Method to get a dict with fields"""
        return {
            "id": user.id,
            "name": user.name,
            "age": user.age,
            "username": user.username,
            "email": user.email,
            "is_admin": user.is_admin,
        }

    @staticmethod
    def generate_hash(password):
        """Method for generating hashed password"""
        return sha256.hash(password)

    @staticmethod
    def verify_hash(password, hash_):
        """Method to verify password"""
        return sha256.verify(password, hash_)


class RevokedTokenModel(base):
    __tablename__ = 'revoked_tokens'
    id_ = Column(Integer, primary_key=True)
    jti = Column(String(120))
    blacklisted_on = Column(DateTime, default=datetime.utcnow)

    def add(self):
        """Method to save changes into DB"""
        session.add(self)
        session.commit()

    @classmethod
    def is_jti_blacklisted(cls, jti):
        """Method to check if this unique identifier for token is in blacklist"""
        query = session.query(cls).filter_by(jti=jti).first()
        return bool(query)
