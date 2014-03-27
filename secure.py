"""secure.py checks /var/log/secure for new occurrences of "Failed password"
mesages and sends a mail for new break-in attempts on the system. I also
plan to add a feature to drop any traffic from an IP that has attempted to
break-in more than configured times."""

import os
import sqlite3
import sys
import time

# initially set to 0, MTIME keeps a track of the latest modification time for
# /var/log/secure file

MTIME = 0

def database_exists():
    return os.path.exists("var_log_secure.db") #and os.path.exists("count.db")


def create_database():
    """We will create two databases. One for logging the details of attempt
    like date & ip while another for keeping a track of number of attempts made
    from a particular IP. In future we plan to drop all packets coming from an
    IP that has made X (say, 5) attempts using firewall rules.
    """
    try:
        db = sqlite3.connect("var_log_secure.db")
        cursor = db.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS
                       attempts(id INTEGER PRIMARY KEY, day INTEGER, month INTEGER,
                       year INTEGER, ip TEXT)''')
        db.commit()
    except Exception as e:
        print e
    finally: db.close()


def fetch_last_from_db():
    """ Code in this function will fetch the last entry in the db. This is
    is helpful in figuring out if the data parsed by the program is newer
    than the existing db entries."""
    pass


def insert_into_db(data):
    """ This funtion inserts into the database the break-in attempts that are
    newer than the last one as returned by fetch_last_from_db() function"""
    
    day, month, year = data["day"], data["month"], data["year"]
    user, ip = data["user"], data["ip"]
    
    try:
        db1 = sqlite3.connect("var_log_secure.db")
        cursor1 = db1.cursor()
        cursor1.execute("INSERT INTO attempts(day, month, year, ip) VALUES(?, ?,\
                        ?, ?)", (day, month, year, ip))
        db1.commit()
    except Exception as e:
        db1.rollback()
        print e
    finally:
        db1.close()
        

def new_attempts_from_last():
    """This function will determine the break-in attempts newer than the last
    break-in attempt"""
    pass


def database_operations(date, msg):
    """ This function takes a list of break-in attempt log messages that our
    program found from /var/log/secure and then performs database operations
    on it like - finding last break-in attempt's details, ensure to insert
    and notify only for attempts newer than last attempt, insert these new
    entries into the database"""
    year, month, day = date[0], date[1], date[2]
    user, ip = msg[6], msg[8]
    data = {"year" : year, "month" : month, "day" : day, "ip" : ip, "user" :
            user}
    insert_into_db(data)


def check_for_failed_password(list_of_readlines):
    l = list_of_readlines
    for i in range(len(l)):
        if ' '.join(l[i].split(' ')[3:6]) == 'Failed password for':
            x = l[i].split('T')  # Temporary variable to fetch date.
            date = x[0].split('-')
            message = l[i].split(' ')
            database_operations(date, message)
        else:
            continue


def scan_var_log_secure():
    global MTIME
    new_MTIME = os.path.getmtime("/var/log/secure")
    if MTIME == new_MTIME:
        return
    else:
        list_of_readlines = []
        try:
            with open('/var/log/secure') as f:
                list_of_readlines = f.readlines()
                check_for_failed_password(list_of_readlines)
        except IOError as e:
            print "You do not have enough permissions to access the file.\n" \
                  "Run the program as sudo or root user and try again."
            sys.exit()

        #print "new_MTIME = %f" % new_MTIME
        MTIME = new_MTIME
    return


def main():
    if not database_exists():
        create_database()

    global DB1
    global DB2
    try:
        DB1 = sqlite3.connect("var_log_secure.db")
        DB2 = sqlite3.connect("count.db")
        while 1:
            scan_var_log_secure()
            time.sleep(5)
    except Exception as e:
        DB1.rollback()
        DB2.rollback()
        print e
        sys.exit(1)
    finally:
        DB1.close()
        DB2.close()


if __name__ == "__main__":
    if os.path.exists("/var/log/secure"):
        sys.exit(main())
    else:
        print '/var/log/secure does not exist. Make sure the file exists and '\
              'try again later.'
        sys.exit(1)
