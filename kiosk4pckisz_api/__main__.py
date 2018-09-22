from logging import basicConfig, INFO

from kiosk4pckisz_api.lambda_function import lambda_handler

basicConfig(level=INFO)
print(lambda_handler())
