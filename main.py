import sqlite3
#import bcrypt  # for password hashing
import time
import re
import getpass
from datetime import datetime
import random

# Constant Value that uses team1.db
DATABASE_NAME = "new.db"
# may want to move this somewhere or make it a fucntion
def tweeterbase():
    wrong = True
    while wrong:
        DATABASE_NAME = str(input('Enter the database name (with ".db"):')).strip() # should this be enforced ???
        if DATABASE_NAME[-3:] == '.db':
            # should we check if the name provided exists in the current directory
            #because a new db gets created in dir if not in there
            return DATABASE_NAME
            wrong = False
        else:
            print('provide a valid database')

def connect(path):
    global connection, cursor

    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    cursor.execute(' PRAGMA foreign_keys=ON; ')
    connection.commit()
    return

def create_users_table():  #ERROR AND FIX TO INTEGER AND FLOAT
    '''
    CREATING USERS TABLE
    '''
    global connection, cursor

    cursor = connection.cursor() 
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            usr int PRIMARY KEY,
            pwd TEXT,
            name TEXT,
            email TEXT,
            city TEXT,
            timezone FLOAT
        );        
    ''')




    connection.commit()
    return


def create_other_table():
    '''
    CREATING ALL TABLES TOGETHER
    '''

    global connection, cursor

    cursor = connection.cursor() 

    cursor.execute('''
        create table IF NOT EXISTS follows (
        flwer       int,
        flwee       int,
        start_date  date,
        primary key (flwer,flwee),
        foreign key (flwer) references users,
        foreign key (flwee) references users
        );
    ''')

    cursor.execute('''
        create table IF NOT EXISTS tweets (
            tid	      int,
            writer      int,
            tdate       date,
            text        text,
            replyto     int,
            primary key (tid),
            foreign key (writer) references users,
            foreign key (replyto) references tweets
            );
    ''')

    cursor.execute('''
        create table IF NOT EXISTS hashtags (
            term        text,
            primary key (term)
            );
    ''')

    cursor.execute('''
        create table IF NOT EXISTS mentions (
            tid         int,
            term        text,
            primary key (tid,term),
            foreign key (tid) references tweets,
            foreign key (term) references hashtags
            );
    ''')

    cursor.execute('''
        create table IF NOT EXISTS retweets (
            usr         int,
            tid         int,
            rdate       date,
            primary key (usr,tid),
            foreign key (usr) references users,
            foreign key (tid) references tweets
            );
    ''')

    cursor.execute('''
        create table IF NOT EXISTS lists (
            lname        text,
            owner        int,
            primary key (lname),
            foreign key (owner) references users
            );

    ''')

    cursor.execute('''
        create table IF NOT EXISTS includes (
            lname       text,
            member      int,
            primary key (lname,member),
            foreign key (lname) references lists,
            foreign key (member) references users
            );
    ''')

    connection.commit()
    return



def doLogin():
    '''
    LOGIN USERS
    '''
    global connection, cursor 

    while True:

        usr = input("Enter your registered userid: ").strip() # want want to change it to say userid

        cursor.execute('SELECT usr, pwd FROM users WHERE usr = ?', (usr,))
        user_data = cursor.fetchone()
        #print(user_data)
        if not user_data:
            print("User does not exist")

        else:
            stored_password = user_data[1]
            while True:
                pwd = getpass.getpass("Enter your password: ") #THE PASSWORD IS ENCRYPTED

                if pwd == stored_password:
                    print("Login Successful")
                    break
                else:
                    print("Incorrect password, Try again!")
            break

    connection.commit()
    
    return usr

    

def doRegister():
    '''
    REGISTERING USERS
    '''
    global connection, cursor  # Use the global connection and cursor

    while True:
        input_wrong=True
        while input_wrong:
            usr = input("Enter you userID (must be an integer): ").strip()
            if usr.isdigit():
                usr=int(usr)
                input_wrong=False
            else:
                print("Please make sure the userid is an integer")

        cursor.execute('SELECT usr FROM users WHERE usr = ?', (usr,))
        existing_user = cursor.fetchone()

        if existing_user:
            print("User already exists.")

        else:

            name = str(input("Enter the name: ")).strip()
            while True:  # TO MAKE THE USER GIVE A VALID EMAIL ADDRESS
                email = input("Enter your email address: ")
                if re.match(r'^\w+@\w+\.\w+$', email): #CHAT GPT FORMATTED THIS:
                    break
                else:
                    print("Please enter a valid email address")

            city = str(input("Enter your city name: ")).strip() #froce to string
            
            input_w = True
            while input_w:
                timezone = input("Enter your timezone (must be an integer): ").strip()

                try:
                    timezone = float(timezone)  # Attempt to convert the input to an integer
                    input_w = False  # Exit the loop if successful
                except ValueError:
                    print("Please make sure the timezone is an integer.")

            pwd = getpass.getpass("Enter your password: ").strip() #force to string
        
            # Insert user data into the database using the global connection and cursor
            cursor.execute('''
                INSERT INTO users (usr, pwd, name, email, city, timezone)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (usr, pwd, name, email, city, timezone))

            print("User registered")
            connection.commit()
            break
    return usr

def follows_re_tweets(uid):
    global cursor

    tweetq = 'SELECT DISTINCT t.tid, t.tdate, t.text FROM tweets t JOIN follows f ON t.writer = f.flwee WHERE f.flwer = ? UNION SELECT DISTINCT t.tid, t.tdate, t.text FROM retweets r JOIN tweets t ON r.tid = t.tid JOIN follows f ON r.usr = f.flwee WHERE f.flwer = ? ORDER BY t.tdate DESC;'
    cursor.execute(tweetq,[uid,uid])
    rows = cursor.fetchall()

    return rows

def showTweets(_list,previousNumShowed,MAXI = 5): # this will work a different way for us it will also take a list of tweets and return the how many new tweets were shown 
    if len(_list) == 0 or len(_list) <= previousNumShowed:
        print("No More Tweets Available")

    count = 0
    numcount = previousNumShowed

    for r in _list[previousNumShowed:]:
        if len(_list) <= numcount or count == MAXI:
            break
        else:
            print(f'|Tweetid:{r[0]}\n|{r[1]}\n|{r[2]}')
            print('-'*max(len(r[1]),len(r[2])))
            count += 1
            numcount += 1
    
    return count


def getMoreDetails(tweetNumber,_list,tcount, uid):
    global cursor
    #might be extra just checks if this tweet_id exists/ if we have not displayed it to user
    if tweetNumber not in [int(r[0]) for r in _list[:tcount]]:
        print('This Tweet Has Not Been Displayed or DNE') ## we may want to remove this part and only check with query from tweets
        return


    
    
    '''
    Snehal modification of more options to the menu
    '''

    
    while True:
        print(f'1. Get Tweet Stats: ')
        print(f'2. Compose a reply: ')
        print(f'3. Retweet this tweet: ')
        print(f'4. Return back to the Tweet menu: ') # may need to change text b/c sometime back to tweet menu or main menu
        intin = True
        while(intin):
            option = input("Enter your option: ")
            if(option.isnumeric()):
                option = int(option)
                intin = False
            else:
                print("Please enter an integer value")
        
        if option==1:
            statretq = 'SELECT COUNT(DISTINCT r.usr) FROM retweets r WHERE r.tid = ?'
            statrepq = 'SELECT COUNT(DISTINCT r.tid) FROM tweets r WHERE r.replyto = ?'
            #tid = input('please provide the tweets id: ')
            cursor.execute(statretq,[tweetNumber])
            hail = cursor.fetchall()
            print(f'retweet count: {hail[0][0]}')
            cursor.execute(statrepq,[tweetNumber])
            hail = cursor.fetchall()
            print(f'reply count: {hail[0][0]}')
        if option==2:
            createTweet_MODIFIED_reply(uid=uid,Replyid=tweetNumber)
            print("Successfully performed")
        if option==3:
            createRetweet_MODIFY(who=tweetNumber, uid=uid)
        if option==4:
            return
    
    return



def search_menu():

    return

    


def searchForTweet(uid,_list,numTweetsShown):
    # may have to fix it so it displays 5 at a time through query by doing tid NOT IN 
    global cursor

    entrey = str(input("Search for Tweets (seperate keywords by ' '):")).split(' ')


    tweetq = 'SELECT DISTINCT t.tid,t.text,t.tdate FROM tweets t WHERE '
    conditions = []
    hashtags = []

    for en in entrey:
        if len(en) > 0:
            if en[0] == '#':
                hashtags.append(en[1:]) 

        conditions.append("LOWER(t.text) LIKE ?")

    combined_keywords = ["%" + keyword.lower() + "%" for keyword in entrey]

    for tag in hashtags:
        conditions.append(" t.tid IN(SELECT m.tid FROM mentions m WHERE LOWER(m.term) LIKE ? )")

    tweetq += " OR ".join(conditions)
    combined_keywords += ["%" + keyword.lower() + "%" for keyword in hashtags]

    tweetq += ' ORDER BY t.tdate DESC;'
    
    cursor.execute(tweetq,combined_keywords)
    rows = cursor.fetchall()
    if len(rows) == 0:
        print('there are no tweets with those keywords')
    else:

        TweetsShown = 0
        currentTweetsShown = 0
        currentTweetsShown = showTweets(rows,TweetsShown)
        TweetsShown += currentTweetsShown
        while(True):
            intin = True
            while(intin):
                action = input('''Would you like to:\n 1) See more tweets\n 2) Select a specific tweet\n 3) Search another tweet \n 4) Retweet A Tweet\n 5) Main Menu\n Please enter the number associated with the action: ''')
                if(action.isnumeric()):
                    action = int(action)
                    intin = False
                else:
                    print("Please enter an integer value")

            if action == 1:
                # new function needed to get followers tweets
                
                currentTweetsShown = showTweets(rows,TweetsShown)
                TweetsShown += currentTweetsShown
            elif action == 2:
                if len(rows) != 0:
                    print(f'Selection #')
                    print(f'-----------')
                    pinti = 0
                    bullet_point=[]
                    for r in rows[:TweetsShown]:
                        
                        print(f'{pinti}\t\t| Tweetid: {r[0]} |')
                        bullet_point.append(int(pinti))
                        pinti += 1
                        # the first part seems usless and it will cause problems "tweetNum <= currentNumTweetsShown and" I think tid can be 0 as well no restrictrions need only thing is if tid not in tweets
                    intin = True

                    while intin:
                        # tweetNum = int(input("Which tweet would you like to see (please select a Selection #): "))

                        try:  # Attempt to convert the input to an integer
                            tweetNum = int(input("Which tweet would you like to see (please select a Selection #): "))
                            if tweetNum in bullet_point:
                                tweetNum = int(tweetNum)
                                intin = False
                            else:
                                print("Please enter a valid selection number.")
                        except ValueError:
                            print("Please enter an integer value.")
                    
                    getMoreDetails(rows[tweetNum][0],rows,TweetsShown,uid)
                else:
                    print('no tweets to retweet')

            elif action == 3:
                searchForTweet(uid,_list,numTweetsShown)  #changed this part cuz why do we need to reply from the outside? and I feel giving the user to search another is good
                return
            # dont think we need this if we have time we can do it we just will have to fix stuff cause now the tweet list should include the old and new tweets searched for
                
                
                #createTweet(uid,Replyid = who)

            elif action == 4:
                if len(rows) != 0:
                    print(f'Selection #')
                    print(f'-----------')
                    pinti = 0
                    bullet_point=[]
                    for r in rows[:TweetsShown]:
                        
                        print(f'{pinti}\t\t| Tweetid: {r[0]} |')
                        bullet_point.append(int(pinti))
                        pinti += 1
                        # the first part seems usless and it will cause problems "tweetNum <= currentNumTweetsShown and" I think tid can be 0 as well no restrictrions need only thing is if tid not in tweets
                    intin = True

                    while intin:
                        # tweetNum = int(input("Which tweet would you like to see (please select a Selection #): "))

                        try:  # Attempt to convert the input to an integer
                            tweetNum = int(input("Which tweet would you like to see (please select a Selection #): "))
                            if tweetNum in bullet_point:
                                tweetNum = int(tweetNum)
                                intin = False
                            else:
                                print("Please enter a valid selection number.")
                        except ValueError:
                            print("Please enter an integer value.")

                    createRetweet_MODIFY(uid,rows[tweetNum][0]) # we will ask in the function for which tweet, most likely same saftey check as getMoredetials
                # need to add an exit option --this is our forced exit
                else:
                    print('no tweets to retweet')
            elif action == 5:
                break

    return


def createRetweet(uid):

    global connection, cursor

    cursor.execute('SELECT DISTINCT t.tid FROM tweets t;')
    tids = cursor.fetchall()
    cursor.execute('SELECT DISTINCT t.tid FROM retweets t WHERE t.usr = ?;',(uid,))
    toads = cursor.fetchall()
    fun = True
    date = datetime.now().date()
    while fun:
        intin = True
        while(intin):
            who = input('Which Tweet id would you like to retweet (enter an integer):')
            if(who.isnumeric()):
                who = int(who)
                intin = False
            else:
                print("Please enter an integer value")

        # check if tid exists
        if(who in [r[0] for r in toads]):
            print('you have already retweeted this tweet')
        elif (who in [r[0] for r in tids]):
            Replyid = who
            fun = False
        
        else:
            print('that tweet does not exist')
    
    cursor.execute('''
                    INSERT INTO retweets (usr, tid, rdate)
                    VALUES (?, ?, ?)
                ''', (uid, Replyid, date))

    connection.commit()


    return


def createRetweet_MODIFY(uid, who):
    '''
    Instead of manually entering which tweet you are retweeting, its automatically done.
    '''

    global connection, cursor

    cursor.execute('SELECT DISTINCT t.tid FROM tweets t;')
    tids = cursor.fetchall()
    cursor.execute('SELECT DISTINCT t.tid FROM retweets t WHERE t.usr = ?;',(uid,))
    toads = cursor.fetchall()
    fun = True
    date = datetime.now().date()
    while fun:
        # check if tid exists
        if(who in [r[0] for r in toads]):
            print('you have already retweeted this tweet')
            return
        elif (who in [r[0] for r in tids]):
            Replyid = who
            fun = False
        
        else:
            print('that tweet does not exist')
    
    cursor.execute('''
                    INSERT INTO retweets (usr, tid, rdate)
                    VALUES (?, ?, ?)
                ''', (uid, Replyid, date))
    
    print("Successfully retweeted!")

    connection.commit()


    return

def searchForUser(uid):
    # may need to add to query where the user currently loged in is not displayed
    global cursor

    entry = str(input("Search for Users by name/city(1 keyword): "))
    keyword = "%" + entry.lower() + "%"

    tweetq = '''
        SELECT DISTINCT u.usr, u.city, u.name, u.email 
        FROM users u 
        WHERE LOWER(u.name) LIKE ? 
        ORDER BY LENGTH(u.name) ASC;
    '''

    tweetq2 = '''
        SELECT DISTINCT u2.usr, u2.city, u2.name, u2.email 
        FROM users u2 
        WHERE LOWER(u2.city) LIKE ? 
        AND u2.usr NOT IN (
            SELECT DISTINCT u.usr 
            FROM users u 
            WHERE LOWER(u.name) LIKE ?
        )
        ORDER BY LENGTH(u2.city) ASC;
    '''

    cursor.execute(tweetq, (keyword,))
    rows = cursor.fetchall()

    cursor.execute(tweetq2, (keyword, keyword))
    
    rows += cursor.fetchall()
    #print(rows)
    #print(rows)
    if len(rows) == 0:
        print("no users contain the keyword in their name/city")
    else:
        TweetsShown = 0
        currentTweetsShown = 0
        currentTweetsShown = display_users(rows,TweetsShown)
        TweetsShown += currentTweetsShown

        while(True):
            intin = True
            while(intin):
                action = input('''Would you like to:\n 1) See more users\n 2) Select a specific user\n 3) Main Menu\nPlease enter a value: ''')
                if(action.isnumeric()):
                    action = int(action)
                    intin = False
                else:
                    print("Please enter an integer value")
            
            if action == 1:
                # new function needed to get followers tweets
                
                currentTweetsShown = display_users(rows,TweetsShown)
                TweetsShown += currentTweetsShown
            elif action == 2:
                    # the first part seems usless and it will cause problems "tweetNum <= currentNumTweetsShown and" I think tid can be 0 as well no restrictrions need only thing is if tid not in tweets
                user_information(rows,TweetsShown,uid)
                
            elif action == 3:
                    break


    return

def create_follow(uid,action):
    global connection,cursor
    query = "SELECT f.flwee FROM follows f WHERE f.flwer = ?"
    cursor.execute(query,(uid,))
    cheker = cursor.fetchall()
    #print(cheker)

    while True:
        if action in [int(r[0]) for r in cheker]:
            print('You already follow this user')
            break
        else:
            date = datetime.now().date()
            cursor.execute('''
                    INSERT INTO follows (flwer, flwee, start_date)
                    VALUES (?, ?, ?)
                ''', (uid, action, date))
            
            print("You have successfully followed the user")

            connection.commit()
            break

    return

def display_users(_list,previousNumShowed):
    if len(_list) == 0 or len(_list) <= previousNumShowed:
        print("No More Users Available")

    count = 0
    numcount = previousNumShowed

    for r in _list[previousNumShowed:]:
        if len(_list) <= numcount or count == 5:
            break
        else:
            print(f'|Userid: {r[0]}\n|City: {r[1]}\n|Name: {r[2]}\n|email: {r[3]}')
            print('-'*max(len(r[1]),len(r[2]),len(r[3])))
            count += 1
            numcount += 1
    
    return count

def user_information(_list,tcount,uid):
    # might need to check len of rows and say no users to select if 0
    global cursor
    if tcount == 0: #kind of redundant b/c of other function but always good
        print('there are no users to select')
    else:
        print(f'Selection #')
        print(f'-----------')
        pinti = 0
        for r in _list[:tcount]:
            print(f'{pinti}\t\t| Userid: {r[0]} |')
            pinti += 1

        while True:
            intin = True
            while(intin):
                action = input('Which User would you like to see (please select a Selection #): ')
                if(action.isnumeric()):
                    action = int(action)
                    intin = False
                else:
                    print("Please enter an integer value")

            if action < 0 or action > tcount:
                print('This User Has Not Been Displayed or DNE')
            else:
                print(f'User id: {_list[action][0]}')
                tnumq = "SELECT DISTINCT COUNT(t.tid) FROM tweets t WHERE t.writer = ?;"
                fnumq = "SELECT DISTINCT COUNT(f.flwee) FROM follows f WHERE f.flwer = ?;"
                fernumq = "SELECT DISTINCT COUNT(f.flwer) FROM follows f WHERE f.flwee = ?;"
                t3q = "SELECT DISTINCT t.tid,t.text,t.tdate FROM tweets t WHERE t.writer = ? ORDER BY t.tdate DESC;"
                cursor.execute(tnumq,(_list[action][0],))
                rows = cursor.fetchall()

                print("--------------------------")
                print("Statistics: ")
                print(f'Number of Tweets: {rows[0][0]}')

                cursor.execute(fnumq,(_list[action][0],))
                rows = cursor.fetchall()
                print(f'Number of Following: {rows[0][0]}')

                cursor.execute(fernumq,(_list[action][0],))
                rows = cursor.fetchall()
                print(f'Number of Followed: {rows[0][0]}')

                print("--------------------------")
                
                cursor.execute(t3q,(_list[action][0],))
                rows = cursor.fetchall()
                
                
                numTweetsShown = 0
                currentNumTweetsShown = 0# make it so the user can select to see more tweets then we will show 3 more till max
                if len(rows) != 0:
                    print('3 most recent tweets:')
                    currentNumTweetsShown = showTweets(rows,numTweetsShown,MAXI = 3)
                    numTweetsShown += currentNumTweetsShown
                while True:
                    intin = True
                    while(intin):
                        choice = input(' 1) See more tweets\n 2) Follow the user\n 3) Go back\nPlease Select a Number: ')
                        if(choice.isnumeric()):
                            choice = int(choice)
                            intin = False
                        else:
                            print("Please enter an integer value")
                    if choice == 1:
                        showTweets(rows,numTweetsShown,MAXI = 3)
                        numTweetsShown += currentNumTweetsShown
                    elif choice == 2:
                        create_follow(uid,_list[action][0])
                        break
                    elif choice == 3:
                        break
                    else:
                        print("Please enter a valid integer")
                break
    return


def createTweet(uid,Replyid = None): #may need to check if it is in the list of tweets with count 
    global connection, cursor
    # need to check if replyid is actauly an existing tweetid --> must be done in the if yes and in other function sepratily
    # assuming # are only added to a tweet through the text
    cursor.execute('SELECT DISTINCT t.tid FROM tweets t;')
    tids = cursor.fetchall()

    text = str(input(f'Type Your Tweets Text:\n'))
    hashtags = [word for word in text.split() if word.startswith('#')]
    date = datetime.now().date()
    tid = new_random([r[0] for r in tids], 1, 2147483647)

    if Replyid == None:
        cursor.execute('''
                    INSERT INTO tweets (tid, writer, tdate, text, replyto)
                    VALUES (?, ?, ?, ?, ?)
                ''', (tid, uid, date, text, Replyid))

        connection.commit()
    else:
         cursor.execute('''
                    INSERT INTO tweets (tid, writer, tdate, text)
                    VALUES (?, ?, ?, ?)
                ''', (tid, uid, date, text))

         connection.commit()
    if len(hashtags) != 0:
        cursor.execute('SELECT DISTINCT t.term FROM hashtags t;')
        tids = [f[0] for f in cursor.fetchall()]
        for tag in hashtags:
            if tag[1:len(tag)] not in tids:
               # print(tag[1:len(tag)])
                cursor.execute('INSERT INTO hashtags (term) VALUES (?)', (tag[1:len(tag)],))

                connection.commit()

            
            cursor.execute('''
                    INSERT INTO mentions (tid, term)
                    VALUES (?, ?)
                ''', (tid, tag[1:len(tag)]))
            


            connection.commit()

    print("Tweet posted!")
    
    return


def createTweet_MODIFIED_reply(uid,Replyid = None): #may need to check if it is in the list of tweets with count 
    '''
    SAME LIKE THE RETWEET MODIFICATION, I WILL BE MODIFYING THIS
    CHANGE: I WILL BE MAKING THIS FUNCTION SUITABLE FOR REPLYING
    '''
    global connection, cursor
    # need to check if replyid is actauly an existing tweetid --> must be done in the if yes and in other function sepratily
    # assuming # are only added to a tweet through the text
    cursor.execute('SELECT DISTINCT t.tid FROM tweets t;')
    tids = cursor.fetchall()
    


    text = str(input(f'Type Your Tweets Text:\n'))
    hashtags = [word for word in text.split() if word.startswith('#')]
    date = datetime.now().date()
    tid = new_random([r[0] for r in tids], 1, 2147483647)



    
    cursor.execute('''
                INSERT INTO tweets (tid, writer, tdate, text, replyto)
                VALUES (?, ?, ?, ?, ?)
            ''', (tid, uid, date, text, Replyid))

    connection.commit()

    if len(hashtags) != 0:
        cursor.execute('SELECT DISTINCT t.term FROM hashtags t;')
        tids = [f[0] for f in cursor.fetchall()]
        for tag in hashtags:
            if tag[1:len(tag)] not in tids:
               # print(tag[1:len(tag)])
                cursor.execute('INSERT INTO hashtags (term) VALUES (?)', (tag[1:len(tag)],))

                connection.commit()

            
            cursor.execute('''
                    INSERT INTO mentions (tid, term)
                    VALUES (?, ?)
                ''', (tid, tag[1:len(tag)]))

            connection.commit()
    
    return

def new_random(_list, lower_bound, upper_bound):
    random_number = random.randint(lower_bound, upper_bound)
    
    while random_number in _list:
        random_number = random.randint(lower_bound, upper_bound)
    
    return random_number

def showFollowers(uid):
    global connection, cursor
    #everyone that follows uid
    tweetq = '''
        SELECT DISTINCT u.usr, u.city, u.name, u.email 
        FROM users u, follows f
        WHERE u.usr = f.flwer AND f.flwee = ? 
    '''

    cursor.execute(tweetq, (uid,))
    rows = cursor.fetchall()
    if len(rows) != 0:
        for r in rows:
            print(f'|Userid: {r[0]}\n|City: {r[1]}\n|Name: {r[2]}\n|email: {r[3]}')
            print('-'*max(len(r[1]),len(r[2]),len(r[3])))
        while(True):
            intin = True
            while(intin):
                action = input('''Would you like to:\n 1) Select a specific user\n 2) Main Menu\nPlease enter a value: ''')
                if(action.isnumeric()):
                    action = int(action)
                    intin = False
                else:
                    print("Please enter an integer value")
            if action == 1:
                # new function needed to get followers tweets
                user_information(rows,len(rows),uid)
            elif action == 2:
                break
            else:
                print("Please enter a valid value")
    else:
        print("You have no followers")

    return


def logout():
    exit()

def main():
    '''
    main function prompts the user for input and call given functions based on the input.
    First ask the user to login or register.

    '''
    # may need to fix login, serachusers,searchtweet,followslist, to make it so we select a 
    #tweet/user and then we get options for the selected tweet/user
    #right now we provide the id whenever options are "triggred" 
    global connection, cursor
    DATABASE_NAME = tweeterbase()
    connect(DATABASE_NAME)

    create_users_table()
    create_other_table()
    
    # login = input("Login or Register (Please type Login to login or Register to register): ").strip()
    
    menu_starter=True
    while(menu_starter):
        lol=True
        login=input("-----\nWELCOME TO TWITTER\nPOWERED BY TEAM1\n------\nSelect an option:\n1. Register\n2. Login\n3. Exit\nEnter your input: ").strip()
        while(lol): # Present CL login or register prompt
            if login.lower() == "2":
                uid = doLogin()
                lol=False
                break
            elif login.lower() == "1":
                uid = doRegister()
                lol=False
                break
            elif login.lower() == "3":
                logout()
            login = input("Unknown input, please either select login or register (Please type Login to login or Register to register): ")

        

        _list = follows_re_tweets(uid) # this is for some reason giving us tweets made by uid
        ## nvm im dumb tid 1 and 8 are writen by user 1 and retweeted by either of his followers 2 and 3
        numTweetsShown = 0
        currentNumTweetsShown = 0
        currentNumTweetsShown = showTweets(_list,numTweetsShown)
        numTweetsShown += currentNumTweetsShown

        secondary_menu_main=True
        while(secondary_menu_main):
            intin = True
            while(intin):
                action = input('''Would you like to:\n 1) See more tweets\n 2) Select a specific tweet\n 3) Search for a tweet\n 4) Search for a user\n 5) Compose a tweet\n 6) List all your followers\n 7) Logout\nPlease enter the number associated with the action: ''')
                if(action.isnumeric()):
                    action = int(action)
                    intin = False
                else:
                    print("Please enter an integer value")
            
            if action == 1:
                # new function needed to get followers tweets
                
                currentNumTweetsShown = showTweets(_list,numTweetsShown)
                numTweetsShown += currentNumTweetsShown
            elif action == 2:
                if len(_list) != 0:
                    print(f'Selection #')
                    print(f'-----------')
                    pinti = 1
                    for r in _list[:numTweetsShown]:
                        
                        
                        print(f'{pinti}\t\t| Tweetid: {r[0]} |')
                        pinti += 1
                        # the first part seems usless and it will cause problems "tweetNum <= currentNumTweetsShown and" I think tid can be 0 as well no restrictrions need only thing is if tid not in tweets
                    
                    notInRange = True
                    while(notInRange):
                        intin = True
                        while(intin):
                            tweetNum = input("Which tweet would you like to see (please select a Selection #): ")
                            if(tweetNum.isnumeric()):
                                tweetNum = int(tweetNum)-1
                                intin = False
                            else:
                                print("Please enter an integer value")
                        if len(_list) > tweetNum:
                            getMoreDetails(_list[tweetNum][0],_list,numTweetsShown,uid)
                            break
                        else:
                            print("Please enter a valid value")
                else:
                    print('no tweets to select')      
            elif action == 3:
                searchForTweet(uid,_list,numTweetsShown) #add an option to finish this and go back to login screen
                # i think we should make login a function and then have an option to always go back to login screnn
                #but the tweets shown will be reset on the screen (as in the 5 shown) or maybe not well decide
                #searchForTweet(uid,_list,numTweetsShown)
            elif action == 4:
                searchForUser(uid)
            elif action == 5: 
                createTweet(uid)
            elif action == 6:
                showFollowers(uid)
            elif action == 7:
                secondary_menu_main=False
                
            else:
                print("Please enter a valid integer")

if __name__ == "__main__":
    main()
