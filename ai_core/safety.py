# ai_core/safety.py
from _future_ import annotations

# Newer vertexai SDKs expose separate enum classes.
# We'll import both and resolve names robustly across versions.
try:
    from vertexai.generative_models import (
        SafetySetting,
        HarmCategory,
        HarmBlockThreshold,
    )

    _HARASSMENT = HarmCategory.HARM_CATEGORY_HARASSMENT
    _HATE = HarmCategory.HARM_CATEGORY_HATE_SPEECH
    _SEXUAL = HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT
    _DANGEROUS = HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT
    _CIVIC = HarmCategory.HARM_CATEGORY_CIVIC_INTEGRITY

    _BLOCK_MED = HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE

except Exception:
    # Fallback for older SDK shapes where enums are nested under SafetySetting
    from vertexai.generative_models import SafetySetting  # type: ignore

    _HARASSMENT = SafetySetting.HarmCategory.HARM_CATEGORY_HARASSMENT
    _HATE = SafetySetting.HarmCategory.HARM_CATEGORY_HATE_SPEECH
    _SEXUAL = SafetySetting.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT
    _DANGEROUS = SafetySetting.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT
    _CIVIC = SafetySetting.HarmCategory.HARM_CATEGORY_CIVIC_INTEGRITY

    _BLOCK_MED = SafetySetting.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE

def default_safety():
    return [
        SafetySetting(category=_HARASSMENT, threshold=_BLOCK_MED),
        SafetySetting(category=_HATE,        threshold=_BLOCK_MED),
        SafetySetting(category=_SEXUAL,      threshold=_BLOCK_MED),
        SafetySetting(category=_DANGEROUS,   threshold=_BLOCK_MED),
        SafetySetting(category=_CIVIC,       threshold=_BLOCK_MED),
    ]