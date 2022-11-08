from django.shortcuts import render

def index(request):
    # Initialize new session object
    if "group_name" not in request.session:
        request.session["group_name"] = ""
    return render(request, "chat/index.html")
