from flask import Flask, jsonify, request
from flask import current_app as LOG
from flask_cors import CORS

from src.movieServices import MovieServices
movieServices = MovieServices()

from src.seriesServices import SeriesServices
serieServices = SeriesServices()

app = Flask(__name__)
CORS(app)

folder = 'E:\MEDIA'

#Ruta de prueba
@app.route("/", methods=['GET'])
def test():
    return "<h1 style='color:blue'>Hello There!</h1>"

#Ruta para generar lista de peliculas
@app.route("/movies/generate", methods=['GET'])
def movies_generate():
    try:
        movieServices.getMoviesList(folder)

        return jsonify(success=True,  info='Lista de peliculas generada correctamente!')
    except Exception as e:
        LOG.logger.error(str(e))
        return jsonify(success=False,  info='Algo salio mal', exception=''+str(e))

#Ruta para obtener todas las peliculas
@app.route("/movies/get", methods=['GET'])
def movies_get():
    try:
        return movieServices.getMovies('full')
    except Exception as e:
        LOG.logger.error(str(e))
        return jsonify(success=False,  info='Algo salio mal', exception=''+str(e))

#Ruta para obtener peliculas aleatorias
@app.route("/movies/getCarousel", methods=['GET'])
def movies_get_car():
    try:
        return movieServices.getMovies('carousel')
    except Exception as e:
        LOG.logger.error(str(e))
        return jsonify(success=False,  info='Algo salio mal', exception=''+str(e))
    
#Ruta para buscar peliculas
@app.route("/movies/search", methods=['POST'])
def movies_search():
    try:
        datos = request.get_json()

        return movieServices.search(datos)
    except Exception as e:
        LOG.logger.error(str(e))
        return jsonify(success=False,  info='Algo salio mal', exception=''+str(e))
    
#Ruta para obtener los generos para pelicuals
@app.route("/movies/getGenres", methods=['GET'])
def movies_get_genres():
    try:
        return movieServices.getGenres()
    except Exception as e:
        LOG.logger.error(str(e))
        return jsonify(success=False,  info='Algo salio mal', exception=''+str(e))
    
#Ruta para obtener los directores de pelicuals
@app.route("/movies/getDirectors", methods=['GET'])
def movies_get_directors():
    try:
        return movieServices.getDirectors()
    except Exception as e:
        LOG.logger.error(str(e))
        return jsonify(success=False,  info='Algo salio mal', exception=''+str(e))



#Ruta para generar lista de series
@app.route("/series/generate", methods=['GET'])
def series_generate():
    try:
        serieServices.generateSeries(folder)

        return jsonify(success=True,  info='Lista de series generada correctamente!')
    except Exception as e:
        LOG.logger.error(str(e))
        return jsonify(success=False,  info='Algo salio mal', exception=''+str(e))

#Ruta para obtener todas las series
@app.route("/series/get", methods=['GET'])
def series_get():
    try:
        return serieServices.getSeries('full')
    except Exception as e:
        LOG.logger.error(str(e))
        return jsonify(success=False,  info='Algo salio mal', exception=''+str(e))

#Ruta para obtener series aleatorias
@app.route("/series/getCarousel", methods=['GET'])
def series_get_car():
    try:
        return serieServices.getSeries('carousel')
    except Exception as e:
        LOG.logger.error(str(e))
        return jsonify(success=False,  info='Algo salio mal', exception=''+str(e))
    
#Ruta para buscar series
@app.route("/series/search", methods=['POST'])
def series_search():
    try:
        datos = request.get_json()

        return serieServices.search(datos)
    except Exception as e:
        LOG.logger.error(str(e))
        return jsonify(success=False,  info='Algo salio mal', exception=''+str(e))
    
#Ruta para obtener los generos para series
@app.route("/series/getGenres", methods=['GET'])
def series_get_genres():
    try:
        return serieServices.getGenres()
    except Exception as e:
        LOG.logger.error(str(e))
        return jsonify(success=False,  info='Algo salio mal', exception=''+str(e))

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'POST')
    return response

#Definimos que el host sera "localhost"
if __name__ == "__main__":
    #app.run(host='0.0.0.0')
    app.run(host='0.0.0.0', debug=True)

