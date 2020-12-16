from django.shortcuts import render

def index(request):


    data = {
    }

    return render(request, 'base/base.html', context=data)