import discord
import asyncio
import shutil
import requests
import openai
from discord.ext import commands, tasks
from discord.ui import View
import os
import time
from datetime import datetime, timedelta

user_contexts = {}
context_store = {}
context_store_chat = {}
cooldowns_chat = {}

intents = discord.Intents.default()
intents.message_content = True
bot = commands.AutoShardedBot(command_prefix='ak.', intents=intents, shard_count=2)

api_key = os.getenv("OPENAI_API_KEY")

@tasks.loop(hours=1)
async def update_stats():
    await bot.wait_until_ready()

    await update_topgg_stats()

    await update_sdc_stats()

async def update_topgg_stats():
    bot_id = "bot_id"
    token = "top_gg_token"

    url = f"https://top.gg/api/bots/{bot_id}/stats"
    headers = {
        'Authorization': token
    }
    payload = {
        'server_count': len(bot.guilds)
    }

    response = requests.post(url, headers=headers, data=payload)

    if response.status_code == 200:
        print(f"[Top.gg API] Статистика успешно обновлена: {len(bot.guilds)} серверов.")
    else:
        print(f"[Top.gg API] Ошибка при обновлении статистики: {response.status_code}")
        
async def update_sdc_stats():
    url = "https://api.server-discord.com/v2/bots/{bot_id}/stats"
    headers = {
        'Authorization': "SDC {api_key}"
    }
    data = {
        'servers': len(bot.guilds),
        'shards': bot.shard_count,
    }

    r = requests.post(url=url, headers=headers, data=data)

    if r.status_code == 200:
        print(f"[SDC REQ LOG]: Установлено новое количество серверов на мониторинге: {len(bot.guilds)} и шардов: {bot.shard_count}")
    else:
        print(f"[SDC REQ LOG]: Ошибка в отправке запроса на установку количества серверов! Code: {r.status_code}")

activities_list = [
    discord.Activity(type=discord.ActivityType.playing, name="/help | /imagine"),
    discord.Game(name="Серверов: {server_count}"),
]

async def change_bot_activity():
    current_activity_index = 0
    while True:
        current_activity = activities_list[current_activity_index]
        if current_activity_index == 1:
            current_activity = discord.Game(name=f"Серверов: {len(bot.guilds)}")
        await bot.change_presence(activity=current_activity)
        current_activity_index = (current_activity_index + 1) % len(activities_list)
        await asyncio.sleep(10)  

@bot.event
async def on_shard_connect(shard_id):
    print(f"Shard {shard_id} connected!")        
        
@bot.event
async def on_ready():
    send_embed_toppgg.start()
    send_embed_sdc.start()
    update_stats.start()
    bot.loop.create_task(change_bot_activity())
    current_date = datetime.now()
    if current_date.day == 1:
        for user_id_folder in os.listdir("aika_users"):
            if user_id_folder in blocked_users:
                continue

            user_folder = os.path.join("aika_users", user_id_folder)
            notification_path = os.path.join(user_folder, "settings", "notifications.txt")
            balance_file = os.path.join(user_folder, "balls_balance.txt")
            with open(balance_file, "w") as f:
                f.write("0")

            if os.path.exists(notification_path):
                with open(notification_path, "r") as notify_file:
                    notification_setting = notify_file.read().strip()

            if notification_setting.lower() != "none":
                user = await bot.fetch_user(int(user_id_folder))
                try:
                    embed = discord.Embed(title="Системное уведомление", description='Привет, крутой человек! 😎🌟\n\nПриготовься к волнующим новостям! 🚀 **Твои баллы, которые могли дать тебе скидку до 100% на любую подписку в Aika AI, были обнулены по окончании месяца.** Не переживай, это начало чего-то новенького! Теперь наш путь лежит впереди, и ты можешь в этом участвовать.\n\nТак что не забудь заглянуть на странички Айки на этих мониторингах: [Top.gg](https://top.gg/bot/1104761295833673798) и [AVEX](https://bots-discord.pw/bot/1104761295833673798) и начни копить баллы снова! 😊 Нужны подробности? Просто напиши </pbonus:1147175159694897165> и узнай, как это сделать.\n\nА чтобы не пропустить момент, когда снова можно будет апнуть Айку, подключи нашу удобную напоминалку! Просто введи команду </reminder:1165988191375999038>, и мы будем держать тебя в курсе!\n\nДавай вместе двигаться вперед и создавать что-то удивительное!\n🌈 С любовью и энтузиазмом, Aika AI.', color=0xff5733)
                    embed.set_footer(text="Отключить получение уведомлений можно в настройках профиля (/profile).")
                    await user.send(embed=embed)
                except Exception as e:
                    print(f"{e}")
                    pass

    for Filename in os.listdir('./cogs'):
        if Filename.endswith('.py'):
            await bot.load_extension(f'cogs.{Filename[:-3]}')
    print("Бот активен!")
    try:
        synced = await bot.tree.sync()
        print(f"Синхронизировано {len(synced)} команд")
    except Exception as e:
        print(e)

    users_folder = "aika_users"
    for user_id_folder in os.listdir(users_folder):
        if user_id_folder in blocked_users:
            continue

        user_folder = os.path.join(users_folder, user_id_folder)
        period_path = os.path.join(user_folder, "plus", "period.txt")
        buy_date_path = os.path.join(user_folder, "plus", "buy_date.txt")
        plan_path = os.path.join(user_folder, "plus", "plan.txt")

        if not os.path.exists(period_path) or not os.path.exists(buy_date_path) or not os.path.exists(plan_path):
            continue

        with open(period_path, "r") as f:
            period = f.read().strip()

        with open(buy_date_path, "r") as f:
            buy_date_str = f.read().strip()

        with open(plan_path, "r") as f:
            user_plan = f.read().strip()

        try:
            period_duration = int(period[:-1])
            period_unit = period[-1]

            day, month, year = buy_date_str.split(".")
            buy_date_obj = datetime(int(year), int(month), int(day))

            if period_unit == "M":
                expiration_date = buy_date_obj + timedelta(days=30 * period_duration)
            elif period_unit == "Y":
                expiration_date = buy_date_obj + timedelta(days=365 * period_duration)
            else:
                continue

            current_date = datetime.now()
            if current_date > expiration_date and user_plan != "Free":
                with open(plan_path, "w") as f:
                    f.write("Free")
                with open(period_path, "w") as f:
                    f.write("None")
                with open(buy_date_path, "w") as f:
                    f.write("None")

                user_notification_path = os.path.join(user_folder, "settings", "notifications.txt")
                if os.path.exists(user_notification_path):
                    with open(user_notification_path, "r") as notify_file:
                        notification_setting = notify_file.read().strip()
                        if notification_setting.lower() != "none":
                            user = await bot.fetch_user(int(user_id_folder))
                            try:
                                await user.send('**Ваша подписка истекла. Тариф был изменен на Free.**')
                            except Exception as e:
                                print(f"{e}")
                                pass

        except ValueError as e:
            continue

with open('admins.txt', 'r') as f:
    admins = [int(line.strip()) for line in f]

blocked_users = set()
with open("blocked_users.txt", "r") as blocked_file:
    blocked_users = set(map(str.strip, blocked_file.readlines()))

@tasks.loop(hours=12)
async def send_embed_toppgg():
    users_folder = "aika_users"
    with open("upers.txt", "r") as upers_file:
        upers = set(map(str.strip, upers_file.readlines()))

    for user_id in upers:
        user_folder = os.path.join(users_folder, user_id)
        if os.path.exists(user_folder):
            embed = discord.Embed(title="Время апать!", description="Пришло время апнуть меня на Top.gg", color=discord.Color.orange())
            current_time = datetime.now()
            next_message_time = current_time + timedelta(hours=12)
            view = View()
            topgg_emoji = discord.PartialEmoji(name=':topgg:', id=0000000000)
            button = discord.ui.Button(label="Top.gg", style=discord.ButtonStyle.link, url="https://top.gg/bot/{bot_id}", emoji=topgg_emoji)
            view.add_item(button)
            embed.set_footer(text=f"Следующее напоминание будет через 12 часов, в {next_message_time.strftime('%H:%M')}.")
            try:
                user = await bot.fetch_user(int(user_id))
                await user.send(embed=embed, view=view)
            except Exception as e:
                print(f"Ошибка при отправке сообщения пользователю {user_id}: {e}")
                
@tasks.loop(hours=4)
async def send_embed_sdc():
    users_folder = "aika_users"
    with open("upers.txt", "r") as upers_file:
        upers = set(map(str.strip, upers_file.readlines()))

    for user_id in upers:
        user_folder = os.path.join(users_folder, user_id)
        if os.path.exists(user_folder):
            embed = discord.Embed(title="Время апать!", description="Пришло время апнуть меня на SD.C", color=discord.Color.orange())
            current_time = datetime.now()
            next_message_time = current_time + timedelta(hours=4)
            view = View()
            sdc_emoji = discord.PartialEmoji(name=':sdc:', id=000000000000000000)
            button = discord.ui.Button(label="SD.C", style=discord.ButtonStyle.link, url="https://bots.server-discord.com/{bot_id}", emoji=sdc_emoji)
            view.add_item(button)
            embed.set_footer(text=f"Следующее напоминание будет через 4 часа, в {next_message_time.strftime('%H:%M')}.")
            try:
                user = await bot.fetch_user(int(user_id))
                await user.send(embed=embed, view=view)
            except Exception as e:
                print(f"Ошибка при отправке сообщения пользователю {user_id}: {e}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.startswith('ak.add-money'):
        if message.author.id not in admins:
            await message.channel.send("У вас нет прав для использования этой команды.")
            return

        _, user_id, count = message.content.split()
        user_id = user_id.strip()
        count = int(count.strip())

        user_folder = os.path.join("aika_users", user_id)
        if not os.path.exists(user_folder):
            await message.channel.send("Пользователь не найден.")
            return

        with open("blocked_users.txt", "r") as blocked_users_file:
            blocked_users = [blocked_user.strip() for blocked_user in blocked_users_file.readlines()]

        if user_id in blocked_users:
            await message.channel.send("Пользователь заблокирован и не может получать уведомления.")
            return

        settings_path = os.path.join(user_folder, "settings", "notifications.txt")
        if os.path.exists(settings_path):
            with open(settings_path, 'r') as settings_file:
                notification_preference = settings_file.read().strip().lower()
                if notification_preference != 'none':
                    balance_path = os.path.join(user_folder, "balance.txt")
                    if os.path.exists(balance_path):
                        with open(balance_path, "r") as f:
                            current_balance = int(f.read())
                        new_balance = current_balance + count
                        with open(balance_path, "w") as f:
                            f.write(str(new_balance))

                        await message.channel.send(f"Баланс пользователя {user_id} успешно обновлен: {new_balance}")

                        user = await bot.fetch_user(user_id)
                        if user:
                            await user.send(f'**Ваш баланс был пополнен на {count} руб**')

                        user = message.author.name
                        channel_id = 000000000000000000
                        channel = bot.get_channel(channel_id)
                        await channel.send(f'Админ {user} добавил {count} рублей пользователю с ID {user_id}')
                    else:
                        await message.channel.send("Произошла ошибка при обновлении баланса пользователя.")
                else:
                    await message.channel.send("У пользователя отключены уведомления, но баланс был обновлен.")
        else:
            await message.channel.send("Произошла ошибка при проверке настроек пользователя.")

    elif message.content.startswith('ak.mailing'):
        if message.author.id not in admins:
            await message.channel.send("У вас нет прав для использования этой команды.")
            return

        _, text = message.content.split(' ', 1)
        text = text.strip()
        embed = discord.Embed(title="Уведомление", description=text, colour=0x921294)
        embed.set_footer(text="Отключить получение уведомлений можно в настройках профиля (/profile).")

        for user_id in os.listdir("aika_users"):
            user_folder = os.path.join("aika_users", user_id)
            user_id = str(user_id)
            if os.path.isdir(user_folder):
                with open("blocked_users.txt", "r") as blocked_users_file:
                    blocked_users = [blocked_user.strip() for blocked_user in blocked_users_file.readlines()]
                    if user_id not in blocked_users:
                        settings_file_path = os.path.join(user_folder, "settings", "notifications.txt")
                        if os.path.exists(settings_file_path):
                            with open(settings_file_path, 'r') as settings_file:
                                notification_preference = settings_file.read().strip().lower()
                                if notification_preference not in ['os', 'none']:
                                    try:
                                        user = await bot.fetch_user(int(user_id))
                                        await user.send(embed=embed)
                                    except discord.Forbidden:
                                        await message.channel.send(f"Не удалось отправить уведомление пользователю {user_id}.")

        await message.channel.send("Уведомления успешно отправлены.")

    elif message.content.startswith('ak.deluser'):
        if message.author.id not in admins:
            await message.channel.send("У вас нет прав для использования этой команды.")
            return

        _, user_id = message.content.split()
        user_id = user_id.strip()

        user_folder = os.path.join("aika_users", user_id)
        if not os.path.exists(user_folder):
            await message.channel.send("Пользователь не найден.")
            return

        shutil.rmtree(user_folder)

        await message.channel.send(f"Аккаунт пользователя {user_id} успешно удален.")

        user = message.author.name
        channel_id = 000000000000000000
        channel = bot.get_channel(channel_id)
        await channel.send(f'Админ {user} удалил аккаунт пользователя {user_id}.')

        user = await bot.fetch_user(user_id)
        if user:
            await user.send('**Ваш аккаунт был успешно удален. Если у вас есть вопросы, обратитесь к администратору.**')

    elif message.content.startswith('ak.add-balls'):
        if message.author.id not in admins:
            await message.channel.send("У вас нет прав для использования этой команды.")
            return

        _, user_id = message.content.split()
        user_id = user_id.strip()

        user_folder = os.path.join("aika_users", user_id)
        if not os.path.exists(user_folder):
            await message.channel.send("Пользователь не найден.")
            return

        with open("blocked_users.txt", "r") as blocked_users_file:
            blocked_users = [blocked_user.strip() for blocked_user in blocked_users_file.readlines()]

        if user_id in blocked_users:
            await message.channel.send("Пользователь заблокирован и не может получать баллы.")
            return

        settings_path = os.path.join(user_folder, "settings", "notifications.txt")
        if os.path.exists(settings_path):
            with open(settings_path, 'r') as settings_file:
                notification_preference = settings_file.read().strip().lower()
                if notification_preference != 'none':
                    plan_path = os.path.join(user_folder, "plus", "plan.txt")
                    if not os.path.exists(plan_path):
                        await message.channel.send("Пользователь не имеет тарифного плана.")
                        return

                    with open(plan_path, "r") as f:
                        plan = f.read().strip()

                    balls_path = os.path.join(user_folder, "balls_balance.txt")
                    with open(balls_path, "r") as f:
                        balls_balance = int(f.read())

                    if plan == "Excelsior":
                        balls_balance += 2
                    else:
                        balls_balance += 1

                    with open(balls_path, "w") as f:
                        f.write(str(balls_balance))

                    await message.channel.send(f"Баллы пользователя {user_id} успешно обновлены до {balls_balance}")

                    user = await bot.fetch_user(user_id)
                    if user:
                        await user.send(f'**Вы успешно заработали балл(-ы). Посмотреть текущий баланс можно по команде /profile**')

                    user = message.author.name
                    channel_id = 000000000000000000
                    channel = bot.get_channel(channel_id)
                    await channel.send(f'Админ {user} добавил баллов пользователю с ID {user_id}')
                else:
                    await message.channel.send("У пользователя отключены уведомления, но баллы были обновлены.")
        else:
            await message.channel.send("Произошла ошибка при проверке настроек пользователя.")

    elif message.content.startswith('ak.ban'):
        if message.author.id not in admins:
            await message.channel.send("У вас нет прав для использования этой команды.")
            return

        _, user_id, reason = message.content.split(maxsplit=2)
        user_id = user_id.strip()

        try:
            user = await bot.fetch_user(user_id)
        except discord.NotFound:
            await message.channel.send(f"Пользователь с ID {user_id} не найден.")
            return

        user_folder = os.path.join("aika_users", user_id)
        settings_path = os.path.join(user_folder, "settings", "notifications.txt")

        with open('blocked_users.txt', 'a') as blocked_file:
            blocked_file.write(f"{user_id}\n")

        if os.path.exists(settings_path):
            with open(settings_path, 'r') as settings_file:
                notification_preference = settings_file.read().strip().lower()
                if notification_preference != 'none':
                    try:
                        await user.send(f"**Ваш аккаунт в Aika AI был заблокирован. Причина:** {reason}")
                    except discord.Forbidden:
                        await message.channel.send(f"Не удалось отправить уведомление пользователю {user_id} о блокировке.")
                else:
                    await message.channel.send(f"Пользователь с ID {user_id} отключил уведомления, но был заблокирован.")
        else:
            await message.channel.send(f"Пользователь с ID {user_id} был заблокирован. Причина: {reason}")

        user = message.author.name
        channel_id = 000000000000000000
        channel = bot.get_channel(channel_id)
        await channel.send(f'Админ {user} забанил пользователя {user_id} по причине: {reason}')

    elif message.content.startswith('ak.unban'):
        if message.author.id not in admins:
            await message.channel.send("У вас нет прав для использования этой команды.")
            return

        _, user_id = message.content.split()
        user_id = user_id.strip()

        try:
            with open('blocked_users.txt', 'r') as blocked_file:
                blocked_users = blocked_file.readlines()

            with open('blocked_users.txt', 'w') as blocked_file:
                unbanned = False
                for line in blocked_users:
                    if not line.strip().startswith(str(user_id)):
                        blocked_file.write(line)
                    else:
                        unbanned = True

                if unbanned:
                    user_folder = os.path.join("aika_users", user_id)
                    settings_path = os.path.join(user_folder, "settings", "notifications.txt")

                    if os.path.exists(settings_path):
                        with open(settings_path, 'r') as settings_file:
                            notification_preference = settings_file.read().strip().lower()
                            if notification_preference != 'none':
                                try:
                                    user = await bot.fetch_user(user_id)
                                    await user.send(f"**Ваш аккаунт в Aika AI был разблокирован. Однако если у вас была подписка Aika Plus, то она была отключена при Вашей блокировке.**")
                                except discord.NotFound:
                                    pass

                    await message.channel.send(f"Пользователь с ID {user_id} был разблокирован.")
                    user = message.author.name
                    channel_id = 000000000000000000
                    channel = bot.get_channel(channel_id)
                    await channel.send(f'Админ {user} разбанил пользователя {user_id}')
                else:
                    await message.channel.send(f"Пользователь с ID {user_id} не найден в списке заблокированных.")
        except Exception as e:
            print(e)
            await message.channel.send("Произошла ошибка при разблокировке пользователя.")

    elif message.content.startswith('ak.apb-ban'):
        if message.author.id not in admins:
            await message.channel.send("У вас нет прав на выполнение этой команды.")
            return

        _, user_id, reason = message.content.split(' ')

        blocked_users_file = "apb_ban.txt"

        user_folder_path = f"aika_skills_console_users/{user_id}"
        settings_path = os.path.join(user_folder_path, "settings", "notifications.txt")

        if os.path.exists(settings_path):
            with open(settings_path, 'r') as settings_file:
                notification_preference = settings_file.read().strip().lower()
                if notification_preference == 'none':
                    await message.channel.send(f"У пользователя с ID {user_id} отключены уведомления. Блокировка была применена, но уведомление не отправлено.")
                    return

        with open(blocked_users_file, "a") as f:
            f.write(f"{user_id}\n")

        user = await bot.fetch_user(user_id)
        await user.send(f'**Вам был заблокирован доступ к бонусной системе Aika Plus Bonus по следующей причине:** {reason}')

        user = message.author.name
        channel_id = 000000000000000000
        channel = bot.get_channel(channel_id)
        await channel.send(f'Админ {user} заблокировал доступ к Aika Skills Bonus пользователю {user_id} по причине: {reason}.')
        await message.channel.send("Пользователь был успешно заблокирован.")

    elif message.content.startswith('ak.apb-unban'):
        if message.author.id not in admins:
            await message.channel.send("У вас нет прав на выполнение этой команды.")
            return

        _, user_id = message.content.split(' ')

        blocked_users_file = "apb_ban.txt"

        with open(blocked_users_file, "r") as f:
            blocked_user_ids = [line.strip() for line in f.readlines()]

        if user_id in blocked_user_ids:
            blocked_user_ids.remove(user_id)

        with open(blocked_users_file, "w") as f:
            for blocked_id in blocked_user_ids:
                f.write(f"{blocked_id}\n")

        user_folder_path = f"aika_skills_console_users/{user_id}"
        settings_path = os.path.join(user_folder_path, "settings", "notifications.txt")

        if os.path.exists(settings_path):
            with open(settings_path, 'r') as settings_file:
                notification_preference = settings_file.read().strip().lower()
                if notification_preference == 'none':
                    await message.channel.send(f"У пользователя с ID {user_id} отключены уведомления. Разблокировка была применена, но уведомление не отправлено.")
                    return

        user = await bot.fetch_user(user_id)
        await user.send('**Вам был разблокирован доступ к Aika Plus Bonus.**')

        user = message.author.name
        channel_id = 000000000000000000
        channel = bot.get_channel(channel_id)
        await channel.send(f'Админ {user} разблокировал доступ к Aika Skills Bonus пользователю {user_id}.')
        await message.channel.send("Пользователь был успешно разблокирован.")
        
    elif message.content.startswith('ak.give-plus'):
        if message.author.id not in admins:
            await message.channel.send("У вас нет прав для использования этой команды.")
            return

        _, user_id, plan, duration = message.content.split()
        user_id = user_id.strip()

        user_folder = os.path.join("aika_users", user_id)
        if not os.path.exists(user_folder):
            await message.channel.send("Пользователь не найден.")
            return

        with open("blocked_users.txt", "r") as blocked_users_file:
            blocked_users = [blocked_user.strip() for blocked_user in blocked_users_file.readlines()]

        if user_id in blocked_users:
            await message.channel.send("Пользователь заблокирован и не может получать уведомления.")
            return

        plan_path = os.path.join(user_folder, "plus", "plan.txt")
        if os.path.exists(plan_path):
            with open(plan_path, 'w') as plan_file:
                plan_file.write(plan.strip())

            period_path = os.path.join(user_folder, "plus", "period.txt")
            with open(period_path, 'w') as period_file:
                period_file.write(duration.strip())

            await message.channel.send("Введите причину выдачи подписки:")
            try:
                reason_message = await bot.wait_for("message", check=lambda m: m.author == message.author, timeout=60)
                reason = reason_message.content

                buy_date_path = os.path.join(user_folder, "plus", "buy_date.txt")
                current_date = datetime.now().strftime('%d.%m.%Y')
                with open(buy_date_path, 'w') as buy_date_file:
                    buy_date_file.write(current_date)

                log_channel_id = 000000000000000000
                log_channel = bot.get_channel(log_channel_id)
                log_message = f"Пользователю с ID {user_id} выдана подписка {plan} на {duration} по причине: {reason}"
                await log_channel.send(log_message)

                user = await bot.fetch_user(user_id)
                if user:
                    await user.send(f'Вам была выдана подписка {plan} на {duration} по причине: {reason}')

                await message.channel.send("Подписка успешно выдана.")
            except TimeoutError:
                await message.channel.send("Время на ввод причины истекло.")
        else:
            await message.channel.send("Произошла ошибка при обновлении подписки пользователя.")

    elif message.content.startswith('ak.remove-plus'):
        if message.author.id not in admins:
            await message.channel.send("У вас нет прав для использования этой команды.")
            return

        _, user_id, reason = message.content.split(' ', 2)
        user_id = user_id.strip()

        user_folder = os.path.join("aika_users", user_id)
        if not os.path.exists(user_folder):
            await message.channel.send("Пользователь не найден.")
            return

        with open("blocked_users.txt", "r") as blocked_users_file:
            blocked_users = [blocked_user.strip() for blocked_user in blocked_users_file.readlines()]

        if user_id in blocked_users:
            await message.channel.send("Пользователь заблокирован и не может получать уведомления.")
            return

        plan_path = os.path.join(user_folder, "plus", "plan.txt")
        if os.path.exists(plan_path):
            with open(plan_path, 'w') as plan_file:
                plan_file.write("Free")

            period_path = os.path.join(user_folder, "plus", "period.txt")
            with open(period_path, 'w') as period_file:
                period_file.write("None")

            buy_date_path = os.path.join(user_folder, "plus", "buy_date.txt")
            with open(buy_date_path, 'w') as buy_date_file:
                buy_date_file.write("None")

            await message.channel.send("Подписка успешно изъята.")
            log_channel_id = 000000000000000000
            log_channel = bot.get_channel(log_channel_id)
            log_message = f"Подписка пользователя с ID {user_id} была изъята по причине: {reason}"
            await log_channel.send(log_message)

            user = await bot.fetch_user(user_id)
            if user:
                await user.send(f'Ваша подписка была изъята по причине: {reason}')
        else:
            await message.channel.send("Произошла ошибка при обновлении подписки пользователя.")

    if message.mention_everyone:
        return

    current_date = datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.now().strftime("%H:%M:%S")
    user_id = str(message.author.id)
    user_name = message.author.name
    user_avatar = str(message.author.avatar.url) if message.author.avatar else "N/A"
    user_created_date = message.author.created_at.strftime("%Y-%m-%d %H:%M:%S")
    user_created_date = message.author.created_at.strftime("%Y-%m-%d %H:%M:%S")
    server = message.guild
    server_name = server.name if server else "Direct Message"
    server_id = server.id if server else "N/A"
    server_avatar = str(server.icon.url) if server and server.icon else "N/A"
    server_users = len([member for member in message.guild.members if not member.bot]) if message.guild else 0
    owner_server = server.owner if server else None
    owner_server_name = owner_server.name if owner_server else "N/A"
    owner_server_id = owner_server.id if owner_server else "N/A"
    owner_server_avatar = str(owner_server.avatar.url) if owner_server and owner_server.avatar else "N/A"
    owner_server_created_date = owner_server.created_at.strftime("%Y-%m-%d %H:%M:%S") if owner_server else "N/A"
    server_members = server.member_count if server else 0
    server_bots = sum(1 for member in server.members if member.bot) if server else 0
    server_roles = len(server.roles) if server else 0
    channel_name = message.channel.name if isinstance(message.channel, discord.TextChannel) else "Direct Message"
    channel_id = message.channel.id
    channel_threads = message.channel.threads if isinstance(message.channel, discord.TextChannel) else 0

    with open("chatting_channels.txt", "r") as file:
        allowed_channels = [int(line.strip()) for line in file.readlines()]

    if message.channel.id not in allowed_channels and not bot.user.mentioned_in(message):
        return    
        
    if message.channel.id in allowed_channels or bot.user.mentioned_in(message):
        user_id = str(message.author.id)
        user_folder = os.path.join("aika_users", str(user_id))
        if not os.path.exists(user_folder):
            embed = discord.Embed(title="Ошибка", description="Хм, похоже я с вами еще не знакома. Пожалуйста, воспользуйтесь командой `/register` чтобы создать свой аккаунт", color=discord.Color.red())
            await message.author.send(embed=embed) if isinstance(message.channel, discord.DMChannel) else await message.channel.send(embed=embed)
            return
        current_time = time.time()
        last_used_time = cooldowns_chat.get(user_id, 0)

        if str(user_id) in open("blocked_users.txt").read():
            error_embed = discord.Embed(title="Ошибка", description="Ваш аккаунт заблокирован.", color=discord.Color.red())
            await message.author.send(embed=error_embed) if isinstance(message.channel, discord.DMChannel) else await message.channel.send(embed=error_embed)
            return

        plan_file_path = f"aika_users/{user_id}/plus/plan.txt"
        if os.path.exists(plan_file_path):
            with open(plan_file_path, "r") as plan_file:
                plan_text = plan_file.read().strip()
            if plan_text == "Basic":
                cooldown = 15
            elif plan_text in ["Standart", "Ultimate", "Excelsior"]:
                cooldown = 0
            else:
                cooldown = 30
        else:
            cooldown = 30

        if current_time - last_used_time < cooldown:
            cooldown_error = f"Ваш тарифный план не позволяет отправлять запросы Айке чаще 1 раза в {cooldown} секунд. Подробнее по команде `/plus`\nВы также можете получить любой уровень подписки Aika Plus, апая [здесь](https://bots.server-discord.com/1104761295833673798). Подробнее по команде </pbonus:1147175159694897165>"
            error_embed = discord.Embed(title="Ошибка", description=cooldown_error, color=discord.Color.red())
            await message.author.send(embed=error_embed)
            return

        if not message.content.replace(bot.user.mention, "").strip():
            empty_query_error = "Ошибка: Пустой запрос."
            error_embed = discord.Embed(title="Ошибка", description=empty_query_error, color=discord.Color.red())
            await message.author.send(embed=error_embed)
            return

        cooldowns_chat[user_id] = current_time
        if message.author.id == bot.user:
            return

        query = message.content.replace(bot.user.mention, "").strip()
        now = datetime.now()
        expiration_time = now + timedelta(minutes=120)
        user_id = str(message.author.id)

        if user_id not in context_store_chat:
            context_store_chat[user_id] = {
                "expiration_time": expiration_time,
                "context": []
            }
        else:
            if now > context_store_chat[user_id]["expiration_time"]:
                context_store_chat[user_id] = {
                    "expiration_time": expiration_time,
                    "context": []
                }

        context = context_store_chat[user_id]["context"]
        context.append({"role": "user", "content": query})

        try:
            async with message.channel.typing():
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "system",
                               "content": f"You are helpful assisant"},
                              {"role": "user", "content": query}] + context,
                    api_key=api_key
                )

                reply = response.choices[0].message.content.strip()

                log_embed = discord.Embed(title="Aika Chat Log", color=0x00ff00)
                log_embed.add_field(name="User", value=message.author.display_name, inline=False)
                log_embed.add_field(name="User ID", value=message.author.id, inline=False)
                log_embed.add_field(name="Server", value=message.guild.name if message.guild else "Direct Message", inline=False)
                log_embed.add_field(name="Server ID", value=message.guild.id if message.guild else "N/A", inline=False)
                log_embed.add_field(name="Channel", value=message.channel.name if isinstance(message.channel, discord.TextChannel) else "Direct Message", inline=False)
                log_embed.add_field(name="Query", value=query, inline=False)

                channel_id = 000000000000000000
                channel = bot.get_channel(channel_id)
                if channel:
                    await channel.send(embed=log_embed)

                if len(reply) > 1024:
                    response_chunks = [reply[i:i + 1024] for i in range(0, len(reply), 1024)]

                    for i, chunk in enumerate(response_chunks):
                        embed = discord.Embed(title=f"Response part {i + 1}", description=chunk,
                                              color=discord.Color.green())
                        channel_id = 000000000000000000
                        channel = bot.get_channel(channel_id)
                        if channel:
                            await channel.send(embed=embed)
                else:
                    embed = discord.Embed(title="Response", description=reply, color=discord.Color.green())
                    channel_id = 000000000000000000
                    channel = bot.get_channel(channel_id)
                    if channel:
                        await channel.send(embed=embed)

                if len(reply) > 1999:
                    response_chunks = [reply[i:i + 1999] for i in range(0, len(reply), 1999)]

                    for chunk in response_chunks:
                        if isinstance(message.channel, discord.DMChannel):
                            sent_message = await message.author.send(chunk, reference=message, mention_author=False)
                        else:
                            sent_message = await message.channel.send(chunk, reference=message, mention_author=False)

                        await sent_message.add_reaction("👍")
                        await sent_message.add_reaction("👎")
                else:
                    if isinstance(message.channel, discord.DMChannel):
                        sent_message = await message.author.send(reply, reference=message, mention_author=False)
                    else:
                        sent_message = await message.channel.send(reply, reference=message, mention_author=False)

                    await sent_message.add_reaction("👍")
                    await sent_message.add_reaction("👎")
        except Exception as e:
            print(f"{e}")
            error_message = f"Извините за неудобства. В настоящее время бот не может обработать ваш запрос из-за технических проблем. Мы работаем над их устранением и ожидаем, что проблема будет решена в ближайшее время. Просим вас не удалять Айку с сервера. Спасибо за понимание."
            error_embed = discord.Embed(title="Ошибка", description=error_message, color=discord.Color.red())
            await message.author.send(embed=error_embed) if isinstance(message.channel, discord.DMChannel) else await message.channel.send(embed=error_embed)

if __name__ == '__main__':
    bot.run(os.getenv("DISCORD_BOT_TOKEN"))