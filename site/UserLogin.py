from flask_login import UserMixin

class UserLogin(UserMixin):
    def fromDB(self, user_id, db):
        self.__user = db.getUserById(user_id)
        return self
    
    def create(self, user):
        self.__user = user
        return self

    def get_id(self):
        return self.__user['int_id']

    def getId(self):
        return self.__user['id_user']

    def getName(self):
        return self.__user['name'] if self.__user['name'] else 'Без имени'

    def getSurname(self):
        return self.__user['surname'] if self.__user['surname'] else 'Без фамилии'

    def getAbout(self):
        return self.__user['about'] if self.__user['about'] else 'Нет описания профиля'

    def getEmail(self):
        return self.__user['email'] if self.__user else 'Нет email'
    