from django.contrib import admin

from .models import (
    BodyLog,
    Day,
    Exercise,
    Profile,
    Program,
    SetEntry,
    WorkoutSession,
)


class DayInline(admin.TabularInline):
    model = Day
    extra = 1


class ExerciseInline(admin.StackedInline):
    model = Exercise
    extra = 1


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("display_name", "user", "height_cm", "units")


@admin.register(BodyLog)
class BodyLogAdmin(admin.ModelAdmin):
    list_display = ("measured_at", "weight_kg", "body_fat_pct", "muscle_kg", "source")
    list_filter = ("source",)
    date_hierarchy = "measured_at"


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ("name", "is_default", "created_at")
    inlines = [DayInline]


@admin.register(Day)
class DayAdmin(admin.ModelAdmin):
    list_display = ("program", "name", "order")
    inlines = [ExerciseInline]


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ("name", "day", "target_sets", "target_reps")
    search_fields = ("name",)


@admin.register(WorkoutSession)
class WorkoutSessionAdmin(admin.ModelAdmin):
    list_display = ("day", "profile", "started_at", "finished_at")


@admin.register(SetEntry)
class SetEntryAdmin(admin.ModelAdmin):
    list_display = ("session", "exercise", "set_number", "weight_kg", "reps", "rpe", "done")
