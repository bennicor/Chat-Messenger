import json
from django.shortcuts import render
from django.http import HttpResponseNotAllowed, HttpResponse


# Create your views here.
def lobby(request):
    return render(request, "chat/lobby.html")

def update_session(request):
    if not request.method=='POST':
        return HttpResponseNotAllowed(['POST'])

    # Update django session object with js arbitary data
    content = json.loads(request.body)
    for key, val in content.items():
        request.session[key] = val

    return HttpResponse("OK")
