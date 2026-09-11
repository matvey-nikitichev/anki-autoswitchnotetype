from aqt import mw
from aqt.qt import QAction, QInputDialog
from aqt.utils import showInfo


def change_notes():

    # INITIALISATION
    config = mw.addonManager.getConfig(__name__)

    if config is None:
        return

    # TODO: Make this all one dialogue
    SOURCE_DECK, ok1 = QInputDialog.getText(
        mw, "AutoSwitchCardType", "Source Deck:", text=config.get("SOURCE_DECK", "")
    )

    if ok1:
        config["SOURCE_DECK"] = SOURCE_DECK
    else:
        return

    SOURCE_NOTE_TYPE, ok2 = QInputDialog.getText(
        mw,
        "AutoSwitchCardType",
        "Source Note Type:",
        text=config.get("SOURCE_NOTE_TYPE", ""),
    )

    if ok2:
        config["SOURCE_NOTE_TYPE"] = SOURCE_NOTE_TYPE
    else:
        return

    TARGET_NOTE_TYPE, ok3 = QInputDialog.getText(
        mw,
        "AutoSwitchCardType",
        "Target Note Type:",
        text=config.get("TARGET_NOTE_TYPE", ""),
    )

    if ok3:
        config["TARGET_NOTE_TYPE"] = TARGET_NOTE_TYPE
    else:
        return

    DUE_DAY_LIMIT, ok4 = QInputDialog.getText(
        mw, "AutoSwitchCardType", "Due Day Limit:", text=config.get("DUE_DAY_LIMIT", "")
    )

    if ok4:
        config["DUE_DAY_LIMIT"] = DUE_DAY_LIMIT
    else:
        return

    if ok1 and ok2 and ok3 and ok4:
        mw.addonManager.writeConfig(__name__, config)
        DUE_DAY_LIMIT = int(DUE_DAY_LIMIT)
    else:
        return

    # GET CARDS
    if mw.col is None:
        return False

    target_model = mw.col.models.by_name(TARGET_NOTE_TYPE)

    if target_model is None:
        return False

    card_ids = mw.col.find_cards(
        f"deck:{SOURCE_DECK} note:{SOURCE_NOTE_TYPE} prop:due>={DUE_DAY_LIMIT}"
    )

    if card_ids is None or len(card_ids) < 1:
        return False

    source_model = mw.col.get_card(card_ids[0]).note().note_type()

    if source_model is None or source_model["id"] == target_model["id"]:
        return False

    note_ids = set(mw.col.get_card(cid).nid for cid in card_ids)  # noqa: C401
    card_ids = list(
        set(  # noqa: C401
            card.id for note_id in note_ids for card in mw.col.get_note(note_id).cards()
        )
    )

    info = mw.col.models.change_notetype_info(
        old_notetype_id=source_model["id"], new_notetype_id=target_model["id"]
    )
    info.input.note_ids.extend(note_ids)

    # CHANGE CARDS
    mw.col.sched.schedule_cards_as_new(
        card_ids, restore_position=True, reset_counts=False
    )
    mw.col.models.change_notetype_of_notes(info.input)

    showInfo(f"Done.\nNotes converted: {len(note_ids)}")


action = QAction("Convert note type", mw)

action.triggered.connect(change_notes)

# TODO: Maybe make this a hook
mw.form.menuTools.addAction(action)
