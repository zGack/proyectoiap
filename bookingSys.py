from flask import Flask, request, g, redirect, url_for, render_template, flash, session, abort
import flask
import sys
from flask import json

#VARIABLES DE INICIALIZACION
app = Flask(__name__)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)
app.secret_key = 'random string'
pags = ''#Variable para redireccionar a una pagina
datos = []#Diccionario que almacena la informacion del usuario que inicia sesion
flights2 = []#Diccionario temporal que almacena los vuelos disponbles
errorsF = ''#Variable que almacena el tipo de error a la hora de buscar vuelos
bdata_temp = {'ocity':'','dcity':'','date':''}#Diccionario que almacena temporalmente las opciones de busqueda de una vuelo 
flights_history = []#Diccionario que almacena las reservas que ha hecho un usuario
flights_history2 = []#Diccionario que almacena las reservas (abreviaando las ciudades) que ha hecho un usuario
edit_pref = []#Diccionario que almacena las preferencias de un vuelo para posteriormente editarla

#========================================#
#                                        #
#========================================#

def searchUser(name, file, user):
    #Algoritmo para extraer informacion del usuario solicitado en la base de datos
    for line in file:        
        for part in line.split():            
            if (name == part):                
                user.append(line)

    if(user == []):
        return False
    else:
        return user

#Funcion para iniciar sesion
def loginProcess():
    db = open('db/users.txt', 'r+')
    user = []

    #Compruebo que exista el usuario
    if(searchUser(request.form['username'], db, user) == False):
        return False
    else:
        x = searchUser(request.form['username'], db, user)
        y = x[0]

        #Comprueba si la contraseña coincide
        for tag in y.split():
            if(tag == request.form['password']):
                db.close()
                return True      

        return False

#Funcion para registrar un usuario
def regisUser():
    db = open('db/users.txt', 'r+')
    user = []
    
    #Compruebo que no exista un usuario con el mismo nombre o email
    if(searchUser(request.form["username"],db,user) == False or
       searchUser(request.form["email"],db,user) == False):
        db.close()
        #Compruebo que las contraseñas coincidan
        if(request.form["passw"] == request.form["cpassw"]):
            db = open('db/users.txt', 'r+')
            x = searchUser('id',db,user)
            y = x[0].split()
            nid = int(y[8]) + 1
            db.seek(45)#remplazo el numero total de usuarios en la bd
            db.write(str(nid))
            db.close()

            #Compruebo si el que se va a registrar tiene segundo nombre
            mname = ''
            if(request.form["mname"] == ''):
                mname = 'none'
            else:
                mname = request.form["mname"]

            db = open('db/users.txt', 'a+')
            temp = [nid,request.form["name"],mname,request.form["lname"],request.form["slname"],
                    request.form["username"],request.form["email"],request.form["passw"]]

            #Escribo el usuario a registrar en la bd
            db.write('\n')            
            for tag in temp:
                db.write(str(tag))
                db.write(' ')
            db.close()

            airlines = {'Delta Airlines':'delta','American Airlines':'american',
                        'US Airways':'us','Copa Airlines':'copa','Tradewind Aviation':'trade',
                        'Wright Air':'wright','Travel Air':'travel','Hawaiian Airlines':'hawai',
                        'Norwegian':'norwe','United Airlines':'united','Pacific Airways':'pacific',
                        'Qatar Airways':'qatar','West Je':'west','KLM Airlines':'klm',
                        'Air France':'france','40-Mile Air':'40-mil','Mokulele Airlines':'moku',
                        'Al+aska Seaplane':'alaska','Frontier Airlines':'front','none':'none'}
                        

            #Compruebo si el usuario ingreso mas de una aereolinea preferida
            apref = ''
            if(request.form["apref"] in airlines):
                    apref = airlines[request.form["apref"]]

            anpref = ''
            if(request.form["anpref"] in airlines):
                    anpref = airlines[request.form["anpref"]]

            apref2 = ''
            if(request.form["apref2"] == ''):
                apref2 = 'none'
            else:
                if(request.form["apref2"] in airlines):
                    apref2 = airlines[request.form["apref2"]]

            anpref2 = ''
            if(request.form["anpref2"] == ''):
                anpref2 = 'none'
            else:
                if(request.form["anpref2"] in airlines):
                    anpref2 = airlines[request.form["anpref2"]]

            db2 = open('db/airlines_pref.txt', 'a+')
            temp2 = [nid,apref,apref2,anpref,anpref2]

            #Escribo las preferencias del usuario en la bd
            db2.write('\n')            
            for tag in temp2:
                db2.write(str(tag))
                db2.write(' ')
            db2.close()

            return True
        else:
            return False
    else:
        return False

#Funcion que retorna los datos de un usuario
def getUserData(name):
    db = open('db/users.txt', 'r+')
    db2 = open('db/airlines_pref.txt', 'r+')
    user = []
    user_airlines = []
    x = searchUser(request.form['username'], db, user)
    y = x[0].split()
    z = searchUser(y[0],db2,user_airlines)
    a = z[0].split()
    datos_user = [{'id':0,'name':'','mname':'','lname':'','slname':'',
                   'user':'','email':'','apref':'','anpref':'',
                   'apref2':'','anpref2':''}] 

    airlines = {'delta':'Delta Airlines','american':'American Airlines',
                'us':'US Airways','copa':'Copa Airlines','wright':'Wright Air',
                'trade':'Tradewind Aviation','travel':'Travel Air','norwe':'Norwegian',
                'united':'United Airlines','pacific':'Pacific Airways','qatar':'Qatar Airways',
                'west':'West Jet','klm':'KLM Airlines','france':'Air France','40-mil':'40-Mile Air',
                'moku':'Mokulele Airlines','alaska':'Alaska Seaplane','front':'Frontier Airlines',
                'hawai':'Hawaiian Airlines','none':'none'}

    datos_user[0]['id'] = y[0]                
    datos_user[0]['name'] = y[1]
    datos_user[0]['mname'] = y[2]
    datos_user[0]['lname'] = y[3]
    datos_user[0]['slname'] = y[4]
    datos_user[0]['user'] = y[5]
    datos_user[0]['email'] = y[6]
    
    #Compruebo cuales son las aereolineas de preferencia del usuarios 
    datos_user[0]['apref'] = airlines[a[1]]

    datos_user[0]['apref2'] = airlines[a[2]]

    if(a[2] in airlines):
        datos_user[0]['anpref'] = airlines[a[2]]

    if(a[3] in airlines):
        datos_user[0]['anpref2'] = airlines[a[3]]

    db.close()
    db2.close()
    return datos_user

#Algoritmo para organizar las horas de los vuelos
def join_hour(hour_old):
    lt = ''
    rt = ''

    i = 0
    j = 2
    while(i < 2):
        lt += hour_old[i]
        rt += hour_old[j]
        i += 1
        j += 1

    hour = lt+':'+rt
    return hour.strip()

#Funcion que retorna lo vuelos disponibles con determinadas caracteristicas
def searchFlights(ocity,dcity,use_pref,no_stops,merd):
    global flights2, datos

    cities = {'Albuquerque, New Mexico':'ABQ','Atlanta, Georgia':'ATL','Nashville, Tennessee':'BNA',
              'Boston, Massachusetts':'BOS','Washington D.C.':'DCA','Denver, Colorado':'DEN','Dallas, Texas':'DFW',
              'Detroit, Michigan':'DTW','Houston, Texas':'HOU','New York':'JFK','Los Angeles, California':'LAX',
              'Miami, Florida':'MIA','Minneapolis, Minnesota':'MSP','New Orleans, Louisiana':'MSY',
              'Chicago, Illinois':'ORD','Providence/Newport, Rhode Island':'PVD','Philadelphia, Pennsilvania':'PHL',
              'Phoenix, Arizona':'PHX','Raleigh/Durham, North Carolina':'RDU','Seattle/Tacoma, Washington':'SEA',
              'San Francisco, California':'SFO','St Louis, Missouri':'STL','Tampa, Florida':'TPA'}

    airlines = {'DL':'Delta Airlines','AA':'American Airlines',
                'US':'US Airways','CO':'Copa Airlines','WN':'Wright Air',
                'TW':'Tradewind Aviation','YV':'Travel Air','HP':'Hawaiian Airlines',
                'NW':'Norwegian','UA':'United Airlines','PA':'Pacific Airways','QF':'Qatar Airways',
                'YX':'West Jet','ZK':'KLM Airlines','AD':'Air France','4X':'40-Mile Air',
                'MG':'Mokulele Airlines','AS':'Alaska Seaplane','FF':'Frontier Airlines'}

    airlines2 = {'Delta Airlines':'DL','American Airlines':'AA',
                'US Airways':'US','Copa Airlines':'CO','Wright Air':'WN',
                'Tradewind Aviation':'TW','Travel Air':'YV','Hawaiian Airlines':'HP',
                'Norwegian':'NW','United Airlines':'UA','Pacific Airways':'PA','Qatar Airways':'QF',
                'West Jet':'YX','KLM Airlines':'ZK','Air France':'AD','40-Mile Air':'4X',
                'Mokulele Airlines':'MG','Alaska Seaplane':'AS','Frontier Airlines':'FF'}

    mer_time = {'A':'AM','P':'PM','N':'PM'}


    o_city = ''
    d_city = ''
    o_city = cities[ocity]
    d_city= cities[dcity]

    data = open('db/flights_db.txt', 'r+')
    db = data.readlines()[59:]
    flights = []
    flights2 = []

    #Buscar vuelos sin preferencias de aereolineas
    if (use_pref == '' and no_stops == ''):
        for line in db:
            if (line[8:11] == o_city and line[19:22] == d_city and line[16] == merd):
                flights += {line[0:44]}

        for i in range(0, len(flights)):
            flights2 += [{'aereolinea':airlines[flights[i][0:2]],
                          'vuelo':flights[i][2:6].replace(' ',''),
                          'ori_city':flights[i][8:11],
                          'dep_time':join_hour(flights[i][12:16]),
                          'dmer_time':mer_time[flights[i][16]],
                          'des_city':flights[i][19:22],
                          'arr_time':join_hour(flights[i][23:27]),
                          'amer_time':mer_time[flights[i][27]],
                          'n_stops':flights[i][36],
                          'aircraft':flights[i][41:44]}]

    #Buscar vuelos directos sin preferencias de aereolineas
    elif(use_pref == '' and no_stops != ''):
        for line in db:
            if (line[8:11] == o_city and line[19:22] == d_city and line[16] == merd and
                line[36] == '0'):
                flights += {line[0:44]}

        for i in range(0, len(flights)):
            flights2 += [{'aereolinea':airlines[flights[i][0:2]],
                          'vuelo':flights[i][2:6].replace(' ',''),
                          'ori_city':flights[i][8:11],
                          'dep_time':join_hour(flights[i][12:16]),
                          'dmer_time':mer_time[flights[i][16]],
                          'des_city':flights[i][19:22],
                          'arr_time':join_hour(flights[i][23:27]),
                          'amer_time':mer_time[flights[i][27]],
                          'n_stops':flights[i][36],
                          'aircraft':flights[i][41:44]}]

    
    #Buscar  con preferencias de aereolineas
    elif(use_pref != '' and no_stops == ''):
        apref = airlines2[datos[0]['apref']]
        anpref = airlines2[datos[0]['anpref']]
        apref2 = ''
        anpref2 = ''

        if (datos[0]['apref2'] != 'none'):
            apref2 = airlines2[datos[0]['apref2']]

        if (datos[0]['anpref2'] != 'none'):
            anpref2 = airlines2[datos[0]['anpref2']]

        for line in db:

            if ((line[0:2] == apref and line[0:2] != anpref) and line[8:11] == o_city and line[19:22] == d_city):
                flights += {line[0:44]}

        for i in range(0, len(flights)):
            flights2 += [{'aereolinea':airlines[flights[i][0:2]],
                          'vuelo':flights[i][2:6].replace(' ',''),
                          'ori_city':flights[i][8:11],
                          'dep_time':join_hour(flights[i][12:16]),
                          'dmer_time':mer_time[flights[i][16]],
                          'des_city':flights[i][19:22],
                          'arr_time':join_hour(flights[i][23:27]),
                          'amer_time':mer_time[flights[i][27]],
                          'n_stops':flights[i][36],
                          'aircraft':flights[i][41:44]}]

    #Buscar vuelos directos con preferencias de aereolineas
    elif(use_pref != '' and no_stops != ''):
        apref = airlines2[datos[0]['apref']]
        anpref = airlines2[datos[0]['anpref']]
        apref2 = ''
        anpref2 = ''

        if (datos[0]['apref2'] != 'none'):
            apref2 = airlines2[datos[0]['apref2']]

        if (datos[0]['anpref2'] != 'none'):
            anpref2 = airlines2[datos[0]['anpref2']]

        for line in db:

            if ((line[0:2] == apref and line[0:2] != anpref) and line[8:11] == o_city and line[19:22] == d_city):
                flights += {line[0:44]}

        for i in range(0, len(flights)):
            flights2 += [{'aereolinea':airlines[flights[i][0:2]],
                          'vuelo':flights[i][2:6].replace(' ',''),
                          'ori_city':flights[i][8:11],
                          'dep_time':join_hour(flights[i][12:16]),
                          'dmer_time':mer_time[flights[i][16]],
                          'des_city':flights[i][19:22],
                          'arr_time':join_hour(flights[i][23:27]),
                          'amer_time':mer_time[flights[i][27]],
                          'n_stops':flights[i][36],
                          'aircraft':flights[i][41:44]}]
             

    #Si no hay vuelos retorno false
    data.close()
    if(flights2 != []):
        return flights2
    else:
        return False

#Funcion para obtener las reservas que ha hecho un usuario con las ciudades abreviadas
def flight_history():
    global datos,flights_history
    vuelo = []
    flights = []
    db = open('db/flights_users.txt','r+')
    airlines = {'DL':'Delta Airlines','AA':'American Airlines',
                'US':'US Airways','CO':'Copa Airlines','WN':'Wright Air',
                'TW':'Tradewind Aviation','YV':'Travel Air','HP':'Hawaiian Airlines',
                'NW':'Norwegian','UA':'United Airlines','PA':'Pacific Airways','QF':'Qatar Airways',
                'YX':'West Jet','ZK':'KLM Airlines','AD':'Air France','4X':'40-Mile Air',
                'MG':'Mokulele Airlines','AS':'Alaska Seaplane','FF':'Frontier Airlines'}
    
    vuelos = searchUser(datos[0]['id'],db,vuelo)

    if(vuelos != False):
        for line in vuelos:
            flights += {line[2:]}

        for i in range(0, len(flights)):
            flights_history += [{'aereolinea':airlines[flights[i].split()[0]],
                                 'vuelo':flights[i].split()[1],
                                 'ori_city':flights[i].split()[2],
                                 'dep_time':flights[i].split()[3],
                                 'dmer_time':flights[i].split()[4],
                                 'des_city':flights[i].split()[5],
                                 'arr_time':flights[i].split()[6],
                                 'amer_time':flights[i].split()[7],
                                 'n_stops':flights[i].split()[8],
                                 'aircraft':flights[i].split()[9],
                                 'date':flights[i].split()[10]}]

        db.close()                         
        return flights_history

    else:
        db.close()
        return False

#Funcion para obtener las reservas que ha hecho un usuario
def flight_history2():
    global datos,flights_history2
    vuelo = []
    flights = []
    db = open('db/flights_users.txt','r+')
    airlines = {'DL':'Delta Airlines','AA':'American Airlines',
                'US':'US Airways','CO':'Copa Airlines','WN':'Wright Air',
                'TW':'Tradewind Aviation','YV':'Travel Air','HP':'Hawaiian Airlines',
                'NW':'Norwegian','UA':'United Airlines','PA':'Pacific Airways','QF':'Qatar Airways',
                'YX':'West Jet','ZK':'KLM Airlines','AD':'Air France','4X':'40-Mile Air',
                'MG':'Mokulele Airlines','AS':'Alaska Seaplane','FF':'Frontier Airlines'}           
    cities2 = {'ABQ':'Albuquerque, New Mexico','ATL':'Atlanta, Georgia','BNA':'Nashville, Tennessee',
               'BOS':'Boston, Massachusetts','DCA':'Washington D.C.','DEN':'Denver, Colorado','DFW':'Dallas, Texas',
               'DTW':'Detroit, Michigan','HOU':'Houston, Texas','JFK':'New York','LAX':'Los Angeles, California',
               'MIA':'Miami, Florida','MSP':'Minneapolis, Minnesota','MSY':'New Orleans, Louisiana',
               'ORD':'Chicago, Illinois','PVD':'Providence, Rhode Island','PHL':'Philadelphia, Pennsilvania',
               'PHX':'Phoenix, Arizona','RDU':'Raleigh, North Carolina','SEA':'Seattle, Washington',
               'SFO':'San Francisco, California','STL':'St Louis, Missouri','TPA':'Tampa, Florida'}           

    vuelos = searchUser(datos[0]['id'],db,vuelo)
    print(vuelos)
    #if ((vuelos[len(vuelos)-1]) == (vuelos[len(vuelos)-2])):
    #    vuelos.pop()
    #print(vuelos)

    #for i in vuelos:
    #    print(i)
    #    for j in vuelos:
    #        if (i == j):
    #            vuelos.remove(j)

    if(vuelos != False):
        for line in vuelos:
            flights += {line[2:]}

        for i in range(0, len(flights)):
            flights_history2 += [{'aereolinea':airlines[flights[i].split()[0]],
                                 'vuelo':flights[i].split()[1],
                                 'ori_city':cities2[flights[i].split()[2]],
                                 'dep_time':flights[i].split()[3],
                                 'dmer_time':flights[i].split()[4],
                                 'des_city':cities2[flights[i].split()[5]],
                                 'arr_time':flights[i].split()[6],
                                 'amer_time':flights[i].split()[7],
                                 'n_stops':flights[i].split()[8],
                                 'aircraft':flights[i].split()[9],
                                 'date':flights[i].split()[10]}]

        db.close()                         
        return flights_history2

    else:
        db.close()
        return False

    

#========================================#
#                                        #
#========================================#

@app.route('/', methods=['GET', 'POST'])
def index():
    global pags,datos,errorsF,flights_history,flights_history2,edit_pref

    if(not session.get('logged_in')):
        return render_template('login.html')
    else:
        if (request.method == 'POST' and pags == 'main' or pags == 'his'):
            if datos == []:
                datos = getUserData(request.form['username']) 

            if flights_history == []: 
                flights_history = flight_history()

            if flights_history2 == []: 
                flights_history2 = flight_history2()

            return render_template('index.html', datos=datos, pags=pags, history=flights_history,
                                                 history2=flights_history2)
   
        if(flights2 != []):
            return render_template('index.html', datos=datos ,pags=pags, errors=errorsF, 
                                                 vuelos=flights2, data_temp=bdata_temp,
                                                 history=flights_history,history2=flights_history2)

        if(edit_pref != []):
            return render_template('index.html', datos=datos ,pags=pags, errors=errorsF, 
                                                 vuelos=flights2, data_temp=bdata_temp,
                                                 history=flights_history,history2=flights_history2,
                                                 edits=edit_pref)

        return render_template('index.html', datos=datos ,pags=pags, errors=errorsF,
                                             data_temp=bdata_temp,history=flights_history,
                                             history2=flights_history2)

@app.route('/login', methods=['GET','POST'])
def login():
    global pags

    if (request.method == 'POST'):
        if (loginProcess() == True):
            session['logged_in'] = True
            pags = 'main'
            return index()
        else:
            errors = 'Usuario y/o contraseña invalidos'        
            return render_template('login.html', errors=errors)


    return index()

@app.route('/logout', methods=['GET','POST'])
def logout():
    global datos,data_temp,flights_history,flights_history2
    datos = []
    bdata_temp = {'ocity':'','dcity':'','date':''}
    flights_history = []
    flights_history2 = []
    print(flights_history2)
    print(flights_history)
    session['logged_in'] = False
    return index()

@app.route('/register', methods=['GET','POST'])
def register():
    return render_template('register.html')

@app.route('/signup', methods=['GET','POST'])
def signup():
    global pags
    errors = ''
    errors2 = ''
    if request.method == 'POST':
        if (request.form['btn'] == 'Volver'):
            return render_template('login.html')
        else:
            if(regisUser() == True):
                session['logged_in'] = True
                pags = 'main'
                return index()
            else:
                error = regisUser()
                if (error == 'Usuario y/o contraseña invalidos'):
                    errors = regisUser()
                    return render_template('register.html', errors=errors)
                else:
                    errors2 = regisUser()
                    return render_template('register.html', errors2=errors2)

    return redirect(url_for('login'))

@app.route('/index', methods=['GET', 'POST'])
def index2():
    global pags, data_temp
    bdata_temp['ocity'] = ''
    bdata_temp['dcity'] = ''
    bdata_temp['date'] = ''
    pags = 'main'
    return index()

@app.route('/book', methods=['GET','POST'])
def book():
    global pags,errorsF,flights2
    pags = 'book'
    errorsF = ''
    flights2 = ''
    return index()

@app.route('/flight-book', methods=['GET','POST'])
def flight_book():
    global pags,errorsF,data_temp,flights_history,flights_history2
    ocity = ''
    dcity = ''
    use_pref = ''
    no_stops = ''
    errorsF = ''
    flights_history = []
    flights_history2 = []

    if (request.method == 'POST'):

        if(request.form['btn'] == 'Buscar Vuelos'):
            pags = ''
            ocity = request.form['ocity']
            dcity = request.form['dcity']
            merd = request.form['hour']
            bdata_temp['ocity'] = request.form['ocity']
            bdata_temp['dcity'] = request.form['dcity']
            bdata_temp['date'] = request.form['date']


            if request.form.get('use_pref'):
                use_pref = request.form['use_pref']

            if request.form.get('no_stops'):
                no_stops = request.form['no_stops']

            #print(searchFlights(ocity,dcity,use_pref,no_stops,merd))
            #print(len(searchFlights(ocity,dcity,use_pref,no_stops,merd)))

            if (searchFlights(ocity,dcity,use_pref,no_stops,merd) != False):
                pags = 'book'
                return index()
            elif(searchFlights(ocity,dcity,use_pref,no_stops,merd) == False):
                errorsF = 'Lo sentimos, en estos momentos no hay vuelos disponibles para ese destino'
                bdata_temp['ocity'] = ''
                bdata_temp['dcity'] = ''
                bdata_temp['date'] = ''
                pags = 'book'
                return index()
        
    return index()

@app.route('/reservar', methods=['GET','POST'])
def reservar():
    global pags,flights2,bdata_temp

    if (flights2 != []):
        id_book = request.form['id_book']
        bdata_temp['ocity'] = ''
        bdata_temp['dcity'] = ''
        bdata_temp['date'] = ''
        book = ''

        for flight in flights2:
            if(flight['vuelo'] == id_book):
                book = flight

        airlines2 = {'Delta Airlines':'DL','American Airlines':'AA',
                    'US Airways':'US','Copa Airlines':'CO','Wright Air':'WN',
                    'Tradewind Aviation':'TW','Travel Air':'YV','Hawaiian Airlines':'HP',
                    'Norwegian':'NW','United Airlines':'UA','Pacific Airways':'PA','Qatar Airways':'QF',
                    'West Jet':'YX','KLM Airlines':'ZK','Air France':'AD','40-Mile Air':'4X',
                    'Mokulele Airlines':'MG','Alaska Seaplane':'AS','Frontier Airlines':'FF'}
        
        #Almaceno los datos de la reserva en una lista temporal para despues escribirlos en la bd 
        db = open('db/flights_users.txt','a+')
        temp = [datos[0]['id'],airlines2[book['aereolinea']],book['vuelo'],book['ori_city'],
                book['dep_time'],book['dmer_time'],book['des_city'],
                book['arr_time'],book['amer_time'],book['n_stops'],
                book['aircraft'],request.form['date']]

        print(datos)

        db.write('\n')
        for tag in temp:
            db.write(str(tag))
            db.write(' ')
        db.close()

        pags = 'main'
        return index()
    else:
        session['logged_in'] = False
        return index()

@app.route('/history', methods=['GET','POST'])
def history():
    global pags
    pags = 'his'
    return index()

@app.route('/pref', methods=['GET','POST'])
def pref():
    global pags
    pags = 'pref'
    return index()

@app.route('/edit', methods=['GET','POST'])
def edit():
    global pags,edit_pref,datos
    temp_pref1 = ''
    temp_pref2 = ''

    if (request.method == 'POST' ):

        if datos[0]['apref2'] != 'none':
            temp_pref1 = datos[0]['apref2']

        if datos[0]['anpref2'] != 'none':  
            temp_pref2 = datos[0]['anpref2']

        edit_pref = [{'apref':datos[0]['apref'],'anpref':datos[0]['anpref'],
                      'apref2':temp_pref1,'anpref2':temp_pref2}]

        print(edit_pref)
        pags = 'pref'
        return index()

if(__name__) == '__main__':
    app.run(debug = True)


