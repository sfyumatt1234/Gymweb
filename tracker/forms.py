from django import forms

from .models import BodyLog, Profile, SetEntry


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["display_name", "height_cm", "sex", "units"]
        widgets = {
            "display_name": forms.TextInput(attrs={"class": "input"}),
            "height_cm": forms.NumberInput(attrs={"class": "input", "step": "0.1"}),
            "sex": forms.Select(attrs={"class": "input"}),
            "units": forms.Select(attrs={"class": "input"}),
        }


class BodyLogForm(forms.ModelForm):
    class Meta:
        model = BodyLog
        fields = [
            "measured_at",
            "weight_kg",
            "body_fat_pct",
            "muscle_kg",
            "muscle_pct",
            "source",
            "notes",
        ]
        widgets = {
            "measured_at": forms.DateTimeInput(
                attrs={"class": "input", "type": "datetime-local"},
                format="%Y-%m-%dT%H:%M",
            ),
            "weight_kg": forms.NumberInput(attrs={"class": "input", "step": "0.01"}),
            "body_fat_pct": forms.NumberInput(attrs={"class": "input", "step": "0.1"}),
            "muscle_kg": forms.NumberInput(attrs={"class": "input", "step": "0.01"}),
            "muscle_pct": forms.NumberInput(attrs={"class": "input", "step": "0.1"}),
            "source": forms.Select(attrs={"class": "input"}),
            "notes": forms.Textarea(attrs={"class": "input", "rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["measured_at"].input_formats = ["%Y-%m-%dT%H:%M"]


class SetEntryForm(forms.ModelForm):
    class Meta:
        model = SetEntry
        fields = ["exercise", "set_number", "weight_kg", "reps", "rpe", "done"]
