from telegram.utils.request import Request
from telegram import Update, Bot, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton, InlineKeyboardMarkup, \
    InlineKeyboardButton
from telegram.ext import CallbackContext, Updater, Filters, MessageHandler, CommandHandler, ConversationHandler, \
    CallbackQueryHandler
import random, time


def log_error(f):
    def inner(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            print(f'Ошибка: {e}')
            raise e

    return inner


blue_cards = []
with open('blue_cards.txt', 'r') as blue_cards_file:
    for task in blue_cards_file:
        blue_cards.append(task.strip('\n'))

red_cards = []
with open('red_cards.txt', 'r') as red_cards_file:
    for let in red_cards_file:
        red_cards.append(let.strip('\n'))

PLAYERS = 1

players_list = []
players_dict = {}


@log_error
def start(update, context):
    update.message.reply_text('Для того, чтобы начать игру пришлите мне имена всех игроков через запятую.',
                              reply_markup=ReplyKeyboardRemove())

    return PLAYERS


@log_error
def players(update, context):
    start_game_keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text='Начать игру')]],
        resize_keyboard=True)

    start_command_keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text='/start')]],
        resize_keyboard=True)


    received_text = update.effective_message.text

    if received_text.find(', ') != -1:
        players_string = received_text.replace(', ', ',')
    else:
        players_string = received_text

    global players_list, players_dict
    players_list = players_string.split(',')

    if len(players_list) < 2 or len(players_list) > 8:
        update.message.reply_text('Упс! В игру может играть от 2 до 8 игроков.\n'
                                  'Пожалуйста, нажмите /start и введите имена игроков заново с учётом этих ограничений.',
                                  reply_markup=start_command_keyboard)
    else:
        for i in players_list:
            players_dict[i] = 0

        update.message.reply_text('Отлично, если вы готовы к игре - нажмите "Начать игру".\n'
                                  'Если вы хотите изменить имена игроков - отправьте команду /start',
                                  reply_markup=start_game_keyboard)

    return ConversationHandler.END


@log_error
def game(update, context):
    open_letter_keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text='Открыть букву')]],
        resize_keyboard=True)

    new_game_keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text='/start')]],
        resize_keyboard=True)

    try:
        random.shuffle(blue_cards)
        update.message.reply_photo(blue_cards.pop(), reply_markup=open_letter_keyboard)
    except:
        update.message.reply_text('Игра закончилась', reply_markup=ReplyKeyboardRemove())

        result_str = 'Итоговый счёт:\n'
        for key, value in players_dict.items():
            result_str += f'{key}: {value}\n'

        update.message.reply_text(result_str)

        time.sleep(5)
        update.message.reply_text('Чтобы сыграть снова - нажмите /start', reply_markup=new_game_keyboard)


@log_error
def players_keyboard():
    row_1, row_2, row_3, row_4 = [], [], [], []
    row_5 = [InlineKeyboardButton('Никто. Открыть новую букву.', callback_data='no_one')]

    for i in players_list:
        if len(row_1) != 2:
            row_1.append(InlineKeyboardButton(players_list[players_list.index(i)],
                                              callback_data=players_list[players_list.index(i)]))
        elif len(row_2) != 2:
            row_2.append(InlineKeyboardButton(players_list[players_list.index(i)],
                                              callback_data=players_list[players_list.index(i)]))
        elif len(row_3) != 2:
            row_3.append(InlineKeyboardButton(players_list[players_list.index(i)],
                                              callback_data=players_list[players_list.index(i)]))
        else:
            row_4.append(InlineKeyboardButton(players_list[players_list.index(i)],
                                              callback_data=players_list[players_list.index(i)]))

    keyboard = [row_1, row_2, row_3, row_4, row_5]
    return InlineKeyboardMarkup(keyboard)


@log_error
def letter(update, context):
    try:
        random.shuffle(red_cards)
        update.message.reply_photo(red_cards.pop(), reply_markup=ReplyKeyboardRemove())
    except:
        with open('red_cards.txt', 'r') as red_cards_file:
            for let in red_cards_file:
                red_cards.append(let.strip('\n'))
        random.shuffle(red_cards)
        update.message.reply_photo(red_cards.pop(), reply_markup=ReplyKeyboardRemove())

    time.sleep(2)
    update.message.reply_text('Кто выиграл в этом раунде?', reply_markup=players_keyboard())


@log_error
def winner_of_the_round(update, context):
    next_round_keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text='Следующее задание')]],
        resize_keyboard=True)

    open_letter_keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text='Открыть букву')]],
        resize_keyboard=True)

    query = update.callback_query
    query.answer()

    if query.data != 'no_one':
        players_dict[query.data] += 1
        query.edit_message_text(text=f'Отлично, + 1 очко уходит к {query.data}')
        query.bot.send_message(chat_id=query.message.chat.id,
                               text='Если хотите посмотреть результаты всех игроков, нажмите /points\n'
                                    'Чтобы продолжить игру - нажмите кнопку "Следующее задание"',
                               reply_markup=next_round_keyboard)
    else:
        query.edit_message_text(text='Давай попробуем другую букву!')
        query.bot.send_message(chat_id=query.message.chat.id,
                               text='Чтобы открыть новую букву - нажмите кнопку "Открыть букву"',
                               reply_markup=open_letter_keyboard)


@log_error
def points(update, context):
    points_str = 'Текущий счёт:\n'
    for key, value in players_dict.items():
        points_str += f'{key}: {value}\n'

    update.message.reply_text(points_str)


@log_error
def cancel(update, context):
    update.message.reply_text('Bye! I hope we can talk again some day.',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


@log_error
def main():
    print('Start')

    req = Request(
        connect_timeout=0.5,
    )
    bot = Bot(
        request=req,
        token='token',
        base_url='https://telegg.ru/orig/bot',
    )
    updater = Updater(
        bot=bot,
        use_context=True,
    )

    updater.dispatcher.add_handler(ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            PLAYERS: [MessageHandler(Filters.all, players, pass_user_data=True)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    ))

    updater.dispatcher.add_handler(MessageHandler(Filters.regex('Начать игру'), game))
    updater.dispatcher.add_handler(MessageHandler(Filters.regex('Следующее задание'), game))
    updater.dispatcher.add_handler(MessageHandler(Filters.regex('Открыть букву'), letter))
    updater.dispatcher.add_handler(CallbackQueryHandler(winner_of_the_round))
    updater.dispatcher.add_handler(CommandHandler('points', points))

    updater.start_polling()
    updater.idle()

    print('Finish')


if __name__ == '__main__':
    main()
