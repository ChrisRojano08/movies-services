from flask import jsonify
from flask import current_app as LOG
import os
from os import walk
import json
import requests
from xml.dom import NotFoundErr
import random
import math

class MovieServices:
    def getGenre(idS, genres):
        for item in genres:
            id, name = item.items()
            if id[1] == idS:
                return name[1]
        return ''

    def getMoviesList(self, folder):
        moviesFolder = os.path.join(folder, 'PELICULAS')

        with open('src/files/movies.json', encoding='utf-8') as json_file:
            prevDict = json.load(json_file)
        with open('src/files/moviesGenres.json', encoding='utf-8') as json_file:
            genresF = json.load(json_file)['genres']

        directorsList = open('src/files/directors.txt', encoding='utf-8').read().split('\n')
        fDir = open('src/files/directors.txt', "a", encoding='utf-8')

        newDict = {}
        w = walk(moviesFolder)
        for (dirpath, dirnames, filenames) in w:
            if 'u' in dirpath and '0pendientes0' not in dirpath:
                for file in filenames:
                    movieName, movieExt = os.path.splitext(file)
                    if movieName not in prevDict:
                        urlU = "https://api.themoviedb.org/3/search/movie?query="+movieName+"&language=es-MX"
                        headE = {"accept": "application/json", "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI3MmNjOGE2Yzk4OGVlMDQ5NWU3Yjg4NjU2NzIwM2VhYSIsInN1YiI6IjY0YzU5ZDEzY2FkYjZiMDE0NDBkNzQ0NiIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.xp2Ig-6CfKDLIKx7PgI8xw3BbYe2t30ENEyw4yVqd7Q"}
                            
                        r = requests.get(urlU, headers=headE)
                        response = r.json()
                            
                        if len(response['results'])>0:
                            res = response['results'][0]
                            urlImg = 'https://image.tmdb.org/t/p/w500'

                            urlCred = "https://api.themoviedb.org/3/movie/"+str(res['id'])+"/credits?language=es-MX"
                            rCred = requests.get(urlCred, headers=headE)
                            responseCred = rCred.json()

                            director = ''
                            for crewmate in responseCred['crew']:
                                if crewmate['job'] == 'Director':
                                    director = crewmate['name']

                            if director != '' and director not in directorsList:
                                fDir.write(director)
                                fDir.write('\n')

                                directorsList.append(director)
                            
                            genres = []
                            for genreD in res['genre_ids']:
                                genres.append(MovieServices.getGenre(genreD, genresF))

                            banner = ''
                            if res['backdrop_path']:
                                banner = urlImg+res['backdrop_path']

                            poster = ''
                            if res['poster_path']:
                                poster = urlImg+res['poster_path']
                            
                            axMovie = {
                                'id': res['id'],
                                'banner': banner,
                                'poster': poster,
                                'title': res['title'],
                                'original_title': res['original_title'],
                                'genres': genres,
                                'path': os.path.join(dirpath, file),
                                'description': res['overview'],
                                'director': director,
                                'founded': True
                            }
                        
                        else:
                            axMovie = {
                                'id': '',
                                'banner': '',
                                'poster': '',
                                'title': '',
                                'original_title': '',
                                'genres': '',
                                'path': os.path.join(dirpath, file),
                                'description': '',
                                'director': '',
                                'founded': False
                            }
                        
                        newDict[movieName] = axMovie
        fDir.close()
        
        if len(newDict) > 0:
            if len(prevDict)>0:
                idx = newDict.copy()
                for key, value in prevDict.items():
                    idx[key] = value

                newDict = idx
            with open("src/files/movies.json", "w", encoding="utf-8") as outfile:
                outfile.write( json.dumps(newDict, ensure_ascii=False) )

    def getMovies(self, mode):
        pathFile = "src/files/movies.json"

        try:
            if os.path.exists(pathFile):
                with open(pathFile, encoding="utf8") as f:
                    data = json.load(f)

                moviesS = []
                for key, value in data.items():
                    value['filename'] = key
                    moviesS.append(value)

                
                if mode=="carousel":
                    moviesS = [x for x in moviesS if x['founded']]

                    k = len(moviesS) * 10 // 100
                    indicies = random.sample(range(len(moviesS)), k)
                    moviesS = [moviesS[i] for i in indicies]

                res = {
                        "status": 'Ok',
                        "message": 'Se obtuvo el diccionario con exito!',
                        "data": moviesS,
                        "success": True
                    }

                return jsonify(res)
            else:
                raise NotFoundErr('No se encontró el diccionario! Asegurese de haberlo creado antes')
        except Exception as e:
            LOG.logger.error("Error al obtener la informacion\nVerifique su archivo!")
            return jsonify(status='Error', exception=''+str(e))
        
    def search(self, dataBd):
        pathFile = "src/files/movies.json"

        try:
            if os.path.exists(pathFile):
                with open(pathFile, encoding="utf8") as f:
                    data = json.load(f)

                moviesS = []
                for key, value in data.items():
                    if (dataBd['query'].lower() in value['title'].lower() and dataBd['mode'] == 'search') or (dataBd['query'].lower() in key.lower() and dataBd['mode'] == 'all'):
                        if dataBd['director'] in value['director']:
                            if all(item in value['genres'] for item in dataBd['genre']) or dataBd['genre']==[]:
                                value['filename'] = key
                                moviesS.append(value)

                if dataBd['mode'] == 'search':
                    moviesS = [x for x in moviesS if x['founded']]
                
                moviesFounded=[]
                if len(moviesS) > 0:
                    chunks = [moviesS[i:i + dataBd['limit']] for i in range(0, len(moviesS), dataBd['limit'])]
                    moviesFounded = chunks[dataBd['page']-1]

                res = {
                        "status": 'Ok',
                        "message": 'Se obtuvieron las peliculas con exito!',
                        "data": moviesFounded,
                        "total": len(moviesS),
                        "pages": math.ceil(len(moviesS)/dataBd['limit']),
                        "success": True
                    }

                return jsonify(res)
            else:
                raise NotFoundErr('No se encontró el diccionario! Asegurese de haberlo creado antes')
        except Exception as e:
            LOG.logger.error("Error al obtener la informacion\nVerifique su archivo!")
            return jsonify(status='Error', exception=''+str(e))
        
    def getGenres(self):
        pathFile = "src/files/moviesGenres.json"

        try:
            if os.path.exists(pathFile):
                with open(pathFile, encoding="utf8") as f:
                    data = json.load(f)['genres']
                
                res = {
                        "status": 'Ok',
                        "message": 'Se obtuvieron las categorias con exito!',
                        "data": data,
                        "total": len(data),
                        "success": True
                    }

                return jsonify(res)
            else:
                raise NotFoundErr('No se encontró el diccionario! Asegurese de haberlo creado antes')
        except Exception as e:
            LOG.logger.error("Error al obtener la informacion\nVerifique su archivo!")
            return jsonify(status='Error', exception=''+str(e))

    def getDirectors(self):
        pathFile = "src/files/directors.txt"

        try:
            if os.path.exists(pathFile):
                file = open(pathFile, encoding='utf-8').read().split('\n')
                directors = [x for x in file if x != '']
                
                res = {
                        "status": 'Ok',
                        "message": 'Se obtuvieron los directores con exito!',
                        "data": directors,
                        "total": len(directors),
                        "success": True
                    }

                return jsonify(res)
            else:
                raise NotFoundErr('No se encontró el diccionario! Asegurese de haberlo creado antes')
        except Exception as e:
            LOG.logger.error("Error al obtener la informacion\nVerifique su archivo!")
            return jsonify(status='Error', exception=''+str(e))
