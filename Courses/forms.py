from django.contrib.auth.forms import UserCreationForm, UserChangeForm,AuthenticationForm
from django import forms
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from .models import Course, Module,myuser
from django.forms.models import inlineformset_factory
from django.contrib.auth.models import Group


ModuleFormSet = inlineformset_factory(Course,Module,fields=['title','description'],extra=2,can_delete=True)

class StudentSignUpForm(UserCreationForm):
    #password1 =forms.CharField(max_length=200, widget=forms.PasswordInput(),label='Confirm Password')
    #password =forms.CharField(max_length=200, widget=forms.PasswordInput(), label='Password')

    def __init__(self, *args, **kwargs):
        super(StudentSignUpForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs['placeholder'] = self.fields['email'].label
        self.fields['first_name'].widget.attrs['placeholder'] = self.fields['first_name'].label
        self.fields['last_name'].widget.attrs['placeholder'] = self.fields['last_name'].label
        self.fields['password1'].widget.attrs['placeholder'] = self.fields['password1'].label
        self.fields['password2'].widget.attrs['placeholder'] = self.fields['password2'].label


    class Meta:
        model = myuser
        fields = ('email','first_name','last_name','Department','password1','password2')

    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_student = True
        if commit:
            user.save()
        return user


class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = myuser
        fields = ('email','first_name','last_name','Department')

class StudentLoginForm(AuthenticationForm):
    username = forms.EmailField(label='Email',widget=forms.TextInput(attrs={'placeholder': 'Email'}))
    password = forms.CharField(max_length=32, widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))


class TeacherLoginForm(AuthenticationForm):
    username = forms.EmailField(label='Email',widget=forms.TextInput(attrs={'placeholder': 'Email'}))
    password = forms.CharField(max_length=32, widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))

    error_messages = {
        **AuthenticationForm.error_messages,
        'invalid_login': _(
            "Please enter the correct Email and password for a staff "
            "account. Note that both fields may be case-sensitive."
        ),
    }
    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if not user.is_teacher:
            raise ValidationError(
                self.error_messages['invalid_login'],
                code='invalid_login',
                params={'username': self.username_field.verbose_name}
            )


class TeacherSignUpForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(TeacherSignUpForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs['placeholder'] = self.fields['email'].label
        self.fields['first_name'].widget.attrs['placeholder'] = self.fields['first_name'].label
        self.fields['last_name'].widget.attrs['placeholder'] = self.fields['last_name'].label
        self.fields['password1'].widget.attrs['placeholder'] = self.fields['password1'].label
        self.fields['password2'].widget.attrs['placeholder'] = self.fields['password2'].label

    class Meta:
        model = myuser
        fields = ('email','first_name','last_name','Department','password1','password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_teacher = True
       
        if commit:
            user.save()
            group = Group.objects.get(name='Instructors')
            user.groups.add(group)
        return user