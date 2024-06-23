from django.contrib.auth.models import User
from rest_framework import serializers

from management.models import (
    Prescription,
    GCS,
    Delivery,
    Pharmacist,
    Patient,
    Comment,
    Drone,
    Geolocation,
)


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ["url", "username", "email", "groups"]


class GeolocationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Geolocation
        fields = ["latitude", "longitude", "altitude"]


class DoctorSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Pharmacist
        fields = ["user", "specialization", "phone_number", "biography", "avatar"]


class PatientSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Patient
        fields = ["user", "date_of_birth", "address", "emergency_contact", "avatar"]


class GCSSerializer(serializers.HyperlinkedModelSerializer):
    current_location = GeolocationSerializer(read_only=True)

    class Meta:
        model = GCS
        fields = ["name", "website", "current_location", "created_at", "updated_at"]


class CommentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Comment
        fields = ["content", "author", "parent_comment", "created_at", "updated_at"]


class DroneSerializer(serializers.HyperlinkedModelSerializer):
    current_location = GeolocationSerializer(read_only=True)

    class Meta:
        model = Drone
        fields = [
            "id",
            "model",
            "battery_level",
            "current_location",
            "payload_capacity",
            "created_at",
            "updated_at",
        ]


class DeliverySerializer(serializers.HyperlinkedModelSerializer):
    drone = DroneSerializer(read_only=True)
    pickup_location = GeolocationSerializer(read_only=True)

    class Meta:
        model = Delivery
        fields = [
            "id",
            # "prescription",
            "patient",
            "drone",
            "pickup_time",
            "pickup_location",
            "estimated_delivery_time",
            "status",
            "created_at",
            "updated_at",
        ]


class PrescriptionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Prescription
        fields = [
            "id",
            "image",
            "author",
            "price",
            "comments",
            "approved",
            "content",
            "gcs",
            "delivery_option",
            "delivery_address",
            "created_at",
            "updated_at",
        ]


class PatientPrescriptionSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        super(PatientPrescriptionSerializer, self).__init__(*args, **kwargs)
        if self.context['request'].method != 'GET':
            allowed_fields = ["image", "delivery_option", "delivery_address"]
            for field_name in list(self.fields):
                if field_name not in allowed_fields:
                    self.fields.pop(field_name)

    delivery_address = GeolocationSerializer(required=False)

    class Meta:
        model = Prescription
        fields = [
            "id",
            "image",
            "author",
            "price",
            "comments",
            "approved",
            "content",
            "gcs",
            "delivery_option",
            "delivery_address",
            "created_at",
            "updated_at",
        ]

    def create(self, validated_data):
        if "delivery_address" in validated_data:
            geolocation_data = validated_data.pop('delivery_address')
            geolocation = Geolocation.objects.create(**geolocation_data)
            prescription = Prescription.objects.create(delivery_address=geolocation, **validated_data)
        else:
            prescription = Prescription.objects.create(**validated_data)
        return prescription


class ImageSerializer(serializers.Serializer):
    image = serializers.ImageField(use_url=True)


class CreatePatientSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        Patient.objects.create(user=user)
        return user

    class Meta:
        model = User
        fields = ('id', 'username', 'password')
        extra_kwargs = {
            'password': {'write_only': True}
        }
