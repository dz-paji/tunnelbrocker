import mysql.connector
import configparser

class SQLConnector:
    def __init__(self):
        configger = configparser.ConfigParser()
        configger.read('config/tic.ini')
        host = configger.get("SQL", "Host")
        user = configger.get("SQL", "User")
        password = configger.get("SQL", "Password")
        database = configger.get("SQL", "Database")
        
        db = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        
        
        
