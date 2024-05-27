from django.views.generic import CreateView
from .models import GLTF_Plus_Image

class CreateGLTF(CreateView):
    model = GLTF_Plus_Image
    fields = '__all__'
    template_name = 'home/upload_page.html'
    success_url = '/upload'