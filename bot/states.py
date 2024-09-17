from aiogram.fsm.state import State, StateGroup

class MainSG(StateGroup):
    registration = State()
    login = State()
    main = State()
    create = State()
    edit = State()
    notes_list = State()
    delete = State()
