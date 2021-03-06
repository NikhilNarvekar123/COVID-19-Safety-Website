from django.shortcuts import render, redirect, HttpResponse
from django.template import RequestContext
#from sendgrid import SendGridAPIClient
#from sendgrid.helpers.mail import Mail
from django.core.mail import send_mail
import pyrebase, math, time, os

firebaseConfig = {
    'apiKey': os.environ['API_KEY'],
    'authDomain': "coronaaware-71b77.firebaseapp.com",
    'databaseURL': "https://" + os.environ['PROJECT_NAME'] + ".firebaseio.com",
    'projectId': os.environ['PROJECT_NAME'],
    'storageBucket': os.environ['PROJECT_NAME'] + ".appspot.com",
    'messagingSenderId': "38215757364",
    'appId': os.environ['APP_ID']
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

    contacted = []
    contactHealth = []
    contactmap = db.child(request.session['login']).child('contacted').get(request.session['auth']).val()

    for k in contactmap:
        if(k == 'a'):
            continue
        contactInfo(contacted, contactHealth, contactmap, k, request)

    contactmap = db.child(request.session['login']).child('contacted').get(request.session['auth']).val()

    if(request.method == 'POST'):

        if('sick' in request.POST):
            sick = db.child(request.session['login']).child('sick').get(request.session['auth']).val()
            data = sick.split("+")
            if(data[1] == ''):
                db.child(request.session['login']).child('sick').set('1+' + str(time.time()), request.session['auth'])

                for k in contactmap:
                    if(k == 'a'):
                        continue
                    if(int(contactmap[k].split("+")[3]) < 1):
                        message = 'Hello, this is a message from Safe from COVID. A user you were in contact with recently claims that they are feeling ill. Visit your profile at https://safefromcovid.herokuapp.com to learn more'
                        message += "\nEmail of other user: " + db.child(request.session['login']).child('email').get(request.session['auth']).val() + "\nLocation of contact: https://www.google.com/maps/place/" + str(180*(float(contactmap[k].split("+")[0])/math.pi)) + "," + str(180*(float(contactmap[k].split("+")[1])/math.pi))
                        message += "\nDate of contact: " + time.strftime('%Y-%m-%d', time.localtime(round(float(contactmap[k].split("+")[2]))));
                        email(message, db.child(k).child('email').get(request.session['auth']).val())
                        db.child(request.session['login']).child('contacted').child(k).set(contactmap[k][0:len(contactmap[k]) - 2] + '+1', request.session['auth'])
            else:
                if(time.time() - float(data[1]) > 432000):
                    db.child(request.session['login']).child('sick').set('0+', request.session['auth'])
        else:
            positive = db.child(request.session['login']).child('positive').get(request.session['auth']).val()
            data = positive.split("+")

            if(data[1] == ''):
                db.child(request.session['login']).child('positive').set('1+' + str(time.time()), request.session['auth'])

                for k in contactmap:
                    if(k == 'a'):
                        continue
                    if(int(contactmap[k].split("+")[3]) < 2):
                        message = 'Hello, this is a message from Safe from COVID. A user you were in contact with recently claims that they have tested positive for COVID-19. Visit your profile at https://safefromcovid.herokuapp.com to learn more'
                        message += "\nEmail of other user: " + db.child(request.session['login']).child('email').get(request.session['auth']).val() + "\nLocation of contact: https://www.google.com/maps/place/" + str(180*(float(contactmap[k].split("+")[0])/math.pi)) + "," + str(180*(float(contactmap[k].split("+")[1])/math.pi))
                        message += "\nDate of contact: " + time.strftime('%Y-%m-%d', time.localtime(round(float(contactmap[k].split("+")[2]))));
                        email(message, db.child(k).child('email').get(request.session['auth']).val())
                        db.child(request.session['login']).child('contacted').child(k).set(contactmap[k][0:len(contactmap[k]) - 2] + '+2', request.session['auth'])

            else:
                if(time.time() - float(data[1]) > 1728000):
                    db.child(request.session['login']).child('positive').set('0+', request.session['auth'])

    context['auth'] = chkLogin[1] == 1

    context['contacted'] = contacted
    context['contacthealth'] = contactHealth

    context['sick'] = db.child(request.session['login']).child('sick').get(request.session['auth']).val()
    context['positive'] = db.child(request.session['login']).child('positive').get(request.session['auth']).val()
    context['email'] = db.child(request.session['login']).child('email').get(request.session['auth']).val()

    return render(request, 'profile.html', context)

def contactInfo(contacted, contactHealth, contactmap, k, request):
    timedif = time.time() - float((contactmap[k].split("+"))[2])
    if(timedif/3600 > 360):
        db.child(request.session['login']).child('contacted').child(k).remove(request.session['auth'])
    else:
        contacted.append(contactmap[k])
        contactHealth.append(0)
        if(db.child(k).child('sick').get(request.session['auth']).val().split('+')[0] == '1'):
            contactHealth[len(contactHealth) - 1] = 1
        if(db.child(k).child('positive').get(request.session['auth']).val().split('+')[0] == '1'):
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
                numUsers = db.child('numUsers').get().val()
                if(numUsers < 5000):
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
                        request.session['verified'] = 0
                        request.session['auth'] = auth.current_user['idToken']
                        db.child(auth.current_user['localId']).set(acct, request.session['auth'])
                        db.child('numUsers').set(numUsers + 1, request.session['auth'])
                        return resp
                    except:
                        context['alert'] = 'The email you entered has already been taken. Try again'
                else:
                    context['alert'] = 'Unfortunately, the service has reached its max limit of users. Check our Facebook page for updates'
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
            request.session['verified'] = int(auth.get_account_info(auth.current_user['idToken'])['users'][0]['emailVerified'] == True)
            request.session['auth'] = auth.current_user['idToken']
            if(request.session['verified'] == 0):
                auth.send_email_verification(auth.current_user['idToken'])
            return resp
        except Exception as e:
            context['alert'] = 'Email/password is incorrect! Try again'

    return render(request, 'sign-in.html', context)

def passwordReset(request):
    context = {'alert' : ''}
    if(request.method == 'POST'):
        try:
            auth.send_password_reset_email(request.POST['address'])
            context['alert'] = 'Your account has been identified. Please check your inbox for instructions on resetting your password'
        except:
            context['alert'] = 'Invalid email entered. Try again!'
    return render(request, 'password-reset.html', context)

def tracker(request):
    context = {'navVis' : True, 'auth' : True, 'login' : 1, 'alert' : ""}

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
        db.child('Active').child(request.session['login']).child('lat').set((math.pi * float(request.POST['lat']))/180, request.session['auth'])
        db.child('Active').child(request.session['login']).child('long').set((math.pi * float(request.POST['long']))/180, request.session['auth'])
        db.child('Active').child(request.session['login']).child('lastUp').set(time.time(), request.session['auth'])

        allActive = db.child('Active').get(request.session['auth']).val()
        for user in allActive:
            if(not(user == 'permkey' or user == request.session['login'] or user == 'numTracking')):

                if(time.time() - allActive[user]['lastUp'] > 10 and allActive[user]['lastUp'] != -1):
                    db.child('Active').child(user).remove(request.session['auth'])
                    numTracking = db.child('Active').child('numTracking').get(request.session['auth']).val()
                    db.child('Active').child('numTracking').set(numTracking - 1, request.session['auth'])
                    allActive = db.child('Active').get(request.session['auth']).val()
                    continue

                mylat = (float(request.POST['lat'])/180) * math.pi
                otherlat = float(allActive[user]['lat'])

                mylong = (float(request.POST['long'])/180) * math.pi
                otherlong = float(allActive[user]['long'])

                latDist = (abs(mylat - otherlat)) * 6378134

                factor = (math.cos(mylat) + math.cos(otherlat))/2
                longdist = min(abs(mylong-otherlong), (2*math.pi) - abs(mylong - otherlong)) * factor * 6378134

                dist = math.sqrt(math.pow(latDist, 2)  + math.pow(longdist, 2))

                if(dist < 50):
                    ignore = 0
                    contactmap = db.child(request.session['login']).child('contacted').get(request.session['auth']).val()
                    if(db.child(request.session['login']).child('sick').get(request.session['auth']).val().split('+')[0] == '1'):
                        ignore = 1
                    if(db.child(request.session['login']).child('positive').get(request.session['auth']).val().split('+')[0] == '1'):
                        ignore = 2

                    if(not(user in contactmap) or time.time() - float(contactmap[user].split("+")[2]) > 1800):
                        if(ignore == 1):
                            message = "Hello, this is a message from Safe from COVID. Our records indicate that you were just in close contact with a person claiming to be ill. Visit your profile at https://safefromcovid.herokuapp.com to learn more."
                            message += "\nInformation about contact:\nEmail of other user: " + db.child(request.session['login']).child('email').get(request.session['auth']).val() + "\nLocation of contact: " + 'https://www.google.com/maps/place/' + request.POST['lat'] + ',' +  request.POST['long']
                            email(message, db.child(user).child('email').get(request.session['auth']).val())
                        if(ignore == 2):
                            message = "Hello, this is a message from Safe from COVID. Our records indicate that you were just in close contact with a person claiming to be positive for COVID-19. Visit your profile at https://safefromcovid.herokuapp.com to learn more."
                            message += "\nInformation about contact:\nEmail of other user: " + db.child(request.session['login']).child('email').get(request.session['auth']).val() + "\nLocation of contact: " + 'https://www.google.com/maps/place/' +  request.POST['lat'] + ',' +  request.POST['long']
                            email(message, db.child(user).child('email').get(request.session['auth']).val())

                    contactmap[user] = str(mylat) + '+' + str(mylong) + '+' + str(time.time()) + '+' + str(ignore)
                    db.child(request.session['login']).child('contacted').set(contactmap, request.session['auth'])


        return HttpResponse()

def initiateTracker(request):
    chkLogin = getLoginInfo(request)
    if(chkLogin[1] == -1):
        return logout(request)
    numTracking = db.child('Active').child('numTracking').get(request.session['auth']).val()
    if(numTracking >= 75):
        return HttpResponse('excess_users')

    acct = db.child(request.session['login']).get(request.session['auth']).val()
    del acct['email']
    del acct['contacted']
    del acct['positive']
    del acct['sick']
    acct['lat'] = -1
    acct['long'] = -1
    acct['lastUp'] = -1
    db.child("Active").child(request.session['login']).set(acct, request.session['auth'])
    db.child('Active').child('numTracking').set(numTracking + 1, request.session['auth'])
    return HttpResponse('success')

def suspendTracker(request):
    chk = getLoginInfo(request)
    if(chk[0] == 1 and chk[1] == 1):
        if(request.session['login'] in db.child('Active').get(request.session['auth']).val()):
            db.child("Active").child(request.session['login']).remove(request.session['auth'])
            numTracking = db.child('Active').child('numTracking').get(request.session['auth']).val()
            db.child('Active').child('numTracking').set(numTracking - 1, request.session['auth'])
    return HttpResponse()


def email(message, to):
    send_mail('Important update from Safe from COVID', message, 'coronaaware@gmail.com', [to])

def getLoginInfo(request):
    res = [0, 0]
    if('login' in request.session):
        if(checkValidLogin(request.session['login'], request)):
            res[0] = 1
        else:
            return res
    else:
        return res

    if('verified' in request.session):
        res[1] = request.session['verified']
    else:
        #Verified session var expired but login still valid
        res[1] = -1

    return res


def checkValidLogin(token, request):
    try:
        if(db.child(token).get(request.session['auth']).val() == None):
            return False
    except:
        return False
    return True
