import json

from django import forms
from django.http import HttpResponse, JsonResponse
from django.views import View

from django.contrib.auth import authenticate, login

from django.views.decorators.csrf import csrf_exempt
from django.forms.models import model_to_dict
from django.utils.decorators import method_decorator
from django.core.validators import RegexValidator

from .models import Item, Review

validator = RegexValidator(r"\D")

class ProductValidator(forms.Form):
    title = forms.CharField(max_length=64, validators=[validator])
    description = forms.CharField(max_length=1024, validators=[validator])
    price = forms.IntegerField(min_value=1, max_value=1000000)



class ReviewValidator(forms.Form):
    text = forms.CharField(max_length=1024, validators=[validator])
    grade = forms.IntegerField(min_value=1, max_value=10)



@method_decorator(csrf_exempt, name='dispatch')
class AddItemView(View):

    def post(self, request):
        # Здесь должен быть ваш код
        coded_str = request.headers['authorization'].split()[1]
        decoded_str = base64.b64decode(coded_str).decode('utf-8')
        username, password = decoded_str.split(':')
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_staff:
                try:
                    request_data: dict = json.loads(request.body.decode('utf-8'))
                except:
                    return JsonResponse(data={}, status=400)

                form: object = ProductValidator(request_data)
                if form.is_valid():
                    form_data: dict = form.cleaned_data
                    created_item: object = Item.objects.create(**form_data)
                    data: dict = {'id': created_item.pk}
                    return JsonResponse(data, status=201)
                return JsonResponse(data={}, status=400)
            return JsonResponse({}, status=403)
        return JsonResponse({}, status=401)


        


@method_decorator(csrf_exempt, name='dispatch')
class PostReviewView(View):

    def post(self, request, item_id):
        # Здесь должен быть ваш код
        try:
            item = Item.objects.get(id=item_id)
        except Item.DoesNotExist:
            return JsonResponse(data={}, status=404)

        try:
            request_data: dict = json.loads(request.body.decode('utf-8'))
        except:
            return JsonResponse(data={}, status=400)

        form: object = ReviewValidator(request_data)
        if form.is_valid():
            form_data: dict = form.cleaned_data
            form_data['item'] = item
            created_item: object = Review.objects.create(**form_data)
            data: dict = {'id': created_item.pk}
            return JsonResponse(data, status=201)
        return JsonResponse(data={}, status=400)
        


class GetItemView(View):
    """View для получения информации о товаре.

    Помимо основной информации выдает последние отзывы о товаре, не более 5
    штук.
    """

    def get(self, request, item_id):
        try:
            item = Item.objects.prefetch_related('review_set').get(id=item_id)
        except Item.DoesNotExist:
            return JsonResponse(status=404, data={})
        item_dict = model_to_dict(item)
        item_reviews = [model_to_dict(x) for x in item.review_set.all()]
        item_reviews = sorted(
            item_reviews, key=lambda review: review['id'], reverse=True)[:5]
        for review in item_reviews:
            review.pop('item', None)
        item_dict['reviews'] = item_reviews
        return JsonResponse(item_dict, status=200)
