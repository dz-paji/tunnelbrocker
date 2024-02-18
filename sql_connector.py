import mysql.connector
import configparser
import logging
import hashlib

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
    
class PopEntity:
    '''Pop entity'''
    def __init__(self, sqlResult: tuple):
        self.id = sqlResult[0]
        self.pop_id = sqlResult[1]
        self.pop_v4 = sqlResult[3]
        self.pop_v6 = sqlResult[2]
        self.city = sqlResult[4]
        self.country = sqlResult[5]
        self.isp_short = sqlResult[6]
        self.isp_name = sqlResult[7]
        self.isp_site = sqlResult[8]
        self.isp_asn = sqlResult[9]
        self.isp_lir = sqlResult[10]

    def __str__(self) -> str:
        return "PopEntity (id: %s, pop_id: %s, IPv4: %s, IPv6: %s, City: %s, Country: %s)" % (self.id, self.pop_id, self.pop_v4, self.pop_v6, self.city, self.country)
    
    def connectString(self) -> list[str]:
        ''' Get the connection string of a pop. 
        Prefers IPv4 over IPv6.
        '''
        if self.pop_v6 == '':
            return [self.pop_v4]
        elif self.pop_v4 == '':
            return [self.pop_v6]
        elif self.pop_v4 != '' and self.pop_v6 != '':
            return [self.pop_v4, self.pop_v6]
        else:
            return None
        
class TunnelEntity:
    '''Tunnel entity'''
    def __init__(self, sqlResult: tuple, user: UserEntity, admin: UserEntity, pop: PopEntity):
        self.id = sqlResult[0]
        self.tid = sqlResult[1]
        self.type = sqlResult[2]
        self.endpoint_v6 = sqlResult[3]
        self.endpoint_v6_prefix = sqlResult[4]
        self.endpoint_v4 = sqlResult[5]
        self.user = user
        self.admin = admin
        self.password = sqlResult[8]
        self.heartbeat_interval = sqlResult[9]
        self.mtu = sqlResult[10]
        self.pop = pop

class SQLConnector:
    def __init__(self):
        self.__configger = configparser.ConfigParser()
        self.__configger.read('config/tic.ini')
        host = self.__configger.get("Database", "Host")
        user = self.__configger.get("Database", "User")
        password = self.__configger.get("Database", "Password")
        database = self.__configger.get("Database", "Database")
        
        self.conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        self.conn.autocommit = True
        
        self.logger = logging.getLogger("DB")
        logging.basicConfig(level=logging.DEBUG)
        
    def setup(self):
        '''Create the table for TIC.
        '''
        # === users ===
        # uid: int unique
        # username: text unique
        # password: text
        # state: text
        cur = self.conn.cursor()
        cur.execute("create table if not exists users (uid INT auto_increment, username text not null, password TEXT not null, constraint users_pk primary key (uid), constraint username_uk unique(username));")
        cur.execute("create index if not exists users__index on users (username);")
        cur.execute("alter table users add state text null;")
        # === pops ===
        # id: int unique primary key not null
        # pop_id: text
        # v6_pop: text
        # v4_pop: text
        cur.execute("create table if not exists pops (id INT auto_increment, pop_id text not null, v6_pop text null, v4_pop text null, primary key (id));")
        # === tunnel ===
        # id: int unique primary key not null
        # tid: text
        # type: text not null
        # endpoint_v6: text not null
        # endpoint_v6_prefix: int not null
        # endpoint_v4: text
        # uid: int foreign key (users) CASECADE not null
        # admin_id: int foreign key (users) no action not null
        # password: text
        # heartbeat_interval: int
        # mtu: int
        # pop_id: text foreign key (pops) no action not null      
        # COMPLETED: rework on db structure, as pop_v4 and pop_v6 field moved to another table.  
        cur.execute("""
            create table tunnels
            (
                id                 int auto_increment,
                tid                varchar(255) not null,
                type               varchar(255) not null,
                endpoint_v6        varchar(255) not null,
                endpoint_v6_prefix int          not null,
                endpoint_v4        varchar(255) not null,
                uid                int          not null,
                admin_id           int          not null,
                password           text         not null,
                heartbeat_interval int          null,
                mtu                int          null,
                pop_id             int          not null,
                constraint tunnels_pk
                    primary key (id),
                constraint tunnels_pops_id_fk
                    foreign key (pop_id) references pops (id)
                        on update cascade,
                constraint tunnels_users_uid_fk
                    foreign key (uid) references users (uid)
                        on update cascade on delete cascade,
                constraint tunnels_users_uid_fk_2
                    foreign key (admin_id) references users (uid)
                        on update cascade
            );
        """)
        cur.execute("""
            create index tunnels_endpoint_v4_index
                on tunnels (endpoint_v4);            
        """)
        cur.execute("""
            create index tunnels_endpoint_v6_index
                on tunnels (endpoint_v6);
        """)
        cur.execute("""
            create index tunnels_pop_id_index
                on tunnels (pop_id);
        """)
        cur.execute("""
            create index tunnels_type_index
                on tunnels (type);
        """)
        cur.close()
        
    def addUser(self, thisUser: UserEntity):
        '''Add a user to the database.
        '''
        self.logger.debug("Adding user: %s", thisUser)
        username = thisUser.username
        password = thisUser.password
        
        # work out the salted hash.
        passwd_hasher = hashlib.md5()
        passwd_hasher.update(password.encode("utf-8"))
        passwd_hash = passwd_hasher.hexdigest()
        passwd_hasher = hashlib.md5()
        passwd_hash = self.__configger.get("Database", "Salt") + passwd_hash
        passwd_hasher.update(passwd_hash.encode("utf-8"))
        passwd_hash = passwd_hasher.hexdigest()
        
        state = thisUser.state
        cur = self.conn.cursor()
        cur.execute("insert into users (username, password, state) values (%s, %s, %s)", (username, passwd_hash, state))
        cur.close()
    
    def getUser(self, username: str) -> UserEntity:
        '''Get a user from the database.
        '''
        cur = self.conn.cursor()
        cur.execute("select * from users where username = %s", (username,))
        theOne = cur.fetchone()
        if theOne == None:
            return None
        
        cur.close()
        return UserEntity(theOne[0], theOne[1], theOne[2], theOne[3])
    
    def getUserById(self, uid: int) -> UserEntity:
        '''Get a user from the database by uid.
        '''
        cur = self.conn.cursor()
        cur.execute("select * from users where uid = %s", (uid,))
        theOne = cur.fetchone()
        if theOne == None:
            return None
        thisUser = UserEntity(theOne[0], theOne[1], theOne[2], theOne[3])
        cur.close()
        return thisUser
    
    # DEPRECATED: Use updateUser.
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
        cur.close()
        
    def addTunnel(self, tunnel: TunnelEntity):
        '''Add a tunnel to the database.
        '''
        tid = tunnel.tid
        type = tunnel.type
        endpoint_v6 = tunnel.endpoint_v6
        endpoint_v6_prefix = tunnel.endpoint_v6_prefix
        endpoint_v4 = tunnel.endpoint_v4
        uid = tunnel.user.uid
        admin_id = tunnel.admin.uid
        password = tunnel.password
        heartbeat_interval = tunnel.heartbeat_interval
        mtu = tunnel.mtu
        pop_id = tunnel.pop.id
        cur = self.conn.cursor()
        cur.execute("insert into tunnels (tid, type, endpoint_v6, endpoint_v6_prefix, endpoint_v4, uid, admin_id, password, heartbeat_interval, mtu, pop_id) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (tid, type, endpoint_v6, endpoint_v6_prefix, endpoint_v4, uid, admin_id, password, heartbeat_interval, mtu, pop_id))
        cur.close()

    def getTunnel(self, tid: str) -> TunnelEntity:
        '''Get a tunnel from the database.
        '''
        cur = self.conn.cursor()
        cur.execute("select * from tunnels where tid = %s", (tid,))
        theOne = cur.fetchone()
        if theOne == None:
            return None
        
        self.logger.debug("The one: %s", theOne)
        user = self.getUserById(theOne[6])
        admin = self.getUserById(theOne[7])
        pop = self.getPop(theOne[11])
        cur.close()
        
        return TunnelEntity(theOne, user, admin, pop)
    
    def listTunnels(self, uid: str) -> list[TunnelEntity]:              
        '''List all tunnels of a user.
        '''
        cur = self.conn.cursor()
        cur.execute("select * from tunnels where uid = %s", (uid,))
        tunnels = cur.fetchall()
        resp = []
        for tunnel in tunnels:
            user = self.getUser(tunnel[6])
            admin = self.getUser(tunnel[7])
            pop = self.getPop(tunnel[11])
            resp.append(TunnelEntity(tunnel, user, admin, pop))
        cur.close()
        
        return resp
    
    def updateTunnel(self, tunnel: TunnelEntity):
        '''Update a tunnel.
        '''
        cur = self.conn.cursor()
        cur.execute("update tunnels set type = %s, endpoint_v6 = %s, endpoint_v6_prefix = %s, endpoint_v4 = %s, uid = %s, admin_id = %s, password = %s, heartbeat_interval = %s, mtu = %s, pop_id = %s where tid = %s", (tunnel.type, tunnel.endpoint_v6, tunnel.endpoint_v6_prefix, tunnel.endpoint_v4, tunnel.user.uid, tunnel.admin.uid, tunnel.password, tunnel.heartbeat_interval, tunnel.mtu, tunnel.tid, tunnel.pop_id))
        cur.close()

    def getPop(self, pop_id: str) -> PopEntity:
        '''Get a pop from the database. pop_id can be either id or pop_id.
        '''
        cur = self.conn.cursor()
        cur.execute("select * from pops where id = %s", (pop_id,))
        theOne = cur.fetchone()
        cur.close()
        if theOne == None:
            cur = self.conn.cursor()
            cur.execute("select * from pops where pop_id = %s", (pop_id,))
            theOne = cur.fetchone()
            cur.close()
            if theOne == None:
                return None
            
            thisPop = PopEntity(theOne)
            return thisPop
            
        cur.close()
        thisPop = PopEntity(theOne)
        return thisPop
    
    def listPops(self) -> list[PopEntity]:
        '''List all pops.
        '''
        cur = self.conn.cursor()
        cur.execute("select * from pops")
        pops = cur.fetchall()
        resp = []
        for pop in pops:
            resp.append(PopEntity(pop))
        cur.close()
        return resp
    
    def addPop(self, pop: PopEntity):
        '''Add a pop to the database.
        '''
        cur = self.conn.cursor()
        cur.execute("insert into pops (pop_id, v6_pop, v4_pop) values (%s, %s, %s)", (pop.pop_id, pop.pop_v6, pop.pop_v4))
        cur.close()
        
    def updatePop(self, pop: PopEntity):
        '''Update a pop.
        '''
        cur = self.conn.cursor()
        cur.execute("update pops set v6_pop = %s, v4_pop = %s where pop_id = %s", (pop.pop_v6, pop.pop_v4, pop.pop_id))
        cur.close()
    
    def close(self):
        self.conn.close()
    
if __name__ == "__main__":
    try:
        sql = SQLConnector()
        tid = "1"
        type = "AYIYA"
        endpoint_v6 = "fe80::1"
        v6_pop = "fd00::1"
        endpoint_v6_prefix = 48
        endpoint_v4 = "10.0.0.1"
        v4_pop = "10.0.1.1"
        uid = 1
        admin_id = 1
        password = "admin"
        heartbeat_interval = 120
        mtu = 1500
        pop_id = "desktop.paji.uk"
        # user = sql.getUser("admin")
        # tEntity = TunnelEntity((tid, type, endpoint_v6, v6_pop, endpoint_v6_prefix, endpoint_v4, v4_pop, uid, admin_id, password, heartbeat_interval, mtu, pop_id), user, user)
        # sql.addTunnel(tEntity)
        # sql.setup()
        # pEntity = PopEntity(("1", "desktop", "127.0.0.1", ""))
        admin = UserEntity(1, "admin", "admin", "active")
        sql.addUser(admin)

    except Exception as e:
        print(e)
