from django.shortcuts import render
from .image_comparison.main import Searcher, ColorDescriptor
# Create your views here.

from ctypes import sizeof
import cv2
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from .serializers import LogoSerializer
import os
from logoscan.settings import BASE_DIR, STATIC_ROOT
from pymongo import MongoClient
import gridfs
import pprint
import numpy as np


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
      # filepath = os.path.join(BASE_DIR, f'media/test_folder/{filename}')
      file = fs.get(l['_id']).read()
      # try to use the direct image variable stored in mongo db
      nparr = np.frombuffer(file, np.uint8)
      # location = open(filepath, 'wb')
      # location.write(file)
      # location.close()
      image = cv2.imdecode(nparr,cv2.IMREAD_UNCHANGED)
      features = cd.describe(image)
      features = [str(f) for f in features]
      output1.write("%s,%s\n" % (filename, ",".join(features)))
    output1.close()

    # get the 1440 variable of the user input image

    # filepath = os.path.join(BASE_DIR, f'media/uploaded_logos/{logo.name}')
    uploaded_logo = fs.put(logo, name=logo.name)
    uploaded_logo_data = fs.get(uploaded_logo).read()
    # location = open(filepath, 'wb')
    # location.write(uploaded_logo_data)
    # location.close()
    # image = cv2.imread(filepath)
    nparr = np.frombuffer(uploaded_logo_data, np.uint8)
    image = cv2.imdecode(nparr,cv2.IMREAD_UNCHANGED)
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
    

# fetch the image stored in mongodb
class ImageAPIView(APIView):
    def get(self, request):
        # Connect to MongoDB
        fs = gridfs.GridFS(database)
        # Retrieve the image data from MongoDB
        
        data = database.fs.files.find_one({'name': 'health.png'})
        my_id = data['_id']
        image_data = fs.get(my_id).read()

        # Serialize the image data to return it as a response
        # return Response({'image_data': image_data})
        return HttpResponse(image_data, content_type="image/png")
