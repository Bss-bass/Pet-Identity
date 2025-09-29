import uuid

from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.
class UserManager(BaseUserManager):
    use_in_migrations = True
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    username = None
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    ROLE_CHOICES = (
        ("OWNER", "OWNER"),
        ("DOCTOR", "DOCTOR"),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="OWNER")
    phone_number = models.CharField(max_length=30, blank=True, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = UserManager()

    def __str__(self):
        return f"{self.email} ({self.role})"

class Pet(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="pets")
    name = models.CharField(max_length=120)
    species = models.CharField(max_length=50, blank=True, null=True)
    breed = models.CharField(max_length=100, blank=True, null=True)
    color = models.CharField(max_length=50, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    avatar = models.ImageField(upload_to="pets/avatars/", blank=True, null=True)
    qr_slug = models.CharField(max_length=128, unique=True) # สำหรับเก็บข้อมูล QR code
    is_lost = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.name} ({self.species})"

class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, limit_choices_to={"role": "doctor"})
    pets = models.ManyToManyField(Pet, related_name="doctors", blank=True)
    def __str__(self):
        return f"Dr. {self.doctor.first_name} {self.doctor.last_name}"

class MedicalRecord(models.Model):
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name="medical_records")
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True)
    diagnosis = models.CharField(max_length=255)  # การวินิจฉัยโรค
    treatment = models.TextField()  # วิธีการรักษา
    prescription = models.TextField(blank=True, null=True)  # ยาที่สั่ง
    notes = models.TextField(blank=True, null=True)  # บันทึกเพิ่มเติม   
    date = models.DateField(auto_now_add=True)
