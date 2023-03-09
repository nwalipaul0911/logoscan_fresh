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
from bson.objectid import ObjectId


def index(request):
    return JsonResponse({"message": "This is the backend api."})


database = MongoClient('mongodb://localhost:27017').logoscan


class LogoUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    # renderer_classes= [TemplateHTMLRenderer]
    # template_name = 'upload_logo.html'

    # def get(self, request, *args, **kwargs):
    # serializer = LogoSerializer(data=request.data)
    # return Response({'serializer': serializer})

    def post(self, request, *args, **kwargs):
        data = request.data
        cd = ColorDescriptor((8, 12, 3))
        logo = data['image']
        fs = gridfs.GridFS(database)

        # get all the files in the database and save in csv file.

        # for l in database.fs.files.find():
        #     filename = l['name']
        #     # filepath = os.path.join(BASE_DIR, f'media/test_folder/{filename}')
        #     file = fs.get(l['_id']).read()
        #     # try to use the direct image variable stored in mongo db
        #     nparr = np.frombuffer(file, np.uint8)
        #     # location = open(filepath, 'wb')
        #     # location.write(file)
        #     # location.close()
        #     image = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)
        #     features = cd.describe(image)
        #     features = [float(x) for x in features]
        #     database.index.insert_one(
        #         {
        #             "_id": l["_id"],
        #             "features": features
        #         }
        #     )

        # get the 1440 variable of the user input image

        # filepath = os.path.join(BASE_DIR, f'media/uploaded_logos/{logo.name}')
        uploaded_logo = fs.put(logo, name=logo.name)
        uploaded_logo_data = fs.get(uploaded_logo).read()
        # location = open(filepath, 'wb')
        # location.write(uploaded_logo_data)
        # location.close()
        # image = cv2.imread(filepath)
        nparr = np.frombuffer(uploaded_logo_data, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)
        features = cd.describe(image)
        features = [float(x) for x in features]
        searcher = Searcher()
        results = searcher.search(
            queryFeatures=features, imagesData=database.index.find())
        limit = 3
        images = []
        for i in results[:limit]:
            images.append("http://127.0.0.1:8000/api/image/"+i[0])

        
        database.index.insert_one(
            {
                "_id": uploaded_logo,
                "features": features
            }
        )
        # print("____\n")
        # print(results)
        # print("____\n")
        

        return JsonResponse({'results': images}, status=status.HTTP_201_CREATED)

        # features = cd.describe(image)
        # features = [str(f) for f in features]
        # output1.write("%s,%s\n" % (l._id, ",".join(features)))
        # return JsonResponse({"message":"working"})


# fetch the image stored in mongodb
# class ImageAPIView(APIView):
#     def get(self, request):
#         # Connect to MongoDB
#         fs = gridfs.GridFS(database)
#         # Retrieve the image data from MongoDB

#         data = database.fs.files.find_one({'name': 'health.png'})
#         my_id = data['_id']
#         image_data = fs.get(my_id).read()
#         print(image_data)

#         # Serialize the image data to return it as a response
#         # return Response({'image_data': image_data})
#         return HttpResponse(image_data, content_type="image/png")


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
        # get png or jpg part
        fileExtension = fileName.split(".")[-1]

        # Serialize the image data to return it as a response
        # return Response({'image_data': image_data})
        return HttpResponse(image_data, content_type=f'image/{fileExtension}')