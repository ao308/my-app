from django.shortcuts import render
from django.views.generic import View
from .models import Profile


class IndexView(View):
    def get(self, request, *args, **kwargs):
        profile_data = Profile.objects.all()
        if profile_data.exists():
            profile_data = profile_data.order_by('-id')[0]
            return render(request, 'app/index.html', {
                'profile_data' : profile_data
            })
