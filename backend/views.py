from django.shortcuts import render, HttpResponse
from .image_comparison.main import Searcher, ColorDescriptor
# Create your views here.

from ctypes import sizeof
import cv2
import numpy as np
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
import os
from logoscan.settings import BASE_DIR, STATIC_ROOT
from pymongo import MongoClient
import gridfs
import pprint
import csv
from bson import ObjectId


def index(request):
    return JsonResponse({"message": "This is the backend api."})


# initialize connection with mogoDb 
database= MongoClient('mongodb://localhost:27017').logoscan
index_database= MongoClient('mongodb://localhost:27017').logoscan.index

    
class LogoUploadView(APIView):
  parser_classes = (MultiPartParser, FormParser)

  #renderer_classes= [TemplateHTMLRenderer]
  #template_name = 'upload_logo.html'

  def post(self, request, *args, **kwargs):
    cd = ColorDescriptor((8, 12, 3))
    # Get logo data from the api post request 
    data = request.data
    logo = data['image']
    # initialize gridFs to store logo in database 
    fs = gridfs.GridFS(database)
    logoId = fs.put(logo, name=logo.name)
    # process numpy array with logodata stored in database
    nparr = np.frombuffer(fs.get(logoId).read(), np.uint8)
    # decode numpy array and descibe image for comparison
    image = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)
    features = cd.describe(image)
    # query for logo indexes from the database then store in an array to search for matching logos
    logo_index = index_database.find({}, {'features': 1, 'file_id': 1})
    index_list = []
    for csv_index in logo_index:
       csv_index['features'].insert(0, csv_index['file_id'])
       index_list.append(csv_index['features'])
    searcher = Searcher(index_list)
    results = searcher.search(features)
    features = [str(f) for f in features]
    # query to check if the uploaded logo index is already in the database
    # if not in database store the index 
    
    check_index = index_database.find_one({'features': features}, {'features': 1})
    if check_index is None:
        index_database.insert_one({'file_id':logoId, 'features':features})
    limit = 3
    # create an array of matching logo urls to be called in a get api to display logos in frontend.
    api_result = []
    results = results[:limit]
    for result in results:
      url = 'http://127.0.0.1:8000/api/image/'
      logo = database.fs.files.find_one({'_id':result[1]})
      arr =  url+str(logo['_id'])
      api_result.append(arr)
    return JsonResponse({'results': api_result}, status=status.HTTP_201_CREATED)


class ImageAPIView(APIView):
    def get(self, request, id):
        # Connect to MongoDB
        fs = gridfs.GridFS(database)
        # Retrieve the image data from MongoDB

        image_data = fs.get(ObjectId(id)).read()
        fileName = database.fs.files.find_one(
            {
                "_id": ObjectId(id)
            }
        )["name"]
        # get extension
        fileExtension = fileName.split(".")[-1]
        

        # Serialize the image data to return it as a response
        # return Response({'image_data': image_data})
        return HttpResponse(image_data, content_type=f'image/{fileExtension}')

