# -*- coding: utf-8 -*- 

import sys, os

########################################################################
# Pre-configuration for ERP Libre paths and options
########################################################################

# Try to load GUI App ini values (test if they are stored in a storage
# object first

# sys.path change is not made because of threading
# policies with web2py
# 9/12/2011: back to sys.path.append(..
# App routes.py is not run unless added to the web2py root routes.py
# routes_app patterns

_ini_values = session.get("_ini_values", None)
_load_ini_values = session.get("_load_ini_values", True)

if _ini_values is None and _load_ini_values:
    # read values and pass them to the storage object
    try:
        with open(os.path.join(request.folder, "private", "config.ini"), "r") as config_file:
            session._ini_values = dict()
            for line in config_file.readlines():
                values = line.strip().split("=")
                if len(values) == 2:
                    session._ini_values[values[0]] = values[1]

        # set environment extra values
        _modules_path = os.path.join(session._ini_values["GUI2PY_APP_FOLDER"], "modules")
        session._modules_path = _modules_path

    except IOError, e:
        print "Error accessing config.ini: " + str(e)
        session._modules_path = os.path.join(request.folder, "modules")
        print "Changed modules path to" , session._modules_path

# set _load... as False (avoid redundant load)
session._load_ini_values = False

if session.get("_modules_path", None) is not None:
    if not session._modules_path in sys.path:
        sys.path.append(session._modules_path)

########################################################################
# End of Pre-configuration for ERP Libre paths and options
########################################################################


#########################################################################
## This scaffolding model makes your app work on Google App Engine too
#########################################################################

if request.env.web2py_runtime_gae:            # if running on Google App Engine
    db = DAL('gae')                           # connect to Google BigTable
    session.connect(request, response, db = db) # and store sessions and tickets there
    ### or use the following lines to store sessions in Memcache
    # from gluon.contrib.memdb import MEMDB
    # from google.appengine.api.memcache import Client
    # session.connect(request, response, db = MEMDB(Client()))
else:
    try:
        # else use a normal relational database
        db = DAL(session._ini_values["DB_URI"], folder = session._ini_values["DATABASES_FOLDER"]) # if not, use SQLite or other DB
    except Exception, e:
        # TODO: handle exceptions by class
        raise HTTP(200, "An exception ocurred while connecting to the database. Please check the app configuration.")


## if no need for session
# session.forget()

#########################################################################
## Here is sample code if you need for 
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - crud actions
## (more options discussed in gluon/tools.py)
#########################################################################

# change translation folder to gui2py app's
# T.folder = session._ini_values["GUI2PY_APP_FOLDER"]

# change app's dir to local GUI ERP Libre path
# request.folder = session._ini_values["GUI2PY_APP_FOLDER"]


from gluon.tools import *
mail = Mail()                                  # mailer
auth = Auth(globals(),db)                      # authentication/authorization
crud = Crud(globals(),db)                      # for CRUD helpers using auth
service = Service(globals())                   # for json, xml, jsonrpc, xmlrpc, amfrpc
plugins = PluginManager()

mail.settings.server = 'logging' or 'smtp.gmail.com:587'  # your SMTP server
mail.settings.sender = 'you@gmail.com'         # your email
mail.settings.login = 'username:password'      # your credentials or None

# before define_tables()
auth.settings.hmac_key = session._ini_values["HMAC_KEY"]

# ERP Libre default installation 'sha512:3f00b793-28b8-4b3c-8ffb-081b57fac54a'

# performed on erplibre.define_tables()
# auth.define_tables()                           # creates all needed tables

auth.settings.mailer = mail                    # for user email verification
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.messages.verify_email = 'Click on the link http://'+request.env.http_host+URL(r=request,c='default',f='user',args=['verify_email'])+'/%(key)s to verify your email'
auth.settings.reset_password_requires_verification = True
auth.messages.reset_password = 'Click on the link http://'+request.env.http_host+URL(r=request,c='default',f='user',args=['reset_password'])+'/%(key)s to reset your password'

#########################################################################
## If you need to use OpenID, Facebook, MySpace, Twitter, Linkedin, etc.
## register with janrain.com, uncomment and customize following
# from gluon.contrib.login_methods.rpx_account import RPXAccount
# auth.settings.actions_disabled=['register','change_password','request_reset_password']
# auth.settings.login_form = RPXAccount(request, api_key='...',domain='...',
#    url = "http://localhost:8000/%s/default/user/login" % request.application)
## other login methods are in gluon/contrib/login_methods
#########################################################################

crud.settings.auth = None                      # =auth to enforce authorization on crud

#########################################################################
## Define your tables below (or better in another model file) for example
##
## >>> db.define_table('mytable',Field('myfield','string'))
##
## Fields can be 'string','text','password','integer','double','boolean'
##       'date','time','datetime','blob','upload', 'reference TABLENAME'
## There is an implicit 'id integer autoincrement' field
## Consult manual for more options, validators, etc.
##
## More API examples for controllers:
##
## >>> db.mytable.insert(myfield='value')
## >>> rows=db(db.mytable.myfield=='value').select(db.mytable.ALL)
## >>> for row in rows: print row.id, row.myfield
#########################################################################

###################
# GestionLibre data
###################

# custom serial code creation. Include plain text between \t tab chars: "A\tThis is not randomized\tBN"
# A: alphabetical, B: alphanumeric, N: integers between zero and nine, \t [text] \t: normal text bounds
# To include "A", "B", "N" use the \tA\t syntax. Auxiliar characters are allowed outside \t \t separators
# As expected, no \t characters are allowed inside escaped text
# TODO: Simplify/standarize serial code pseudo-syntax for user html form input

migrate = True

# import GestionLibre database definitions

try:
    import db_erplibre
except ImportError, e:
    msg = "Could not import table definitions: " + str(e)
    print msg
    raise HTTP(200, msg)

db_erplibre.define_tables(db, auth, globals(), web2py = True, migrate=False, fake_migrate=False, T = T)

# Any host can get generic views
# TODO: local webapp restriction rules
response.generic_patterns = ["*",]
