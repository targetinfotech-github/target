import time
import logging
from functools import wraps
from icecream import ic
# # Configure logging
# logger = logging.getLogger(__name__)
# logger.setLevel(logging.INFO)
# handler = logging.StreamHandler()  # Or use FileHandler to log to a file
# handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
# logger.addHandler(handler)

def measure_execution_time(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        start_time = time.time()
        response = view_func(request, *args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time

        ic(f'Execution time for {view_func.__name__}: {execution_time:.4f} seconds')
        return response
    return _wrapped_view
