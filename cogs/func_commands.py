import os
from core.classes import Cog_Extension
import discord
from discord import app_commands
from discord.ui import View, Button

class Func_Commands(Cog_Extension):
    @app_commands.command(name="help", description="Показать все команды Айки")
    async def help(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=False)
        user = interaction.user.name
        message = (f'Пользователь {user} использовал команду `/help` в канале `{interaction.channel.name if isinstance(interaction.channel, discord.TextChannel) else "Direct Message"}`.')
        channel_id = 000000000000000000
        channel = self.bot.get_channel(channel_id)
        await channel.send(message)
        user_id = str(interaction.user.id)
        if str(user_id) in open("blocked_users.txt").read():
            error_embed = discord.Embed(title="Ошибка", description="Ваш аккаунт заблокирован.", color=discord.Color.red())
            await interaction.response.send_message(embed=error_embed)
            return

        embed = discord.Embed(title=f"Список всех доступных команд Айки:", color=0x921294)
        embed.add_field(name="Основные команды:", value="<@{id}> </register:{id}> </imagine:{id}> </text-imagine:{id}> </set-channel:{id}>🆕", inline=False)
        embed.add_field(name="Функц. команды:", value="</help:{id}> </profile:{id}> </settings-set:{id}> </info:{id}> </bug-report:{id}>", inline=False)
        embed.add_field(name="Aika Plus:", value="</plus:{id}> </case:{id}> </buy:{id}> </pbonus:{id}> </reminder:{id}> </up-report:{id}> </transfer:{id}>", inline=False)
        embed.add_field(name="Инструменты:", value="</translate:{id}> </search:{id}> </gen-bot:{id}>", inline=False)
        embed.add_field(name="Развлечения:", value="</meme:{id}> </shoot:{id}> </horoscope:{id}> </lucky:{id}>", inline=False)
        embed.add_field(name="Балбесыч:", value="</balb-chat:{id}> </balb-quote:{id}> </balb-text:{id}>", inline=False)
        await interaction.followup.send(embed=embed)
        return

    @app_commands.command(name="profile", description="Показать профиль пользователя")
    async def profile(self, interaction: discord.Interaction, user: discord.User = None):
        await interaction.response.defer()
        user_name = interaction.user.name
        message = (f'Пользователь {user_name} использовал команду `/profile` в канале `{interaction.channel.name if isinstance(interaction.channel, discord.TextChannel) else "Direct Message"}`.')
        channel_id = 000000000000000000
        channel = self.bot.get_channel(channel_id)
        await channel.send(message)
        if user:
            user_id = user.id
            user_mention = user.mention
        else:
            user_id = interaction.user.id
            user_mention = interaction.user.mention

        try:
            username = str(user or interaction.user)
            self.bot.current_channel = interaction.channel
            if str(user_id) in open("blocked_users.txt").read():
                error_embed = discord.Embed(title="Ошибка", description="Ваш аккаунт заблокирован.", color=discord.Color.red())
                await interaction.followup.send(embed=error_embed, ephemeral=True)
                return
            user_folder = os.path.join("aika_users", str(user_id))
            if not os.path.exists(user_folder):
                error_embed = discord.Embed(title="Ошибка", description="Хм, похоже я с вами еще не знакома. Пожалуйста, воспользуйтесь командой `/register` чтобы создать свой аккаунт", color=discord.Color.red())
                await interaction.followup.send(embed=error_embed, ephemeral=True)
                return

            plan_path = os.path.join(user_folder, "plus", "plan.txt")
            with open(plan_path, "r") as f:
                plan = f.read().strip()

            period_path = os.path.join(user_folder, "plus", "period.txt")
            with open(period_path, "r") as f:
                period = f.read().strip()

            date_path = os.path.join(user_folder, "plus", "buy_date.txt")
            with open(date_path, "r") as f:
                buy_date = f.read().strip()

            with open(os.path.join(user_folder, "balance.txt"), "r") as f:
                balance = f.read()
            with open(os.path.join(user_folder, "balls_balance.txt"), "r") as f:
                balls_balance = f.read()
            with open(os.path.join(user_folder, "reg_date.txt"), "r") as f:
                reg_date = f.read()

            blocked_apb_users_file = "blocked_apb_users.txt"
            if str(user_id) in open(blocked_apb_users_file).read():
                balls_balance_display = "Доступ заблокирован"
            else:
                balls_balance_display = f"{balls_balance} баллов"

            period_mapping = {
                "1M": "1 месяц",
                "3M": "3 месяца",
                "6M": "6 месяцев",
                "1Y": "1 год"
            }

            period_display = period_mapping.get(period, "Неизвестно")

            settings_button = Button(label="Настройки")
            async def settings_callback(interaction):
                user_id = interaction.user.id
                try:
                    with open(f'aika_users/{user_id}/settings/notifications.txt', 'r') as file:
                        notif_type = file.read().strip()
                        if notif_type == "OS":
                            notif_text = "Только системные"
                        elif notif_type == "All":
                            notif_text = "Все"
                        elif notif_type == "None":
                            notif_text = "Никакие"
                        else:
                            notif_text = "Неизвестный тип уведомлений"
                except FileNotFoundError:
                    notif_text = "Файл настроек не найден"

                upers = None
                with open("upers.txt", "r") as upers_file:
                    upers = upers_file.read().splitlines()

                up_status = "<:on:{id}>" if str(user_id) in upers else "<:off:{id}>"

                embed = discord.Embed(title="Настройки пользователя <:beta:{id}>")
                embed.add_field(name=f"Уведомления: {notif_text}", value="То, какие уведомления вам могут приходить", inline=False)
                embed.add_field(name=f"Уведомления об апах: {up_status}", value="Параметр того, получаете ли вы уведомления об апах", inline=False)
                embed.set_footer( text="Изменить статус получения уведомлений можно командой /settings_set, а подключить/отключить 'напоминалку апать' можно командой /reminder")
                await interaction.response.send_message(embed=embed, ephemeral=True)

            settings_button.callback = settings_callback
            view = View()
            button = Button(label="Пополнить баланс", url="https://pay.aika-ai.ru/")
            view.add_item(settings_button)
            view.add_item(button)
            embed = discord.Embed(title=f"Профиль пользователя: {username}")
            embed.add_field(name="Никнейм:", value=user_mention, inline=False)
            embed.add_field(name="ID пользователя:", value=f"{user_id}", inline=False)
            if plan == "Free":
                embed.add_field(name="Тарифный план:", value=f'{plan}\n> *Купите Aika Plus, чтобы получить все возможности лучшего ИИ бота в дискорде. Подробнее: `/plus`*', inline=False)
            else:
                embed.add_field(name="Тарифный план:", value=f'{plan}', inline=True)
                if period_display:
                    embed.add_field(name="Продолжительность:", value=period_display, inline=True)
                    embed.add_field(name="Дата покупки:", value=buy_date, inline=True)
            if user is None or user_id == interaction.user.id:
                embed.add_field(name="Баланс:", value=f"{balance} руб.", inline=True)
                embed.add_field(name="Количество баллов:", value=balls_balance_display, inline=True)
            else:
                embed.add_field(name="Баланс:", value="Скрыто", inline=True)
                embed.add_field(name="Количество баллов:", value="Скрыто", inline=True)
            embed.add_field(name="Дата регистрации:", value=reg_date, inline=False)

            embed.set_thumbnail(url=user.avatar.url if user else interaction.user.avatar.url)
            if user is None or user_id == interaction.user.id:
                await interaction.followup.send(embed=embed, view=view, ephemeral=True)
            else:
                await interaction.followup.send(embed=embed, ephemeral=True)
        except Exception as e:
            print(f"{e}")
            error_message = "При отображении профиля произошла ошибка"
            error_embed = discord.Embed(title="Ошибка", description=error_message, color=discord.Color.red())
            await interaction.followup.send(embed=error_embed, ephemeral=True)
            
    @app_commands.command(name="settings-set", description="Настройки уведомлений")
    @app_commands.choices(notifications=[
        app_commands.Choice(name="Все", value="All"),
        app_commands.Choice(name="Только системные", value="OS"),
        app_commands.Choice(name="Никакие", value="None")
    ])
    async def set_notifications(self, interaction, notifications: str):
        try:
            user_id = str(interaction.user.id)
            blocked_users_file_path = "blocked_users.txt"

            with open(blocked_users_file_path, "r") as blocked_users_file:
                blocked_users = blocked_users_file.readlines()
            blocked_users = [user.strip() for user in blocked_users]
            if user_id in blocked_users:
                error_embed = discord.Embed(title="Ошибка", description="Ваш аккаунт заблокирован.", color=discord.Color.red())
                await interaction.response.send_message(embed=error_embed, ephemeral=True)
                return

            user_folder = os.path.join("aika_users", str(user_id))
            if not os.path.exists(user_folder):
                error_embed = discord.Embed(title="Ошибка", description="Хм, похоже я с вами еще не знакома. Пожалуйста, воспользуйтесь командой `/register` чтобы создать свой аккаунт", color=discord.Color.red())
                await interaction.response.send_message(embed=error_embed, ephemeral=True)
                return

            user_id = interaction.user.id
            user_folder = os.path.join("aika_users", str(user_id), "settings")
            if not os.path.exists(user_folder):
                os.makedirs(user_folder)

            notifications_file_path = os.path.join(user_folder, "notifications.txt")

            with open(notifications_file_path, "r") as file:
                current_notifications = file.read().strip()

            notification_names = {
                "All": "Все",
                "OS": "Только системные",
                "None": "Никакие"
            }

            user = interaction.user.name
            message = (f'Пользователь {user} изменил статус уведомлений на `{notification_names}` в канале `{interaction.channel.name if isinstance(interaction.channel, discord.TextChannel) else "Direct Message"}`.')
            channel_id = 000000000000000000
            channel = self.bot.get_channel(channel_id)
            await channel.send(message)

            if current_notifications == notifications:
                error_embed = discord.Embed(title="Ошибка", description=f"Данный статус уведомлений уже установлен: {notification_names.get(notifications)}", color=discord.Color.red())
                await interaction.response.send_message(embed=error_embed, ephemeral=True)
            else:
                with open(notifications_file_path, "w") as file:
                    file.write(notifications)
                success_embed = discord.Embed(title="Уведомления установлены", description=f"Статус уведомлений успешно изменен на: {notification_names.get(notifications)}", color=discord.Color.green())
                await interaction.response.send_message(embed=success_embed, ephemeral=True)

        except Exception as e:
            print(f"{e}")
            error_embed = discord.Embed(title="Ошибка", description=f"При установке уведомлений произошла ошибка", color=discord.Color.red())
            await interaction.response.send_message(embed=error_embed, ephemeral=True)

    @app_commands.command(name="reminder", description="Вкл/выкл напоминания об апах Айки")
    async def reminder_command(self, interaction):
        try:
            user_id = interaction.user.id
            blocked_users_file_path = "blocked_users.txt"
            reminder_file_path = "upers.txt"
            user_folder = os.path.join("aika_users", str(user_id))

            with open(blocked_users_file_path, "r") as blocked_users_file:
                blocked_users = blocked_users_file.readlines()
            blocked_users = [user.strip() for user in blocked_users]
            if str(user_id) in blocked_users:
                error_embed = discord.Embed(title="Ошибка", description="Ваш аккаунт заблокирован.", color=discord.Color.red())
                await interaction.response.send_message(embed=error_embed, ephemeral=True)
                return

            if not os.path.exists(user_folder):
                error_embed = discord.Embed(title="Ошибка", description="Хм, похоже я с вами еще не знакома. Пожалуйста, воспользуйтесь командой `/register` чтобы создать свой аккаунт", color=discord.Color.red())
                await interaction.response.send_message(embed=error_embed, ephemeral=True)
                return

            reminder_enabled = False

            with open(reminder_file_path, "r+") as file:
                user_ids = file.readlines()
                file.seek(0)
                found = False
                for line in user_ids:
                    if str(user_id) not in line.strip():
                        file.write(line)
                    else:
                        found = True
                file.truncate()

                if not found:
                    file.write(str(user_id) + "\n")
                    reminder_enabled = True
                    response_message = "Напоминалка была включена."
                    footer_text = "Отключить напоминалку можно вновь повторным вводом команды."
                    color = discord.Color.green()
                else:
                    reminder_enabled = False
                    response_message = "Напоминалка была отключена."
                    footer_text = "Включить напоминалку можно вновь повторным вводом команды."
                    color = discord.Color.red()

            if reminder_enabled:
                embed = discord.Embed(title="Напоминания включены", description=response_message, color=color)
                embed.set_footer(text=footer_text)
                user = interaction.user.name
                message = (f'Пользователь {user} включил напоминалку об апах')
                channel_id = 000000000000000000
                channel = self.bot.get_channel(channel_id)
                await channel.send(message)
            else:
                embed = discord.Embed(title="Напоминания отключены", description=response_message, color=color)
                embed.set_footer(text=footer_text)
                user = interaction.user.name
                message = (f'Пользователь {user} выключил напоминалку об апах')
                channel_id = 000000000000000000
                channel = self.bot.get_channel(channel_id)
                await channel.send(message)
            await interaction.response.send_message(embed=embed, ephemeral=True)

        except Exception as e:
            print(f"{e}")
            error_embed = discord.Embed(title="Ошибка", description=f"При управлении напоминаниями произошла ошибка", color=discord.Color.red())
            await interaction.response.send_message(embed=error_embed, ephemeral=True)

    @app_commands.command(name="info", description="Информация о Айке")
    async def info(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=False)
        user = interaction.user.name
        message = (f'Пользователь {user} использовал команду `/info` в канале `{interaction.channel.name if isinstance(interaction.channel, discord.TextChannel) else "Direct Message"}`.')
        channel_id = 000000000000000000
        channel = self.bot.get_channel(channel_id)
        await channel.send(message)
        user_id = str(interaction.user.id)
        if str(user_id) in open("blocked_users.txt").read():
            error_embed = discord.Embed(title="Ошибка", description="Ваш аккаунт заблокирован.", color=discord.Color.red())
            await interaction.response.send_message(embed=error_embed)
            return
        server_count = len(self.bot.guilds)
        ping_ms = round(self.bot.latency * 1000)

        aika_users_dir = "aika_users"
        if os.path.exists(aika_users_dir) and os.path.isdir(aika_users_dir):
            user_count = len(os.listdir(aika_users_dir))
        else:
            user_count = 0

        embed = discord.Embed(title=f"Информация о Aika AI:", color=0x921294)
        embed.add_field(name="Версия:", value=f"4.8.45", inline=False)
        embed.add_field(name="Статус:", value=f"🟢 - В полном порядке", inline=False)
        embed.add_field(name="Пинг:", value=f"{ping_ms} мс", inline=False)
        embed.add_field(name="Последнее обновление:", value=f"<t:1698077760:D>, <t:1698077760:R>", inline=False)
        embed.add_field(name="Количество серверов:", value=f"{server_count}", inline=False)
        embed.add_field(name="Количество пользователей:", value=f"{user_count}", inline=False)
        embed.add_field(name="Прочая информация:", value=f"**[Политика конфиденциальности](https://example.com) [Условия использования](https://example.com)\n[Сервер поддержки](https://discord.gg/JACFfNHdYF)**", inline=False)
        await interaction.followup.send(embed=embed)
        return

    @app_commands.command(name="bug-report", description="Отправить отчет об ошибке")
    async def bug_report(self, interaction: discord.Interaction, text: str, image_url: str = None):
        user_id = str(interaction.user.id)

        if str(user_id) in open("blocked_users.txt").read():
            error_embed = discord.Embed(title="Ошибка", description="Ваш аккаунт заблокирован.", color=discord.Color.red())
            await interaction.response.send_message(embed=error_embed, ephemeral=True)
            return

        user_folder = os.path.join("aika_users", str(user_id))
        if not os.path.exists(user_folder):
            error_embed = discord.Embed(title="Ошибка", description="Хм, похоже я с вами еще не знакома. Пожалуйста, воспользуйтесь командой `/register` чтобы создать свой аккаунт", color=discord.Color.red())
            await interaction.response.send_message(embed=error_embed, ephemeral=True)
            return

        if image_url:
            if not image_url.startswith("https://"):
                error_embed = discord.Embed(title="Ошибка", description="Вы указали некорректную ссылку на изображение.", color=discord.Color.red())
            await interaction.response.send_message(embed=error_embed, ephemeral=True)
            return

            if image_url.endswith((".png", ".jpeg", ".jpg")):
                bug_report_embed.set_image(url=image_url)
            else:
                error_embed = discord.Embed(title="Ошибка", description="Ссылка на изображение должна заканчиваться на .png, .jpeg или .jpg", color=discord.Color.red())
                await interaction.response.send_message(embed=error_embed, ephemeral=True)
                return

        bug_report_embed = discord.Embed(title="Отчет об ошибке", color=discord.Color.orange())
        bug_report_embed.add_field(name="Текст отчета", value=text)

        channel_id = 000000000000000000
        channel = self.bot.get_channel(channel_id)
        await channel.send(embed=bug_report_embed)
        success_embed = discord.Embed(title="Успех", description="Отчет об ошибке успешно отправлен.", color=discord.Color.green())
        await interaction.response.send_message(embed=success_embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Func_Commands(bot))