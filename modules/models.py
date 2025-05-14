import MySQLdb
from flask_login import UserMixin
from extensions import login_manager

class User(UserMixin):
    def __init__(self, user_id, username, is_admin=False):
        self.id = user_id
        self.username = username
        self.is_admin = is_admin
        
    def get_id(self):
        return str(self.id)
        
    @property
    def is_authenticated(self):
        return True
        
    @property
    def is_active(self):
        return True
        
    @property
    def is_anonymous(self):
        return False

@login_manager.user_loader
def load_user(user_id):
    from modules.database import get_db
    db = get_db()
    cursor = db.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT id, username, is_admin FROM users WHERE id = %s", (user_id,))
    user_data = cursor.fetchone()
    if user_data:
        return User(
            user_id=user_data['id'],
            username=user_data['username'],
            is_admin=bool(user_data['is_admin'])
        )
    return None