from django.views.generic import CreateView, DetailView, ListView
from wagtail.images.models import Image
from .models import GLTF_Plus_Image


class CreateGLTF(CreateView):
    model = GLTF_Plus_Image
    fields = '__all__'
    template_name = 'home/upload_page.html'
    success_url = '/upload'

class DetailGLTF(DetailView):
    model = GLTF_Plus_Image
    template_name = 'home/gltf_detail.html'
    context_object_name = 'gltf'

class ListGLTF(ListView):
    model = GLTF_Plus_Image
    template_name = 'home/gltf_gallery.html'
    context_object_name = 'gltfs'


class CreateImage(CreateView):
    model = Image
    fields = '__all__'
    template_name = 'home/upload_page.html'
    success_url = '/upload-image'