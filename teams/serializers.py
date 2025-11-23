from rest_framework import serializers
from .models import Team, TeamMember, TeamInvitation
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class TeamMemberSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = TeamMember
        fields = ['id', 'user', 'role', 'joined_at']


class TeamSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    members = TeamMemberSerializer(many=True, read_only=True)
    member_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Team
        fields = ['id', 'name', 'owner', 'members', 'member_count', 'created_at']
    
    def get_member_count(self, obj):
        return obj.members.count()


class TeamInvitationSerializer(serializers.ModelSerializer):
    invited_by = UserSerializer(read_only=True)
    team_name = serializers.CharField(source='team.name', read_only=True)
    
    class Meta:
        model = TeamInvitation
        fields = ['id', 'team', 'team_name', 'email', 'role', 'invited_by', 'status', 'created_at', 'expires_at']
