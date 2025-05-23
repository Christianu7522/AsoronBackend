from django.http import JsonResponse


def block_direct_access(get_response):
    def middleware(request):
        allowed_origin = ['https://asoron.netlify.app']

        request_origin = request.headers.get('Origin')

        if request_origin in allowed_origin:
            return get_response(request)


        return JsonResponse({'error': 'Acceso no permitido'}, status=403)

    return middleware
