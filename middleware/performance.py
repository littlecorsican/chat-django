import time

# THIS MEASURES THE PERFORMANCE OF THE WRAPPED FUNCTION

def measure_performance(get_response):
    # One-time configuration and initialization.

    def middleware(request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        start_time = time.time()
        response = get_response(request)
        print("--- %s seconds ---" % (time.time() - start_time))
        # Code to be executed for each request/response after
        # the view is called.

        return response

    return middleware