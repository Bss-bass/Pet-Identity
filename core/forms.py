from django import forms
from django.forms import ModelForm
from .models import Pet, MedicalRecord, User

class RegistrationForm(ModelForm):
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput(attrs={"class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"}))
    password2 = forms.CharField(label="Confirm Password", widget=forms.PasswordInput(attrs={"class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"}))

    class Meta:
        model = User
        fields = ["first_name","last_name","email","role","phone_number"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"}),
            "last_name": forms.TextInput(attrs={"class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"}),
            "email": forms.EmailInput(attrs={"class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"}),
            "role": forms.Select(choices=User.ROLE_CHOICES, attrs={"class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"}),
            "phone_number": forms.TextInput(attrs={"class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"}),
        }

    def clean_password1(self):
        # valid passsword strength
        p1 = self.cleaned_data.get("password1")
        if len(p1) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long")
        if not any(char.isdigit() for char in p1):
            raise forms.ValidationError("Password must contain at least one digit")
        if not any(char.isalpha() for char in p1):
            raise forms.ValidationError("Password must contain at least one letter")
        return p1

    def clean_password2(self):
        p1 = self.cleaned_data.get("password1")
        p2 = self.cleaned_data.get("password2")
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Passwords do not match")
        return p2
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

class LoginForm(forms.Form):
    email = forms.EmailField(label="Email")
    password = forms.CharField(label="Password", widget=forms.PasswordInput(attrs={"autocomplete": "current-password", "class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"}))

class PetForm(ModelForm):
    class Meta:
        model = Pet
        fields = ["name","species","breed","color","birth_date","avatar"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"}),
            "species": forms.TextInput(attrs={"class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"}),
            "breed": forms.TextInput(attrs={"class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"}),
            "color": forms.TextInput(attrs={"class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"}),
            "birth_date": forms.DateInput(attrs={"type": "date", "class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"}),
            "avatar": forms.ClearableFileInput(attrs={"class": "mt-1 block w-full"}),
        }

    def clean_birth_date(self):
        b = self.cleaned_data.get("birth_date")
        from datetime import date
        if b and b > date.today():
            raise forms.ValidationError("Birthday cannot be in the future")
        return b

class MedicalRecordForm(ModelForm):
    class Meta:
        model = MedicalRecord
        fields = ["diagnosis","treatment","prescription","notes"]
        widgets = {
            "diagnosis": forms.TextInput(attrs={"class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"}),
            "treatment": forms.Textarea(attrs={"class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2", "rows": 3}),
            "prescription": forms.Textarea(attrs={"class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2", "rows": 3}),
            "notes": forms.Textarea(attrs={"class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2", "rows": 3}),
        }

class UserProfileForm(ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "phone_number"]
        widgets = {
            "first_name": forms.TextInput(attrs={
                "class": "mt-1 block w-full border border-gray-300 rounded-lg shadow-sm px-4 py-3 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-200",
                "placeholder": "Enter your first name"
            }),
            "last_name": forms.TextInput(attrs={
                "class": "mt-1 block w-full border border-gray-300 rounded-lg shadow-sm px-4 py-3 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-200",
                "placeholder": "Enter your last name"
            }),
            "email": forms.EmailInput(attrs={
                "class": "mt-1 block w-full border border-gray-300 rounded-lg shadow-sm px-4 py-3 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-200",
                "placeholder": "Enter your email address"
            }),
            "phone_number": forms.TextInput(attrs={
                "class": "mt-1 block w-full border border-gray-300 rounded-lg shadow-sm px-4 py-3 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-200",
                "placeholder": "Enter your phone number"
            }),
        }

class PetEditForm(ModelForm):
    class Meta:
        model = Pet
        fields = ["name", "species", "breed", "color", "birth_date", "avatar"]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "mt-1 block w-full border border-gray-300 rounded-lg shadow-sm px-4 py-3 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-200",
                "placeholder": "Enter pet's name"
            }),
            "species": forms.TextInput(attrs={
                "class": "mt-1 block w-full border border-gray-300 rounded-lg shadow-sm px-4 py-3 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-200",
                "placeholder": "e.g., Dog, Cat, Bird"
            }),
            "breed": forms.TextInput(attrs={
                "class": "mt-1 block w-full border border-gray-300 rounded-lg shadow-sm px-4 py-3 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-200",
                "placeholder": "Enter breed"
            }),
            "color": forms.TextInput(attrs={
                "class": "mt-1 block w-full border border-gray-300 rounded-lg shadow-sm px-4 py-3 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-200",
                "placeholder": "Enter color"
            }),
            "birth_date": forms.DateInput(attrs={
                "type": "date",
                "class": "mt-1 block w-full border border-gray-300 rounded-lg shadow-sm px-4 py-3 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-200"
            }),
            "avatar": forms.ClearableFileInput(attrs={
                "class": "mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
            }),
        }

    def clean_birth_date(self):
        b = self.cleaned_data.get("birth_date")
        from datetime import date
        if b and b > date.today():
            raise forms.ValidationError("Birthday cannot be in the future")
        return b
