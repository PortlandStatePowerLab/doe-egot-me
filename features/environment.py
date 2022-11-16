from behave import *
import ModelController

def before_all(context):
    try:
        ModelController.main(test_mode=True)
    except SystemExit:
        pass