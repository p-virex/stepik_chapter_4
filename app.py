from random import shuffle
from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy

from flask_migrate import Migrate
from sqlalchemy.dialects.postgresql import JSON

from data import days
from forms import RequestForm

app = Flask(__name__)
app.secret_key = "randomstring"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data/my_app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

teacher_goals = db.Table(
    "teachers_goals",
    db.Column("teacher_id", db.Integer, db.ForeignKey("teachers.id")),
    db.Column("goal_id", db.Integer, db.ForeignKey("goals.id")),
)


class Teacher(db.Model):
    __tablename__ = "teachers"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    about = db.Column(db.String)
    rating = db.Column(db.Integer)
    photo = db.Column(db.String)
    price = db.Column(db.Integer)
    schedule = db.Column(JSON)
    goals = db.relationship("Goal", secondary=teacher_goals, back_populates="teachers")


class Goal(db.Model):
    __tablename__ = "goals"
    id = db.Column(db.Integer, primary_key=True)
    goal = db.Column(db.String)
    goal_tag = db.Column(db.String)
    teachers = db.relationship("Teacher", secondary=teacher_goals, back_populates="goals")


class Booking(db.Model):
    __tablename__ = "bookings"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    day = db.Column(db.String)
    time = db.Column(db.String)
    name_user = db.Column(db.String)
    phone_user = db.Column(db.String)


class Request(db.Model):
    __tablename__ = "requests"
    id = db.Column(db.Integer, primary_key=True)
    goal = db.Column(db.String)
    free_time = db.Column(db.String)
    name_user = db.Column(db.String)
    phone_user = db.Column(db.String)


def get_goals_id_dict():
    return {goal.id: goal.goal for goal in db.session.query(Goal).all()}


def get_teacher_info(teacher_id):
    teacher_info = db.session.query(Teacher).get_or_404(teacher_id)
    return {
        'name': teacher_info.name,
        'photo': teacher_info.photo,
        'rating': teacher_info.rating,
        'price': teacher_info.price,
        'about': teacher_info.about,
        'id': teacher_info.id,
        'free': teacher_info.schedule
    }


def migrate_data_from_json():
    from collect_data import g_data
    for tag, goal in g_data.get_from_data('goals').items():
        db.session.add(Goal(goal=goal, goal_tag=tag))
    for info in g_data.get_from_data('teachers'):
        teacher = Teacher(name=info['name'],
                          about=info['about'],
                          rating=info['rating'],
                          photo=info['picture'],
                          price=info['price'],
                          schedule=info['free'])
        db.session.add(teacher)
        for goal in info['goals']:
            id_goal = db.session.query(Goal).filter(Goal.goal_tag == goal).first()
            teacher.goals.append(id_goal)
    db.session.commit()


@app.route('/')
def render_index():
    """
    Выводим рандомных 6 учителя
    """
    teachers_list = [{
        'id': teacher.id,
        'name': teacher.name,
        'about': teacher.about,
        'rating': teacher.rating,
        'photo': teacher.photo,
        'price': teacher.price,
    } for teacher in db.session.query(Teacher).all()]
    shuffle(teachers_list)
    return render_template('index.html',
                           goals=get_goals_id_dict(),
                           teachers=teachers_list[:6])


@app.errorhandler(500)
def render_server_error(error):
    return "Что-то не так, но мы все починим"


@app.errorhandler(404)
def render_not_found(error):
    return "Ничего не нашлось! Вот неудача, отправляйтесь на главную!"


@app.route('/all/')
def render_all():
    """
    Выводим все учителей без рандомайзера
    """
    teachers = db.session.query(Teacher).all()
    teachers_list = [{
        'id': teacher.id,
        'name': teacher.name,
        'about': teacher.about,
        'rating': teacher.rating,
        'photo': teacher.photo,
        'price': teacher.price,
    } for teacher in teachers]
    return render_template("index.html",
                           goals=get_goals_id_dict(),
                           teachers=teachers_list)


@app.route('/goals/<goal_id>/')
def render_goal(goal_id):
    teachers_goal = Goal.query.filter(Goal.id == goal_id).scalar()
    current_goal = db.session.query(Goal).get(goal_id)
    teachers_list = [get_teacher_info(teacher_id) for teacher_id in
                     [id_teacher.id for id_teacher in teachers_goal.teachers]]
    return render_template("goal.html",
                           goal=current_goal.goal,
                           id_goal=goal_id,
                           goals=get_goals_id_dict(),
                           teachers=teachers_list)


@app.route('/profiles/<id_profile>/')
def render_profile(id_profile):
    teachers_goal = Teacher.query.filter(Teacher.id == id_profile).scalar()
    str_goal = ''
    for goal_id in teachers_goal.goals:
        goal_query = db.session.query(Goal).get(goal_id.id)
        str_goal += goal_query.goal + ' '
    return render_template("profile.html",
                           teacher=get_teacher_info(id_profile),
                           tag_goals=str_goal,
                           days=days)


@app.route('/request/')
def render_request():
    form = RequestForm()
    return render_template("request.html",
                           form=form)


@app.route('/booking_done/', methods=["GET", "POST"])
def render_booking_done():
    form = RequestForm()
    if request.method == 'POST':
        booking = Booking(name=form.client_teacher.data,
                          day=form.client_weekday.data,
                          time=form.client_time.data,
                          name_user=form.name.data,
                          phone_user=form.phone.data)
        db.session.add(booking)
        db.session.commit()
        return render_template("booking_done.html",
                               form=form)
    return render_template("request.html",
                           form=form)


@app.route('/request_done/', methods=["GET", "POST"])
def render_done():
    form = RequestForm()
    if request.method == 'POST':
        req = Request(goal=form.goal.data,
                      name_user=form.name.data,
                      phone_user=form.phone.data,
                      free_time=form.free_time.data)
        db.session.add(req)
        db.session.commit()
        return render_template("request_done.html",
                               form=form,
                               goals=get_goals_id_dict())
    return render_template("request.html",
                           form=form)


@app.route('/booking/<id_teach>/<day_weekly>/<time>/')
def render_booking(id_teach, day_weekly, time):
    form = RequestForm()
    teacher_info = db.session.query(Teacher).get_or_404(id_teach)
    return render_template("booking.html",
                           name_teacher=teacher_info.name,
                           day=days[day_weekly],
                           time=time,
                           form=form)


if __name__ == '__main__':
    # migrate_data_from_json()
    app.run(port=8060)
