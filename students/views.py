from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, FormView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from Courses.models import Course
from .forms import CourseEnrollForm
from django.shortcuts import render,redirect
from Courses.forms import StudentSignUpForm



def StudentSignup(request):
    if request.method == 'POST':
        form = StudentSignUpForm(request.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data.get('email')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(email=email, password=raw_password)
            login(request, user)
            return redirect('home')
    else:
        form = StudentSignUpForm()
    return render(request, 'students/student/registration.html', {'form': form})


class StudentEnrollCourseView(LoginRequiredMixin, FormView):
    course = None
    form_class = CourseEnrollForm
    #template_name = 'students/course/list.html'

    def form_valid(self, form):
        self.course = form.cleaned_data['course']
        self.course.students.add(self.request.user)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('student_course_list')


class StudentCourseListView(LoginRequiredMixin, ListView):#done
    model = Course
    template_name = 'students/course/list.html'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(students__in=[self.request.user])


class StudentCourseDetailView(DetailView):
    model = Course
    template_name = 'students/course/CourseView.html'
    #template_name = 'students/course/detail.html'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(students__in=[self.request.user])

    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # get course object
        course = self.get_object()
        if ('module_id' in self.kwargs) and ('content_id' in self.kwargs):
            # get current module
            context['module'] = course.modules.get(id=self.kwargs['module_id'])
            modx = course.modules.get(id=self.kwargs['module_id'])
            context['mod'] = modx.contents.get(id= self.kwargs['content_id'])
        else:
            # get first module
            mod= course.modules.all()[0]
            try:
                modx = course.modules.get(id=mod.id)
                contents = modx.contents.get(id = modx.id)
            except:
                context['mod'] = mod
            else:
                context['mod'] = modx.contents.get(id= contents.id)
    
            
            #context['mod'] = modx.contents.get(id= self.kwargs['content_id'])[0]
        return context



