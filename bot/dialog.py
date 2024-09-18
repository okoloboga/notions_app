from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.text import Format
from aiogram_dialog.widgets.kbd import Button, Row
from aiogram_dialog.widgets.input.text import TextInput

from getter import *
from handler import *
from states import MainSG
from services import validate_password


dialog = Dialog(
    Window(
        Format('{registration}'),
        TextInput(
            id='registration',
            type_factory=validate_password,
            on_success=registration_result,
            on_error=wrong_input
            ),
        getter=registration_getter,
        state=MainSG.registration
        ),
    Window(
        Format('{login}'),
        TextInput(
            id='login',
            type_factory=str,
            on_success=login_result,
            on_error=wrong_input
        ),
        getter=login_getter,
        state=MainSG.login
    ),
    Window(
        Format('{main_menu}'),
        Button(Format('{button_create_note}'), id='b_create_note', on_click=create_note),
        
        # Однажды, они потребуются...

        # Row(
        #     Button(Format('{button_delete_note}'), id='b_delete_note', on_click=delete_note),
        #     Button(Format('{button_edit_note}'), id='b_edit_note', on_click=edit_note)
        #     ),

        Button(Format('{button_my_notes}'), id='b_my_notes', on_click=my_notes),
        TextInput(
            id='search',
            type_factory=str,
            on_success=tags_notes_list,
            on_error=wrong_input
            ),
        getter=main_getter,
        state=MainSG.main
        ),
    Window(
        Format('{fill_title}'),
        TextInput(
            id='fill_title',
            type_factory=str,
            on_success=check_title,
            on_error=wrong_input
            ),
        getter=title_getter,
        state=MainSG.title
        ),
    Window(
        Format('{fill_content}'),
        TextInput(
            id='fill_content',
            type_factory=str,
            on_success=check_content,
            on_error=wrong_input
            ),
        getter=content_getter,
        state=MainSG.content
        ),
    Window(
        Format('{fill_tags}'),
        TextInput(
            id='fill_tags',
            type_factory=str,
            on_success=check_tags,
            on_error=wrong_input
            ),
        getter=tags_getter,
        state=MainSG.tags
        ),
    Window(
        Format('{complete_note}'),
        Button(Format('{button_confirm}'), id='b_confirm', on_click=confirm),
        Button(Format('{button_cancel}'), id='b_cancel', on_click=cancel),
        getter=complete_getter,
        state=MainSG.complete
        )
    )
    
    # Заготовка для расширения функционала по удалению и редактированию
    # заметок через бота

    # Window(
    #     Format('{delete_note}'),
    #     TextInput(
    #         id='delete',
    #         type_factory=str,
    #         on_success=check_delete_note,
    #         on_error=wrong_input
    #         ),
    #     Button(Format('{button_back}'), id='b_back', on_clik=back),
    #     getter=delete_getter,
    #     state=MainSG.delete
    #     ),
    # Window(
    #     Format('{edit_note}'),
    #     TextInput(
    #         id='edit',
    #         type_factory=str,
    #         on_success=check_edit_note,
    #         on_error=wrong_input
    #         ),
    #     Button(Format('{button_back}'), id='b_back', on_clik=back),
    #     getter=edit_getter,
    #     state=MainSG.edit
    #     )

