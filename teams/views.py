from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Team, TeamMember, TeamInvitation
from .serializers import TeamSerializer, TeamMemberSerializer, TeamInvitationSerializer
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import secrets


class TeamViewSet(viewsets.ModelViewSet):
    serializer_class = TeamSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Return teams where user is owner or member
        user = self.request.user
        owned_teams = Team.objects.filter(owner=user)
        member_teams = Team.objects.filter(members__user=user)
        return (owned_teams | member_teams).distinct()
    
    def perform_create(self, serializer):
        team = serializer.save(owner=self.request.user)
        # Automatically add owner as team member
        TeamMember.objects.create(
            team=team,
            user=self.request.user,
            role='owner'
        )
    
    @action(detail=True, methods=['post'])
    def invite_member(self, request, pk=None):
        team = self.get_object()
        
        # Check if user has permission to invite
        member = TeamMember.objects.filter(team=team, user=request.user).first()
        if not member or member.role not in ['owner', 'admin']:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        email = request.data.get('email')
        role = request.data.get('role', 'member')
        
        if not email:
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create invitation
        token = secrets.token_urlsafe(32)
        invitation = TeamInvitation.objects.create(
            team=team,
            email=email,
            role=role,
            invited_by=request.user,
            token=token,
            expires_at=timezone.now() + timedelta(days=7)
        )
        
        # TODO: Send email with invitation link
        
        return Response({
            'message': 'Invitation sent',
            'invitation': TeamInvitationSerializer(invitation).data
        })
    
    @action(detail=True, methods=['post'])
    def remove_member(self, request, pk=None):
        team = self.get_object()
        user_id = request.data.get('user_id')
        
        # Check permission
        requester_member = TeamMember.objects.filter(team=team, user=request.user).first()
        if not requester_member or requester_member.role not in ['owner', 'admin']:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        # Remove member
        member = TeamMember.objects.filter(team=team, user_id=user_id).first()
        if not member:
            return Response({'error': 'Member not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if member.role == 'owner':
            return Response({'error': 'Cannot remove team owner'}, status=status.HTTP_400_BAD_REQUEST)
        
        member.delete()
        return Response({'message': 'Member removed'})
    
    @action(detail=True, methods=['post'])
    def update_member_role(self, request, pk=None):
        team = self.get_object()
        user_id = request.data.get('user_id')
        new_role = request.data.get('role')
        
        # Check permission
        requester_member = TeamMember.objects.filter(team=team, user=request.user).first()
        if not requester_member or requester_member.role != 'owner':
            return Response({'error': 'Only owner can change roles'}, status=status.HTTP_403_FORBIDDEN)
        
        member = TeamMember.objects.filter(team=team, user_id=user_id).first()
        if not member:
            return Response({'error': 'Member not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if member.role == 'owner':
            return Response({'error': 'Cannot change owner role'}, status=status.HTTP_400_BAD_REQUEST)
        
        member.role = new_role
        member.save()
        
        return Response(TeamMemberSerializer(member).data)


class TeamInvitationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TeamInvitationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return TeamInvitation.objects.filter(
            team__in=Team.objects.filter(owner=self.request.user)
        )
    
    @action(detail=False, methods=['post'])
    def accept(self, request):
        token = request.data.get('token')
        
        try:
            invitation = TeamInvitation.objects.get(token=token, status='pending')
        except TeamInvitation.DoesNotExist:
            return Response({'error': 'Invalid or expired invitation'}, status=status.HTTP_404_NOT_FOUND)
        
        if invitation.expires_at < timezone.now():
            invitation.status = 'expired'
            invitation.save()
            return Response({'error': 'Invitation expired'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create team member
        TeamMember.objects.create(
            team=invitation.team,
            user=request.user,
            role=invitation.role
        )
        
        invitation.status = 'accepted'
        invitation.save()
        
        return Response({'message': 'Invitation accepted', 'team': TeamSerializer(invitation.team).data})
