from flask import Flask, render_template
from flask_googlemaps import GoogleMaps, Map
from home import Home
from flask import request, redirect
from database import *
import googlemaps
from datetime import datetime

app = Flask(__name__)
api_key = ''
dados = DataBase()

with open('.env') as f:
    api_key = f.readline()
    api_key = api_key.rstrip('\n')
    f.close()

GoogleMaps(app, key = api_key)

def gen_markers(homes):
    keys = ['lat', 'lng', 'infobox', 'zIndex', 'icon']
    dft = [999, "http://maps.google.com/mapfiles/ms/icons/green-dot.png"]

    atts = []
    for i in range(0, len(homes)):
        atts.append(homes[i].get_atts() + dft)
    
    mmarkers = []
    for i in range(0, len(homes)):
        mmarkers.append(dict(zip(keys, atts[i])))
    
    return mmarkers

def gen_circles(raio):
     circle = {
        'stroke_color': '#FF0000',
        'stroke_opacity': .5,
        'stroke_weight': 10,
        # line(stroke) style
        'fill_color': '#FF0000',
        'fill_opacity': .2,
        # fill style
        'center': {  # set circle to user_location
            'lat':-22.978993,
            'lng':-43.232999
        },
        'radius': raio*100  # meters
     }

@app.route("/" ,  methods=['GET', 'POST'])
def mapview():
    if request.method == 'POST': ##filtra imoveis disponiveis
        valor = request.form['valor']
        raio = request.form['distancia']
        tipos = ["Apartamento", "República"]

        try:
            tipo_apartamento = request.form['apartamento']
        except:
            tipos.remove("Apartamento")
        try:
            tipo_republica = request.form['republica']
        except:
            tipos.remove("República")

        homes = dados.get_filtered_home_list(valor, raio, tipos)

        print(homes)
        rmarkers = gen_markers(homes)
        circle = gen_circles(raio)

        mymap = Map(
            identifier="sndmap",
            style=(
                "height:55%;"
                "width:50%;"
                "top:100px;"
                "left:550px;"
                "position:absolute;"
                "zIndex:999;"
            ),
            lat=-22.978993,
            lng= -43.232999,
            markers=rmarkers,
            zoom="16",
            circles=[circle,  [-22.978995,-43.232994, int(raio)*1000],
            (33.685, -116.251, 1500)],
        )

        return render_template('map.html', sndmap=mymap)

    else:
        homes = dados.get_homes_list()
        rmarkers = gen_markers(homes)

        mymap = Map(
            identifier="sndmap",
            style=(
                "height:75%;"
                "width:50%;"
                "top:100px;"
                "left:550px;"
                "position:absolute;"
                "zIndex:999;"
            ),
            lat=-22.978993,
            lng=-43.233160,
            markers = rmarkers,
            zoom="16"
        )
        return render_template('map.html', sndmap=mymap)

@app.route("/registrar", methods=['GET', 'POST'])
def regImoveis():
    if request.method == 'POST': ##registra novo ap
        nome = request.form['nome']
        cpf = request.form['cpf']
        tel = request.form['telefone']
        email = request.form['_email']
        vagas = int(request.form['vagas'])
        rua = request.form['rua']
        cep = request.form['cep']
        num = int(request.form['num'])
        apt = int(request.form['apt'])
        dscp = request.form['descricao']
        tipo = request.form['_type']
        valor = request.form['valor']

        gmaps = googlemaps.Client(key=api_key)
        try:
            geocode_result = gmaps.geocode(str(num) + ' ' + rua + ', Rio de Janeiro, ' + 'RJ')
            lat = float(geocode_result[0]['geometry']['location']['lat'])
            lng = float(geocode_result[0]['geometry']['location']['lng'])
        except:
            print("Unable to get latitude and longitude from address")
            raise (ValueError)

        h = Home(lat, lng, tipo, vagas, dscp, nome, cpf, tel, cep, rua, tipo, num, valor, apt)
        dados.insert_data(h)
        return redirect(request.url)

    else:
        return render_template('regImovel.html')

7
if __name__ == "__main__":
    app.run(debug=False )

