from . import mongo



class User:
    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password

    def to_dict(self):
        return {
            'username': self.username,
            'email': self.email,
            'password': self.password
            
        }


class Post:
    def create_post(self, title, content, author):
        
        pass
    
    def get_post(self, post_id):
        
        pass
