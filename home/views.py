from django.views.generic import CreateView
from .models import GLTImage

class CreateGLTF(CreateView):
    model = GLTImage
    fields = '__all__'
    template_name = 'home/upload_page.html'
    success_url = '/'