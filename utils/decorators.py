from functools import wraps

from rest_framework import status
from rest_framework.response import Response


def required_params(method='GET', params=None):
    '''
    When we use @required_params(params=['some_param']), it will return a
    decorator function. The params for decorator function is the params wrapped
    by @required_params.
    '''
    if params is None:
        params = []

    def decorator(view_func):
        '''
        decorator 函数通过 wraps 来将 func 里的参数解析出来传给 _wrapped_view
        这里的 instance 参数其实就是在 func 里的 self
        '''
        @wraps(view_func)
        def _wrapped_view(instance, request, *args, **kwargs):
            if method == 'GET':
                data = request.query_params
            else:
                data = request.data

            for param in params:
                if param not in data:
                    return Response({
                        'message': f'missing {param} in request',
                        'success': False,
                    }, status=status.HTTP_400_BAD_REQUEST)

            return view_func(instance, request, *args, **kwargs)
        return _wrapped_view
    return decorator
