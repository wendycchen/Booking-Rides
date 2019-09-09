import sqlite3
from datetime import datetime
import datetime
import base64
import getpass
import hashlib
import re

def login_menu():
    print("\nCMPUT 291 - Mini Project 1")
    print("------")
    print("A - login as existing user")
    print("B - create new user")
    print("C - exit")
    print("------")
    while True:
        user_input = input("Choose an option> ")
        if user_input.upper() in ('A', 'B', 'C'):
            return user_input.upper()
        else:
            print("Input invalid")
            continue
    conn.close()

def login_main(conn):
    while True:
        print("Please input your email and password. ")
        email = input("Email: ")
        pw = getpass.getpass("Password (Input Hidden): ")
             
        #Query DB for matching profiles
        cursor = conn.cursor()
        cursor.execute("SELECT name, phone FROM members WHERE email = ? AND pwd = ?;", (email, pw))
        chosen = cursor.fetchall()
        if chosen: 
            for row in chosen:
                name = str(row[0])
                phone = str(row[1])
            break
        
        if not chosen:
            print("Login Unknown. Please Retry.\n")
            continue
    
    return email, name, phone

def emails_seen(conn, email):
    i, seen, unseen, x = 0, 0, 0, 0 
    format_name = ""
    format_content = ""
    seen_change = "y"   
    content_list = []
    
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM inbox WHERE email = ?", (email,))
    info = cursor.fetchall()
    for values in info:
        emails = values[0]
        read = values[5]
        if read == 'n':
            unseen += 1
            content = values[3]
            content_list.append(content)
        elif read == 'y':
            seen += 1
        i += 1
    
    while unseen > 0:
        print("You have", i, "messages:", seen, "read messages and", unseen, "unread messages.")
        read_choice = input("Would you like to open the unread messages?\nPlease type in your choice in Y/N: ")
        if read_choice.upper() == 'Y':
            print("|---------------|-----------------------------------------")
            print("|Sender%-9s|Content%-30s" % (format_name, format_content))
            print("|---------------|-------------------------------------------------")
            for x in range(len(content_list)):
                cursor.execute("SELECT sender FROM inbox WHERE content =?", (content_list[x],))
                sender_retrieved = cursor.fetchall()
                sender = sender_retrieved[0][0]
                print("|%-15s|%-30s" % (sender, content_list[x]))
                print("|---------------|-------------------------------------------------")
                cursor.execute("UPDATE inbox SET seen = ? WHERE content =?", (seen_change, content))
                conn.commit()
                seen += 1
                unseen -= 1
                x += 1  
            break
                         
        if read_choice.upper() == 'N':
            break
    
    if unseen == 0:
        print("You have no new messages.")

def login_create(conn):
    i = 0
    found = False
    check = False
    print("Please provide an unique email, name, phone number, and a password to create a new account.")
    email = input("Email: ")
    name = input("Name: ")
    phone = input("Phone: ")
    query = "SELECT email FROM members"
    cursor = conn.cursor()
    cursor.execute(query)
    email_rows = cursor.fetchall()
    
    while email_rows[i] != email_rows[-1]: 
        if email_rows[i][0] != email:
            i += 1
        if email_rows[i][0] == email:
            found = True
            break
    
    while found == False:
        cursor.execute("INSERT INTO members VALUES(?, ?, ?, Null)", (email, name, phone,))
        conn.commit()
        
        while check == False: #check this 
            pwd = getpass.getpass("Please type in your password: ")
            confirm_pwd = getpass.getpass("Please confirm your password (input hidden): ")
        
            if pwd == confirm_pwd:
                cursor.execute("UPDATE members SET pwd = ? WHERE email = ?", (pwd, email))
                conn.commit()
                print("You have successfully created a profile in our database. Please proceed forward to log in for further actions.")
                check = True
            
            elif pwd != confirm_pwd:
                print("Your passwords do not match. Please retry.")
                continue
        break
        
    while found == True:
        print("You're a reigstered member. Please log in instead.")
        return login_menu()

def service_options(conn, email):
    while True: 
        proceed_choice = str(input("1. Offer a ride\n2. Search for rides\n3. Book members\n4. Cancel bookings\n5. Post ride requests\n6. Search and delete ride requests\n7. Log out\nYour choice: "))
        if proceed_choice in ('1','2','3','4','5', '6', '7'):
            break
        else:
            print("Wrong input. Try again.")
            continue
    return proceed_choice

def offer_rides(conn, email):
    cno = ''
    rno_list = []
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM locations")
    location_fetched = cursor.fetchall()
    
    #stores each rno from the rides into a list
    cursor.execute("SELECT rno FROM rides")
    allrno = cursor.fetchall()
    for i in range(len(allrno)):
        rno_list.append(allrno[i][0])
    
    carnum_list = []
    o, m= 0, 0
    unirno = int(100)
    now = datetime.datetime.now().date()
    src_list = []
    dst_list = [] 
    temp_list = []
    
    while True:
        confirm_ride = input("Would you like to offer a ride? (Y/N): ")
        if confirm_ride.upper() == 'Y':
            while True:
                date = input("Please input a date you would like to offer a ride in (YYYY-MM-DD): ")

                try:
                    if date > str(now):
                        break
                    else:
                        print("Please input a future time.")
                        continue
                except ValueError:
                    print("Wrong input. Please try again.")
            while True:
                seats_offered = input("How many seats are offered? ")
                try:
                    int(seats_offered)
                    break
                except ValueError:
                    print("That's not an integer input.")
                    continue
            while True:
                price_pseat = input("What is the price per seat? $")
                try:
                    int(price_pseat)
                    break
                except ValueError:
                    print("That's not an integer input.")
                    continue
            while True:
                lugdesc = input("What is your luggage size? L for a large bag or S for a small bag: ")
                if lugdesc.upper() == 'L':
                    lugdesc = 'large bag'
                    break
                elif lugdesc.upper() == 'S':
                    lugdesc = 'small bag'
                    break
                elif lugdesc == '':
                    print("Please fill in an option.")
                    continue
                else:
                    print("Wrong option. Try again.")
                    continue
            
            while True:
                value = 0
                usersrc_lcode = input("Where is your source starting location? ")
                srcdst_format = re.compile("^[a-z]{2}[0-9]{1}$")
                
                while value < (len(location_fetched)):
                    if usersrc_lcode == location_fetched[value][0]:
                        src_list.append(usersrc_lcode)
                        value += 1
                    elif usersrc_lcode.title() == location_fetched[value][1]:
                        srccode = location_fetched[value][0]
                        src_list.append(srccode)
                        value += 1
                    elif usersrc_lcode.title() == location_fetched[value][2]:
                        srccode = location_fetched[value][0]
                        src_list.append(srccode)
                        value += 1
                    elif usersrc_lcode.title() == location_fetched[value][3]:
                        srccode = location_fetched[value][0]
                        src_list.append(srccode)
                        value += 1
                    else:
                        value += 1
            
                if src_list:
                    length = len(src_list)
                    while True:
                        if len(src_list) <= 5:
                            for m in range(len(src_list)):
                                print(str(m+1)+ ".", src_list[m])
                            choice = input("Option >> ")
                            src = src_list[(int(choice) - 1)]
                            break
                        else:
                            while True:
                                for i in range(5):
                                    try:
                                        src_list[o + i]
                                        print(str(i+1) + ".",src_list[o + i])
                                        length -= 1
                                    except IndexError:
                                        break
                                if length != 0:
                                    print("N. Next Match.")
                                    choice = input("Option >> ")
                                    if choice.title() == 'N':
                                        o += 5
                                        continue
                                    else:
                                        src = src_list[o + (int(choice) -  1)]
                                        break
                                else:
                                    print("B. Back")
                                    choice = input("Option >> ")
                                    if choice.title() == 'B':
                                        o = 0
                                        continue
                                    else:
                                        src = src_list[o + (int(choice) - 1)]
                                        break
                    
                    cursor.execute("SELECT city, prov FROM locations WHERE lcode = ?", (src,))
                    ans = cursor.fetchone()
                    print("Your starting location code:", src, ",", ans)
                    break
                if not src_list:
                    print("Wrong input.")
                    continue
            
            while True:
                values = 0
                userdst_lcode = input("Where is your destination location? ")
                srcdst_format = re.compile("^[a-z]{2}[0-9]{1}$")                
                
                print(userdst_lcode)
                while values < (len(location_fetched)):
                    if userdst_lcode == location_fetched[values][0]:
                        dst_list.append(userdst_lcode)
                        values += 1
                    elif userdst_lcode.title() == location_fetched[values][1]:
                        dstcode = location_fetched[values][0]
                        dst_list.append(dstcode)
                        values += 1
                    elif userdst_lcode.title() == location_fetched[values][2]:
                        dstcode = location_fetched[values][0]
                        dst_list.append(dstcode)
                        values += 1
                    elif userdst_lcode.title() == location_fetched[values][3]:
                        dstcode = location_fetched[values][0]
                        dst_list.append(dstcode)
                        values += 1
                    else:
                        values += 1

                if dst_list:
                    length = len(dst_list)
                    while True:
                        if len(dst_list) <= 5:
                            for i in range(len(dst_list)):
                                print(str(i+1)+ ".", dst_list[i]) 
                            choice = input("Option >> ")
                            dst = dst_list[(int(choice) - 1)]
                            break                                
                        else:
                            while True:
                                for i in range(5):
                                    try:
                                        print(str(i+1) + ".",dst_list[m + i])
                                        length -= 1
                                    except IndexError:
                                        break
                                if length != 0:
                                    print("N. Next Match.")
                                    choice = input("Option >> ")
                                    if choice.title() == 'N':
                                        m += 5
                                        continue
                                    else:
                                        dst = dst_list[m + (int(choice) -  1)]
                                        break
                                else:
                                    print("B. Back")
                                    choice = input("Option >> ")
                                    if choice.title() == 'B':
                                        m = 0
                                        continue
                                    else:
                                        dst = dst_list[m + (int(choice) - 1)]
                                        break
                    
                    cursor.execute("SELECT city, prov FROM locations WHERE lcode = ?", (dst,))
                    ans = cursor.fetchone()
                    print("Your destination location code:", dst, ",", ans)  
                    break
            
                if not dst_list:
                    print("Invalid input.")
                    continue

            cnodb_list = []
            cno_list = []
            cursor.execute("SELECT cno FROM cars WHERE owner = ?", (email,))
            cnofromdb = cursor.fetchall()
            for i in cnofromdb:
                carno = i[0]
                cnodb_list.append(carno)
              
            while True:
                a = 0 
                more_info = input("Would you like to add more information?\n1.A car number\n2.Enroute locations\n3.Nothing else\nOption >> ")
                if more_info == '1':
                    cno = int(input("What is your car number? "))
                    while a < len(cnodb_list):
                        if cnodb_list[a] == cno:
                            cno_list.append(cno)
                            break
                        a += 1
                    
                    if cno_list:
                        for i in range(len(cno_list)):
                            print("Your cno input:", cno_list[i])
                        continue
                    if not cno_list:
                        print("Unfortunately, you do not have a registered car in our system, so you are prohibited from providing a ride to our other members.")
                        break
                    
                elif more_info == '2':
                    enroute_lcode = input("What enroute locations would you like to add on? ")
                elif more_info == '3':
                    break
            
            print(unirno, price_pseat, seats_offered, date, lugdesc, src, dst, cno_list, email)
            
            for i in range(len(rno_list)):
                if unirno == rno_list[i]:
                    unirno += 1
            
            if cno:
                cursor.execute("INSERT INTO rides VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (unirno, price_pseat, date, seats_offered, lugdesc, src, dst, email, cno))
            if not cno:
                cursor.execute("INSERT INTO rides VALUES (?, ?, ?, ?, ?, ?, ?, ?, Null)", (unirno, price_pseat, date, seats_offered, lugdesc, src, dst, email,))
                
            conn.commit()
            break
 
        elif confirm_ride.upper() == 'N':
            break
        else:
            print("Input invalid. Please try again.")
            continue
    
def search_rides(conn, email):
    y, r, rvalue, value, values, valuess = 0, 0, 0, 0, 0, 0
    lcode_list, city_list, prov_list, add_list, userlcode, usercity, userprov, useradd, finallcode, alist, enroute_list = [], [], [], [], [], [], [], [], [], [], []
    
    now = datetime.datetime.now().date() 
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT * FROM locations")
    location_fetched = cursor.fetchall()
    cursor.execute("SELECT DISTINCT * FROM enroute")
    enroute = cursor.fetchall()
    
    for i in range(len(location_fetched)):
        lcode_list.append(location_fetched[i][0])
        city_list.append(location_fetched[i][1])
        prov_list.append(location_fetched[i][2])
        add_list.append(location_fetched[i][3])
    
    kywds = input("Please type in up to 3 keywords to search for rides (Separated by commas): ").split(",")

    srcdst_format = re.compile("^[a-z]{2}[0-9]{1}$")
    
    for j in kywds:
        if srcdst_format.match(j):
            finallcode.append(j)
        else:
            j = j.title()
            
            for k in range(len(city_list)):
                if j == city_list[k]:
                    if j not in usercity:
                        usercity.append(city_list[k])
            for l in range(len(prov_list)):
                if j == prov_list[l]:
                    if j not in userprov:
                        userprov.append(prov_list[l])
            for m in range(len(add_list)):
                if j == add_list[m]:
                    if j not in useradd:
                        useradd.append(city_list[m])         
    
    if usercity:
        for value in range(len(usercity)):
            cursor.execute("SELECT lcode FROM locations WHERE city = ?", (usercity[value],))
            ans = cursor.fetchall()
            for i in range(len(ans)):
                finallcode.append(ans[i][0])
    
    if userprov:
        for values in range(len(userprov)):
            cursor.execute("SELECT lcode FROM locations WHERE prov = ?", (userprov[values],))
            ans = cursor.fetchall()
            for i in range(len(ans)):
                finallcode.append(ans[i][0])
        
    if useradd:
        for valuess in range(len(useradd)):
            cursor.execute("SELECT lcode FROM locations WHERE address = ?", (useradd[valuess],))
            ans = cursor.fetchall()
            for i in range(len(ans)):
                finallcode.append(ans[i][0])

    print(finallcode)
    for item in finallcode:
        for i in enroute:
            if item == i[1]:
                cursor.execute("SELECT rides.rno, rides.price, rides.rdate, rides.seats, rides.lugDesc, rides.src, rides.dst, rides.driver, rides.cno, cars.make, cars.model, cars.year, cars.seats FROM rides, cars WHERE rides.rno= ? AND rides.cno = cars.cno", (i[0],))
                ans = cursor.fetchall()
                cursor.execute("SELECT * FROM rides, enroute WHERE enroute.lcode = ? AND rides.rno = enroute.rno", (i[0],))
                for i in (cursor.fetchall()):
                    ans.append(i)
                for i in ans:
                    if i not in alist:
                        alist.append(i)         
    
    for rvalue in range(len(finallcode)):
        cursor.execute("SELECT rides.rno, rides.price, rides.rdate, rides.seats, rides.lugDesc, rides.src, rides.dst, rides.driver, rides.cno, cars.make, cars.model, cars.year, cars.seats FROM rides, cars WHERE src = ? AND rides.cno = cars.cno", (finallcode[rvalue],))
        ans = cursor.fetchall()
        cursor.execute("SELECT * FROM rides WHERE src = ? AND rides.cno is NULL", (finallcode[rvalue],))
        for i in (cursor.fetchall()):
            ans.append(i)
        for i in ans:
            if i not in alist:
                alist.append(i)
        
        cursor.execute("SELECT rides.rno, rides.price, rides.rdate, rides.seats, rides.lugDesc, rides.src, rides.dst, rides.driver, rides.cno, cars.make, cars.model, cars.year, cars.seats FROM rides, cars WHERE dst = ? AND rides.cno = cars.cno", (finallcode[rvalue],))
        ans = cursor.fetchall()
        cursor.execute("SELECT * FROM rides WHERE dst = ? AND rides.cno is NULL", (finallcode[rvalue],))
        for i in (cursor.fetchall()):
            ans.append(i)
        for i in ans:
            if i not in alist:
                alist.append(i)  
    
    alist.sort(key= lambda x : x[0])
                
    length = len(alist)
    total_length = length
    
    while True:
        if length <= 5:
            print("|---|-----|--------|----------|------|----------|-----|-----|---------------|-----|------------|--------|------|----------|")
            print("|#%2s|rno%-2s|Price%-3s|Date%-6s|Seats%-1s|Luggage%-3s|SRC%-2s|DST%-2s|Driver Email%-3s|CNO%-2s|Make%-8s|Model%-3s|Year%-2s|SeatsInCar%-s|" % ("","","","","","","","", "", "", "", "", "", ""))
            print("|---|-----|--------|----------|------|----------|-----|-----|---------------|-----|------------|--------|------|----------|")
            print(alist)
            for r in range(len(alist)):
                print("|", str(r+1)+ " |%-5s|%-8s|%-10s|%-6s|%-10s|%-5s|%-2s|%-15s|%-5s|%-12s|%-8s|%-6s|%-10s|" % (alist[r][0], alist[r][1], alist[r][2], alist[r][3], alist[r][4], alist[r][5], alist[r][6], alist[r][7], alist[r][8], alist[r][9], alist[r][10], alist[r][11], alist[r][12]))
                print("|---|-----|--------|----------|------|----------|-----|-----|---------------|-----|------------|--------|------|----------|")
                if not alist[r][8]:
                    print("|", str(r+1)+ " |%-5s|%-8s|%-10s|%-6s|%-10s|%-5s|%-5s|%-15s|%-5s|%-12s|%-8s|%-6s|%-10s|" % (alist[r][0], alist[r][1], alist[r][2], alist[r][3], alist[r][4], alist[r][5], alist[r][6], alist[r][7], alist[r][8], "Null", "Null", "Null", "Null"))
                    print("|---|-----|--------|----------|------|----------|-----|-----|---------------|-----|------------|--------|------|----------|")                    
            choice = input("Option >> ")
            try:
                selected = alist[(int(choice) -  1)][0]
                break
            except ValueError:
                print("Wrong input. Please try again")
                continue 
        else:
            while True:
                print("|---|-----|--------|----------|------|----------|-----|-----|---------------|-----|------------|--------|------|----------|")
                print("|#%2s|rno%-2s|Price%-3s|Date%-6s|Seats%-1s|Luggage%-3s|SRC%-2s|DST%-2s|Driver Email%-3s|CNO%-2s|Make%-8s|Model%-3s|Year%-2s|SeatsInCar%-s|" % ("","","","","","","","", "", "", "", "", "", ""))
                print("|---|-----|--------|----------|------|----------|-----|-----|---------------|-----|------------|--------|------|----------|") 
                for r in range(5):
                    try:
                        alist[y + r]
                        if alist[y + r][8]:
                            print("|", str(r+1)+ " |%-5s|%-8s|%-10s|%-6s|%-10s|%-5s|%-5s|%-15s|%-5s|%-12s|%-8s|%-6s|%-10s|" % (alist[y+r][0], alist[y+r][1], alist[y+r][2], alist[y+r][3], alist[y+r][4], alist[y+r][5], alist[y+r][6], alist[y+r][7], alist[y+r][8], alist[y+r][9], alist[y+r][10], alist[y+r][11], alist[y+r][12]))
                            print("|---|-----|--------|----------|------|----------|-----|-----|---------------|-----|------------|--------|------|----------|")  
                        if not alist[y+r][8]:
                            print("|", str(r+1)+ " |%-5s|%-8s|%-10s|%-6s|%-10s|%-5s|%-5s|%-15s|%-5s|%-12s|%-8s|%-6s|%-10s|" % (alist[y+r][0], alist[y+r][1], alist[y+r][2], alist[y+r][3], alist[y+r][4], alist[y+r][5], alist[y+r][6], alist[y+r][7], alist[y+r][8], "Null", "Null", "Null", "Null"))
                            print("|---|-----|--------|----------|------|----------|-----|-----|---------------|-----|------------|--------|------|----------|")                             
                    except IndexError:
                        break
                
                print("y:", y)      
                if 4 < y < (total_length - 5):
                    print("N. Next Match")
                    print("B. Back")
                    choice = input("Option >> ")
                    if choice.title() == 'N':
                        y += 5
                        continue 
                    elif choice.title() == 'B':
                        y -= 5
                        continue
                    else:
                        try:
                            selected = alist[y + (int(choice) -  1)][0]
                            break
                        except ValueError:
                            print("Wrong input. Please try again")
                            continue 
                
                elif y + 5 >= total_length:
                    print("B. Back")
                    choice = input("Option >> ")
                    if choice.title() == 'B':
                        y -= 5
                        continue
                    elif choice.title() == 'N':
                        print("Wrong input.")
                        continue
                    else:
                        try:
                            selected = alist[y + (int(choice) -  1)][0]
                            break
                        except ValueError:
                            print("Wrong input. Please try again.")
                            continue  
                            
                elif y < total_length:
                    print("N. Next Match.")
                    choice = input("Option >> ")
                    if choice.title() == 'N':
                        y+= 5
                        continue
                    else:
                        try:
                            selected = alist[y + (int(choice) -  1)][0]
                            break
                        except ValueError:
                            print("Wrong input. Please try again")
                            continue 
        break
        
    cursor.execute("SELECT driver FROM rides WHERE rno = ?", (selected,))
    driver_email = cursor.fetchone()
    cursor.execute("SELECT rdate FROM rides WHERE rno = ?", (selected,))
    date = cursor.fetchone()
    cursor.execute("SELECT seats FROM rides WHERE rno = ?", (selected,))
    seats_available = cursor.fetchone()
    print("Your driver's email is:", driver_email[0])
    
    while True:
        seats_needed = int(input("How many seats would you like to book for the ride? "))
        if seats_needed > seats_available[0]:
            print("You're asking for too many seats, which is not provided from the driver.")
        else:
            print("An automatic message of the following content would be delivered for you to your driver: \n'Hello, I would like to book", seats_needed, "for the following date:", date[0],"\nThank you.'")
            content = "Hello, I would like to book for %s seats on %s for %s ride"
            break
         
    today = datetime.datetime.now().date()
    driver_email = driver_email[0]
    cursor.execute("INSERT INTO inbox VALUES (?,?,?,?,?,'N')", (driver_email, today, email, content%(seats_needed,date[0],selected), selected, ))
    conn.commit()
        
def book_members(conn, email):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM rides WHERE driver = ?", (email,))
    ride_info = cursor.fetchall()
    print(ride_info)
    length = len(ride_info)
    total_length = length
    j = 0
    options = True
    while True:
        if length == 0:
            print("You do not currently provide any ride. Please proceed back to option 1 to offer a ride.")
            return options
        
        elif length <= 5:
            print("Below is a list of the rides you provide as of currently:")
            print("|---|-----|--------|----------|------|----------|-----|-----|---------------|-----|------------|--------|------|----------|")
            print("|#%2s|rno%-2s|Price%-3s|Date%-6s|Seats%-1s|Luggage%-3s|SRC%-2s|DST%-2s|Driver Email%-3s|CNO%-2s|Make%-8s|Model%-3s|Year%-2s|SeatsInCar%-s|" % ("","","","","","","","", "", "", "", "", "", ""))
            print("|---|-----|--------|----------|------|----------|-----|-----|---------------|-----|------------|--------|------|----------|")    
            for i in range(len(ride_info)):
                if ride_info[i][8]:
                    print("|", str(i+1)+ " |%-5s|%-8s|%-10s|%-6s|%-10s|%-5s|%-2s|%-15s|%-5s|%-12s|%-8s|%-6s|%-10s|" % (ride_info[i][0], ride_info[i][1], ride_info[i][2], ride_info[i][3], ride_info[i][4], ride_info[i][5], ride_info[i][6], ride_info[i][7], ride_info[i][8], ride_info[i][9], ride_info[i][10], ride_info[i][11], ride_info[i][12]))
                    print("|---|-----|--------|----------|------|----------|-----|-----|---------------|-----|------------|--------|------|----------|")
                if not ride_info[i][8]:
                    print("|", str(i+1)+ " |%-5s|%-8s|%-10s|%-6s|%-10s|%-5s|%-5s|%-15s|%-5s|%-12s|%-8s|%-6s|%-10s|" % (ride_info[i][0], ride_info[i][1], ride_info[i][2], ride_info[i][3], ride_info[i][4], ride_info[i][5], ride_info[i][6], ride_info[i][7], ride_info[i][8], "Null", "Null", "Null", "Null"))
                    print("|---|-----|--------|----------|------|----------|-----|-----|---------------|-----|------------|--------|------|----------|")
            choice = input("Option >> ")
            try:
                selected = alist[y + (int(choice) -  1)][0]
                break
            except ValueError:
                print("Wrong input. Please try again")
                continue

        else:
            print("Below is a list of the rides you provide as of currently:")
            while True:
                print("|---|-----|--------|----------|------|----------|-----|-----|---------------|-----|------------|--------|------|----------|")
                print("|#%2s|rno%-2s|Price%-3s|Date%-6s|Seats%-1s|Luggage%-3s|SRC%-2s|DST%-2s|Driver Email%-3s|CNO%-2s|Make%-8s|Model%-3s|Year%-2s|SeatsInCar%-s|" % ("","","","","","","","", "", "", "", "", "", ""))
                print("|---|-----|--------|----------|------|----------|-----|-----|---------------|-----|------------|--------|------|----------|") 
                for i in range(5):
                    try:
                        ride_info[j + i]
                        if ride_info[j + i][8]:
                            print("|", str(i+1)+ " |%-5s|%-8s|%-10s|%-6s|%-10s|%-5s|%-2s|%-15s|%-5s|%-12s|%-8s|%-6s|%-10s|" % (ride_info[j + i][0], ride_info[j + i][1], ride_info[j + i][2], ride_info[j + i][3], ride_info[j + i][4], ride_info[j + i][5], ride_info[j + i][6], ride_info[j + i][7], ride_info[j + i][8], ride_info[j + i][9], ride_info[j + i][10], ride_info[j + i][11], ride_info[j + i][12]))
                            print("|---|-----|--------|----------|------|----------|-----|-----|---------------|-----|------------|--------|------|----------|")  
                        if not ride_info[j + i][8]:
                            print("|", str(i+1)+ " |%-5s|%-8s|%-10s|%-6s|%-10s|%-5s|%-5s|%-15s|%-5s|%-12s|%-8s|%-6s|%-10s|" % (ride_info[j + i][0], ride_info[j + i][1], ride_info[j + i][2], ride_info[j + i][3], ride_info[j + i][4], ride_info[j + i][5], ride_info[j + i][6], ride_info[j + i][7], ride_info[j + i][8], "Null", "Null", "Null", "Null"))
                            print("|---|-----|--------|----------|------|----------|-----|-----|---------------|-----|------------|--------|------|----------|")
                    except IndexError:
                        break
                
                print("j:", j)      
                if 4 < j < (total_length - 5):
                    print("N. Next Match")
                    print("B. Back")
                    choice = input("Option >> ")
                    if choice.title() == 'N':
                        j += 5
                        continue 
                    elif choice.title() == 'B':
                        j -= 5
                        continue
                    else:
                        try:
                            selected = ride_info[j + (int(choice) -  1)][0]
                            break
                        except ValueError:
                            print("Wrong input. Please try again")
                            continue 
                
                elif j + 5 >= total_length:
                    while True:
                        print("B. Back")
                        choice = input("Option >> ")
                        if choice.title() == 'B':
                            j -= 5
                            break
                        elif choice.title() == 'N':
                            print("Wrong input.")
                            continue
                        else:
                            try:
                                selected = ride_info[j + (int(choice) -  1)][0]
                                break
                            except ValueError:
                                print("Wrong input. Please try again.")
                                continue  
                            
                elif j < total_length:
                    print("N. Next Match.")
                    choice = input("Option >> ")
                    if choice.title() == 'N':
                        j += 5
                        continue
                    else:
                        try:
                            selected = ride_info[j + (int(choice) -  1)][0]
                            break
                        except ValueError:
                            print("Wrong input. Please try again")
                            continue 
        break
    
    bno_list = []
    unibno = 10
    print("You have selected ride", selected, "to book.")
    member_email = input("Please type in the member's email for whom you'd like to book the ride for: ")
    cursor.execute("SELECT seats FROM rides WHERE rno = ?", (selected,))
    seats_available = cursor.fetchone()
    while True:
        seats_booked = int(input("The number of seats needed: "))
        if seats_booked > seats_available[0]:
            ans = input("Warning: the ride is being overbooked.\nIf you'd like to allow overbooking, please type in Y; or else, N: ")
            if ans.upper() == 'Y':
                break
            elif ans.upper() == 'N':
                continue
            else:
                print("Wrong input. Please try again")
                continue
        else:
            break
    cost_perseat = input("The cost per seat: ")
    src = input("The pickup location code: ")
    dst = input("The dropoff location code: ")
    
    cursor.execute("SELECT bno FROM bookings")
    bno = cursor.fetchall()
    
    #stores retrieved bno values into a list
    for i in range(len(bno)):
        bno_list.append(bno[i][0])
    
    #goes through the bno list to find a unique bno number to use for the booking
    for i in range(len(bno_list)):
        if unibno == bno_list[i]:
            unibno += 1
    
    cursor.execute("SELECT rdate FROM rides WHERE rno =?", (selected,))
    date = cursor.fetchone()
    
    cursor.execute("INSERT INTO bookings VALUES (?,?,?,?,?,?,?)", (unibno, member_email, selected, cost_perseat, seats_booked, src, dst))
    conn.commit()
    
    today = datetime.datetime.now().date()
    print(today)
    content = "Hello, I have booked you for %s seats on %s for %s ride" 
    cursor.execute("INSERT OR REPLACE INTO inbox VALUES (?,?,?,?,?,'N')", (member_email, today, email, content%(seats_booked,date[0],selected), selected,))
    conn.commit()
    
def cancel_bookings(conn, email):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bookings, rides WHERE bookings.rno = rides.rno AND rides.driver = ?", (email,))
    bookings = cursor.fetchall()
    option = True
    
    if not bookings:
        print("You do not have any booking records in our system. Please proceed to option 1 to register a ride first.")
        return option
    
    print("Below is a chart of all the bookings you have coming up.")
    print("|---|----------------|-----|-----|-----|-------|-------|")
    print("|BNO%-s|Email%-11s|rno%-2s|Cost%-1s|Seats%-s|PickUp%-1s|DropOff%-s|" % ("", "", "", "", "", "", ""))
    print("|---|----------------|-----|-----|-----|-------|-------|")
    for i in range(len(bookings)):
        print("|%-3s|%-16s|%-5s|%-5s|%-5s|%-7s|%-7s|" % (bookings[i][0], bookings[i][1], bookings[i][2], bookings[i][3], bookings[i][4], bookings[i][5], bookings[i][6]))
        print("|---|----------------|-----|-----|-----|-------|-------|")
    while True:
        ans = int(input("Please type in the bno number of the ride you would like to cancel: "))
        for i in range(len(bookings)):
            if bookings[i][0] == ans:
                confirm = input("Please confirm the ride number inputted is the booking number you would like to cancel (Y/N): ")
                if confirm.upper() == "Y":
                    break
                elif confirm.upper() == "N":
                    continue
            else:
                continue
            
        break
    
    cursor.execute("SELECT email, rno FROM bookings WHERE bno =?", (ans,))
    fetched = cursor.fetchall()
    print(fetched)
    member_email = fetched[0][0]
    rno = fetched[0][1]
    today = datetime.datetime.now().date()
    content = "Hello, due to an unfortunate personal reason, I have cancelled your booking for ride %s.\nSorry for the inconvenience." 
    cursor.execute("INSERT OR REPLACE INTO inbox VALUES (?,?,?,?,?,'N')", (member_email, today, email, content%(ans), rno, ))
    conn.commit()    
    
    cursor.execute("DELETE FROM bookings WHERE bno = ?", (ans,))
    conn.commit()
    print("An email has been forwarded for you to the customer.")

def post_requests(conn, email):
    cursor = conn.cursor()
    cursor.execute("SELECT lcode FROM locations")
    lcode_list = cursor.fetchall()
    now = datetime.datetime.now().date()
    print("In order to post a ride request, you would need to provide a date, a pickup location code, a drop off location code, and the amount you are willing to pay per seat.")
    while True:
        date = input("Please type in the date you would like to request for a ride (YYYY-MM-DD): ")
        try:
            if date > str(now):
                break
            else:
                print("Please input a future time.")
                continue
        except ValueError:
            print("Wrong input. Please try again.")
    
    srcdst_format = re.compile("^[a-z]{2}[0-9]{1}$")
    while True:
        src = input("Pickup location code: ")
        if srcdst_format.match(src):
            for i in range(len(lcode_list)):
                if src == lcode_list[i][0]:
                    break
                else:
                    continue
        else:
            print("Please type in the location code, i.e. ab0")
            continue
        break
        
    while True:
        dst = input("Dropoff location code: ")
        if srcdst_format.match(dst):
            for i in range(len(lcode_list)):
                if dst == lcode_list[i][0]:
                    break
                else:
                    continue
        else:
            print("Please type in the location code, i.e. ab0")
            continue
        break
    
    while True:
        money = input("The amount you are willing to pay per seat: $")
        try:
            money = int(money)
            break
        except ValueError:
            continue
    
    unirid = 1
    rid_list = []
    cursor = conn.cursor()
    cursor.execute("SELECT rid FROM requests")
    rid = cursor.fetchall()
    
    for i in range(len(rid)):
        rid_list.append(rid[i][0])
    
    for i in range(len(rid_list)):
        if unirid == rid_list[i]:
            unirid += 1 
    
    cursor.execute("INSERT INTO requests VALUES (?,?,?,?,?,?)", (unirid, email, date, src, dst, money))
    conn.commit()
    print("A ride request has been posted for you.")
    
def seardel_requests(conn, email): #need to fix it so that when a user inputs a false answer, such as calgary, no result shows up so it loops back
    j = 0
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM requests WHERE email = ?", (email,))
    requests = cursor.fetchall()
    print("Below is a chart of the requests you have made:")
    print("|----|-----------------|----------|------|--------|------|")
    print("|rid%-1s|Email%-12s|Date%-6s|PickUp%-s|DropOff%-1s|Amount%-s|" %("","","","","",""))
    print("|----|-----------------|----------|------|--------|------|")
    for i in range(len(requests)):
        print("|%-4s|%-17s|%-10s|%-6s|%-8s|%-6s|" % (requests[i][0], requests[i][1], requests[i][2], requests[i][3], requests[i][4], requests[i][5]))
        print("|----|-----------------|----------|------|--------|------|")
        
    cursor.execute("SELECT DISTINCT pickup FROM requests")
    pkup = cursor.fetchall()
    fetched = []

    while True:
        choice = input("Please type in a location code or a city name to find the specific ride requests: ")
        src_format = re.compile("^[a-z]{2}[0-9]{1}$")
        
        
        for i in range(len(pkup)):
            if choice == src_format:
                cursor.execute("SELECT * FROM requests WHERE pickup = ?", (choice,))
                fetched = cursor.fetchall()
                print(fetched)
                break

            elif choice == pkup[i][0]:
                print(pkup[i][0])
                cursor.execute("SELECT * FROM requests WHERE pickup = ?", (choice,))
                fetched = cursor.fetchall()
                print(fetched)
                break

            else:
                choice = choice.title() 
                cursor.execute("SELECT DISTINCT locations.lcode FROM locations, requests WHERE locations.city = ? AND locations.lcode = requests.pickup", (choice,))
                city_lcode = cursor.fetchall()
                for x in range(len(city_lcode)):
                    cursor.execute("SELECT requests.rid, requests.email, requests.rdate, requests.pickup, requests.dropoff, requests.amount FROM requests, locations WHERE requests.pickup = locations.lcode AND locations.lcode = ?", (city_lcode[x][0],))
                    fetched_info = cursor.fetchall()
                    print(fetched_info)
                    for y in range(len(fetched_info)):
                        fetched.append(fetched_info[y])
                break
        break

        
    print(fetched)
    length = range(len(fetched))
    total_length = len(length)
    
    while True:
        if total_length <= 5:    
            print("|----|-----------------|----------|------|--------|------|")
            print("|rid%-1s|Email%-12s|Date%-6s|PickUp%-s|DropOff%-1s|Amount%-s|" %("","","","","",""))
            print("|----|-----------------|----------|------|--------|------|")  
            for i in range(len(fetched)):
                print("|%-4s|%-17s|%-10s|%-6s|%-8s|%-6s|" % (fetched[i][0], fetched[i][1], fetched[i][2], fetched[i][3], fetched[i][4], fetched[i][5]))
                print("|----|-----------------|----------|------|--------|------|")
            choice = input("Option >> ")
            break
        else:
            while True:
                print("|----|-----------------|----------|------|--------|------|")
                print("|rid%-1s|Email%-12s|Date%-6s|PickUp%-s|DropOff%-1s|Amount%-s|" %("","","","","",""))
                print("|----|-----------------|----------|------|--------|------|")
                for i in range(5):
                    try:
                        print("|%-4s|%-17s|%-10s|%-6s|%-8s|%-6s|" % (fetched[j + i][0], fetched[j + i][1], fetched[j + i][2], fetched[j + i][3], fetched[j + i][4], fetched[j + i][5]))
                        print("|----|-----------------|----------|------|--------|------|") 
                    except IndexError:
                        break
                
                print("j:", j)      
                if 4 < j < (total_length - 5):
                    print("N. Next Match")
                    print("B. Back")
                    choice = input("Option >> ")
                    if choice.title() == 'N':
                        j += 5
                        continue 
                    elif choice.title() == 'B':
                        j -= 5
                        continue
                    else:
                        try:
                            selected = int(choice)
                            cursor.execute("SELECT email FROM requests WHERE rid = ?", (selected,))
                            member_email = cursor.fetchone()                            
                            break
                        except ValueError:
                            print("Wrong input. Please try again")
                            continue 
                
                elif j + 5 >= total_length:
                    while True:
                        print("B. Back")
                        choice = input("Option >> ")
                        if choice.title() == 'B':
                            j -= 5
                            break
                        elif choice.title() == 'N':
                            print("Wrong input.")
                            continue
                        else:
                            try:
                                selected = int(choice)
                                cursor.execute("SELECT email FROM requests WHERE rid = ?", (selected,))
                                member_email = cursor.fetchone()                            
                                break
                            except ValueError:
                                print("Wrong input. Please try again.")
                                continue  
                        
                elif j < total_length:
                    print("N. Next Match.")
                    choice = input("Option >> ")
                    if choice.title() == 'N':
                        j += 5
                        continue
                    else:
                        try:
                            selected = int(choice)
                            cursor.execute("SELECT email FROM requests WHERE rid = ?", (selected,))
                            member_email = cursor.fetchone()                            
                            break
                        except ValueError:
                            print("Wrong input. Please try again.")
                            continue
            break    

    today = datetime.datetime.now().date()
    #cursor.execute("SELECT email FROM requests WHERE rid = ?", (selected,))
    #member_email = cursor.fetchone()
    
    print("The member's email is: ", member_email[0])
    content = input("Please type in the content of the email that you would like to deliver to the email address' owner: ")
    
    cursor.execute("INSERT INTO inbox VALUES (?,?,?,?,Null,'N')", (member_email[0], today, email, content,))
    conn.commit()
    print("An email has been delivered for you to the owner of that address.")
        

def main():
    conn = sqlite3.connect('/Users/Wendy/CMPUT291/MiniProject1/miniproj1.db')
    cursor = conn.cursor()
    cursor.execute('PRAGMA foreign_keys = ON;')
    
    email = ""
    name = ""
    phone = ""
    proceed_choice = None
    
    #Allow user to select their task
    while True:
        user_input = login_menu()
        if user_input == 'A':
            email, name, phone = login_main(conn)
            print("[Email:", email + "] | [Name:", name + "] | [Phone:", phone + "]")
            emails_seen(conn, email)
            while True:
                print("------")
                proceed_choice = service_options(conn, email)
                if proceed_choice == '1':
                    offer_rides(conn, email)
                    continue
                elif proceed_choice == '2':
                    search_rides(conn, email)
                    continue
                elif proceed_choice == '3':
                    options = book_members(conn, email)
                    continue
                elif proceed_choice == '4':
                    options = cancel_bookings(conn, email)
                    continue
                elif proceed_choice == '5':
                    post_requests(conn, email)
                    continue
                elif proceed_choice == '6':
                    seardel_requests(conn, email) 
                    continue
                elif proceed_choice == '7':
                    logoutchoice = input("Are you sure you'd like to log out right now? ")
                    if logoutchoice.upper() == 'Y':
                        break
                    elif logoutchoice.upper() == 'N':
                        continue
        elif user_input == 'B':
            login_create(conn)
        elif user_input == 'C':
            break


if __name__ == "__main__":
    main()