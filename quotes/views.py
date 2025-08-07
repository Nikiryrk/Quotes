import json
import random
from django.db.models import F
from django.views.decorators.csrf import csrf_protect
from .models import Quote, Source
from django.http import JsonResponse
from django.shortcuts import render, redirect
from .forms import QuoteForm
from django.views.decorators.http import require_POST
from difflib import SequenceMatcher


def similar(a, b, threshold=0.9):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio() >= threshold
def index(request):
    quote = Quote.objects.raw("""
        SELECT q1.* 
        FROM quotes_quote q1
        JOIN (
            SELECT SUM(weight) AS total FROM quotes_quote
        ) AS totals
        WHERE (
            SELECT SUM(q2.weight) 
            FROM quotes_quote q2 
            WHERE q2.id <= q1.id
        ) >= RAND() * totals.total
        ORDER BY q1.id
        LIMIT 1
    """)[0]

    quote.views += 1
    quote.save()
    return render(request, 'quotes/random_quote.html', {'quote': quote})


def top_quotes(request):
    top_quotes = Quote.objects.order_by('-likes')[:10]
    return render(request, 'quotes/top_quotes.html', {'top_quotes': top_quotes})


@csrf_protect
@require_POST
def rate_quote(request, quote_id):
    try:
        quote = Quote.objects.get(pk=quote_id)
        data = json.loads(request.body.decode('utf-8'))
        if quote.id not in request.session.get('rated_quotes', []):
            if data.get('action') == 'like':
                quote.likes = F('likes') + 1
            elif data.get('action') == 'dislike':
                quote.dislikes = F('dislikes') + 1

            request.session.setdefault('rated_quotes', []).append(quote.id)
            request.session.modified = True
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


def new_quote(request):
    if request.method == 'POST':
        form = QuoteForm(request.POST)
        if form.is_valid():
            new_quote_text = form.cleaned_data['text']

            for existing_quote in Quote.objects.all():
                if similar(new_quote_text, existing_quote.text):
                    form.add_error('text', 'Такая цитата уже существует!')
                    return render(request, 'quotes/new_quote.html', {'form': form})

            form.save()
            return redirect('index')
    else:
        form = QuoteForm()

    return render(request, 'quotes/new_quote.html', {'form': form})