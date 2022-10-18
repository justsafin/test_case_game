import random
import telebot


token = ""
grass_ico = u"\U0001F7E9"
wolf_ico = u"\U0001F43A"
officer_ico = u'\U0001F482'
horse_ico = u'\U0001F434'

up_ico = u"\U00002B06"
down_ico = u"\U00002B07"
left_ico = u"\U00002B05"
right_ico = u"\U000027A1"

bot = telebot.TeleBot(token)


officer_move_keyboard = telebot.types.InlineKeyboardMarkup()
officer_move_keyboard.row( telebot.types.InlineKeyboardButton(left_ico, callback_data='o_m_left'),
			  telebot.types.InlineKeyboardButton(up_ico, callback_data='o_m_up'),
			  telebot.types.InlineKeyboardButton(down_ico, callback_data='o_m_down'),
			  telebot.types.InlineKeyboardButton(right_ico, callback_data='o_m_right'))

officer_attack_keyboard = telebot.types.InlineKeyboardMarkup()
officer_attack_keyboard.row( telebot.types.InlineKeyboardButton(u"\U00002196", callback_data='o_a_up_left'),
			  telebot.types.InlineKeyboardButton(u"\U00002197", callback_data='o_a_up_right'),
			  telebot.types.InlineKeyboardButton(u"\U00002199", callback_data='o_a_down_left'),
			  telebot.types.InlineKeyboardButton(u"\U00002198", callback_data='o_a_down_right'),
              telebot.types.InlineKeyboardButton(u"\U0000274C", callback_data='o_a_skip'))

horse_move_keyboard = telebot.types.InlineKeyboardMarkup()
horse_move_keyboard.row( telebot.types.InlineKeyboardButton(up_ico+left_ico+left_ico, callback_data='h_m_left_up'),
              telebot.types.InlineKeyboardButton(up_ico+up_ico+left_ico, callback_data='h_m_up_left'),
              telebot.types.InlineKeyboardButton(up_ico+up_ico+right_ico, callback_data='h_m_up_right'),
              telebot.types.InlineKeyboardButton(up_ico+right_ico+right_ico, callback_data='h_m_right_up'))
horse_move_keyboard.row( telebot.types.InlineKeyboardButton(down_ico+left_ico+left_ico, callback_data='h_m_left_down'),
			  telebot.types.InlineKeyboardButton(down_ico+down_ico+left_ico, callback_data='h_m_down_left'),
			  telebot.types.InlineKeyboardButton(down_ico+down_ico+right_ico, callback_data='h_m_down_right'),
			  telebot.types.InlineKeyboardButton(down_ico+right_ico+right_ico, callback_data='h_m_right_down'))

horse_attack_keyboard = telebot.types.InlineKeyboardMarkup()
horse_attack_keyboard.row( telebot.types.InlineKeyboardButton(up_ico+left_ico+left_ico, callback_data='h_a_left_up'),
              telebot.types.InlineKeyboardButton(up_ico+up_ico+left_ico, callback_data='h_a_up_left'),
              telebot.types.InlineKeyboardButton(up_ico+up_ico+right_ico, callback_data='h_a_up_right'),
              telebot.types.InlineKeyboardButton(up_ico+right_ico+right_ico, callback_data='h_a_right_up'))
horse_attack_keyboard.row( telebot.types.InlineKeyboardButton(down_ico+left_ico+left_ico, callback_data='h_a_left_down'),
			  telebot.types.InlineKeyboardButton(down_ico+down_ico+left_ico, callback_data='h_a_down_left'),
			  telebot.types.InlineKeyboardButton(down_ico+down_ico+right_ico, callback_data='h_a_down_right'),
			  telebot.types.InlineKeyboardButton(down_ico+right_ico+right_ico, callback_data='h_a_right_down'))
horse_attack_keyboard.row(telebot.types.InlineKeyboardButton(u"\U0000274C", callback_data='h_a_skip'))


maps = {}


def get_map_str(cols, rows):
    game_map = []
    for i in range(rows):
        row = []
        for j in range(cols):
            row.append(grass_ico)
        row.append("\n")
        game_map.append(row)

    return game_map


def place_unit(game_map, unit_ico, cols, rows):
    while True:
        coord_x = random.randint(0, cols - 1)
        coord_y = random.randint(0, rows - 1)
        if game_map[coord_y][coord_x] == grass_ico:
            game_map[coord_y][coord_x] = unit_ico
            break
    return game_map, coord_y, coord_x


@bot.message_handler(commands=['play'])
def play_message(message):
    cols = 8
    rows = 8
    game_map = get_map_str(cols, rows)

    wolf_count = 3
    wolf_units = {}
    for wolf_i in range(wolf_count):
        game_map, coord_y, coord_x = place_unit(game_map, wolf_ico, cols, rows)
        wolf_units[(coord_y, coord_x)] = {"hp":2}

    game_map, coord_y, coord_x = place_unit(game_map, officer_ico, cols, rows)
    officer = [coord_y, coord_x]
    game_map,  coord_y, coord_x = place_unit(game_map, horse_ico, cols, rows)
    horse = [coord_y, coord_x]

    user_data = {
        "game_map" : game_map,
        "wolf_units" : wolf_units,
        "officer" : officer,
        "horse" : horse
    }

    maps[message.chat.id] = user_data
    map_str = ''.join(sum(game_map, []))
    map_str += "Officer move turn"

    bot.send_message(message.from_user.id, map_str, reply_markup=officer_move_keyboard)


def attack_the_wolf(attack_x, attack_y, damage, user_data):
    wolf_units = user_data['wolf_units']
    if attack_y > 7 or attack_y < 0 or attack_x > 7 or attack_x < 0:
        map_str = "Error: Некого атаковать"
        return user_data, map_str, officer_attack_keyboard

    if user_data['game_map'][attack_y][attack_x] == wolf_ico:
        wolf_units[attack_y, attack_x]["hp"] -= damage
        if wolf_units[(attack_y, attack_x)]["hp"] < 1:
            user_data['game_map'][attack_y][attack_x] = grass_ico
            wolf_units.pop((attack_y, attack_x))
        user_data['wolf_units'] = wolf_units
        map_str = ''.join(sum(user_data['game_map'], []))
        map_str += "Horse move turn"
        return user_data, map_str, horse_move_keyboard
    else:
        map_str = "Error: Некого атаковать"
        return user_data, map_str, officer_attack_keyboard


def horse_attack_the_wolf(attack_x, attack_y, damage, user_data, horse):
    wolf_units = user_data['wolf_units']
    if attack_y > 7 or attack_y < 0 or attack_x > 7 or attack_x < 0:
        message = "Error: Некого атаковать"
        return user_data, message, horse_attack_keyboard

    if user_data['game_map'][attack_y][attack_x] == wolf_ico:
        wolf_units[attack_y, attack_x]["hp"] -= damage
        if wolf_units[(attack_y, attack_x)]["hp"] < 1:
            user_data['game_map'][attack_y][attack_x] = horse_ico
            user_data['game_map'][horse[0]][horse[1]] = grass_ico
            horse = [attack_y, attack_x]
            user_data['horse'] = horse
            wolf_units.pop((attack_y, attack_x))
            user_data['wolf_units'] = wolf_units
            message = "Officer move turn"
        else:
            message = f"Конь нанёс {damage} урона волку \n"
            message += "Officer move turn"
        return user_data, message, officer_move_keyboard
    else:
        message = "Error: Некого атаковать"
        return user_data, message, horse_attack_keyboard


def officer_move(query, user_data):
    officer = user_data['officer']
    player_x = officer[1]
    player_y = officer[0]

    if query.data == 'o_m_left':
        new_x = player_x - 1
        new_y = player_y
    elif query.data == 'o_m_right':
        new_x = player_x + 1
        new_y = player_y
    elif query.data == 'o_m_up':
        new_y = player_y - 1
        new_x = player_x
    elif query.data == 'o_m_down':
        new_y = player_y + 1
        new_x = player_x

    if new_x < 0 or new_x > 7 or new_y < 0 or new_y > 7:
        map_str = "Error: выход за края!"
        return user_data, map_str, officer_move_keyboard
    if user_data['game_map'][new_y][new_x] != grass_ico:
        map_str = "Error: Клетка занята другим юнитом"
        return user_data, map_str, officer_move_keyboard

    officer[1] = new_x
    officer[0] = new_y
    user_data['officer'] = officer
    user_data['game_map'][new_y][new_x] = user_data['game_map'][player_y][player_x]
    user_data['game_map'][player_y][player_x] = grass_ico
    map_str = ''.join(sum(user_data['game_map'], []))
    map_str += "Officer attack turn"

    return user_data, map_str, officer_attack_keyboard


def officer_attack(query, user_data):
    officer = user_data['officer']
    wolf_units = user_data['wolf_units']
    player_x = officer[1]
    player_y = officer[0]

    if query.data == 'o_a_up_left':
        attack_x = player_x - 1
        attack_y = player_y - 1
        user_data, map_str, keyboard = attack_the_wolf(attack_x, attack_y, 2, user_data)
        return user_data, map_str, keyboard
    elif query.data == 'o_a_up_right':
        attack_x = player_x + 1
        attack_y = player_y - 1
        user_data, map_str, keyboard = attack_the_wolf(attack_x, attack_y, 2, user_data)
        return user_data, map_str, keyboard
    elif query.data == 'o_a_down_left':
        attack_x = player_x - 1
        attack_y = player_y + 1
        user_data, map_str, keyboard = attack_the_wolf(attack_x, attack_y, 2, user_data)
        return user_data, map_str, keyboard
    elif query.data == 'o_a_down_right':
        attack_x = player_x + 1
        attack_y = player_y + 1
        user_data, map_str, keyboard = attack_the_wolf(attack_x, attack_y, 2, user_data)
        return user_data, map_str, keyboard
    elif query.data == 'o_a_skip':
        map_str = ''.join(sum(user_data['game_map'], []))
        map_str += "Horse move turn"
        return user_data, map_str, horse_move_keyboard


def horse_move(query, user_data):
    horse = user_data['horse']
    horse_x = horse[1]
    horse_y = horse[0]

    if query.data == 'h_m_up_left':
        new_x = horse_x - 1
        new_y = horse_y - 2
    elif query.data == 'h_m_up_right':
        new_x = horse_x + 1
        new_y = horse_y - 2
    elif query.data == 'h_m_down_left':
        new_x = horse_x - 1
        new_y = horse_y + 2
    elif query.data == 'h_m_down_right':
        new_x = horse_x + 1
        new_y = horse_y + 2
    elif query.data == 'h_m_left_up':
        new_x = horse_x - 2
        new_y = horse_y - 1
    elif query.data == 'h_m_left_down':
        new_x = horse_x - 2
        new_y = horse_y + 1
    elif query.data == 'h_m_right_up':
        new_x = horse_x + 2
        new_y = horse_y - 1
    elif query.data == 'h_m_right_down':
        new_x = horse_x + 2
        new_y = horse_y + 1

    if new_x < 0 or new_x > 7 or new_y < 0 or new_y > 7:
        map_str = "Error: выход за края!"
        return user_data, map_str, horse_move_keyboard

    if user_data['game_map'][new_y][new_x] != grass_ico:
        map_str = "Error: Клетка занята другим юнитом"
        return user_data, map_str, horse_move_keyboard

    horse[1] = new_x
    horse[0] = new_y
    user_data['horse'] = horse
    user_data['game_map'][new_y][new_x] = user_data['game_map'][horse_y][horse_x]
    user_data['game_map'][horse_y][horse_x] = grass_ico
    map_str = ''.join(sum(user_data['game_map'], []))
    map_str += "Horse attack turn"

    return user_data, map_str, horse_attack_keyboard


def horse_attack(query, user_data):
    horse = user_data['horse']
    wolf_units = user_data['wolf_units']
    horse_x = horse[1]
    horse_y = horse[0]

    if query.data == 'h_a_up_left':
        attack_x = horse_x - 1
        attack_y = horse_y - 2
        user_data, map_str, keyboard = horse_attack_the_wolf(attack_x, attack_y, 1, user_data, horse)
    elif query.data == 'h_a_up_right':
        attack_x = horse_x + 1
        attack_y = horse_y - 2
        user_data, map_str, keyboard = horse_attack_the_wolf(attack_x, attack_y, 1, user_data, horse)
    elif query.data == 'h_a_down_left':
        attack_x = horse_x - 1
        attack_y = horse_y + 2
        user_data, map_str, keyboard = horse_attack_the_wolf(attack_x, attack_y, 1, user_data, horse)
    elif query.data == 'h_a_down_right':
        attack_x = horse_x + 1
        attack_y = horse_y + 2
        user_data, map_str, keyboard = horse_attack_the_wolf(attack_x, attack_y, 1, user_data, horse)
    elif query.data == 'h_a_left_up':
        attack_x = horse_x - 2
        attack_y = horse_y - 1
        user_data, map_str, keyboard = horse_attack_the_wolf(attack_x, attack_y, 1, user_data, horse)
    elif query.data == 'h_a_left_down':
        attack_x = horse_x - 2
        attack_y = horse_y + 1
        user_data, map_str, keyboard = horse_attack_the_wolf(attack_x, attack_y, 1, user_data, horse)
    elif query.data == 'h_a_right_up':
        attack_x = horse_x + 2
        attack_y = horse_y - 1
        user_data, map_str, keyboard = horse_attack_the_wolf(attack_x, attack_y, 1, user_data, horse)
    elif query.data == 'h_a_right_down':
        attack_x = horse_x + 2
        attack_y = horse_y + 1
        user_data, map_str, keyboard = horse_attack_the_wolf(attack_x, attack_y, 1, user_data, horse)
    elif query.data == 'h_a_skip':
        map_str = "Officer move turn"
        keyboard = officer_move_keyboard

    return user_data, map_str, keyboard


def wolf_turn(user_data, message):
    wolf_units = user_data["wolf_units"]
    game_map = user_data["game_map"]
    wolf_list = list(wolf_units)
    for wolf in wolf_list:
        counter = 0
        y = wolf[0]
        x = wolf[1]
        move_direction = random.randint(1,4)
        while True:
            if move_direction == 1:
                new_x = x + 1
                if new_x < 0 or new_x > 7 or game_map[y][new_x] != grass_ico:
                    move_direction += 1
                else:
                    game_map[y][new_x] = wolf_ico
                    game_map[y][x] = grass_ico
                    wolf_units[(y, new_x)] = wolf_units.pop(wolf)
                    break
            if move_direction == 2:
                new_x = x - 1
                if new_x < 0 or new_x > 7 or game_map[y][new_x] != grass_ico:
                    move_direction += 1
                else:
                    game_map[y][new_x] = wolf_ico
                    game_map[y][x] = grass_ico
                    wolf_units[(y, new_x)] = wolf_units.pop(wolf)
                    break
            if move_direction == 3:
                new_y = y + 1
                if new_y < 0 or new_y > 7 or game_map[new_y][x] != grass_ico:
                    move_direction += 1
                else:
                    game_map[new_y][x] = wolf_ico
                    game_map[y][x] = grass_ico
                    wolf_units[(new_y, x)] = wolf_units.pop(wolf)
                    break
            if move_direction == 4:
                new_y = y - 1
                if new_y < 0 or new_y > 7 or game_map[new_y][x] != grass_ico:
                    move_direction = 1
                else:
                    game_map[new_y][x] = wolf_ico
                    game_map[y][x] = grass_ico
                    wolf_units[(new_y, x)] = wolf_units.pop(wolf)
                    break
            counter += 1
            if counter == 2:
                break
    user_data["game_map"] = game_map
    user_data["wolf_units"] = wolf_units
    map_str = ''.join(sum(user_data['game_map'], []))
    map_str += message
    return user_data, map_str


@bot.callback_query_handler(func=lambda call: True)
def callback_func(query):
    user_data = maps[query.message.chat.id]
    if "o_m_" in query.data:
        user_data, map_str, keyboard = officer_move(query, user_data)
        if "Error" in map_str:
            bot.answer_callback_query(callback_query_id=query.id, text=map_str)
            return None
    elif "o_a_" in query.data:
        user_data, map_str, keyboard = officer_attack(query, user_data)
        if "Error" in map_str:
            bot.answer_callback_query(callback_query_id=query.id, text=map_str)
            return None
    elif "h_m_" in query.data:
        user_data, map_str, keyboard = horse_move(query, user_data)
        if "Error" in map_str:
            bot.answer_callback_query(callback_query_id=query.id, text=map_str)
            return None
    elif "h_a_" in query.data:
        user_data, map_str, keyboard = horse_attack(query, user_data)
        if "Error" in map_str:
            bot.answer_callback_query(callback_query_id=query.id, text=map_str)
            return None
        else:
            user_data, map_str = wolf_turn(user_data, map_str)

    if len(user_data["wolf_units"]) == 0:
        bot.edit_message_text(chat_id=query.message.chat.id,
                              message_id=query.message.id,
                              text="Вы победили")
    else:
        maps[query.message.chat.id] = user_data
        bot.edit_message_text(chat_id=query.message.chat.id,
                              message_id=query.message.id,
                              text=map_str,
                              reply_markup=keyboard)


bot.polling(none_stop=False, interval=0)
