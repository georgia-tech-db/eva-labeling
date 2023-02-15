from django.shortcuts import render, HttpResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .utils import add_to_eva

# Create your views here.


@api_view(["POST"])
def task_created(request):
    """
    If any video is added, upload it to EVA DB
    """
    print(request.method, "\n\n", request.data, "\n")
    if request.data["action"] == "TASKS_CREATED":
        print("Tasks were created")
        add_to_eva(request.data)
    if request.data["action"] == "TASKS_DELETED":
        print("Tasks were deleted")
    return HttpResponse({"result": "success"})

@api_view(["GET"])
def other_tasks(request):

    print(request)
    return HttpResponse("everything ok")