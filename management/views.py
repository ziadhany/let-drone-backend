from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
import requests
from rest_framework import status

from let_drone.settings import CLIENT_ID, CLIENT_SECRET
from management.models import (
    Drone,
    Comment,
    Prescription,
    GCS,
    Delivery,
    Pharmacist,
    Patient,
    Geolocation, TROCRModel,
)

from django.contrib.auth.models import User
from rest_framework import permissions, viewsets

from management.serializers import UserSerializer, DroneSerializer, GCSSerializer, CommentSerializer, \
    PrescriptionSerializer, DeliverySerializer, DoctorSerializer, PatientSerializer, \
    GeolocationSerializer, CreatePatientSerializer, ImageSerializer, PatientPrescriptionSerializer

from rest_framework.views import APIView
from rest_framework.response import Response

from .permissions import IsPharmacist, IsPatient
from PIL import Image
import torch


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserSerializer


class DroneViewSet(viewsets.ModelViewSet):
    queryset = Drone.objects.all()
    serializer_class = DroneSerializer
    permission_classes = (IsAuthenticated,)


class GCSViewSet(viewsets.ModelViewSet):
    queryset = GCS.objects.all()
    serializer_class = GCSSerializer
    permission_classes = [IsAuthenticated]


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticated,)


class PrescriptionPharmacistViewSet(viewsets.ModelViewSet):
    queryset = Prescription.objects.all()
    serializer_class = PrescriptionSerializer

    # def get_permissions(self):
    #     if self.action != 'retrieve':
    #         self.permission_classes = [IsAuthenticated]
    #     else:
    #         self.permission_classes = [IsAuthenticated]  # TODO ADD IsPharmacist
    #     return super().get_permissions()


class PrescriptionPatientViewSet(viewsets.ModelViewSet):
    queryset = Prescription.objects.all()
    serializer_class = PatientPrescriptionSerializer
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user.patient)

    def get_queryset(self):
        queryset = self.queryset
        query_set = queryset.filter(author=self.request.user.patient)
        return query_set


class DeliveryViewSet(viewsets.ModelViewSet):
    queryset = Delivery.objects.all()
    serializer_class = DeliverySerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = self.queryset
        query_set = queryset.filter(patient=self.request.user.patient)
        return query_set


class PharmacistViewSet(viewsets.ModelViewSet):
    queryset = Pharmacist.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = (IsAuthenticated,)


class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = (IsAuthenticated,)


class GeolocationViewSet(viewsets.ModelViewSet):
    queryset = Geolocation.objects.all()
    serializer_class = GeolocationSerializer
    permission_classes = (IsAuthenticated,)


model = TROCRModel()  # Load model


class OCRAPIView(APIView):
    permission_classes = [IsPharmacist]  # Apply custom permission

    def post(self, request):
        serializer = ImageSerializer(data=request.data)
        if serializer.is_valid():
            image_file = serializer.validated_data['image']
            image = Image.open(image_file).convert("RGB")
            prediction = model.predict(image)
            return Response({'text': prediction})
        else:
            return Response(serializer.errors, status=400)


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """
    Registers user to the server. Input should be in the format:
    {"username": "username", "password": "1234abcd"}
    """
    # Put the data from the request into the serializer
    serializer = CreatePatientSerializer(data=request.data)
    # Validate the data
    if serializer.is_valid():
        # If it is valid, save the data (creates a user).
        serializer.save()
        # Then we get a token for the created user.
        # This could be done differentley
        r = requests.post('http://127.0.0.1:8000/o/token/',
                          data={
                              'grant_type': 'password',
                              'username': request.data['username'],
                              'password': request.data['password'],
                              'client_id': CLIENT_ID,
                              'client_secret': CLIENT_SECRET,
                          },
                          )

        return Response(r.json())
    return Response(serializer.errors)


@api_view(['POST'])
@permission_classes([AllowAny])
def token(request):
    """
    Gets tokens with username and password. Input should be in the format:
    {"username": "username", "password": "1234abcd"}
    """
    r = requests.post(
        'http://127.0.0.1:8000/o/token/',
        data={
            'grant_type': 'password',
            'username': request.data['username'],
            'password': request.data['password'],
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
        },
    )
    return Response(r.json())


@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token(request):
    """
    Registers user to the server. Input should be in the format:
    {"refresh_token": "<token>"}
    """
    r = requests.post(
        'http://127.0.0.1:8000/o/token/',
        data={
            'grant_type': 'refresh_token',
            'refresh_token': request.data['refresh_token'],
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
        },
    )
    return Response(r.json())


@api_view(['POST'])
@permission_classes([AllowAny])
def revoke_token(request):
    """
    Method to revoke tokens.
    {"token": "<token>"}
    """
    r = requests.post(
        'http://127.0.0.1:8000/o/revoke_token/',
        data={
            'token': request.data['token'],
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
        },
    )
    # If it goes well return sucess message (would be empty otherwise)
    if r.status_code == requests.codes.ok:
        return Response({'message': 'token revoked'}, r.status_code)
    # Return the error if it goes badly
    return Response(r.json(), r.status_code)
