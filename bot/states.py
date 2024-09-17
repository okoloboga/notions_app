from aiogram.fsm.state import State, StateGroup

class MainSG(StateGroup):
    start = State()
    main = State()
    create = State()
    edit = State()
    search = State()
    delete = State()
