# Browse XR

Repo to demonstrate XR functionality in WagtailCMS. 

> 🏆 Goal: support XR galleries as a WagtailCMS package.

## Requirements
- Python 3.12
- Wagtail 6.1
- pygltflib 1.16.2
- aframe.io 1.6.0 CDN in template

## Get Started
1. clone the repository
2. `pip install -r requirements.txt`
3. `python manage.py migrate`
4. `python manage.py runserver`
5. go to localhost:8000/upload in your browser to upload a file
6. go to localhost:8000/gallery in your browser to see your gallery of uploaded files

## Thank you
[Augmented Reality Design and Development](https://ardd.tech) and [CMD Limes - Python Agency](https://cmdlimes.com) - the agencies in collaboration that made this demo happen.

Also, thank you to Pillow, Puput that inspired some of the forthcoming development decsions in the package.

-----
## About XR + Wagtail

### What is Wagtail
[Wagtail CMS](https://wagtail.org) is the leading open-source Python CMS used by NHS, Google, MIT, The Wharton School at The University of Pennsylvania. It gives an intuitive interface out of the box that gives control to the editor for content. Its extensible in Python, on top of Django, to allow your app to remain Pythonic and support common web patterns easily while keeping it tightly coupled to the Wagtail admin interface.

This demo was first created for [Wagtail Space US 2024]().

### What is WebXR and A-Frame?
[WebXR](https://developer.mozilla.org/en-US/docs/Web/API/WebXR_Device_API/Fundamentals) is a Web API that describes support for accessing Augmented reality and virtual relaity devices -- including your browser. These are standards defined by the W3C groups, the Immersive Web Community Group and the Immersive Web Working Group. 

[A-Frame](https://aframe.io/) [1.6.0](https://aframe.io/docs/1.6.0/) is a web framework for building virtual reality experiences and helps integrate on top of HTML. It is the leading framework as of the development of this application. It includes a 3D scene graph represented in mark up language, as well as a composable structure to three.js declaratively. This demo is focused on web use case but it supports most VR headsets like Vive, Rift, Windows Mixed Reality, Cardboard, Oculus Go and can be used for Augmented Reality; where a camera is engaged and 3D forms are overlayed on video input. 

## How it works
You'll want to start with a 3D asset `.glb`, `.gltf`, `.gltk` file type. There are many mobile apps that can help you with this. For the purposes of testing, we've used [Polycam](https://poly.cam/) which uses LiDAR scanning and photogrammetry technology on iPhon or Android devices. They also provide [free 3D models](https://poly.cam/explore) that you can explore shared by their community.

The file is uploaded as an AbstractImage file and supports standard image file formats with the same uploader. The gallery blocks in html will adjust the mark up based off of the file type.

```python models.py
# https://docs.wagtail.org/en/stable/advanced_topics/images/custom_image_model.html
# 3D Image model
class GLTF_Plus_Image(AbstractImage):
    # Add any extra fields for images here
    width = models.IntegerField(verbose_name=_("width"), editable=False, default=1024)
    height = models.IntegerField(verbose_name=_("height"), editable=False, default=1024)
    file = GLTF_Plus_ImageField()
    # primitives field will have multiple primitives in the future 
    scene = scene_info_here
    primitive = primitive_info_here
    context = models.CharField(max_length=255)
    admin_form_fields = Image.admin_form_fields + (
        'scene',
        'primitive',
        'context',
        # more to come
    )
```


## TODO

- [ ] Enable Aframe functionality in the Wagtail admin
    - [ ] [environment](https://github.com/supermedium/aframe-environment-component)
    - [ ] [state](https://npmjs.com/package/aframe-state-component)
    - [ ] [particle systems](https://github.com/IdeaSpaceVR/aframe-particle-system-component)
    - [ ] [physics](https://github.com/n5ro/aframe-physics-system)
    - [ ] [multiuser](https://github.com/networked-aframe/networked-aframe)
    - [ ] [oceans](https://github.com/n5ro/aframe-extras/tree/master/src/primitives)
    - [ ] [teleportation](https://github.com/fernandojsg/aframe-teleport-controls)
    - [ ] [super hands](https://github.com/wmurphyrd/aframe-super-hands-component)
    - [ ] [augmented reality](https://github.com/jeromeetienne/AR.js#augmented-reality-for-the-web-in-less-than-10-lines-of-html)
    - [ ] create better gallery block for standard and 3D image assets
- [ ] Frontend browse
- [ ] add Node interpreter and remove Aframe CDN
- [ ] Platforms other than the browser
- [ ] Perfromance benchmarks for development and testing
- [ ] Front end testing with Playwright
- [x] SQLite
- [ ] PostgreSQL

## With VS Code
