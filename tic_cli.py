from sql_connector import SQLConnector, UserEntity, TunnelEntity, PopEntity
import sys

class TicCLI():
    '''
    TIC Admin CLI
    '''
    def addUser(usrname: str, passwd: str):
        db = SQLConnector()
        thisUser = UserEntity(1, usrname, passwd, "enabled")
        db.addUser(thisUser)
    
    def initDB():
        db = SQLConnector()
        db.setup()
    
    def addPop(pop_id, pop_v4, pop_v6, city, country, isp_short, isp_name, isp_site, isp_asn, isp_lir):
        db = SQLConnector()
        popTupple = (0, pop_id, pop_v4, pop_v6, city, country, isp_short, isp_name, isp_site, isp_asn, isp_lir)
        thisPop = PopEntity(popTupple)
        db.addPop(thisPop)
    
    def getUser(name: str):
        db = SQLConnector()
        thisUser = db.getUser(name)
        print(thisUser)
        
    def updateUser(uid: int, name: str, password: str):
        db = SQLConnector()
        thisUser = UserEntity(uid, name, password, "enabled")
        db.updateUser(thisUser)
        
    def addTunnel(tid: str, type: str, endpoint_v6: str, endpoint_v6_prefix: str, endpoint_v4: str, username: str, adminState: str, password: str, heartbeat_interval: str, mtu: str, pop_id: str):
        db = SQLConnector()
        tunnelUser = db.getUser(username)
        userState = tunnelUser.state
        tunnelPop = db.getPop(pop_id)
        tunnelTuple = (0, tid, type, endpoint_v6, endpoint_v6_prefix, endpoint_v4, username, userState, adminState, password, heartbeat_interval, mtu, pop_id)
        thisTunnel = TunnelEntity(tunnelTuple, tunnelUser, tunnelPop)
        db.addTunnel(thisTunnel)
        
    def updateTunnel(tid: str, type: str, endpoint_v6: str, endpoint_v6_prefix: str, endpoint_v4: str, username: str, adminState: str, password: str, heartbeat_interval: str, mtu: str, pop_id: str):
        db = SQLConnector()
        tunnelUser = db.getUser(username)
        userState = tunnelUser.state
        tunnelPop = db.getPop(pop_id)
        tunnelTuple = (0, tid, type, endpoint_v6, endpoint_v6_prefix, endpoint_v4, username, userState, adminState, password, heartbeat_interval, mtu, pop_id)
        thisTunnel = TunnelEntity(tunnelTuple, tunnelUser, tunnelPop)
        print(thisTunnel)
        db.updateTunnel(thisTunnel)
        
    def updatePop(pop_id, pop_v4, pop_v6):
        db = SQLConnector()
        popTupple = (0, pop_id, pop_v4, pop_v6, "", "", "", "", "", "", "")
        thisPop = PopEntity(popTupple)
        db.updatePop(thisPop)
        
    def getPop(pop_id):
        db = SQLConnector()
        thisPop = db.getPop(pop_id)
        print(thisPop)
        
    def getTunnel(tid):
        db = SQLConnector()
        thisTunnel = db.getTunnel(tid)
        print(thisTunnel)
        
    def help():
        print("Usage: ")
        print("initDB")
        print("addUser <username> <password>")
        print("addPop <pop_id> <pop_v4> <pop_v6> <city> <country> <isp_short> <isp_name> <isp_site> <isp_asn> <isp_lir>")
        print("addTunnel <tid> <ipv4_them|heartbeat|ayiya> <endpoint_v6> <endpoint_v6_prefix> <endpoint_v4> <username> <enabled|disabled> <password> <heartbeat_interval> <mtu> <pop_id>")
        print("updateUser <uid> <name> <password>")
        print("updateTunnel <tid> <ipv4_them|heartbeat|ayiya> <endpoint_v6> <endpoint_v6_prefix> <endpoint_v4> <username> <enabled|disabled> <password> <heartbeat_interval> <mtu> <pop_id>")
        print("updatePop <pop_id> <pop_v4> <pop_v6>")
        print("getUser <name>")
        print("getPop <pop_id>")
        print("getTunnel <tid>")        
    
if __name__ == "__main__":
    args = sys.argv[1:]
    cmd = args[0]
    match cmd:
        case "help":
            TicCLI.help()
        case "initDB":
            TicCLI.initDB()          
        case "addUser":
            usrname = args[1]
            passwd = args[2]
            TicCLI.addUser(usrname, passwd)        
        case "addTunnel":
            tid = args[1]
            type = args[2]
            endpoint_v6 = args[3]
            endpoint_v6_prefix = args[4]
            endpoint_v4 = args[5]
            username = args[6]
            adminState = args[7]
            password = args[8]
            heartbeat_interval = args[9]
            mtu = args[10]
            pop_id = args[11]
            TicCLI.addTunnel(tid, type, endpoint_v6, endpoint_v6_prefix, endpoint_v4, username, adminState, password, heartbeat_interval, mtu, pop_id)      
        case "addPop":
            pop_id = args[1]
            pop_v4 = args[2]
            pop_v6 = args[3]
            city = args[4]
            country = args[5]
            isp_short = args[6]
            isp_name = args[7]
            isp_site = args[8]
            isp_asn = args[9]
            isp_lir = args[10]
            TicCLI.addPop(pop_id, pop_v4, pop_v6, city, country, isp_short, isp_name, isp_site, isp_asn, isp_lir)
        case "addTunnel":
            TicCLI.addTunnel()       
        case "getUser":
            usrname = args[1]
            TicCLI.getUser(usrname)       
        case "updateUser":
            uid = args[1]
            usrname = args[2]
            passwd = args[3]
            TicCLI.updateUser(uid, usrname, passwd)       
        case "updateTunnel":
            tid = args[1]
            type = args[2]
            endpoint_v6 = args[3]
            endpoint_v6_prefix = args[4]
            endpoint_v4 = args[5]
            username = args[6]
            adminState = args[7]
            password = args[8]
            heartbeat_interval = args[9]
            mtu = args[10]
            pop_id = args[11]
            TicCLI.updateTunnel(tid, type, endpoint_v6, endpoint_v6_prefix, endpoint_v4, username, adminState, password, heartbeat_interval, mtu, pop_id)        
        case "updatePop":
            pop_id = args[1]
            pop_v4 = args[2]
            pop_v6 = args[3]
            TicCLI.updatePop(pop_id, pop_v4, pop_v6)
        case "getPop":
            pop_id = args[1]
            TicCLI.getPop(pop_id)
        case "getTunnel":
            tid = args[1]
            TicCLI.getTunnel(tid)