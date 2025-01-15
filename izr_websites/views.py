from django.shortcuts import render


def index_sarah_website(request):
    return render(request, "sarahfoudhaili/index.html")


# View for website 2
def index_izr_website(request):
    return render(request, "izr/index.html")


# View for website 3
def index_izr_screen(request):
    return render(request, "izr_screen/index.html")
