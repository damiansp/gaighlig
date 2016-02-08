# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
#########################################################################

def index():
    '''
    After log-in or registration has been done, allow user to view or enter
    data
    '''
    add_data = A('Add Data', _class = 'btn btn-success',
                 _href = URL('default', 'add_data'))
    view_data = A('View Existing Data', _class = 'btn btn-primary',
                  _href = URL('default', 'dictionary_display'))
    return dict(add_data = add_data, view_data = view_data)
    


def register():
    row = db(db.people.user_id == auth.user_id).select().first() # or None
    db.people.user_id.readable = db.people.user_id.writable = False
    db.people.id.readable = db.people.id.writable = False
    form = SQLFORM(db.people, record = row)
    if form.process().accepted:
        session.flash = T('Welcome, %s' %form.vars.name)
        redirect(URL('default', 'start'))
    return dict(form = form)
    


# For dictionary input, specify allowed values for fields, where necessary
allowed_pos = ['n', 'v', 'adj', 'adv', 'prep', 'expr', 'art', 'conj']
allowed_pos_detail = ['coll', 'irr', 'np']
allowed_gender = ['f', 'm', '']



# Validators for dictionary entries
# TO DO: Update to only allow relevant fields for pos type
def check_pos(form):
    if form.vars.pos not in allowed_pos:
        form.errors.pos = T('Accepted parts of speech are: "adj", "adv", ' +
                            '"art", "conj", "expr", "n", "prep", and "v".')
def check_gender(form):
    if form.vars.gender not in allowed_gender:
        form.errors.gender = T('Accepted genders are "f" and "m".')

def check_entry(form):
    check_pos(form)
    check_gender(form)

    
@auth.requires_login()
def add_data():
    '''Allow a user to input a new dictionary entry'''
    form = SQLFORM(db.gaighlig)

    if form.process(onvalidation = check_entry).accepted:
        session.flash = T('Entry added.')
        redirect(URL('add_data'))

    view_button = A('View Database', _class = 'btn btn-primary',
                    _href = URL('default', 'dictionary_display'))

    return dict(form = form, view_button = view_button)


@auth.requires_login()
def dictionary_display():
    '''Show contents of the dictiorary database (gaighlig.db)'''
    q = db.gaighlig
    grid = SQLFORM.grid(
        q,
        editable = True, # must be logged in to work
        deletable = False
    )

    return dict(grid = grid)


@auth.requires_login()
def entry_edit():
    entry = db.gaighlig(request.args(0))
    if entry is None:
        session.flash = T('Entry does not exist')
        redirect(URL('default', 'dictionary_display'))
    form = SQLFORM(db.gaighlig, record = entry)
    if form.process(onvalidation = check_entry).accepted:
        session.flash = T('Entry updated')
        redirect(URL('default', 'entry_edit', args = [entry.id]))
    edit_button = A('View updated',
                    _class = 'btn btn-success',
                    _href = URL('default', 'dictionary_display',
                    args = [entry.id]))
    return dict(form = form, edit_button = edit_button)

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
    """
    return dict(form=auth())


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()
