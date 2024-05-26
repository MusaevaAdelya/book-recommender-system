import firebase_admin
from firebase_admin import credentials, auth

cred = credentials.Certificate('book-recommender-system-31c25-firebase-adminsdk-2s4mt-6529c6940f.json')
firebase_admin.initialize_app(cred)
