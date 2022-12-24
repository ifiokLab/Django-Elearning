from django.shortcuts import render,redirect
from django.contrib.auth import login, authenticate
from numpy import kaiser
from .forms import *
from django.urls import reverse_lazy
from django.views.generic.detail import DetailView
from django.shortcuts import redirect, get_object_or_404
from django.views.generic.base import TemplateResponseMixin, View
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.forms.models import modelform_factory
from django.apps import apps
from braces.views import CsrfExemptMixin, JsonRequestResponseMixin
from .models import Course, Module, Content,Categories,myuser
from django.db.models import Count
from django.core.cache import cache
from .forms import ModuleFormSet,TeacherSignUpForm
from django.views.decorators.http import require_http_methods,condition
from django.contrib.auth.models import Group
from students.forms import CourseEnrollForm


# Create your views here.

#def home(request):
   # course = Course.objects.all()
    #return render(request,'Courses/home.html',{'courses':course})

def Teach(request):
    return render(request,'Courses/teach.html',)
    

def TeacherSignupView(request):
    if request.method == 'POST':
        form = TeacherSignUpForm(request.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data.get('email')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(email=email, password=raw_password)
            login(request, user)
            return redirect('home')
    else:
        form = TeacherSignUpForm()
    return render(request, 'Courses/signup.html', {'form': form})

'''
class TeacherSignUpView(CreateView):
    model = myuser
    form_class = TeacherSignUpForm
    template_name = 'Courses/teacher_signup.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'teacher'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        group = Group.objects.get(name='Instructors')
        user.groups.add(group)
        login(self.request, user)
        return redirect('home')
'''

class OwnerMixin(object):
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(owner=self.request.user)

class OwnerEditMixin(object):
    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)



class OwnerCourseMixin(OwnerMixin,LoginRequiredMixin,PermissionRequiredMixin):
    model = Course
    fields = ['category','course_code' ,'title', 'slug', 'overview','thumbnail']
    success_url = reverse_lazy('manage_course_list')


class OwnerCourseEditMixin(OwnerCourseMixin, OwnerEditMixin):
    template_name = 'Courses/manage/Courses/form.html'


class ManageCourseListView(OwnerCourseMixin, ListView):
    template_name = 'Courses/manage/Courses/list.html'
    permission_required = 'Courses.view_course'

class CourseCreateView(OwnerCourseEditMixin, CreateView):
    permission_required = 'Courses.add_course'
    #changes


class CourseUpdateView(OwnerCourseEditMixin, UpdateView):
    permission_required = 'Courses.change_course'


class CourseDeleteView(OwnerCourseMixin, DeleteView):
    template_name = 'Courses/manage/Courses/delete.html'
    permission_required = 'Courses.delete_course'


class CourseModuleUpdateView(TemplateResponseMixin, View):
    template_name = 'Courses/manage/module/formset.html'
    course = None

    def get_formset(self, data=None):
        return ModuleFormSet(instance=self.course,
                             data=data)

    def dispatch(self, request, pk):
        self.course = get_object_or_404(Course,
                                        id=pk,
                                        owner=request.user)
        return super().dispatch(request, pk)

    def get(self, request, *args, **kwargs):
        formset = self.get_formset()
        return self.render_to_response({'course': self.course,
                                        'formset': formset})

    def post(self, request, *args, **kwargs):
        formset = self.get_formset(data=request.POST)
        if formset.is_valid():
            formset.save()
            return redirect('manage_course_list')
        return self.render_to_response({'course': self.course,
                                        'formset': formset})



class ContentCreateUpdateView(TemplateResponseMixin, View):
    module = None
    model = None
    obj = None
    template_name = 'Courses/manage/content/form.html'

    def get_model(self, model_name):
        if model_name in ['text', 'video', 'image', 'file']:
            return apps.get_model(app_label='Courses',
                                  model_name=model_name)
        return None

    def get_form(self, model, *args, **kwargs):
        Form = modelform_factory(model, exclude=['owner',
                                                 'order',
                                                 'created',
                                                 'updated'])
        return Form(*args, **kwargs)

    def dispatch(self, request, module_id, model_name, id=None):
        self.module = get_object_or_404(Module,
                                       id=module_id,
                                       course__owner=request.user)
        self.model = self.get_model(model_name)
        if id:
            self.obj = get_object_or_404(self.model,
                                         id=id,
                                         owner=request.user)
        return super().dispatch(request, module_id, model_name, id)

    def get(self, request, module_id, model_name, id=None):
        form = self.get_form(self.model, instance=self.obj)
        return self.render_to_response({'form': form,
                                        'object': self.obj})

    def post(self, request, module_id, model_name, id=None):
        form = self.get_form(self.model,
                             instance=self.obj,
                             data=request.POST,
                             files=request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.owner = request.user
            obj.save()
            if not id:
                # new content
                Content.objects.create(module=self.module,
                                       item=obj)
            return redirect('module_content_list', self.module.id)

        return self.render_to_response({'form': form,
                                        'object': self.obj})


class ContentDeleteView(View):
    def post(self, request, id):
        content = get_object_or_404(Content,
                                    id=id,
                                    module__course__owner=request.user)
        module = content.module
        content.item.delete()
        content.delete()
        return redirect('module_content_list', module.id)


class ModuleContentListView(TemplateResponseMixin, View):
    template_name = 'Courses/manage/module/content_list.html'

    def get(self, request, module_id):
        module = get_object_or_404(Module,
                                   id=module_id,
                                   course__owner=request.user)

        return self.render_to_response({'module': module})


class ModuleOrderView(CsrfExemptMixin,
                      JsonRequestResponseMixin,
                      View):
    def post(self, request):
        for id, order in self.request_json.items():
            Module.objects.filter(id=id,
                   course__owner=request.user).update(order=order)
        return self.render_json_response({'saved': 'OK'})


class ContentOrderView(CsrfExemptMixin,
                       JsonRequestResponseMixin,
                       View):
    def post(self, request):
        for id, order in self.request_json.items():
            Content.objects.filter(id=id,
                       module__course__owner=request.user) \
                       .update(order=order)
        return self.render_json_response({'saved': 'OK'})


class CourseListView(ListView):#unusedView
    model = Course
    template_name = 'Courses/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user= myuser.objects.filter(id = self.request.user.id)
        print(user)
        
        
        #if 'module_id' in self.kwargs:
            #context['module'] = course.modules.get(id = self.kwargs['module_id'])
        #context['enroll_form'] = CourseEnrollForm(initial={'course':self.object})
        return context
    


class CourseDetailView(DetailView):
    model = Course
    template_name = 'Courses/course_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.get_object()
        context['enroll_form'] = CourseEnrollForm(initial={'course':self.object})
        if 'module_id' in self.kwargs:
            context['module'] = course.modules.get(id = self.kwargs['module_id'])
        #context['enroll_form'] = CourseEnrollForm(initial={'course':self.object})
        return context



#def CourseView(request):
    #return render(request,'Courses/CourseView.html',)


class CourseView(DetailView):
    model = Course
    #template_name = 'Courses/CourseView.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.get_object()
        if 'module_id' in self.kwargs:
            context['module'] = course.modules.get(id = self.kwargs['module_id'])
        #context['enroll_form'] = CourseEnrollForm(initial={'course':self.object})
        return context