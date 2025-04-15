from django.shortcuts import render
from django.http import HttpResponse

def game_list(request):
    return HttpResponse("게임 목록 페이지입니다.")