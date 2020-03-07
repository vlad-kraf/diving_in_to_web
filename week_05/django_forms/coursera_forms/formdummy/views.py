from django.shortcuts import render
import json
from jsonschema import validate
from jsonschema.exeptions import ValidationError
from django.views import View
from .forms import DummyForm
from .schemas import REVIEW_CHEMA

class FormDummyView(View):

    def get(self, request):
        form = DummyForm()
        return render(request, 'form.html', {'form': form})

    def post(self, request):
        form = DummyForm(request.POST)

        if form.is_valid():
            context = form.cleaned_data
            return render(request, 'form.html', context)
        else:
            return render(request, 'error.html', {'error': form.errors})


class SchemaView(View):

    def post(self, request):
        if form.is_valid():
            context = form.cleaned_data
            return render(request, 'form.html', context)
        else:
            return render(request, 'error.html', {'error': form.errors})