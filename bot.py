import random
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters


# проверка на выигрыш
# проверяет нет ли победной комбинации в строчках, столбцах или по диагонали
# arr - массив
# who - кого надо проверить: нужно передать значение is_win'х' или '0'
def is_win(arr, who):
    if (((arr[0] == who) and (arr[4] == who) and (arr[8] == who)) or
            ((arr[2] == who) and (arr[4] == who) and (arr[6] == who)) or
            ((arr[0] == who) and (arr[1] == who) and (arr[2] == who)) or
            ((arr[3] == who) and (arr[4] == who) and (arr[5] == who)) or
            ((arr[6] == who) and (arr[7] == who) and (arr[8] == who)) or
            ((arr[0] == who) and (arr[3] == who) and (arr[6] == who)) or
            ((arr[1] == who) and (arr[4] == who) and (arr[7] == who)) or
            ((arr[2] == who) and (arr[5] == who) and (arr[8] == who))):
        return True
    return False


# возвращает количество неопределенных ячеек (т.е. количество ячеек, в которые можно сходить)
# cell_array - массив данных из callback_data, полученных после нажатия на callBack-кнопку
def count_undefined_cells(cell_array):
    global symbol_undef
    counter = 0
    for i in cell_array:
        if i == symbol_undef:
            counter += 1
    return counter


# callback_data формат:
# n????????? - общее описание
# n - номер кнопки
# ? - один из вариантов значения клетки
# пример: 5❌❌⭕⭕❌❌◻◻❌
# означает, что была нажата пятая кнопка, и текущий вид поля:
# ❌❌⭕
# ⭕❌❌
# ◻◻❌
# данные обо всем состоянии поля необходимо помещать в кнопку,
# т.к. бот имеет доступ к информации только из текущего сообщения

# игра: проверка возможности хода крестиком, проверка победы крестика, ход бота (ноликом), проверка победы ботом
# возвращает:
# message - сообщение, которое надо отправить
# callback_data - данные для формирования callback данных обновленного игрового поля
def game(callback_data):
    global symbol_undef
    # global message  # использование глобальной переменной message
    message = your_turn  # сообщение, которое вернется
    alert = None

    # считывание нажатой кнопки, преобразуя ее из строки в число
    button_number = int(callback_data[0])
    if not button_number == 9:  # цифра 9 передается в первый раз в качестве заглушки. Т.е. если передана цифра 9,
        # то клавиатура для сообщения создается впервые
        # строчка callback_data разбивается на посимвольный список "123" -> ['1', '2', '3']
        char_list = list(callback_data)
        # удаление из списка первого элемента: который отвечает за выбор кнопки
        char_list.pop(0)
        # проверка: если в нажатой кнопке не выбран крестик/нолик, то можно туда сходить крестику
        if char_list[button_number] == symbol_undef:
            char_list[button_number] = symbol_x  # эмуляция хода крестика
            if is_win(char_list, symbol_x):  # проверка: выиграл ли крестик после своего хода
                message = your_win
            else:  # если крестик не выиграл, то может сходит бот, т.е. нолик
                # проверка: есть ли свободные ячейки для хода
                if count_undefined_cells(char_list) != 0:
                    # если есть, то ходит бот (нолик)
                    is_cycle_continue = True
                    # запуск бесконечного цикла т.к. необходимо, чтобы бот походил в свободную клетку, а клетка выбирается случайным образом
                    while (is_cycle_continue):
                        # генерация случайного числа - клетки, в которую сходит бот
                        rand = random.randint(0, 8)
                        # если клетка неопределенна, то ходит бот
                        if char_list[rand] == symbol_undef:
                            char_list[rand] = symbol_o
                            is_cycle_continue = False  # смена значения переменной для остановки цикла
                            # проверка: выиграл ли бот после своего кода
                            if is_win(char_list, symbol_o):
                                message = bot_win

        # если клетка, в которую хотел походить пользователь уже занята:
        else:
            alert = error

        # проверка: остались ли свободные ячейки для хода и что изначальное сообщение не поменялось
        # (означает, что победителя нет, и что это был не ошибочный ход)
        if count_undefined_cells(char_list) == 0 and message == your_turn:
            message = draw

        # формирование новой строчки callback_data на основе сделанного хода
        callback_data = ''
        for i in char_list:
            callback_data += i

    # проверка, что игра закончилась (message равно одному из трех вариантов: победил Х, 0 или ничья):
    if message == your_win or message == bot_win or message == draw:
        message += '\n'
        for i in range(0, 3):
            message += '\n | '
            for j in range(0, 3):
                message += callback_data[j + i * 3] + ' | '
        callback_data = None  # обнуление callback_data

    return message, callback_data, alert


# Формат объекта клавиатуры
# в этом примере описана клавиатура из трех строчек кнопок
# в первой строчке две кнопки
# во 2-ой и 3-ей строчке по одной
# keyboard = [
#     # строчка из кнопок:
#     [
#         # собственно кнопки
#         InlineKeyboardButton("Кнопка 1", callback_data='1'),
#         InlineKeyboardButton("Кнопка 2", callback_data='2'),
#     ],
#     [InlineKeyboardButton("Кнопка 3", callback_data='3')],
#     [InlineKeyboardButton("Кнопка 4", callback_data='4')],
# ]
# для формирования объекта клавиатуры, необходимо выполнить следующую команду:
# InlineKeyboardMarkup(keyboard)

# возвращает клавиатуру для бота
# на вход получает callback_data - данные с callback-кнопки
def get_key_board(callback_data):
    keyboard = [[], [], []]  # заготовка объекта клавиатуры, которая вернется

    if callback_data != None:
        # формирование объекта клавиатуры
        for i in range(0, 3):
            for j in range(0, 3):
                keyboard[i].append(InlineKeyboardButton(
                    callback_data[j + i * 3], callback_data=str(j + i * 3) + callback_data))

    return keyboard


def new_game(update, context):
    global symbol_undef
    # сформировать callBack данные для первой игры, то есть строку, состояющую из 9 неопределенных символов
    data = ''
    for i in range(0, 9):
        data += symbol_undef

    # отправить сообщение для начала игры
    update.message.reply_text(
        your_turn, reply_markup=InlineKeyboardMarkup(get_key_board(data)))


def button(update, context):
    query = update.callback_query
    callback_data = query.data  # получение callback_data, скрытых в кнопке

    message, callback_data, alert = game(callback_data)  # игра
    # если не получен сигнал тревоги (alert==None), то редактируем сообщение и меняем клавиатуру
    if alert is None:
        callback_data
        query.answer()  # обязательно нужно что-то отправить в ответ, иначе могут возникнуть проблемы с ботом
        query.edit_message_text(
            text=message, reply_markup=InlineKeyboardMarkup(get_key_board(callback_data)))
    # если получен сигнал тревоги (alert!=None), то отобразить сообщение о тревоге
    else:
        query.answer(text=alert, show_alert=True)


def main() -> None:
    updater = Updater('5564454006:AAHONt2C53lVkF2Q1qw_iEc2_LnOqmVhihw')

    # добавление обработчиков
    updater.dispatcher.add_handler(CommandHandler('start', new_game))
    updater.dispatcher.add_handler(MessageHandler(Filters.text, new_game))
    # добавление обработчика на CallBack кнопки
    updater.dispatcher.add_handler(CallbackQueryHandler(button))

    # Запуск бота
    print('server start')
    updater.start_polling()
    updater.idle()


# символы, которые используются
symbol_x = '❌'
symbol_o = '⭕'
symbol_undef = '◻'

# ответы бота
your_turn = 'Ваш ход'
your_win = 'Вы победили'
bot_win = 'Победил бот'
draw = 'Ничья'

# ошибка
error = 'Нажимать можно только на ' + symbol_undef


if __name__ == '__main__':
    main()
