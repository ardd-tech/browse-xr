from django.db import models
from django.core import checks
from wagtail.images.models import Image, AbstractImage, AbstractRendition, IMAGE_FORMAT_EXTENSIONS, WagtailImageFieldFile
from wagtail.models import Page
from django.db.models.fields.files import FileDescriptor
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from django.forms import ImageField, FileField
from home.utilities import upload_glt

from django.utils.translation import gettext_lazy as _

from io import BytesIO

from pathlib import Path

from pygltflib import GLTF2, BufferFormat

# Add format type 
# TODO: I don't think this is currently being used
IMAGE_FORMAT_EXTENSIONS = IMAGE_FORMAT_EXTENSIONS.update(gltf=".gltf", glb=".glb")
GLTF_EXTENSIONS = {
    "gltf": ".gltf",
    "glk": ".glk",
    "glb": ".glb",
}

GLTF_MIME = {
    "gltf": "model/gltf+json",
    "glk": "model/gltf+json",
    "glb": "model/gltf-binary", 
    "bin": "application/octet-stream",
}

class HomePage(Page):
    # TODO: Create ecommerce frontend on the homepage
    pass

class GLTF_Plus_ImageFieldFile(WagtailImageFieldFile):
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
        return [ext.lower()[1:] for ext in Image.EXTENSION].append('glb')

        

def glt_plus_validator(value):
    """
    Validates existing image formats and glt file formats
    """
    return FileExtensionValidator(allowed_extensions=glt_plus_get_available_image_extensions())(
        value
    )

class GLTF_Plus_ImageFieldForm(FileField):
    default_validators = [glt_plus_validator]
    # ImageField
    default_error_messages = {
        "invalid_image": (
            "Upload a valid 3D or 2D image. The file you uploaded was either not an "
            "image or a corrupted image."
        ),
    }
    def to_python(self, data):
        """
        Check that the file-upload field data contains a valid image GLT since (GIF, JPG,
        PNG, etc. -- what Pillow supports).
        """
        import pdb; pdb.set_trace()
        print(data)
        f = super().to_python(data)
        if f is None:
            return None

        from PIL import Image

        # We need to get a file object for Pillow. We might have a path or we might
        # have to read the data into memory.
        if hasattr(data, "temporary_file_path"):
            file = data.temporary_file_path()
        else:
            if hasattr(data, "read"):
                file = BytesIO(data.read())
            else:
                file = BytesIO(data["content"])
        print(file)
        try:
            # load() could spot a truncated JPEG, but it loads the entire
            # image in memory, which is a DoS vector. See #3848 and #18520.
            # TODO: if file path is regular image else glt use upload_glt
            # TODO: move this to something cleaner and more reusable
            extension = Path(data.name).suffix[1:].lower()
            if extension in [ext.lower() for ext in GLTF_EXTENSIONS]:
                # why does it need to be opened if we have the
                image = GLTF2().load(file)
                image.convert_buffers(BufferFormat.BINARYBLOB) # convert buffers to GLB blob
                f.content_type = GLTF_MIME.get(extension, None)
            else:
                image = Image.open(file)
                # verify() must be called immediately after the constructor.
                image.verify()
                f.content_type = Image.MIME.get(image.format)

            # Annotating so subclasses can reuse it for their own validation
            f.image = image
            # Pillow doesn't detect the MIME type of all formats. In those
            # cases, content_type will be None.
            # TODO: make sure to add the content_type file type - this line will likely trip us up
            
        except Exception as exc:
            # Pillow doesn't recognize it as an image.
            raise ValidationError(
                self.error_messages["invalid_image"],
                code="invalid_image",
            ) from exc
        if hasattr(f, "seek") and callable(f.seek):
            f.seek(0)
        return f

class GLTF_Plus_FileDescriptor(FileDescriptor):
    """
    Just like the FileDescriptor, but for GLTF_Plus_ImageFields. The only difference is
    assigning the width/height to the width_field/height_field, if appropriate.
    """
    def __set__(self, instance, value):
        previous_file = instance.__dict__.get(self.field.attname)
        super().__set__(instance, value)

        # To prevent recalculating image dimensions when we are instantiating
        # an object from the database (bug #11084), only update dimensions if
        # the field had a value before this assignment.  Since the default
        # value for FileField subclasses is an instance of field.attr_class,
        # previous_file will only be None when we are called from
        # Model.__init__().  The ImageField.update_dimension_fields method
        # hooked up to the post_init signal handles the Model.__init__() cases.
        # Assignment happening outside of Model.__init__() will trigger the
        # update right here.
        if previous_file is not None:
            self.field.update_dimension_fields(instance, force=True)


class GLTF_Plus_ImageField(models.FileField):
    """
    Override the attr_class on the Django ImageField Model to inject our ImageFieldFile
    with GLT support.
    """
    attr_class = GLTF_Plus_ImageFieldFile
    descriptor_class = GLTF_Plus_FileDescriptor
    description = _("3D Image")
    def __init__(
        self,
        verbose_name=None,
        name=None,
        **kwargs,
    ):
        super().__init__(verbose_name, name, **kwargs)

    def check(self, **kwargs):
        return [
            *super().check(**kwargs),
            *self._check_gltf_library_installed(),
        ]

    def _check_gltf_library_installed(self):
        try:
            from pygltflib import GLTF2  # NOQA
        except ImportError:
            return [
                checks.Error(
                    "Cannot use GLTF_Plus_ImageField because pygltflib is not installed.",
                    hint=(
                        "Get pygltflib at https://pypi.org/project/pygltflib/ "
                        'or run command "python -m pip install pygltflib".'
                    ),
                    obj=self,
                    id="fields.E210",
                )
            ]
        else:
            return []

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        return name, path, args, kwargs

    def contribute_to_class(self, cls, name, **kwargs):
        super().contribute_to_class(cls, name, **kwargs)
        pass

    def update_dimension_fields(self, instance, force=False, *args, **kwargs):
        """
        Update field's width and height fields, if defined.

        This method is hooked up to model's post_init signal to update
        dimensions after instantiating a model instance.  However, dimensions
        won't be updated if the dimensions fields are already populated.  This
        avoids unnecessary recalculation when loading an object from the
        database.

        Dimensions can be forced to update with force=True, which is how
        ImageFileDescriptor.__set__ calls this method.
        """
        pass

    def formfield(self, **kwargs):
        return super().formfield(
            **{
                "form_class": GLTF_Plus_ImageFieldForm,
                **kwargs,
            }
        )
    

# https://docs.wagtail.org/en/stable/advanced_topics/images/custom_image_model.html
# 3D Image model
class GLTF_Plus_Image(AbstractImage):
    # Add any extra fields for images here
    width = models.IntegerField(verbose_name=_("width"), editable=False, default=1024)
    height = models.IntegerField(verbose_name=_("height"), editable=False, default=1024)
    file = GLTF_Plus_ImageField()
    context = models.CharField(max_length=255)
    admin_form_fields = Image.admin_form_fields + (
        # Add the fields for images here 
        'context',
    )

class CustomRendition(AbstractRendition):
    image = models.ForeignKey(GLTF_Plus_Image, on_delete=models.CASCADE, related_name='glt_render' )

    class Meta:
        unique_together = (
            ('image', 'filter_spec', 'focal_point_key'),
        )