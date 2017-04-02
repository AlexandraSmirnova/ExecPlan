from django.contrib import admin
from django.contrib.admin import TabularInline


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
    list_display = ('project', 'user', 'position', 'is_project_admin', 'is_active')
    list_filter = ('is_project_admin', 'is_active')

    search_fields = ('project', 'user', 'position')
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


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'is_active')
    list_filter = ('is_active',)

    search_fields = ('name', 'author', 'description')
    ordering = ('created', 'name')
    list_editable = ('is_active', )

    readonly_fields = ('created', 'updated')
    inlines = [PredecessorsInline]