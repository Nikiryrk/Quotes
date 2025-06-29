from django.shortcuts import render
from .models import Quote
import random
# Create your views here.
def index(request):
    quotes = list(Quote.objects.all())
    weights = [q.weight for q in quotes]
    random_quote = random.choices(quotes, weights=weights, k=1)[0]

    random_quote.views += 1
    random_quote.save()

    return render(request, 'quotes/random_quote.html', {'quote': random_quote})