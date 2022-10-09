from django.shortcuts import render

# Create your views here.
def lobby(request):
    if "group_name" not in request.session:
        request.session["group_name"] = ""
    return render(request, "chat/lobby.html")
