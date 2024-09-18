from aiogram.fsm.state import State, StatesGroup

class MainSG(StatesGroup):
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
