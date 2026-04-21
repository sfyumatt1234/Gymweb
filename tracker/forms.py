from django import forms

from .i18n_ui import bilingual_line
from .models import UNITS_IMPERIAL, UNITS_METRIC, BodyLog, Profile, SetEntry


def _choice_bilingual(en: str, zh: str) -> str:
    """Single-line label for &lt;select&gt; options (avoids HTML escaping issues)."""
    return f"{en} · {zh}"


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["display_name"].label = bilingual_line("Display name", "顯示名稱")
        self.fields["height_cm"].label = bilingual_line("Height (cm)", "身高（公分）")
        self.fields["sex"].label = bilingual_line("Sex", "性別")
        self.fields["units"].label = bilingual_line("Units", "單位")
        self.fields["sex"].choices = [
            ("", _choice_bilingual("Prefer not to say", "不願透露")),
            ("male", _choice_bilingual("Male", "男")),
            ("female", _choice_bilingual("Female", "女")),
            ("other", _choice_bilingual("Other", "其他")),
        ]
        self.fields["units"].choices = [
            (UNITS_METRIC, _choice_bilingual("Metric (kg / cm)", "公制（公斤／公分）")),
            (UNITS_IMPERIAL, _choice_bilingual("Imperial (lb / in)", "英制（磅／吋）")),
        ]


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
        self.fields["measured_at"].label = bilingual_line("Measured at", "測量時間")
        self.fields["weight_kg"].label = bilingual_line("Weight (kg)", "體重（公斤）")
        self.fields["body_fat_pct"].label = bilingual_line("Body fat (%)", "體脂率（%）")
        self.fields["muscle_kg"].label = bilingual_line("Muscle (kg)", "肌肉量（公斤）")
        self.fields["muscle_pct"].label = bilingual_line("Muscle (%)", "肌肉率（%）")
        self.fields["source"].label = bilingual_line("Source", "來源")
        self.fields["notes"].label = bilingual_line("Notes", "備註")
        src = self.fields["source"]
        src.choices = [
            (BodyLog.Source.MANUAL, _choice_bilingual("Manual entry", "手動輸入")),
            (BodyLog.Source.SCALE, _choice_bilingual("Smart scale", "體脂計／智能秤")),
            (BodyLog.Source.CALIPER, _choice_bilingual("Calipers", "皮脂鉗")),
            (BodyLog.Source.DEXA, _choice_bilingual("DEXA / professional", "DEXA／專業檢測")),
            (BodyLog.Source.OTHER, _choice_bilingual("Other", "其他")),
        ]


class SetEntryForm(forms.ModelForm):
    class Meta:
        model = SetEntry
        fields = ["exercise", "set_number", "weight_kg", "reps", "rpe", "done"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["exercise"].label = bilingual_line("Exercise", "動作")
        self.fields["set_number"].label = bilingual_line("Set #", "組數")
        self.fields["weight_kg"].label = bilingual_line("Weight (kg)", "重量（公斤）")
        self.fields["reps"].label = bilingual_line("Reps", "次數")
        self.fields["rpe"].label = bilingual_line("RPE", "自覺吃力程度（RPE）")
        self.fields["done"].label = bilingual_line("Done", "完成")
