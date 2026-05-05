from django.http import JsonResponse

def questions_list(request):
    return JsonResponse([
        {"id": 1, "text": "How can we improve engagement?"},
        {"id": 2, "text": "What tools should we use?"},
        {"id": 3, "text": "How do we measure success?"}
    ], safe=False)