import socket
import sys
import StringIO
import operator
from collections import Counter
import time
#Config
nick = "Angstwoman" #define nick
network = "my.irc.server"
port = 6667
chan = "#lobby"
admins = ["SocksPls", "sockspls"]

#Don't change this
reg = 0
j = 0
helpme = 0
wrong = []

def most_common(iterable):
    totals = {}
    for letter in iterable:
        if letter in totals:
            totals[letter] += 1
        else:
            totals[letter] = 1
    print totals
    print iterable
    c = Counter(totals)
    if len(c) == 0:
        return False
    else:
        return c.most_common(1)[0][0]

with open('wordlist.txt') as f:
    words = f.read().splitlines()

def connect():
    irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Define IRC network

    print "[*] Connecting"
    irc.connect((network,port))
    print "[*] Connected"

    irc.recv (4096)
    irc.send('NICK ' + nick + '\r\n') #Set nick
    irc.send('USER ' + nick + " " + nick + " " + nick + " " + nick + "\r\n") #Sent user info
    irc.send('JOIN ' + chan + "\r\n")
    return irc

def join(chan):
    print("[*] Trying to join " + str(chan))
    irc.send('JOIN ' + chan + "\r\n")

def ping(data):
    irc.send('PONG ' + data.split()[1] + '\r\n') #Send back a PONG

def msgchan(msg, chan):
    irc.send('PRIVMSG ' + chan + " :" + msg + "\r\n")

def voice(tovoice, chan):
    irc.send("MODE " + chan + " v:" + tovoice + "\r\n")

irc = connect()

def privmsgdetails(data):
    sender = data.split("!")[0][1:]
    senderhostname = data.split()[0].split("!")[1]
    fromchannel = data.split()[2]
    messagesent = ":".join(data.split(":")[2:])
    return(sender, senderhostname, fromchannel, messagesent)

while True:
    data = irc.recv (4096)
    print data
    if reg == 1 and j == 0:
        join(chan)
        j = 1
    if data.find('PING') != -1:
        ping(data)
    elif data.split()[1] == "PRIVMSG":
        sender, senderhostname, fromchannel, messagesent = privmsgdetails(data)
        if messagesent.startswith("!join") and sender in admins:
            join(messagesent[6:])
            print ("Joining " + messagesent[6:])
        elif messagesent.startswith("!quit") and sender in admins:
            exit()
        elif messagesent.startswith("!helpme") and sender in admins:
            helpme = 1
            time.sleep(0.2)
            msgchan(".g", chan)
        elif sender.lower() == "angstman" and fromchannel == chan and helpme == 1:
            if messagesent.startswith("You guessed the ") or messagesent.startswith("Incorrect guesses:") or messagesent.startswith("You win!"):
                if messagesent.startswith("Incorrect guesses:"):
                    #If the message sent contains the incorrect letters list and
                    # the user has requested help, save the incorrect letters
                    #list to wrong
                    wrong = [x for x in messagesent.split(": ")[1]]
            else:
                #Gets the clue and removes spaces, prints clue for debugging
                clue = messagesent.strip()
                clue = clue.replace(" ", "")
                print("Clue", clue)

                #Gets words of matching length, that also match the clue
                matchinglen = []
                match = []
                correct = clue.replace("_", "")
                for word in words:
                    if len(clue) == len(word):
                        nomatch = 0
                        for i, c in enumerate(word):
                            if (clue[i] == "_") and c not in wrong and c not in correct:
                                pass
                            elif (clue[i] == c) and c not in wrong:
                                pass
                            else:
                                nomatch = 1
                        if (nomatch == 0):
                            match.append(word)
                print match
                match = list(set(match)) #Removes duplicates from the matching words just in case
                match.sort() #Sorts the list of words for some reason
                bestguess = []
                if len(match) == 1: #If there's only one matching word
                    msgchan("The word is " + match[0], chan) #Show the word

                for word in match:
                    for letter in word:
                        if letter not in correct:
                            bestguess.append(letter)

                msgchan("Your best guess is " + str(most_common(bestguess)), chan)

                #Reset some variables for next run
                helpme = 0
                wrong = []
                toremove = []
                print correct
