import mysql.connector
import configparser

class UserEntity:
    '''User entity'''
    def __init__(self, uid: int, username: str, password: str, state: str):
        self.uid = uid
        self.username = username
        self.password = password
        self.state = state

    def __eq__(self, other):
        if other == None:
            return False
        return self.uid == other.uid and self.username == other.username
    
    def __str__(self) -> str:
        return "UserEntity (uid: %d, username: %s, password: %s, state: %s)" % (self.uid, self.username, self.password, self.state)
    
class TunnelEntity:
    '''Tunnel entity'''
    def __init__(self, sqlResult: tuple, user: UserEntity, admin: UserEntity):
        self.tid = sqlResult[0]
        self.type = sqlResult[1]
        self.endpoint_v6 = sqlResult[2]
        self.v6_pop = sqlResult[3]
        self.endpoint_v6_prefix = sqlResult[4]
        self.endpoint_v4 = sqlResult[5]
        self.v4_pop = sqlResult[6]
        self.user = user
        self.admin = admin
        self.password = sqlResult[9]
        self.heartbeat_interval = sqlResult[10]
        self.mtu = sqlResult[11]
        self.pop_id = sqlResult[12]

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
        
        self.conn.autocommit = True
        
    def setup(self):
        '''Create the table for TIC.
        '''

        cur = self.conn.cursor()
        # === users ===
        # uid: int unique
        # username: text unique
        # password: text
        # state: text
        cur.execute("create table if not exists users (uid INT auto_increment, username text not null, password TEXT not null, constraint users_pk primary key (uid), constraint username_uk unique(username)); create index users__index on users (username);")
        cur.execute("alter table users add state text null;")
        
        # === tunnel ===
        # tid: text unique primary key not null
        # type: text not null
        # endpoint_v6: text not null
        # v6_pop: text
        # endpoint_v6_prefix: int not null
        # endpoint_v4: text
        # v4_pop: text
        # uid: int foreign key (users) CASECADE not null
        # admin_id: int foreign key (users) no action not null
        # password: text
        # heartbeat_interval: int
        # mtu: int
        # pop_id: text foreign key not null
        
        cur.execute("""
            create table if not exists tunnels
            (
                tid                text,
                type               text not null,
                endpoint_v6        text not null,
                v6_pop             text null,
                endpoint_v6_prefix int  not null,
                endpoint_v4        text null,
                v4_pop             text null,
                uid                int  not null,
                admin_id           int  not null,
                password           text null,
                heartbeat_interval int  null,
                mtu                int  null,
                constraint tunnels_admin_fk
                    foreign key (admin_id) references users (uid),
                constraint tunnels_user_fk
                    foreign key (uid) references users (uid)
                        on delete cascade
            );

            create index tunnels_tid_index
                on tunnels (tid);

            create index tunnels_type_index
                on tunnels (type);

            create index tunnels_uid_index
                on tunnels (uid);

            alter table tunnels
                add constraint tunnels_pk
                    primary key (tid);

            alter table tunnels
                modify tid text auto_increment;
        """)
        cur.execute("""
            alter table tunnels
                add pop_id text not null;

            create index tunnels_pop_id_index
                on tunnels (pop_id);

        """)
        
    def addUser(self, thisUser: UserEntity):
        '''Add a user to the database.
        '''
        username = thisUser.username
        password = thisUser.password
        state = thisUser.state
        cur = self.conn.cursor()
        cur.execute("insert into users (username, password, state) values (%s, %s)", (username, password, state))
    
    def getUser(self, username: str) -> UserEntity:
        '''Get a user from the database.
        '''
        cur = self.conn.cursor()
        cur.execute("select * from users where username = %s", (username,))
        theOne = cur.fetchone()
        if theOne == None:
            return None
        return UserEntity(theOne[0], theOne[1], theOne[2], theOne[3])
    
    # def changePassword(self, user: UserEntity):
    #     '''Change the password of a user.
    #     '''
    #     username = user.username
    #     password = user.password
    #     cur = self.conn.cursor()
    #     cur.execute("update users set password = %s where username = %s", (password, username))
        
    # def changeUsername(self, old: str, new: str):
    #     '''Change the username of a user.
    #     '''
    #     cur = self.conn.cursor()
    #     cur.execute("update users set username = %s where username = %s", (new, old))
        
    # def updateState(self, user: UserEntity):
    #     '''Update the state of a user.
    #     '''
    #     uid = user.uid
    #     state = user.state
    #     cur = self.conn.cursor()
    #     cur.execute("update users set state = %s where uid = %s", (state, uid))
    
    def updateUser(self, user: UserEntity):
        '''Update a user.
        '''
        uid = user.uid
        username = user.username
        password = user.password
        state = user.state
        cur = self.conn.cursor()
        cur.execute("update users set username = %s, password = %s, state = %s where uid = %s", (username, password, state, uid))
        
    def addTunnel(self, tunnel: TunnelEntity):
        '''Add a tunnel to the database.
        '''
        tid = tunnel.tid
        type = tunnel.type
        endpoint_v6 = tunnel.endpoint_v6
        v6_pop = tunnel.v6_pop
        endpoint_v6_prefix = tunnel.endpoint_v6_prefix
        endpoint_v4 = tunnel.endpoint_v4
        v4_pop = tunnel.v4_pop
        uid = tunnel.user.uid
        admin_id = tunnel.admin.uid
        password = tunnel.password
        heartbeat_interval = tunnel.heartbeat_interval
        mtu = tunnel.mtu
        pop_id = tunnel.pop_id
        cur = self.conn.cursor()
        cur.execute("insert into tunnels (tid, type, endpoint_v6, v6_pop, endpoint_v6_prefix, endpoint_v4, v4_pop, uid, admin_id, password, heartbeat_interval, mtu, pop_id) values (%s %s %s %s %s %s %s %s %s %s %s %s %s)", (tid, type, endpoint_v6, v6_pop, endpoint_v6_prefix, endpoint_v4, v4_pop, uid, admin_id, password, heartbeat_interval, mtu, pop_id))

    def getTunnel(self, tid: str) -> TunnelEntity:
        '''Get a tunnel from the database.
        '''
        cur = self.conn.cursor()
        cur.execute("select * from tunnels where tid = %s", (tid,))
        theOne = cur.fetchone()
        if theOne == None:
            return None
        user = self.getUser(theOne[7])
        admin = self.getUser(theOne[8])
        return TunnelEntity(theOne, user, admin)
    
    def listTunnels(self, uid: str) -> list:              
        '''List all tunnels of a user.
        '''
        cur = self.conn.cursor()
        cur.execute("select * from tunnels where uid = %s", (uid,))
        tunnels = cur.fetchall()
        resp = []
        for tunnel in tunnels:
            user = self.getUser(tunnel[7])
            admin = self.getUser(tunnel[8])
            resp.append(TunnelEntity(tunnel, user, admin))
        
        return resp
    
    def updateTunnel(self, tunnel: TunnelEntity):
        '''Update a tunnel.
        '''
        cur = self.conn.cursor()
        cur.execute("update tunnels set type = %s, endpoint_v6 = %s, v6_pop = %s, endpoint_v6_prefix = %s, endpoint_v4 = %s, v4_pop = %s, uid = %s, admin_id = %s, password = %s, heartbeat_interval = %s, mtu = %s where tid = %s", (tunnel.type, tunnel.endpoint_v6, tunnel.v6_pop, tunnel.endpoint_v6_prefix, tunnel.endpoint_v4, tunnel.v4_pop, tunnel.user.uid, tunnel.admin.uid, tunnel.password, tunnel.heartbeat_interval, tunnel.mtu, tunnel.tid))

    def close(self):
        self.conn.close()
    
if __name__ == "__main__":
    try:
        sql = SQLConnector()
        print(sql.getUser("admin"))
    except Exception as e:
        print(e)
