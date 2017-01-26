import os
import json
from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.core.files.storage import default_storage
from django.http import HttpResponse
from django.utils.text import slugify
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .image import resize, get_sizes
from .forms import FileForm


UPLOAD_PATH = getattr(settings, 'AJAXIMAGE_DIR', 'ajaximage/')
AUTH_TEST = getattr(settings, 'AJAXIMAGE_AUTH_TEST', lambda u: u.is_staff)
FILENAME_NORMALIZER = getattr(settings, 'AJAXIMAGE_FILENAME_NORMALIZER', slugify)


@require_POST
@user_passes_test(AUTH_TEST)
def ajaximage(request, upload_to=None, max_width=None, max_height=None, crop=None, form_class=FileForm,
              valid_width=None, valid_height=None):
    form = form_class(request.POST, request.FILES)
    if form.is_valid():
        file_ = form.cleaned_data['file']

        image_types = ['image/png', 'image/jpg', 'image/jpeg', 'image/pjpeg',
                       'image/gif']

        if file_.content_type not in image_types:
            data = json.dumps({'error': 'Bad image format.'})
            return HttpResponse(data, content_type="application/json", status=403)

        valid_width, valid_height = int(valid_width or 0), int(valid_height or 0)
        width, height = get_sizes(file_)

        if (valid_width and valid_width != width) or (valid_height and valid_height != height):
            data = json.dumps({'error': 'Bad image size: %sx%s is required' % (valid_width, valid_height)})
            return HttpResponse(data, content_type="application/json", status=405)

        file_ = resize(file_, max_width, max_height, crop)
        file_name, extension = os.path.splitext(file_.name)
        safe_name = '{0}{1}'.format(FILENAME_NORMALIZER(file_name), extension)

        name = os.path.join(upload_to or UPLOAD_PATH, safe_name)
        path = default_storage.save(name, file_)
        url = default_storage.url(path)

        return HttpResponse(json.dumps({'url': url, 'filename': path}), content_type="application/json")

    return HttpResponse(status=403)
