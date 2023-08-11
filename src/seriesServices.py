from flask import jsonify
from flask import current_app as LOG
import os
from os import walk
import json
import requests
from xml.dom import NotFoundErr
import random
import math

class SeriesServices():
    def getGenre(idS, genres):
        for item in genres:
            id, name = item.items()
            if id[1] == idS:
                return name[1]
        return ''
    
    def getEpisodes(filenames, dirpath):
        filesSeason = []
        for episode in filenames:
            episodeName, _ = os.path.splitext(episode)

            episodeAx = {
                'name': episodeName,
                'path': os.path.join(dirpath, episode)
            }

            filesSeason.append(episodeAx)

        return filesSeason
    
    def generateSeries(self, folder):
        moviesFolder = os.path.join(folder, 'SERIES')

        with open('src/files/series.json', encoding='utf-8') as json_file:
            prevDict = json.load(json_file)
        with open('src/files/tvGenres.json', encoding='utf-8') as json_file:
            genresF = json.load(json_file)['genres']

        newDict = {}
        w = walk(moviesFolder)
        for (dirpath, dirnames, filenames) in w:
            if 'h' in dirpath:
                if 'Temporada' in dirpath:
                    path = dirpath.split('\\')
                    serieName = path[len(path)-2]
                    seasonName = path[len(path)-1]

                    if serieName not in prevDict and serieName not in newDict:
                        url = "https://api.themoviedb.org/3/search/tv?query="+serieName+"&include_adult=false&language=es-MX&page=1"
                        headE = {"accept": "application/json", "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI3MmNjOGE2Yzk4OGVlMDQ5NWU3Yjg4NjU2NzIwM2VhYSIsInN1YiI6IjY0YzU5ZDEzY2FkYjZiMDE0NDBkNzQ0NiIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.xp2Ig-6CfKDLIKx7PgI8xw3BbYe2t30ENEyw4yVqd7Q"}
                            
                        r = requests.get(url, headers=headE)
                        response = r.json()

                        if len(response['results'])>0:
                            res = response['results'][0]
                            urlImg = 'https://image.tmdb.org/t/p/w500'

                            genres = []
                            for genreD in res['genre_ids']:
                                genres.append(SeriesServices.getGenre(genreD, genresF))

                            banner = ''
                            if res['backdrop_path']:
                                banner = urlImg+res['backdrop_path']

                            poster = ''
                            if res['poster_path']:
                                poster = urlImg+res['poster_path']
                        
                            axSerie = {
                                'id': res['id'],
                                'banner': banner,
                                'poster': poster,
                                'title': res['name'],
                                'original_title': res['original_name'],
                                'genres': genres,
                                'seasons': {},
                                'path': dirpath.replace(seasonName, ''),
                                'description': res['overview'],
                                'founded': True
                            }

                        else:
                            axSerie = {
                                'id': '',
                                'banner': '',
                                'poster': '',
                                'title': '',
                                'original_title': '',
                                'genres': '',
                                'seasons': {},
                                'path': dirpath.replace(seasonName, ''),
                                'description': '',
                                'founded': False
                            }

                        axSerie['seasons'][seasonName] = SeriesServices.getEpisodes(filenames, dirpath)
                        
                        newDict[serieName] = axSerie
                    else:
                        if serieName in prevDict :
                            if seasonName not in prevDict[serieName]['seasons']:
                                prevDict[serieName]['seasons'][seasonName] = SeriesServices.getEpisodes(filenames, dirpath)
                        
                        if serieName in newDict:
                            if seasonName not in newDict[serieName]['seasons']:
                                newDict[serieName]['seasons'][seasonName] = SeriesServices.getEpisodes(filenames, dirpath)
        
        if len(newDict) > 0:
            if len(prevDict)>0:
                idx = newDict.copy()
                for key, value in prevDict.items():
                    idx[key] = value

                newDict = idx
        else:
            newDict = prevDict

        with open("src/files/series.json", "w", encoding="utf-8") as outfile:
            outfile.write( json.dumps(newDict, ensure_ascii=False) )

    def getSeries(self, mode):
        pathFile = "src/files/series.json"

        try:
            if os.path.exists(pathFile):
                with open(pathFile, encoding="utf8") as f:
                    data = json.load(f)

                seriesS = []
                for key, value in data.items():
                    value['filename'] = key
                    seriesS.append(value)

                
                if mode=="carousel":
                    seriesS = [x for x in seriesS if x['founded']]

                    k = len(seriesS) * 40 // 100
                    indicies = random.sample(range(len(seriesS)), k)
                    seriesS = [seriesS[i] for i in indicies]

                res = {
                        "status": 'Ok',
                        "message": 'Lista de series obtenida correctamente!',
                        "data": seriesS,
                        "success": True
                    }

                return jsonify(res)
            else:
                raise NotFoundErr('No se encontró el archivo de series! Asegurese de haberlo creado antes')
        except Exception as e:
            LOG.logger.error("Error al obtener la informacion\nVerifique su archivo!")
            return jsonify(status='Error', exception=''+str(e))

    def search(self, dataBd):
        pathFile = "src/files/series.json"

        try:
            if os.path.exists(pathFile):
                with open(pathFile, encoding="utf8") as f:
                    data = json.load(f)

                seriesS = []
                for key, value in data.items():
                    if (dataBd['query'].lower() in value['title'].lower() and dataBd['mode']=='search') or (dataBd['query'].lower() in key.lower() and dataBd['mode']=='all'):
                        if all(item in value['genres'] for item in dataBd['genre']) or dataBd['genre']==[]:
                            value['filename'] = key
                            seriesS.append(value)
                
                if dataBd['mode'] == 'search':
                    seriesS = [x for x in seriesS if x['founded']]

                seriesFounded=[]
                if len(seriesS) > 0:
                    chunks = [seriesS[i:i + dataBd['limit']] for i in range(0, len(seriesS), dataBd['limit'])]
                    seriesFounded = chunks[dataBd['page']-1]
                
                res = {
                        "status": 'Ok',
                        "message": 'Se obtuvieron las series con exito!',
                        "data": seriesFounded,
                        "total": len(seriesS),
                        "pages": math.ceil(len(seriesS)/dataBd['limit']),
                        "success": True
                    }

                return jsonify(res)
            else:
                raise NotFoundErr('No se encontró el diccionario! Asegurese de haberlo creado antes')
        except Exception as e:
            LOG.logger.error("Error al obtener la informacion\nVerifique su archivo!")
            return jsonify(status='Error', exception=''+str(e))
        
    def getGenres(self):
        pathFile = "src/files/tvGenres.json"

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
