from aiogram.fsm.state import State, StateGroup

class MainSG(StateGroup):
    registration = State()
    login = State()
    main = State()
    title = State()
    content = State()
    tags = State()
    complete = State()
    # edit = State()
    notes_list = State()
    # delete = State()
