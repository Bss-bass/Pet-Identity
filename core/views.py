from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from .models import Pet, Doctor, MedicalRecord
from .forms import PetForm, MedicalRecordForm, RegistrationForm, UserProfileForm, PetEditForm
from django.views import View
from django.http import HttpResponseForbidden, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group
from django.http import FileResponse, Http404, HttpResponse
from .utils import generate_qr_image
from django.core.mail import send_mail
from django.conf import settings
import os
import mimetypes
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.forms import PasswordChangeForm
import uuid
import json

class RegisterView(View):
    def get(self, request):
        form = RegistrationForm()
        return render(request, 'register.html', {'form': form})

    def post(self, request):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
        return render(request, 'register.html', {'form': form})

class LoginView(View):
    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            # check user role and redirect accordingly
            if user.role == 'OWNER':
                user.groups.clear()
                try:
                    owner_group = Group.objects.get(name='Owner')
                    user.groups.add(owner_group)
                except Group.DoesNotExist:
                    # Create Owner group if it doesn't exist
                    owner_group = Group.objects.create(name='Owner')
                    user.groups.add(owner_group)
                return redirect('dashboard')
            elif user.role == 'DOCTOR':
                user.groups.clear()
                try:
                    doctor_group = Group.objects.get(name='Doctor')
                    user.groups.add(doctor_group)
                except Group.DoesNotExist:
                    # Create Doctor group if it doesn't exist
                    doctor_group = Group.objects.create(name='Doctor')
                    user.groups.add(doctor_group)
                return redirect('doctor_dashboard')
        return render(request, 'login.html', {'error': 'Invalid credentials'})

class LogoutView(LoginRequiredMixin, View):
    def post(self, request):
        logout(request)
        return redirect('login')

class PasswordChangeView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'change_password.html')

    def post(self, request):
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
        return render(request, 'change_password.html', {'form': form})

class DashboardView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ['core.view_pet', 'core.view_medicalrecord', 'core.view_doctor']

    def get(self, request):
        if request.user.role != 'OWNER':
            return HttpResponseForbidden("You are not authorized to view this page.")
        pets = Pet.objects.filter(owner=request.user)
        if (not pets.exists()):
            return redirect('create_pet')
        return render(request, 'owner_dashboard.html', {'pets': pets})
    
class DoctorDashboardView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/core/login/'
    permission_required = ['core.view_medicalrecord', 'core.view_pet']

    def get(self, request):
        if request.user.role != 'DOCTOR':
            return HttpResponseForbidden("You are not authorized to view this page.")

        # สร้าง Doctor record หากยังไม่มี
        doctor, created = Doctor.objects.get_or_create(user=request.user)
        pets = doctor.pets.all()
        total_records = MedicalRecord.objects.filter(doctor=doctor).count()
        return render(request, 'doctor_dashboard.html', {'pets': pets, 'total_records': total_records})

class CreatePetView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ['core.add_pet']

    def get(self, request):
        if request.user.role != 'OWNER':
            return HttpResponseForbidden("You are not authorized to view this page.")
        form = PetForm()
        return render(request, 'create_pet.html', {'form': form})

    def post(self, request):
        if request.user.role != 'OWNER':
            return HttpResponseForbidden("You are not authorized to perform this action.")
        form = PetForm(request.POST, request.FILES)
        if form.is_valid():
            pet = form.save(commit=False)
            pet.owner = request.user
            pet.qr_slug = str(uuid.uuid4()).replace("-", "")
            pet.save()
            return redirect('dashboard')
        return render(request, 'create_pet.html', {'form': form})

class PetCardView(View):
    def get(self, request, qr_slug):
        pet = get_object_or_404(Pet, qr_slug=qr_slug)
        return render(request, 'pet_card.html', {'pet': pet})

class GenerateQRCodeView(LoginRequiredMixin, View):
    login_url = '/core/login/'

    def get(self, request, pet_id):
        if request.user.role != 'OWNER':
            return HttpResponseForbidden("You are not authorized to perform this action.")
        
        pet = get_object_or_404(Pet, id=pet_id, owner=request.user)
        qr_image = generate_qr_image(pet.qr_slug)
        
        response = FileResponse(qr_image, content_type='image/png')
        response['Content-Disposition'] = f'attachment; filename="{pet.name}_qr_code.png"'
        return response

class GrantAccessView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ['core.change_pet', 'core.view_doctor']

    def get(self, request, pet_id):
        if request.user.role != 'OWNER':
            return HttpResponseForbidden("You are not authorized to perform this action.")
        
        pet = get_object_or_404(Pet, id=pet_id, owner=request.user)
        doctors = Doctor.objects.all()
        return render(request, 'grant_access.html', {'pet': pet, 'doctors': doctors})
    
    def post(self, request, pet_id):
        if request.user.role != 'OWNER':
            return HttpResponseForbidden("You are not authorized to perform this action.")
        
        pet = get_object_or_404(Pet, id=pet_id, owner=request.user)
        doctor_id = request.POST.get('doctor_id')
        
        if doctor_id:
            doctor = get_object_or_404(Doctor, id=doctor_id)
            pet.doctors.add(doctor)
            pet.save()
        
        return redirect('dashboard')

class ViewMedicalRecordView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ['core.view_medicalrecord', 'core.view_pet']

    def get(self, request, pet_id):
        pet = get_object_or_404(Pet, id=pet_id)
        
        # ตรวจสอบสิทธิ์การเข้าถึง
        if request.user.role == 'OWNER' and pet.owner != request.user:
            return HttpResponseForbidden("You are not authorized to view this page.")
        elif request.user.role == 'DOCTOR':
            doctor = get_object_or_404(Doctor, user=request.user)
            if pet not in doctor.pets.all():
                return HttpResponseForbidden("You are not authorized to view this page.")
        
        medical_records = MedicalRecord.objects.filter(pet=pet).order_by('-date')
        form = MedicalRecordForm()
        return render(request, 'medical_record.html', {'pet': pet, 'medical_records': medical_records, 'form': form})
    
    def post(self, request, pet_id):
        if request.user.role != 'DOCTOR':
            return HttpResponseForbidden("You are not authorized to perform this action.")
        
        pet = get_object_or_404(Pet, id=pet_id)
        doctor = get_object_or_404(Doctor, user=request.user)
        
        if pet not in doctor.pets.all():
            return HttpResponseForbidden("You are not authorized to perform this action.")
        
        form = MedicalRecordForm(request.POST)
        if form.is_valid():
            medical_record = form.save(commit=False)
            medical_record.pet = pet
            medical_record.doctor = doctor
            medical_record.save()
            return redirect('view_medical_record', pet_id=pet.id)
        
        medical_records = MedicalRecord.objects.filter(pet=pet).order_by('-date')
        return render(request, 'medical_record.html', {'pet': pet, 'medical_records': medical_records, 'form': form})

class AddMedicalRecordView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ['core.add_medicalrecord', 'core.view_pet']

    def get(self, request, pet_id):
        if request.user.role != 'DOCTOR':
            return HttpResponseForbidden("You are not authorized to perform this action.")
        
        pet = get_object_or_404(Pet, id=pet_id)
        doctor = get_object_or_404(Doctor, user=request.user)
        
        if pet not in doctor.pets.all():
            return HttpResponseForbidden("You are not authorized to perform this action.")
        
        form = MedicalRecordForm()
        return render(request, 'add_medical_record.html', {'pet': pet, 'form': form})
    
    def post(self, request, pet_id):
        if request.user.role != 'DOCTOR':
            return HttpResponseForbidden("You are not authorized to perform this action.")
        
        pet = get_object_or_404(Pet, id=pet_id)
        doctor = get_object_or_404(Doctor, user=request.user)
        
        if pet not in doctor.pets.all():
            return HttpResponseForbidden("You are not authorized to perform this action.")
        
        form = MedicalRecordForm(request.POST)
        if form.is_valid():
            medical_record = form.save(commit=False)
            medical_record.pet = pet
            medical_record.doctor = doctor
            medical_record.save()
            return redirect('view_medical_record', pet_id=pet.id)
        
        return render(request, 'add_medical_record.html', {'pet': pet, 'form': form})

class ToggleLostStatusView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'core.change_pet'

    def post(self, request, pet_id):
        if request.user.role != 'OWNER':
            return HttpResponseForbidden("You are not authorized to perform this action.")
        
        pet = get_object_or_404(Pet, id=pet_id, owner=request.user)
        
        # Toggle lost status
        pet.is_lost = not pet.is_lost
        pet.save()
        
        return redirect('dashboard')
    
# class ReportLostPetView(LoginRequiredMixin, View):
#     def post(self, request, pet_id):
#         if request.user.role != 'OWNER':
#             return HttpResponseForbidden("You are not authorized to perform this action.")
        
#         pet = get_object_or_404(Pet, id=pet_id, owner=request.user)
        
#         subject = f"📢 มีคนพบสัตว์เลี้ยงของคุณ: {pet.name}"
#         body = f""
#         send_mail(subject, body, "no-reply@yourdomain.com", [pet.owner.email])
#         pet.save()
        
#         return redirect('dashboard')

@method_decorator(csrf_exempt, name='dispatch')
class SendLocationAlertView(View):
    def post(self, request, pet_id):
        try:
            # Get the pet information
            pet = get_object_or_404(Pet, id=pet_id)
            
            # Parse JSON data from request
            data = json.loads(request.body)
            latitude = data.get('latitude')
            longitude = data.get('longitude')
            timestamp = data.get('timestamp')
            
            if not latitude or not longitude:
                return JsonResponse({'success': False, 'error': 'Location data missing'})
            
            # Create Google Maps link
            maps_link = f"https://www.google.com/maps?q={latitude},{longitude}"
            
            # Prepare email content
            subject = f"🚨 URGENT: Your pet {pet.name} has been found!"
            
            email_body = f"""
Hello {pet.owner.first_name} {pet.owner.last_name},

Great news! Someone has found your pet {pet.name} and is trying to contact you.

📍 View Location on Google Maps: {maps_link}
📅 Timestamp: {timestamp}

Best regards,
PetID Team
            """
            
            # Send email to pet owner
            try:
                send_mail(
                    subject=subject,
                    message=email_body,
                    from_email='petid555@gmail.com',
                    recipient_list=[pet.owner.email],
                    fail_silently=False,
                )
                
                return JsonResponse({
                    'success': True, 
                    'message': 'Location alert sent successfully to pet owner!'
                })
                
            except Exception as email_error:
                print(f"Email sending error: {email_error}")
                return JsonResponse({
                    'success': False, 
                    'error': 'Failed to send email alert'
                })
                
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON data'})
        except Exception as e:
            print(f"Location alert error: {e}")
            return JsonResponse({'success': False, 'error': 'Server error occurred'})

@method_decorator(csrf_exempt, name='dispatch')
class SendManualLocationAlertView(View):
    def post(self, request, pet_id):
        try:
            # Get the pet information
            pet = get_object_or_404(Pet, id=pet_id)
            
            # Parse JSON data from request
            data = json.loads(request.body)
            location_description = data.get('locationDescription', '').strip()
            contact_info = data.get('contactInfo', '').strip()
            timestamp = data.get('timestamp')
            
            if not location_description:
                return JsonResponse({'success': False, 'error': 'Location description is required'})
            
            # Prepare email content
            subject = f"🔍 Location Report for {pet.name}"
            
            email_body = f"""
Hello {pet.owner.first_name} {pet.owner.last_name},

Someone has found your pet {pet.name} and provided the following location information:

📍 Location Description:
{location_description}

📅 Report Time: {timestamp}
"""
            
            if contact_info:
                email_body += f"""
👤 Contact Information: {contact_info}
"""
            
            email_body += """
Please contact the person who found your pet as soon as possible.

Best regards,
PetID Team
            """
            
            # Send email to pet owner
            try:
                send_mail(
                    subject=subject,
                    message=email_body,
                    from_email='petid555@gmail.com',
                    recipient_list=[pet.owner.email],
                    fail_silently=False,
                )
                
                return JsonResponse({
                    'success': True, 
                    'message': 'Manual location report sent successfully to pet owner!'
                })
                
            except Exception as email_error:
                print(f"Email sending error: {email_error}")
                return JsonResponse({
                    'success': False, 
                    'error': 'Failed to send location report email'
                })
                
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON data'})
        except Exception as e:
            print(f"Manual location alert error: {e}")
            return JsonResponse({'success': False, 'error': 'Server error occurred'})

class EditUserProfileView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ['core.change_user', 'core.view_user']

    def get(self, request):
        form = UserProfileForm(instance=request.user)
        return render(request, 'edit_user_profile.html', {'form': form})
    
    def post(self, request):
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            if request.user.role == 'OWNER':
                return redirect('dashboard')
            elif request.user.role == 'DOCTOR':
                return redirect('doctor_dashboard')
        return render(request, 'edit_user_profile.html', {'form': form})

class EditPetView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ['core.change_pet', 'core.view_pet']

    def get(self, request, pet_id):
        pet = get_object_or_404(Pet, id=pet_id, owner=request.user)
        form = PetEditForm(instance=pet)
        return render(request, 'edit_pet.html', {'form': form, 'pet': pet})
    
    def post(self, request, pet_id):
        pet = get_object_or_404(Pet, id=pet_id, owner=request.user)
        form = PetEditForm(request.POST, request.FILES, instance=pet)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
        return render(request, 'edit_pet.html', {'form': form, 'pet': pet})

class EditMedicalRecordView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ['core.change_medicalrecord', 'core.view_medicalrecord']

    def get(self, request, record_id):
        if request.user.role != 'DOCTOR':
            return HttpResponseForbidden("You are not authorized to perform this action.")
        
        record = get_object_or_404(MedicalRecord, id=record_id)
        
        # Check if doctor has access to this pet
        doctor = get_object_or_404(Doctor, user=request.user)
        if record.pet not in doctor.pets.all():
            return HttpResponseForbidden("You don't have access to this pet's medical records.")
        
        form = MedicalRecordForm(instance=record)
        return render(request, 'edit_medical_record.html', {'form': form, 'record': record, 'pet': record.pet})
    
    def post(self, request, record_id):
        if request.user.role != 'DOCTOR':
            return HttpResponseForbidden("You are not authorized to perform this action.")
        
        record = get_object_or_404(MedicalRecord, id=record_id)
        
        # Check if doctor has access to this pet
        doctor = get_object_or_404(Doctor, user=request.user)
        if record.pet not in doctor.pets.all():
            return HttpResponseForbidden("You don't have access to this pet's medical records.")
        
        form = MedicalRecordForm(request.POST, instance=record)
        if form.is_valid():
            form.save()
            return redirect('view_medical_record', pet_id=record.pet.id)
        return render(request, 'edit_medical_record.html', {'form': form, 'record': record, 'pet': record.pet})

class DeleteMedicalRecordView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ['core.delete_medicalrecord']

    def post(self, request, record_id):
        if request.user.role != 'DOCTOR':
            return HttpResponseForbidden("You are not authorized to perform this action.")
        
        record = get_object_or_404(MedicalRecord, id=record_id)
        
        # Check if doctor has access to this pet
        doctor = get_object_or_404(Doctor, user=request.user)
        if record.pet not in doctor.pets.all():
            return HttpResponseForbidden("You don't have access to this pet's medical records.")
        
        pet_id = record.pet.id
        record.delete()
        return redirect('view_medical_record', pet_id=pet_id)


class ServeMediaView(View):
    """Custom view to serve media files in production"""
    
    def get(self, request, path):
        # ตรวจสอบว่าไฟล์อยู่ใน media directory
        file_path = os.path.join(settings.MEDIA_ROOT, path)
        
        # ตรวจสอบว่าไฟล์มีอยู่จริง
        if not os.path.exists(file_path):
            raise Http404("File not found")
        
        # ตรวจสอบว่าไฟล์อยู่ใน media directory (security check)
        if not file_path.startswith(settings.MEDIA_ROOT):
            raise Http404("File not found")
        
        # หา content type
        content_type, _ = mimetypes.guess_type(file_path)
        if content_type is None:
            content_type = 'application/octet-stream'
        
        # อ่านไฟล์และส่งกลับ
        try:
            with open(file_path, 'rb') as f:
                response = HttpResponse(f.read(), content_type=content_type)
                
                # เพิ่ม headers เพื่อแก้ปัญหาการ cache และ CORS (รองรับ ngrok)
                response['Cache-Control'] = 'public, max-age=86400'  # Cache 1 วัน
                response['Access-Control-Allow-Origin'] = '*'
                response['Access-Control-Allow-Methods'] = 'GET'
                response['Access-Control-Allow-Headers'] = 'Content-Type, ngrok-skip-browser-warning'
                response['X-Frame-Options'] = 'SAMEORIGIN'
                response['ngrok-skip-browser-warning'] = 'true'  # Skip ngrok warning
                
                # เพิ่ม filename สำหรับ download
                filename = os.path.basename(file_path)
                response['Content-Disposition'] = f'inline; filename="{filename}"'
                
                return response
        except IOError:
            raise Http404("File not found")
