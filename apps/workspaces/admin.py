from django.contrib import admin

from .models import Workspace, WorkspaceInvitation, WorkspaceMembership


class WorkspaceMembershipInline(admin.TabularInline):
    model = WorkspaceMembership
    extra = 0
    raw_id_fields = ('user',)


@admin.register(Workspace)
class WorkspaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'plan', 'max_members', 'max_projects', 'created_at')
    list_filter = ('plan',)
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [WorkspaceMembershipInline]


@admin.register(WorkspaceMembership)
class WorkspaceMembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'workspace', 'role', 'invited_at')
    list_filter = ('role',)
    raw_id_fields = ('user', 'workspace', 'invited_by')


@admin.register(WorkspaceInvitation)
class WorkspaceInvitationAdmin(admin.ModelAdmin):
    list_display = ('email', 'workspace', 'role', 'accepted', 'expires_at')
    list_filter = ('accepted', 'role')
    raw_id_fields = ('workspace', 'invited_by')
