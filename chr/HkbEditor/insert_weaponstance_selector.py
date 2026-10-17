from hkb_editor.templates import *
from hkb_editor.hkb.hkb_enums import (
    hkbClipGenerator_PlaybackMode as PlaybackMode,
)

def run(
    ctx: TemplateContext,
    parent_id: str,
    child_index: int = 0,
    animation_category: int = 17,
    animation_id: int = -1,

    playback_mode: PlaybackMode = PlaybackMode.SINGLE_PLAY,
    selected_index_can_change_after_activate: bool = False,
):
    """Insert WeaponStanceSelector

    Inserts a WeaponStanceSelector hkbManualSelectorGenerator into the selected parent generator
    replacing one of its child generators and setting it as its own first child.

    Author: Karandra

    Status: ...

    Parameters
    ----------
    ctx : TemplateContext
        The template context.
    parent_id : str
        The parent generator id.
    child_index : str
        The parent's child index to replace.
    animation_id : int
        The moveset category (the Y part in aXXX_YYYYYY).
    playback_mode : PlaybackMode
        The playback mod for the clip generators.
    selected_index_can_change_after_activate : bool
        Whether the active generator index is allowed to change while active.
    """
    if not 0 <= animation_category <= 999:
        raise ValueError("animation_category must be in [0..999]")

    if not 0 <= animation_id <= 999999:
        raise ValueError("animation_id must be in [0..999999]")

    parent: HkbRecord = ctx.find(f"id={parent_id}")
    if not parent:
        raise ValueError(f"Object with id={parent_id} is not found")

    child = parent["generators"][child_index]
    if not child or not child.get_value():
        raise ValueError(f"Child node #{child_index} was not found in '{parent}'")

    child_name = child.get_target()["name"].get_value().replace("_CMSG", "");
    selector_name = f"WeaponStanceSelector<{child_name}>"

    # Low Stance
    animation_id_low = 400000 + animation_id
    animation_low = ctx.animation(f"a{animation_category:03d}_{animation_id_low:06d}")
    stance_low = ctx.make_copy(child.get_target(), animId=animation_id_low, name=f"WeaponStanceCMSG<{child_name}, LowStance>", generators=[ctx.new_clip(animation_low, mode=playback_mode)])
    
    bindset_ptr = stance_low["variableBindingSet"];
    if bindset_ptr.get_value():
        print(f"Reference CMSG '{child.get_target()}' uses hkbVariableBindingSet, making a copy of it")
        
        bindset_copy = ctx.make_copy(bindset_ptr.get_target())
        stance_low["variableBindingSet"].set_value(bindset_copy)

    stanceSelector = ctx.new_manual_selector("WeaponStanceIndex", name=selector_name, generators=[child.get_target(), stance_low], selectedIndexCanChangeAfterActivate=selected_index_can_change_after_activate)
    parent["generators"][child_index].set_value(stanceSelector)
