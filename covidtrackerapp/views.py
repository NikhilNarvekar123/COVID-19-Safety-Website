from django.shortcuts import render, redirect, HttpResponse
from django.template import RequestContext
from django.contrib.auth import hashers
import pyrebase, math, time, smtplib

firebaseConfig = {
    'apiKey': "AIzaSyAWFTpdWykYSeXZJWUEBb26S69f0WYm2nQ",
    'authDomain': "coronaaware-71b77.firebaseapp.com",
    'databaseURL': "https://coronaaware-71b77.firebaseio.com",
    'projectId': "coronaaware-71b77",
    'storageBucket': "coronaaware-71b77.appspot.com",
    'messagingSenderId': "38215757364",
    'appId': "1:38215757364:web:8762c29d5086e8c08e2461"
 }

fb = pyrebase.initialize_app(firebaseConfig)
auth = fb.auth()
db = fb.database()

def home(request):
    context = {'login' : 0, 'navVis' : True, 'auth' : False}

    chkLogin = getLoginInfo(request)
    if(chkLogin[1] == -1):
        return logout(request)
    context['login'] = chkLogin[0]
    context['auth'] = chkLogin[1] == 1

    return render(request, 'index.html', context)


def profile(request):
    context = {'login' : 0, 'navVis' : True, 'auth' : False, 'sick' : -1, 'positive': -1}

    chkLogin = getLoginInfo(request)

    if(chkLogin[1] == -1):
        return logout(request)

    if(chkLogin[0] == 0):
        return redirect('home')
    else:
        context['login'] = 1

    contacted = None
    contactHealth = None
    contactmap = db.child(request.session['login']).child('contacted').get().val()

    if(request.method == 'POST'):

        if('sick' in request.POST):
            print('passed')
            sick = db.child(request.session['login']).child('sick').get().val()
            data = sick.split("+")
            if(data[1] == ''):
                db.child(request.session['login']).child('sick').set('1+' + str(time.time()))
                contacted = []
                contactHealth = []
                for k in contactmap:
                    if(k == 'a'):
                        continue
                    if(int(contactmap[k].split("+")[3]) < 1):
                        message = 'Hello, this is a message from safefromcovid.com. A user you were in contact with recently claims that they are feeling ill. Visit your profile at safefromcovid.com to learn more'
                        message += "\nEmail of other user: " + db.child(request.session['login']).child('email').get().val() + "\nLocation of contact: https://www.google.com/maps/place/" + contactmap[k].split("+")[0] + "," + contactmap[k].split("+")[1]
                        email(message, db.child(k).child('email').get().val())
                        contactInfo(contacted, contactHealth, contactmap, k)
                        db.child(request.session['login']).child('contacted').child(k).set(contactmap[k][0:len(contactmap[k]) - 2] + '+1')
            else:
                if(time.time() - float(data[1]) > 432000):
                    db.child(request.session['login']).child('sick').set('0+')
        else:
            positive = db.child(request.session['login']).child('positive').get().val()
            data = positive.split("+")

            if(data[1] == ''):
                db.child(request.session['login']).child('positive').set('1+' + str(time.time()))
                contacted = []
                contactHealth = []
                for k in contactmap:
                    if(k == 'a'):
                        continue
                    if(int(contactmap[k].split("+")[3]) < 2):
                        message = 'Hello, this is a message from safefromcovid.com. A user you were in contact with recently claims that they have tested positive for COVID-19. Visit your profile at safefromcovid.com to learn more'
                        message += "\nEmail of other user: " + db.child(request.session['login']).child('email').get().val() + "\nLocation of contact: https://www.google.com/maps/place/" + contactmap[k].split("+")[0] + "," + contactmap[k].split("+")[1]
                        email(message, db.child(k).child('email').get().val())
                        contactInfo(contacted, contactHealth, contactmap, k)
                        db.child(request.session['login']).child('contacted').child(k).set(contactmap[k][0:len(contactmap[k]) - 2] + '+2')

            else:
                if(time.time() - float(data[1]) > 1728000):
                    db.child(request.session['login']).child('positive').set('0+')

    context['auth'] = chkLogin[1] == 1

    if(contacted == None):
        contacted = []
        contactHealth = []
        for k in contactmap:
            if(k == 'a'):
                continue
            contactInfo(contacted, contactHealth, contactmap, k)

    context['contacted'] = contacted
    context['contacthealth'] = contactHealth

    context['sick'] = db.child(request.session['login']).child('sick').get().val()
    context['positive'] = db.child(request.session['login']).child('positive').get().val()
    context['email'] = db.child(request.session['login']).child('email').get().val()

    return render(request, 'profile.html', context)

def contactInfo(contacted, contactHealth, contactmap, k):
    timedif = time.time() - float((contactmap[k].split("+"))[2])
    if(timedif/3600 > 360):
        db.child(request.session['login']).child('contacted').child(k).remove()
    else:
        contacted.append(contactmap[k])
        contactHealth.append(0)
        if(db.child(k).child('sick').get().val().split('+')[0] == '1'):
            contactHealth[len(contactHealth) - 1] = 1
        if(db.child(k).child('positive').get().val().split('+')[0] == '1'):
            contactHealth[len(contactHealth) - 1] = 2


def newProf(request):
    context = {'navVis' : False, 'alert' : ''}

    if(request.method == 'POST'):
        email = request.POST['address']
        psswrd = request.POST['password']
        if(len(psswrd) < 6):
            context['alert'] = 'Password must be at least 6 characters in length'
        else:
            if(request.POST['password-conf'] == psswrd):
                try:
                    auth.create_user_with_email_and_password(email, psswrd)
                    auth.sign_in_with_email_and_password(email, psswrd)
                    auth.send_email_verification(auth.current_user['idToken'])
                    acct = {
                        'email' : email,
                        'contacted' : {'a':'0'},
                        'positive' : '0+',
                        'sick' : '0+',
                    }
                    resp = redirect('home')

                    request.session['login'] = auth.current_user['localId']
                    request.session['verified'] = 1
                    db.child(auth.current_user['localId']).set(acct)
                    return resp
                except:
                    context['alert'] = 'The email you entered has already been taken. Try again'
            else:
                context['alert'] = 'Passwords do not match! Try again'

    return render(request, 'new-profile.html', context)

def signIn(request):
    context = {'navVis' : False, 'alert' : ''}
    chkLogin = getLoginInfo(request)

    if(chkLogin[1] == -1):
        return logout(request)

    if(chkLogin[0] == 1):
        return redirect('home')

    if(request.method == 'POST'):
        email = request.POST['address']
        psswrd = request.POST['password']
        try:
            auth.sign_in_with_email_and_password(email, psswrd)
            resp = redirect('home')

            request.session['login'] = auth.current_user['localId']
            request.session['verified'] = 1#int(auth.get_account_info(auth.current_user['idToken'])['users'][0]['emailVerified'] == True)
            return resp
        except Exception as e:
            print(e)
            context['alert'] = 'Email/password is incorrect! Try again'

    return render(request, 'sign-in.html', context)

def tracker(request):
    context = {'navVis' : True, 'auth' : True, 'login' : 1}

    chkLogin = getLoginInfo(request)

    if(chkLogin[1] == -1):
        return logout(request)

    if(chkLogin[0] == 0 or chkLogin[1] == 0):
        return redirect('home')

    return render(request, 'tracker.html', context)

def about(request):
    chkLogin = getLoginInfo(request)
    if(chkLogin[1] == -1):
        return logout(request)
    context = {'navVis' : True, 'login' : 0, 'auth' : False}
    context['login'] = chkLogin[0]
    context['auth'] = chkLogin[1] == 1
    return render(request, 'about.html', context)

def logout(request):
    if('login' in request.session):
        del request.session['login']
    if('verified' in request.session):
        del request.session['verified']

    return redirect('home')

def updateTracker(request):
    chkLogin = getLoginInfo(request)
    if(chkLogin[0] == 0):
        return redirect('logout')
    else:
        db.child('Active').child(request.session['login']).child('lat').set(request.POST['lat'])
        db.child('Active').child(request.session['login']).child('long').set(request.POST['long'])

        allActive = db.child('Active').get().val()
        for user in allActive:
            if(not(user == 'permkey' or user == request.session['login'])):
                mylat = (float(request.POST['lat'])/180) * math.pi
                otherlat = (float(allActive[user]['lat'])/180) * math.pi

                mylong = (float(request.POST['long'])/180) * math.pi
                otherlong = (float(allActive[user]['long'])/180) * math.pi

                latDist = (abs(mylat - otherlat)) * 6378134

                factor = (math.cos(mylat) + math.cos(otherlat))/2
                longdist = min(abs(mylong-otherlong), (2*math.pi) - abs(mylong - otherlong)) * factor * 6378134

                dist = math.sqrt(math.pow(latDist, 2)  + math.pow(longdist, 2))

                if(dist < 50):
                    ignore = 0
                    contactmap = db.child(request.session['login']).child('contacted').get().val()
                    if(db.child(request.session['login']).child('sick').get().val().split('+')[0] == '1'):
                        ignore = 1
                    if(db.child(request.session['login']).child('positive').get().val().split('+')[0] == '1'):
                        ignore = 2

                    if(not(user in contactmap) or time.time() - float(contactmap[user].split("+")[2]) > 43200):
                        if(ignore == 1):
                            message = "Hello, this is a message from safefromcovid.com. Our records indicate that you were in close contact with a person claiming to be ill. Visit your profile at safefromcovid.com to learn more."
                            message += "\nInformation about contact:\nEmail of other user: " + db.child(request.session['login']).child('email').get().val() + "\nLocation of contact: " + 'https://www.google.com/maps/place/' + request.POST['lat'] + ',' + request.POST['long']
                            email(message, db.child(user).child('email').get().val())
                        if(ignore == 2):
                            message = "Hello, this is a message from safefromcovid.com. Our records indicate that you were in close contact with a person claiming to be positive for COVID-19. Visit your profile at safefromcovid.com to learn more."
                            message += "\nInformation about contact:\nEmail of other user: " + db.child(request.session['login']).child('email').get().val() + "\nLocation of contact: " + 'https://www.google.com/maps/place/' + request.POST['lat'] + ',' + request.POST['long']
                            email(message, db.child(user).child('email').get().val())

                    contactmap[user] = str(mylat) + '+' + str(mylong) + '+' + str(time.time()) + '+' + str(ignore)
                    db.child(request.session['login']).child('contacted').set(contactmap)


        return HttpResponse()

def initiateTracker(request):
    chkLogin = getLoginInfo(request)
    if(chkLogin[1] == -1):
        return logout(request)

    acct = db.child(request.session['login']).get().val()
    del acct['email']
    del acct['contacted']
    del acct['positive']
    del acct['sick']
    acct['lat'] = -1
    acct['long'] = -1
    db.child("Active").child(request.session['login']).set(acct)

    return HttpResponse()

def suspendTracker(request):
    print("passed")
    db.child("Active").child(request.session['login']).remove()
    return HttpResponse()


def email(message, to):
    message = 'Subject: ' + 'Important update from safefromcovid.com\n\n' + message
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login('coronaaware@gmail.com', 'covidtracker20')
    print(to)
    server.sendmail('coronaaware@gmail.com', to, message)

def getLoginInfo(request):
    res = [0, 0]
    if('login' in request.session):
        if(checkValidLogin(request.session['login'])):
            res[0] = 1
        else:
            return res
    else:
        return res

    if('verified' in request.session):
        res[1] = request.session['verified']
    else:
        #Verified cookie expired but login still valid
        res[1] = -1

    return res


def checkValidLogin(token):
    try:
        if(db.child(token).get().val() == None):
            return False
    except:
        return False
    return True