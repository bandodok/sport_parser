from django.shortcuts import redirect, render


def index(request):
    return render(request, 'khl_index.html')
#    return redirect('/khl/stats/21')

