from sql_connector import SQLConnector, UserEntity
import sys

class TicCLI():
    '''
    TIC Admin CLI
    '''
    def addUser(usrname: str, passwd: str):
        db = SQLConnector()
        thisUser = UserEntity(usrname, passwd, "enabled")
        db.addUser(thisUser)
    
    def initDB():
        db = SQLConnector()
        db.setup()
        
    def addTunnel():
        pass
    
    def addPop():
        pass
    
    def help():
        print("Usage: ")
        print("addUser <username> <password>")
        print("addTunnel <name> <src> <dst>")
        print("addPop <name> <ip>")
        print("initDB")
    
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
        case "addPop":
            TicCLI.addPop()
        case "addTunnel":
            TicCLI.addTunnel()
