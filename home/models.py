from django.db import models

from wagtail.images.models import Image, AbstractImage, AbstractRendition, IMAGE_FORMAT_EXTENSIONS, WagtailImageFieldFile
from wagtail.models import Page
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from django.forms import ImageField
from home.utilities import upload_glt

from io import BytesIO

# Add format type 
IMAGE_FORMAT_EXTENSIONS = IMAGE_FORMAT_EXTENSIONS.update(gltf=".gltf", glb=".glb")


class HomePage(Page):
    pass

class GLTImageFieldFile(WagtailImageFieldFile):
    """
    Override the ImageFieldFile in order to use Willow instead
    of Pillow.

    TODO: Override get_image_dimensions ? 
    """
    pass


def glt_plus_get_available_image_extensions():
    """_summary_
    PIL and GLT file extensions
    Returns:
        _type_: _description_
    """
    try:
        from PIL import Image
        # TODO: from pygltflib import something that references all file types
    except ImportError:
        return []
    else:
        Image.init()
        # TODO: add all the file types in the GLT file as well then return
        # TODO: remove 'glb' added to the end and make this programatic
        return [ext.lower()[1:] for ext in Image.EXTENSION].add('glb')

        

def glt_plus_validator(value):
    """
    Validates existing image formats and glt file formats
    """
    return FileExtensionValidator(allowed_extensions=glt_plus_get_available_image_extensions())(
        value
    )

class GLTImageFieldForm(ImageField):
    default_validators = [glt_plus_validator]
    def to_python(self, data):
        """
        Check that the file-upload field data contains a valid image GLT since (GIF, JPG,
        PNG, etc. -- what Pillow supports).
        """
        f = super().to_python(data)
        if f is None:
            return None

        # We need to get a file object for Pillow. We might have a path or we might
        # have to read the data into memory.
        if hasattr(data, "temporary_file_path"):
            file = data.temporary_file_path()
        else:
            if hasattr(data, "read"):
                file = BytesIO(data.read())
            else:
                file = BytesIO(data["content"])

        try:
            # load() could spot a truncated JPEG, but it loads the entire
            # image in memory, which is a DoS vector. See #3848 and #18520.
            # image = Image.open(file)
            image = upload_glt(file)
            # verify() must be called immediately after the constructor.
            image.verify()

            # Annotating so subclasses can reuse it for their own validation
            f.image = image
            # Pillow doesn't detect the MIME type of all formats. In those
            # cases, content_type will be None.
            # TODO: make sure to add the content_type file type - this line will likely trip us up
            f.content_type = Image.MIME.get(image.format)
        except Exception as exc:
            # Pillow doesn't recognize it as an image.
            raise ValidationError(
                self.error_messages["invalid_image"],
                code="invalid_image",
            ) from exc
        if hasattr(f, "seek") and callable(f.seek):
            f.seek(0)
        return f
        pass


class GLTImageField(models.ImageField):
    """
    Override the attr_class on the Django ImageField Model to inject our ImageFieldFile
    with GLT support.
    """
    def formfield(self, **kwargs):
        return super().formfield(
            **{
                "form_class": GLTImageFieldForm,
                **kwargs,
            }
        )
    attr_class = GLTImageFieldFile

# https://docs.wagtail.org/en/stable/advanced_topics/images/custom_image_model.html
# 3D Image model
class GLTImage(AbstractImage):
    # Add any extra fields for images here
    file = GLTImageField()
    context = models.CharField(max_length=255)
    admin_form_fields = Image.admin_form_fields + (
        # Add the fields for images here 
        'context',
    )

class CustomRendition(AbstractRendition):
    image = models.ForeignKey(GLTImage, on_delete=models.CASCADE, related_name='glt_render' )

    class Meta:
        unique_together = (
            ('image', 'filter_spec', 'focal_point_key'),
        )