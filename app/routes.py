# -*- coding: utf-8 -*-
"""
Created on Thu Apr 29 13:53:03 2021

@author: gizem
"""

from app import app,db
from app.models import User
from app.forms import LoginForm, RegistrationForm
from app.grouping import Grouping, add_ToGroup, next_step, skip_grouping, save, reload_saved_grouping, add_for_regrouping, regrouping_next
from flask import render_template,flash,redirect, url_for, request, send_from_directory
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Home')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    #current_user variable comes from Flask-Login and can be used  
    #at any time during the handling to obtain the user object that 
    #represents the client of the request 
    if current_user.is_authenticated: 
        return redirect(url_for('index'))    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html',title='Sign In', form = form)

@app.route('/logout')
@login_required
def logout():
#    filename = current_user.username + ".json"
#    grouping = Grouping.getInstance()
#    save(grouping,filename)
    logout_user()
    return redirect(url_for('index'))   

@app.route('/init')
@login_required
def init_grouping():
    try:
        grouping = Grouping()    
    except:
        grouping = Grouping.getInstance() 
        grouping.initialize_values()
    return redirect(url_for('new_grouping'))


@app.route('/grouping', methods=['GET', 'POST'])
@login_required
def new_grouping():

    grouping = Grouping.getInstance()
    
    grouping.g1_name = "Group " + str(grouping.level) + "-" + str(grouping.curr_child_index-1);
    grouping.g2_name = "Group " + str(grouping.level) + "-" + str(grouping.curr_child_index);
    music = None
    if request.method == 'POST':
        if request.form['submit_button'] == 'play':
            music = grouping.get_music()
        elif request.form['submit_button'] == 'add_g1':
            add_ToGroup(0, grouping.main_dict, grouping.g1_dict,grouping)
        elif request.form['submit_button'] == 'add_g2':
            add_ToGroup(0, grouping.main_dict, grouping.g2_dict,grouping)
        elif request.form['submit_button'] == 'remove_g1':
            add_ToGroup(1, grouping.g1_dict, grouping.main_dict,grouping)
        elif request.form['submit_button'] == 'remove_g2':
            add_ToGroup(2, grouping.g2_dict, grouping.main_dict,grouping)
        elif request.form['submit_button'] == 'next':
            next_step(grouping)
        elif request.form['submit_button'] == 'skip':
            skip_grouping(grouping)
        elif request.form['submit_button'] == 'save':
            filename = current_user.username + ".json"
            save(grouping,filename)
        elif request.form['submit_button'] == 'add_regrouping':
            add_for_regrouping(grouping, 0)
    if grouping.grouping_done:
        filename = current_user.username + ".json"
        save(grouping,filename,True)
        return redirect(url_for('last'))
    elif grouping.phase1_done:
        return redirect(url_for('regrouping_operation'))
    return render_template('grouping.html', music=music, grouping=grouping)


@app.route('/regrouping', methods=['GET', 'POST'])
@login_required
def regrouping_operation():   
    
    grouping = Grouping.getInstance()
    
    group_elems = grouping.regrouping_next_group()
    music = None
   
    if request.method == 'POST':
        if request.form['submit_button'] == 'play':
            music = grouping.get_music()
        elif request.form['submit_button'] == 'add_g':
            add_ToGroup(3,grouping.regrouping_dict,grouping.groups_dict[grouping.regrouping_curr_group_key]["elems"],grouping)
        elif request.form['submit_button'] == 'add_regrouping':
            add_for_regrouping(grouping, 4)
        elif request.form['submit_button'] == 'next':
            group_elems = regrouping_next(grouping)
        elif request.form['submit_button'] == 'save':
            filename = current_user.username + ".json"
            save(grouping,filename)
                
    if grouping.grouping_done:
        filename = current_user.username + ".json"
        save(grouping,filename,True)
        return redirect(url_for('last'))
    return render_template('regrouping.html', grouping = grouping , music = music, g_elems = group_elems)

@app.route('/reload', methods=['GET', 'POST'])
@login_required
def reload_grouping():

    try:
        grouping = Grouping()    
    except:
        grouping = Grouping.getInstance() 
        grouping.initialize_values()    

    filename = current_user.username + ".json"
    
    reload_saved_grouping(grouping,filename)
    
    if(grouping.phase1_done):
        return redirect(url_for('regrouping_operation'))
    else:
        return redirect(url_for('new_grouping'))

@app.route('/last', methods=['GET', 'POST'])
@login_required
def last():
    #dir_name = "outputs"
    #filename = current_user.username + ".json"
    #return send_from_directory(dir_name, filename=filename, as_attachment=True)
    return render_template('last.html')
    
@app.route('/getfile', methods=['GET', 'POST'])
@login_required
def download_file():
    dir_name = "outputs"
    filename = current_user.username + ".json"
    return send_from_directory(dir_name, filename=filename, as_attachment=True)
    
