from utils.auth import verify
from functools import wraps
from django.http import Http404
from django.http import HttpResponseRedirect

def some_decorator(*args):
    print("args", args)

    def decorator(function):
        def wrapper(request, *args, **kwargs):
            if 1==1:
                return function(request, *args, **kwargs)
            raise Http404

        return wrapper

    return decorator