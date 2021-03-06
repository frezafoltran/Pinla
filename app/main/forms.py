from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, BooleanField, IntegerField
from wtforms.validators import ValidationError, DataRequired, Length
from flask_babel import _, lazy_gettext as _l
from app.models import User
import boto3
from markupsafe import Markup

dynamodb = boto3.resource("dynamodb")
rhyme_table = dynamodb.Table("Rhyme")

class EditProfileForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired()])
    about_me = TextAreaField(_l('About me'), validators=[Length(min=0, max=140)])
    submit = SubmitField(_l('Submit'))

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()

            if user is not None:
                raise ValidationError(_('This username is already being used. Please use a different one.'))

class PostForm(FlaskForm):
    post = TextAreaField(_l('Share an Idea'), validators=[DataRequired(), Length(min=1, max=140)])
    submit = SubmitField(_l('Submit'))



class JinniRhymeDistanceForm(FlaskForm):

    word_1 = StringField(_l('First word'), validators=[DataRequired()])
    word_2 = StringField(_l('Second word'), validators=[DataRequired()])
    rhyme_at_start = BooleanField('Front-word rhyme')
    submit = SubmitField(_l('Get distance!'))


class JinniBlankCanvasForm(FlaskForm):
    req_word = StringField(_l('next sentence related to'))
    rhyme_with_line = StringField(_l('rhyming with line or word'))
    submit_value = Markup('<img src="{{url_for(\'static\', filename=\'images/add.jpg\')}}" style="width:40px;height:40px;">')
    submit = SubmitField(submit_value)

    def validate_req_word(self, req_word):

        req_word = str(req_word.data).lower()
        one_word = req_word.strip(' ').split(' ')

        if len(one_word) > 1:
            raise ValidationError('Please type only one word.')

        """
        if not req_word:
            raise ValidationError('Please type a word.')
            """
        if req_word:
            try:
                response = rhyme_table.get_item(
                    Key={
                        'id': req_word
                    }
                )

                return response['Item']['rhymes']
            except KeyError:
                raise ValidationError(req_word + ' is not currently in the database')



class JinniCustomSong(FlaskForm):

    req_word = StringField(_l('Enter a topic of your choice'))
    submit = SubmitField(_l('Create a Song!'))

    # TODO validator not working!
    def validate_req_word(self, req_word):

        req_word = str(req_word.data).lower()
        one_word = req_word.strip(' ').split(' ')

        if len(one_word) > 1:
            raise ValidationError('Please type only one word.')

        if not req_word:
            raise ValidationError('Please type a word.')

        try:
            response = rhyme_table.get_item(
                Key={
                    'id': req_word
                }
            )

            return response['Item']['rhymes']
        except KeyError:
            raise ValidationError(req_word + ' is not currently in the database')

class DefZeroProb(FlaskForm):

    n = IntegerField(_l('Number of distinct species in network:'), validators=[DataRequired()])
    submit = SubmitField(_l('Plot results'))


class SearchForm(FlaskForm):
    q = StringField(_l('Search'), validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'csrf_enabled' not in kwargs:
            kwargs['csrf_enabled'] = False
        super(SearchForm, self).__init__(*args, **kwargs)