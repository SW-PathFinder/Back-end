from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

def game_list(request):
    """게임 목록 페이지"""
    return render(request, 'saboteur/game_list.html')

def chat_room(request, room_name):
    """채팅방 페이지"""
    return render(request, 'saboteur/chat_room.html', {
        'room_name': room_name
    })

@csrf_exempt
def create_room(request):
    """새 방 생성 API"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            room_name = data.get('room_name')
            
            if not room_name:
                return JsonResponse({'error': '방 이름이 필요합니다.'}, status=400)
                
            # 방 생성 로직 (실제로는 DB에 저장할 수 있음)
            return JsonResponse({
                'success': True,
                'room_name': room_name,
                'message': f'방 "{room_name}"이 생성되었습니다.'
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': '잘못된 JSON 형식입니다.'}, status=400)
    
    return JsonResponse({'error': 'POST 요청만 허용됩니다.'}, status=405)