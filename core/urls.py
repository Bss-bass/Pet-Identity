from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('change_password/', views.PasswordChangeView.as_view(), name='change_password'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('doctor_dashboard/', views.DoctorDashboardView.as_view(), name='doctor_dashboard'),
    path('create_pet/', views.CreatePetView.as_view(), name='create_pet'),
    path('pet/<str:qr_slug>/card/', views.PetCardView.as_view(), name='pet_card'),
    path('pet/<uuid:pet_id>/generate-qr/', views.GenerateQRCodeView.as_view(), name='generate_qr'),
    path('pet/<uuid:pet_id>/grant-access/', views.GrantAccessView.as_view(), name='grant_access'),
    path('pet/<uuid:pet_id>/medical-record/', views.ViewMedicalRecordView.as_view(), name='view_medical_record'),
    path('pet/<uuid:pet_id>/add-medical-record/', views.AddMedicalRecordView.as_view(), name='add_medical_record'),
    path('pet/<uuid:pet_id>/toggle-lost/', views.ToggleLostStatusView.as_view(), name='toggle_lost_status'),
    # path('report-lost-pet/<uuid:pet_id>/', views.ReportLostPetView.as_view(), name='report_lost_pet'),
    path('pet/<uuid:pet_id>/send-location-alert/', views.SendLocationAlertView.as_view(), name='send_location_alert'),
    path('pet/<uuid:pet_id>/send-manual-location-alert/', views.SendManualLocationAlertView.as_view(), name='send_manual_location_alert'),
    path('profile/edit/', views.EditUserProfileView.as_view(), name='edit_user_profile'),
    path('pet/<uuid:pet_id>/edit/', views.EditPetView.as_view(), name='edit_pet'),
    path('medical-record/<int:record_id>/edit/', views.EditMedicalRecordView.as_view(), name='edit_medical_record'),
    path('medical-record/<int:record_id>/delete/', views.DeleteMedicalRecordView.as_view(), name='delete_medical_record'),
]