from django.contrib import admin
from django.contrib.admin import TabularInline

from core.models import User
from scheduling.models import Project, Task, ProjectMember, Predecessor


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'is_active')
    list_filter = ('is_active',)

    search_fields = ('name', 'author')
    ordering = ('author', 'name')
    list_editable = ('is_active',)

    readonly_fields = ('created', 'updated')


@admin.register(ProjectMember)
class ProjectMemberAdmin(admin.ModelAdmin):
    list_display = ('project', 'user', 'role', 'is_project_admin', 'is_active')
    list_filter = ('is_project_admin', 'is_active')

    search_fields = ('project', 'user', 'role')
    ordering = ('project', 'user')
    list_editable = ('is_active',)

    readonly_fields = ('created', 'updated')


class PredecessorsInline(TabularInline):
    model = Predecessor
    fields = ('predecessor',)
    fk_name = 'task'
    extra = 1

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "predecessor":
            if len(request.resolver_match.args) > 0:
                parent_obj_id = request.resolver_match.args[0]
                kwargs["queryset"] = Task.objects.exclude(id=parent_obj_id)
        return super(TabularInline, self).formfield_for_foreignkey(db_field, request, **kwargs)


class ExecutorsInline(TabularInline):
    model = Task.executors.through


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'project', 'executor', 'soft_deadline', 'hard_deadline', 'is_active')
    list_filter = ('is_active', 'project')

    search_fields = ('name', 'author', 'description')
    ordering = ('created', 'name')
    list_editable = ('is_active', )

    readonly_fields = ('created', 'updated')
    exclude = ('executors',)
    inlines = [PredecessorsInline, ExecutorsInline]