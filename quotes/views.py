import json

from django.db.models import F
from django.shortcuts import render
from .models import Quote
import random
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import JsonResponse
# Create your views here.
def index(request):
    quotes = list(Quote.objects.all())
    weights = [q.weight for q in quotes]
    random_quote = random.choices(quotes, weights=weights, k=1)[0]

    random_quote.views += 1
    random_quote.save()

    return render(request, 'quotes/random_quote.html', {'quote': random_quote})

def top_quotes(request):
    top_quotes = Quote.objects.order_by('-likes')[:10]  # Топ-10 по лайкам
    return render(request, 'quotes/top_quotes.html', {'top_quotes': top_quotes})


@csrf_exempt
@require_POST
def rate_quote(request, quote_id):
    try:
        quote = Quote.objects.get(pk=quote_id)
        data = json.loads(request.body.decode('utf-8'))

        if data.get('action') == 'like':
            quote.likes = F('likes') + 1
        elif data.get('action') == 'dislike':
            quote.dislikes = F('dislikes') + 1

        quote.save(update_fields=['likes', 'dislikes'])
        quote.refresh_from_db()

        return JsonResponse({
            'status': 'success',
            'likes': quote.likes,
            'dislikes': quote.dislikes
        })
    except Quote.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Цитата не найдена'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)