from django.shortcuts import render
from .forms import UserForm
from .calculate import calculate
from django.http import HttpResponse
from django.template.response import TemplateResponse


def index(request):
    if request.method == "POST":
        id = request.POST.get("id")
        month = int(request.POST.get("month"))
        year = int(request.POST.get("year"))

        result = calculate(id, month, year)
        context = {'result': result}
        return render(request, 'index2.html', context)
    else:
        userform = UserForm()
        return render(request, "index.html", {"form": userform})