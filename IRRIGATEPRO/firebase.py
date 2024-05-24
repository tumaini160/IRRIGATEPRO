import firebase_admin
from firebase_admin import credentials, db

cred = credentials.Certificate('irrigatepro-524d5-firebase-adminsdk-ndsw9-57e6cc54b5.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://irrigatepro-524d5-default-rtdb.firebaseio.com'
})
