# @author Daniel McCoy Stephenson
"""Every key that may be set on LoopState.flags, in one place.

A flag is something that happened *this* loop and that the bell forgets: a
rope hung, a lamp lit, a choice someone will hold you to for the day. The
dict stays free-form in the save file (schemas/save.json allows any object),
but the game only ever writes these names, so an ending can be looked up by
its flag and a typo is an import error rather than a silent no-op.
"""

# Things done to the village that an ending turns on.
ROPE_HUNG = "ropeHung"
LAMP_LIT = "lampLit"
# Set at nine when the lit lamp meets the storm and the rope is hung too: the
# light held, the loop goes on to eleven, and the bell ending becomes the
# whole of the night.
LIGHT_HELD = "lightHeld"

# Choices people hold you to for the day - see Scene.remember.
TOLD_MARGARET_ABOUT_TOM = "toldMargaretAboutTom"
HURRIED_ADA = "hurriedAda"
TOLD_TOM_OF_NELL = "toldTomOfNell"
SHAMED_GILBERT = "shamedGilbert"

ALL = (
    ROPE_HUNG,
    LAMP_LIT,
    LIGHT_HELD,
    TOLD_MARGARET_ABOUT_TOM,
    HURRIED_ADA,
    TOLD_TOM_OF_NELL,
    SHAMED_GILBERT,
)
