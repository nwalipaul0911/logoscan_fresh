from django.shortcuts import render
from .image_comparison.main import Searcher, ColorDescriptor
# Create your views here.

from ctypes import sizeof
import cv2
from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from .serializers import LogoSerializer
import os
from logoscan.settings import BASE_DIR, STATIC_ROOT
from pymongo import MongoClient
import gridfs
import pprint


def index(request):
    return JsonResponse({"message": "This is the backend api."})

database= MongoClient('mongodb://localhost:27017').logoscan

class LogoUploadView(APIView):
  parser_classes = (MultiPartParser, FormParser)

  #renderer_classes= [TemplateHTMLRenderer]
  #template_name = 'upload_logo.html'

  #def get(self, request, *args, **kwargs):
    #serializer = LogoSerializer(data=request.data)
    #return Response({'serializer': serializer})

  def post(self, request, *args, **kwargs):
    data = request.data
    cd = ColorDescriptor((8, 12, 3))
    logo = data['image']
    fs = gridfs.GridFS(database)
    output1 = open("index1.csv", "w")

    
    # get all the files in the database and save in csv file.

    for l in database.fs.files.find():
      filename = l['name']
      filepath = os.path.join(BASE_DIR, f'media/test_folder/{filename}')
      file = fs.get(l['_id']).read()
      location = open(filepath, 'wb')
      location.write(file)
      location.close()
      image = cv2.imread(filepath)
      features = cd.describe(image)
      features = [str(f) for f in features]
      output1.write("%s,%s\n" % (filename, ",".join(features)))
    output1.close()
    filepath = os.path.join(BASE_DIR, f'media/uploaded_logos/{logo.name}')
    uploaded_logo = fs.put(logo, name=logo.name)
    uploaded_logo_data = fs.get(uploaded_logo).read()
    location = open(filepath, 'wb')
    location.write(uploaded_logo_data)
    location.close()
    image = cv2.imread(filepath)
    features = cd.describe(image)
    searcher = Searcher("index1.csv")
    results = searcher.search(features)
    limit = 3
    results = results[:limit]

    return JsonResponse({'results': results}, status=status.HTTP_201_CREATED)

      
      # features = cd.describe(image)
      # features = [str(f) for f in features]
      # output1.write("%s,%s\n" % (l._id, ",".join(features)))
    # return JsonResponse({"message":"working"})
    

