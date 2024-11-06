from django.shortcuts import render 

# Create your views here.
def main(request):
    return render(request, 'index.html')

def main_2(request):
    return render(request, 'index_2.html')