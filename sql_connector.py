import mysql.connector
import configparser

class UserEntity:
    '''User entity'''
    def __init__(self, uid: int, username: str, password: str):
        self.uid = uid
        self.username = username
        self.password = password

    def __eq__(self, other):
        return self.uid == other.uid and self.username == other.username

class SQLConnector:
    def __init__(self):
        configger = configparser.ConfigParser()
        configger.read('config/tic.ini')
        host = configger.get("Database", "Host")
        user = configger.get("Database", "User")
        password = configger.get("Database", "Password")
        database = configger.get("Database", "Database")
        
        self.conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        
    def createTable(self):
        '''Create the table for TIC.
        '''

        cur = self.conn.cursor()
        # === users ===
        # uid: int unique
        # username: text unique
        # password: text
        cur.execute("create table if not exists users (uid INT auto_increment, username text not null, password TEXT not null, constraint users_pk primary key (uid), constraint username_uk unique(username)); create index users__index on users (username);")
        
    def addUser(self, thisUser: UserEntity):
        '''Add a user to the database.
        '''
        username = thisUser.username
        password = thisUser.password
        cur = self.conn.cursor()
        cur.execute("insert into users (username, password) values (%s, %s)", (username, password))
        self.conn.commit()
    
    def getUser(self, username: str) -> UserEntity:
        '''Get a user from the database.
        '''
        cur = self.conn.cursor()
        cur.execute("select * from users where username = %s", (username,))
        theOne = cur.fetchone()
        if theOne == None:
            return None
        return UserEntity(theOne[0], theOne[1], theOne[2])
    
    def changePassword(self, user: UserEntity):
        '''Change the password of a user.
        '''
        username = user.username
        password = user.password
        cur = self.conn.cursor()
        cur.execute("update users set password = %s where username = %s", (password, username))
        self.conn.commit()
        
    def changeUsername(self, old: str, new: str):
        '''Change the username of a user.
        '''
        cur = self.conn.cursor()
        cur.execute("update users set username = %s where username = %s", (new, old))
        self.conn.commit()
        
    def close(self):
        self.conn.close()
    
if __name__ == "__main__":
    try:
        sql = SQLConnector()
        a = sql.getUser("admin")
        print(a)
    except Exception as e:
        print(e)
