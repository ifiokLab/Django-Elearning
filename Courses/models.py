from distutils.command.upload import upload
from email.policy import default
from tabnanny import verbose
from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from matplotlib.image import thumbnail
from .fields import OrderField
from .managers import CustomUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin



level = [
    ('100','100'),
    ('200','200'),
    ('300','300'),
    ('400','400'),
    ('500','500'),
    ('spill','spill'),
]

department = [
    ('Agric Engineering','Agric Engineering'),
    ('Mechanical Engineering','Mechanical Engineering'),
    ('Chemical Engineering','Chemical Engineering'),
    ('Petroluem Engineering','Petroluem Engineering'),
    ('Civil Engineering','Civil Engineering'),
    ('Electrical Engineering','Electrical Engineering'),
    ('Computer Engineering','Computer Engineering'),
    ('Food Engineering','Food Engineering'),
]

class myuser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=40,blank=False)
    last_name = models.CharField(max_length=40,blank=False)
    Department = models.CharField(max_length=100,choices=department)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_student = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)

     
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name','last_name','Department',]
    objects = CustomUserManager()

    def __str__(self):
        return f'{self.first_name} {self.last_name}'



class Student(models.Model):
    student = models.OneToOneField(myuser,on_delete=models.CASCADE)
    Reg_no = models.CharField(max_length=40)
    Level = models.CharField(max_length=100,choices=level)

class Lecturers(models.Model):
    lecturer = models.OneToOneField(myuser,on_delete=models.CASCADE)
     
    class Meta:
        verbose_name_plural = 'Lecturers'
        



class Categories(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        ordering = ['title']
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.title


class Course(models.Model):
    owner = models.ForeignKey(myuser, related_name='courses_created',on_delete=models.CASCADE)
    students = models.ManyToManyField(myuser,related_name='courses_joined', blank=True)
    category = models.ForeignKey(Categories,related_name='courses',on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    thumbnail = models.ImageField(upload_to ='thumbnail')
    course_code = models.CharField(max_length=200 )
    slug = models.SlugField(max_length=200, unique=True)
    overview = models.CharField(max_length=100)
    description = models.TextField(null=True)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(null=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.title

class Requirements(models.Model):
    course = models.ForeignKey(Course, related_name='requirements',on_delete=models.CASCADE)
    title = models.CharField(max_length=60)

class Module(models.Model):
    course = models.ForeignKey(Course, related_name='modules',on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = OrderField(blank=True, for_fields=['course'])
    
    
    def __str__(self):
        return f'{self.order}. {self.title}'

    class Meta:
        ordering = ['order']


class Content(models.Model):
    module = models.ForeignKey(Module, related_name='contents',on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType,on_delete=models.CASCADE,limit_choices_to={'model__in':('text','video','image', 'file')})
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey('content_type', 'object_id')
    order = OrderField(blank=True, for_fields=['module'])

    class Meta:
        ordering = ['order']


from django.template.loader import render_to_string
class ItemBase(models.Model):
    owner = models.ForeignKey(myuser, related_name='%(class)s_related',on_delete=models.CASCADE)
    title = models.CharField(max_length=250)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.title

    def render(self):
        return render_to_string(f'students/course/content/{self._meta.model_name}.html', {'item': self})

   

class Text(ItemBase):
    content = models.TextField()

class File(ItemBase):
    file = models.FileField(upload_to='files')

class Image(ItemBase):
    file = models.FileField(upload_to='images')

class Video(ItemBase):
    url = models.URLField()