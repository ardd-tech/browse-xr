import os
import sys
import json

from django.template.response import TemplateResponse

from pygltflib import GLTF2, BufferFormat

def upload_glt(request, image_file, scene):
    gltf = GLTF2().load(image_file)
    if scene:
        gltf.scenes.append(scene)
    gltf.convert_buffers(BufferFormat.BINARYBLOB) # convert buffers to GLB blob
    gltf.save()
    gltf_context = ''
    return TemplateResponse(
        request,
        "upload_page.html",
        {
            "glt_image": gltf,
            "glt_context": gltf_context,
        }
    )