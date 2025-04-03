from django.shortcuts import render
from django.http import JsonResponse, HttpResponse, HttpResponseForbidden
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from .models import Tournament


import json, time, secrets

def generate_tournament_id() -> str:
	timestamp = int(time.time())
	token = secrets.token_hex(4)
	return f"t:{timestamp}:{token}"


@login_required
@require_http_methods(["POST"])
def tournament_create(request):
	if Tournament.player_in_tournament(str(request.user.uuid)): # check for uuid instead
		return JsonResponse({
			'status': 'error',
			'message': 'You are already in a tournament'
		}, status=400)

	tournament_id = generate_tournament_id()
	tournament = Tournament.create_tournament(
		tournament_id=tournament_id,
		players=[request.user.username]
	)
	
	return JsonResponse({
		'status': 'created',
		'tournament_id': tournament_id
	})


@login_required
@require_http_methods(["DELETE"])
def tournament_leave(request):
	tournament = Tournament.objects.filter(
		player_ids__has_key=str(request.user.uuid),
		status__in=['REGISTERING', 'IN_PROGRESS']
	).first()

	if tournament and tournament.status == 'IN_PROGRESS':
		return JsonResponse({
			'status': 'error',
			'message': 'Cant leave a tournament in progress'
		}, status=400)

	if not tournament:
		return JsonResponse({
			'status': 'error',
			'message': 'You are not in a tournament'
		}, status=400)

	tournament.players = [p for p in tournament.players if p != request.user.username]
	del tournament.player_ids[str(request.user.uuid)]
	
	if not tournament.players:
		tournament.delete()
		return JsonResponse({'status': 'tournament_deleted'})
	
	tournament.save()
	return JsonResponse({'status': 'left'})


@login_required
@require_http_methods(["PUT"])
def tournament_join(request):
	data = json.loads(request.body)
	tournament_id = data.get('tournament_id')

	if Tournament.player_in_tournament(str(request.user.uuid)): # check for uuid instead
		return JsonResponse({
			'status': 'error',
			'message': 'You are already in a tournament'
		}, status=400)

	tournament = Tournament.objects.filter(tournament_id=tournament_id).first()
	if not tournament:
		return JsonResponse({
			'status': 'error',
			'message': 'Tournament not found'
		}, status=404)
		
	if tournament.status != 'REGISTERING':
		return JsonResponse({
			'status': 'error',
			'message': 'Tournament not accepting players'
		}, status=400)

	tournament.players = tournament.players + [request.user.username]

	user_mapping = {str(request.user.uuid): request.user.username}
	tournament.player_ids.update(user_mapping)
	
	if len(tournament.players) >= tournament.max_players:
		tournament.start_tournament()
	else:
		tournament.save()
	
	return JsonResponse({
		'status': 'joined',
		'tournament_id': tournament_id,
	})


@login_required
@require_http_methods(["GET"])
def tournament_list(request):
	username = request.user.username
	user_uuid = str(request.user.uuid)
	# user's tournament
	user_tournament = Tournament.objects.filter(
		player_ids__has_key=user_uuid,
		status__in=['REGISTERING', 'IN_PROGRESS']
	).first()
	

	# all active tournaments
	tournaments = Tournament.objects.filter(
		status__in=['REGISTERING', 'IN_PROGRESS']
	).order_by('-created_at')
	
	current_tournament_data = None
	if user_tournament:
		current_tournament_data = {
			'players': user_tournament.players,
			'current_round': user_tournament.current_round,
			'rounds': user_tournament.rounds,
			'status': user_tournament.status
		}
		
		# matches that belong to the current user
		if user_tournament.rounds and user_tournament.current_round < len(user_tournament.rounds):
			current_round = user_tournament.rounds[user_tournament.current_round]
			for match in current_round:
				match['is_player_match'] = (match['player1'] == username or match['player2'] == username)

	return JsonResponse({
		'in_tournament': bool(user_tournament),
		'current_tournament_id': user_tournament.tournament_id if user_tournament else None,
		'current_tournament': current_tournament_data,
		'tournaments': [{
			'tournament_id': t.tournament_id,
			'status': t.status,
			'player_count': len(t.players),
			'max_players': t.max_players
		} for t in tournaments]
	})


@login_required
@require_http_methods(["GET"])
def user_tournaments(request):
    user_uuid = str(request.user.uuid)
    last_tournament = Tournament.objects.filter(
        player_ids__has_key=user_uuid,
        status='COMPLETED'
    ).order_by('-updated_at').first()

    if not last_tournament:
        return JsonResponse({
            'status': 'success',
            'has_history': False
        })

    elimination_round = None
    if last_tournament.winner_id != user_uuid:
        for round_num, round_matches in enumerate(last_tournament.rounds):
            for match in round_matches:
                player1_id = None
                player2_id = None
                
                for uuid, username in last_tournament.player_ids.items():
                    if username == match['player1']:
                        player1_id = uuid
                    elif username == match['player2']:
                        player2_id = uuid
                
                if (player1_id == user_uuid or player2_id == user_uuid) and match['status'] == 'COMPLETED':
                    winner_id = None
                    for uuid, username in last_tournament.player_ids.items():
                        if username == match['winner']:
                            winner_id = uuid
                            break

                    # if user isn't the winner, they were eliminated in this round
                    if winner_id != user_uuid:
                        elimination_round = round_num + 1
                        break
            if elimination_round:
                break

    return JsonResponse({
        'status': 'success',
        'has_history': True,
        'tournament': {
            'id': last_tournament.tournament_id,
            'winner': last_tournament.winner,
            'winner_id': last_tournament.winner_id,
            'elimination_round': elimination_round,
            'total_rounds': len(last_tournament.rounds),
            'players': last_tournament.players
        }
    })