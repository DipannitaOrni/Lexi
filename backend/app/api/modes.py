"""
GET /modes — lists available accessibility modes with display labels and
descriptions, for the ModeSelector.jsx frontend component, so the mode
list is defined once (in rewrite_prompts.py) and never drifts between
frontend and backend.
"""
from fastapi import APIRouter

from app.prompts.rewrite_prompts import MODE_RULES
from app.schemas.modes_schema import ModeInfo, ModesResponse

router = APIRouter()

_MODE_LABELS = {
    "dyslexia": ("Dyslexia-Friendly", "Short sentences, simple words, and clear spacing."),
    "focus": ("Focus Mode", "Key points up front, bullet points, and bolded essentials."),
    "screen_reader": ("Screen Reader", "Speech-friendly punctuation and simple sentence structure."),
    "non_native": ("Non-Native English", "Simplified vocabulary with inline clarifications."),
    "civic": ("Civic / Government Forms", "Clear requirements, deadlines, fees, and steps."),
    "dyscalculia": ("Dyscalculia-Friendly", "Tables and statistics explained in plain language."),
    "low_vision": ("Low Vision", "Short scannable paragraphs, lists instead of tables."),
}


@router.get("/modes", response_model=ModesResponse)
async def list_modes():
    modes = [
        ModeInfo(id=mode_id, label=_MODE_LABELS[mode_id][0], description=_MODE_LABELS[mode_id][1])
        for mode_id in MODE_RULES.keys()
    ]
    return ModesResponse(modes=modes)
