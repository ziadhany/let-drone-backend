import uuid
from django.contrib.auth.models import User
from django.db import models
from django.contrib.gis.db import models as geomodels
from transformers import pipeline
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from PIL import Image
import requests
from io import BytesIO


class Pharmacist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    specialization = models.CharField(max_length=255, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    biography = models.TextField(blank=True)
    avatar = models.ImageField(
        upload_to="doctors/", blank=True, default="default_doctor.jpg"
    )

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_of_birth = models.DateField(blank=True, null=True)
    address = models.CharField(max_length=255, blank=True)
    emergency_contact = models.CharField(max_length=255, blank=True)
    avatar = models.ImageField(
        upload_to="patients/", blank=True, default="default_patient.jpg"
    )

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


class Geolocation(geomodels.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()
    altitude = models.FloatField(null=True, blank=True)


class Drone(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4(), editable=False)
    model = models.CharField(max_length=255)
    battery_level = models.IntegerField()
    current_location = models.ForeignKey(Geolocation, on_delete=models.CASCADE)
    payload_capacity = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class GCS(models.Model):
    name = models.CharField(max_length=128)
    website = models.URLField(help_text="The website of the GSC")
    current_location = models.ForeignKey(Geolocation, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}-{self.website}"


class Comment(models.Model):
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    parent_comment = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Prescription(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    image = models.ImageField(upload_to='prescription_images/')
    author = models.ForeignKey(Patient, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    comments = models.ManyToManyField(Comment, blank=True)
    approved = models.BooleanField(default=False)
    content = models.TextField(
        help_text="The content of the prescription after OCR scan ( medication_names in text )"
    )
    gcs = models.ForeignKey(GCS, max_length=255, null=True, blank=True, on_delete=models.SET_NULL)

    delivery_option = models.CharField(
        max_length=10, choices=[("PICKUP", "Pickup"), ("DRONE", "Drone Delivery")]
    )
    delivery_address = models.ForeignKey(
        Geolocation, on_delete=models.SET_NULL, null=True, blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Delivery(geomodels.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4(), editable=False)
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    drone = models.ForeignKey(Drone, on_delete=models.SET_NULL, null=True, blank=True)
    pickup_time = models.DateTimeField()
    pickup_location = models.ForeignKey(Geolocation, on_delete=models.CASCADE)
    estimated_delivery_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ("PREPARING", "Preparing"),
            ("IN_FLIGHT", "In Flight"),
            ("DELIVERED", "Delivered"),
        ],
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class TROCRModel:
    def __init__(self):
        self.processor = TrOCRProcessor.from_pretrained("microsoft/trocr-large-handwritten")
        self.model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-large-handwritten")

    def predict(self, image: Image.Image):
        pixel_values = self.processor(images=image, return_tensors="pt").pixel_values
        generated_ids = self.model.generate(pixel_values)
        text = self.processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
        return text
