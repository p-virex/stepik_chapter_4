from wtforms.validators import InputRequired
from flask_wtf import FlaskForm
from wtforms import StringField, RadioField

from data import goals, free_times


class RequestForm(FlaskForm):
    name = StringField('name', validators=[InputRequired()])
    client_weekday = StringField('client_weekday', [InputRequired()])
    client_time = StringField('client_time', [InputRequired()])
    client_teacher = StringField('client_teacher', [InputRequired()])
    phone = StringField('phone', validators=[InputRequired()])
    goal = RadioField('goal', validators=[InputRequired()], choices=[(key, value) for key, value in goals.items()], )
    free_time = RadioField('free_time', validators=[InputRequired()], choices=free_times)
