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

database= MongoClient('mongodb://localhost:27017').logoscan
index_database= MongoClient('mongodb://localhost:27017').index

class LogoUploadView(APIView):
  parser_classes = (MultiPartParser, FormParser)

  #renderer_classes= [TemplateHTMLRenderer]
  #template_name = 'upload_logo.html'

  def post(self, request, *args, **kwargs):
    data = request.data
    cd = ColorDescriptor((8, 12, 3))
    logo = data['image']
    fs = gridfs.GridFS(database)


    uploaded_logo = fs.put(logo, name=logo.name)
    print(uploaded_logo)
    uploaded_logo_data = fs.get(uploaded_logo).read()
    nparr = np.frombuffer(uploaded_logo_data, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)
    features = cd.describe(image)
    searcher = Searcher("index.csv")
    results = searcher.search(features)
    features = [str(f) for f in features]
    output1 = open('index.csv', "a")
    output1.write("%s,%s\n" % (logo.name, ",".join(features)))
    output1.close()   
    limit = 3
    results = results[:limit]
    result = dict(results)

    return JsonResponse({'results': results}, status=status.HTTP_201_CREATED)

    
class LogoUploadView2(APIView):
  parser_classes = (MultiPartParser, FormParser)

  #renderer_classes= [TemplateHTMLRenderer]
  #template_name = 'upload_logo.html'

  def post(self, request, *args, **kwargs):
    data = request.data
    cd = ColorDescriptor((8, 12, 3))
    logo = data['image']
    fs = gridfs.GridFS(database)
    nparr = np.frombuffer(logo.read(), np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)
    features = cd.describe(image)
    searcher = Searcher('index.csv')
    results = searcher.search(features)
    features = [str(f) for f in features]
    index = "%s,%s\n" % (logo.name, ",".join(features))
    logoId = fs.put(logo, name=logo.name, csv_index=index)
    print(fs.get(logoId).read())
    index1 = open('index.csv', 'a')
    index1.write(index)
    index1.close()
    limit = 3
    api_result = []
    for result in results:
      logo = database.fs.files.find_one({'name':result[1]})
      arr = (logo['name'], str(logo['_id']))
      api_result.append(arr)
    api_results = dict(api_result)
    return JsonResponse(api_results, status=status.HTTP_201_CREATED)


class ImageAPIView(APIView):
    def get(self, request, id, extension):
        # Connect to MongoDB
        fs = gridfs.GridFS(database)
        # Retrieve the image data from MongoDB

        data = database.fs.files.find_one({'_id': ObjectId(id)})
        my_id = data['_id']
        image_data = fs.get(my_id).read()

        # Serialize the image data to return it as a response
        # return Response({'image_data': image_data})
        return HttpResponse(image_data, content_type=f'image/{extension}')

