import sqlite3, random, datetime, math, time

class DataBase:
    def __init__(self, db):
        self.__db = db
        self.__cur = db.cursor()

    def getKeyId(self, id_user):
        self.__cur.execute(f"SELECT int_id from users WHERE id_user = '{id_user}' LIMIT 1")
        res = self.__cur.fetchone()
        id_user = res['int_id']
        return id_user

    def addPost(self, title, text, id_user, image):

        def generateIdPost():
            post_id = random.randrange(10000000, 99999999, 1)
            res = self.__cur.execute("SELECT id_post FROM posts").fetchall()
            if post_id not in res:
                return post_id
            generateIdPost()
        
        try: 
            id_post = generateIdPost()
            tm = datetime.datetime.today().strftime("%d.%m.%y %H:%M")
            timeint = math.floor(time.time())
            if image:
                img = sqlite3.Binary(image)
                self.__cur.execute(f"INSERT INTO posts VALUES(?, ?, ?, ?, ?, ?, ?)", (id_post, id_user, title, text, tm, timeint, img))
            else:
                self.__cur.execute(f"INSERT INTO posts VALUES(?, ?, ?, ?, ?, ?, NULL)", (id_post, id_user, title, text, tm, timeint))
            self.__db.commit()
        except sqlite3.Error as err:
            print(f"Error adding an article to the DB: {err}")
            return False
        return True

    def getAvatar(self, id_user):
        try:
            self.__cur.execute(f"SELECT avatar FROM users WHERE int_id = '{id_user}' LIMIT 1")
            res = self.__cur.fetchone()
            if not res:
                print('Avatar not found')
            return res['avatar']
        except sqlite3.Error as err:
            print(f'Error getting an avatar from the DB: {err}')

        return 'Not Found'

    def getPostById(self, id_post):
        try:
            self.__cur.execute(f"SELECT users.id_user, id_post, name, surname, avatar, title, post_text, time, img FROM users INNER JOIN posts ON users.int_id = posts.id_user WHERE id_post = {id_post} LIMIT 1")
            res = self.__cur.fetchone()
            if res:
                return res
        except sqlite3.Error as err:
            print(f"Error getting an article from the DB: {err}")
        return []

    def getPostsOfUser(self, id_user):
        try: 
            self.__cur.execute(f"SELECT * from (SELECT * FROM posts WHERE id_user = '{id_user}') ORDER BY timeint DESC")
            res = self.__cur.fetchall()
            if res: return res
        except sqlite3.Error as err:
            print(f"Error getting a user list of articles from the DB: {err}")
        return []

    def addUser(self, name, surname, email , password):

        def generateIdUser():
            id = random.randrange(100000, 999999, 1)
            res = self.__cur.execute("SELECT id_user FROM users").fetchall()
            if id not in res:
                return id
            generateIdUser()
        
        id_user = generateIdUser()
        try:
            self.__cur.execute(f"SELECT COUNT() as count FROM users WHERE email like '{email}'")
            res = self.__cur.fetchone()
            if res['count'] > 0 :
                print('A user with such email exists already')
                return False

            self.__cur.execute(f"INSERT INTO users VALUES('{id_user}', '{id_user}', '{name}', '{surname}', '{email}', '{password}',  NULL, 'Нет описания профиля')")
            self.__db.commit()

        except sqlite3.Error as err:
            print(f"Error adding a user to the DB: {err}")
            return False
            
        return True

    def getUserById(self, id_user):
        try:
            self.__cur.execute(f"SELECT * FROM users WHERE int_id = '{id_user}' LIMIT 1")
            res = self.__cur.fetchone()
            if not res:
                print('User not found')
                return False
            return res
        except sqlite3.Error as err:
            print(f'Error getting a user from the DB: {err}')

        return False

    def joinPostsUsers(self):
        try:
            self.__cur.execute("SELECT users.id_user, id_post, name, surname, avatar, title, post_text, time, img FROM users INNER JOIN posts ON users.int_id = posts.id_user  ORDER BY timeint DESC")
            res = self.__cur.fetchall()
            if not res:
                print('There is no rows in the DB')
                return []
            return res
        except sqlite3.Error as err:
            print(f'Error getting rows from the DB: {err}')

        return []

    def getUserByEmail(self, email):
        try:
            self.__cur.execute(f"SELECT * FROM users WHERE email = '{email}' LIMIT 1")
            res = self.__cur.fetchone()
            if not res:
                print('User not found')
                return False
            return res
        except sqlite3.Error as err:
            print(f'Error getting a user from the DB: {err}')
        return False

    def updateUserAvatar(self, img, id):
        if not img:
            return False
        try:
            ava = sqlite3.Binary(img)
            self.__cur.execute(f"UPDATE users SET avatar = ? WHERE int_id = ? ", (ava, id))
            self.__db.commit()
        except sqlite3.Error as err:
            print('Error updating avatar in DB')
            return False
        
        return True

    def addComment(self, id_user, id_post, comment):
        def generateIdComment():
            id = random.randrange(1000000000, 9999999999, 1)
            res = self.__cur.execute("SELECT id_comment FROM comments").fetchall()
            if id not in res:
                return id
            generateIdComment()
        
        try: 
            id_comment = generateIdComment()
            tm = datetime.datetime.today().strftime("%d.%m.%y %H:%M")
            timeint = math.floor(time.time())
            self.__cur.execute(f"INSERT INTO comments VALUES({id_comment}, {id_post}, '{id_user}', '{comment}', '{tm}', {timeint})")
            self.__db.commit()
        except sqlite3.Error as err:
            print(f"Error adding a comment to the DB: {err}")
            return False
        return True

    def getCommentsByIdPost(self, id_post):
        try: 
            self.__cur.execute(f"SELECT posts.id_post, users.avatar, users.name, users.surname, users.id_user, comments.comment_text, comments.time, comments.id_comment FROM posts JOIN comments ON  comments.id_post = posts.id_post JOIN users ON comments.id_user = users.int_id WHERE posts.id_post = {id_post} ORDER BY comments.timeint DESC")
            res = self.__cur.fetchall()
        except sqlite3.Error as err:
            print(f"Error join tables from DB (comments, users, posts): {err}")
            return []
        return res

    def getCommentById(self, id_comment):
        try: 
            self.__cur.execute(f"SELECT id_post FROM comments WHERE id_comment = {id_comment} LIMIT 1")
            res = self.__cur.fetchone()
        except sqlite3.Error as err:
            print(f"Error getting comment from the DB: {err}")
            return []
        return res

    def editUserInfo(self, id_user, name, surname, about, email):
        try:
            self.__cur.execute(f"UPDATE users SET id_user = '{id_user}', name = '{name}', surname = '{surname}', about = '{about}' WHERE email = '{email}'")
            self.__db.commit()
        except sqlite3.Error as err:
            print(f"Error editing info about user in the DB: {err}")
            return False
            
        return True

    def deleteUser(self, id_user):
        try:
            self.__cur.execute(f"DELETE FROM users WHERE int_id = {id_user}")
            self.__db.commit()
            self.__cur.execute(f"DELETE FROM posts WHERE id_user = '{id_user}'")
            self.__db.commit()
            self.__cur.execute(f"DELETE FROM comments WHERE id_user = '{id_user}'")
            self.__db.commit()
        except sqlite3.Error as err:
            print(f"Error deleting user from the DB: {err}")
            return False
            
        return True
    
    def deleteCom(self, id_comment):
        try:
            self.__cur.execute(f"DELETE FROM comments WHERE id_comment = '{id_comment}'")
            self.__db.commit()
        except sqlite3.Error as err:
            print(f"Error deleting comment from the DB: {err}")
            return False
            
        return True

    def editComment(self, id_comment, text):
        try:
            res = self.__cur.execute(f"UPDATE comments SET comment_text = '{text}' WHERE id_comment = {id_comment}")
            self.__db.commit()
            if not res:
                print('Error updating comment in the DB')
                return False
        except sqlite3.Error as err:
            print(f"Error updating comment in the DB: {err}")
            return False
            
        return True

    def addPostImage(self, img, id_post):
        if not img:
            return False
        try:
            image = sqlite3.Binary(img)
            self.__cur.execute(f"UPDATE posts SET img = ? WHERE id_post = ? ", (image, id_post))
            self.__db.commit()
        except sqlite3.Error as err:
            print('Error adding image in the DB: {err}')
            return False
        
        return True

    def checkId(self, id):
        self.__cur.execute(f"SELECT COUNT() as count FROM users WHERE id_user = '{id}'  LIMIT 1")
        res = self.__cur.fetchone()
        if res['count'] > 0:
            return True
        return False