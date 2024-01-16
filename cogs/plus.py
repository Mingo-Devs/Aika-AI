import os
import math
from core.classes import Cog_Extension
import asyncio
import discord
import random
import time
from datetime import datetime
from discord import app_commands

context_store = {}

cooldowns = {}

cooldowns_ai = {}

class Plus(Cog_Extension):
    @app_commands.command(name="plus", description="Узнать подробнее про Aika Plus")
    async def plus(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=False)
        user = interaction.user.name
        message = (f'Пользователь {user} использовал команду `/plus` в канале `{interaction.channel.name if isinstance(interaction.channel, discord.TextChannel) else "Direct Message"}`.')
        channel_id = 000000000000000000
        channel = self.bot.get_channel(channel_id)
        await channel.send(message)
        user_id = str(interaction.user.id)
        two_text = """2. Введите команду `/buy` и укажите:
            item: название подписки (Basic, Standard, Ultimate, Excelsior)
            period: длительность (1 мес, 3 мес, 6 мес, 1 год)
            payment_type: выберите "Деньгами" или "Баллами"."""
        if str(user_id) in open("blocked_users.txt").read():
            error_embed = discord.Embed(title="Ошибка", description="Ваш аккаунт заблокирован.", color=discord.Color.red())
            await interaction.response.send_message(embed=error_embed, ephemeral=True)
            return
        embed = discord.Embed(title="Aika Plus", description="Aika Plus - это улучшенный опыт с Aika. Выбирайте из уровней: Basic, Standard, Ultimate и Excelsior. Получите уникальные возможности для лучшего общения и ответов.", color=0x921294)
        embed.add_field(name="Basic:", value=f"99 рублей/баллов.\n**[Преимущества уровня](https://example.com/)**", inline=True)
        embed.add_field(name="Standart:", value=f"199 рублей/баллов.\n**[Преимущества уровня](https://example.com/)**", inline=True)
        embed.add_field(name="Ultimate:", value=f"299 рублей/баллов.\n**[Преимущества уровня](https://example.com/)**", inline=True)
        embed.add_field(name="Excelsior:", value=f"399 рублей/баллов.\n**[Преимущества уровня](https://example.com/)**", inline=True)
        embed.add_field(name="Кейс:", value=f"89 рублей/баллов.\n**Испытайте удачу в том, какая подписка вам выпадет**", inline=True)
        embed.add_field(name="Как купить Aika Plus в несколько шагов:", value=f"1. Пополните баланс на своем аккаунте через `/profile`.\n{two_text}\n3. Подтвердите покупку после ввода параметров `/buy`.\nСледуйте этому гайду, чтобы получить доступ к Aika Plus и его возможностям.", inline=False)
        embed.set_footer( text="Вы также можете сэкономить до 100% от стоимости подписки. Подробнее по команде `/pbonus`.")
        await interaction.followup.send(embed=embed)
        return

    @app_commands.command(name="case", description="Открыть кейс с Aika Plus (89 руб)")
    @app_commands.choices(pay_type=[
        app_commands.Choice(name="Деньгами", value="money"),
        app_commands.Choice(name="Баллами", value="points"),
    ])
    async def case(self, interaction: discord.Interaction, pay_type: str):
        user_id = str(interaction.user.id)
        await interaction.response.defer()
        current_time = time.time()

        if not os.path.exists(f"aika_users/{user_id}/"):
            error_embed = discord.Embed( title="Ошибка", description="Хм, похоже я с вами еще не знакома. Пожалуйста, воспользуйтесь командой `/register` чтобы создать свой аккаунт", color=discord.Color.red())
            await interaction.followup.send(embed=error_embed, ephemeral=True)
            return

        blocked_users = set()
        with open("blocked_apb_users.txt", "r") as blocked_users_file:
            for line in blocked_users_file:
                blocked_users.add(line.strip())

        if pay_type == "points" and user_id in blocked_users:
            error_embed = discord.Embed( title="Ошибка", description="Ошибка: ваш ID находится в списке заблокированных пользователей для оплаты баллами.", color=discord.Color.red())
            await interaction.followup.send(embed=error_embed, ephemeral=True)
            return

        if pay_type == "money":
            balance_path = f"aika_users/{user_id}/balance.txt"
            try:
                with open(balance_path, "r") as balance_file:
                    balance = int(balance_file.read())
                    if balance < 89:
                        error_embed = discord.Embed( title="Ошибка", description="Недостаточно денег.", color=discord.Color.red())
                        await interaction.followup.send(embed=error_embed, ephemeral=True)
                        return
                    new_balance = balance - 89
                with open(balance_path, "w") as balance_file:
                    balance_file.write(str(new_balance))
            except FileNotFoundError:
                error_embed = discord.Embed( title="Ошибка", description="Ваш баланс нельзя использовать.", color=discord.Color.red())
                await interaction.followup.send(embed=error_embed, ephemeral=True)
                return
            except ValueError:
                error_embed = discord.Embed( title="Ошибка", description="Неверный формат баланса.", color=discord.Color.red())
                await interaction.followup.send(embed=error_embed, ephemeral=True)
                return
        elif pay_type == "points":
            points_path = f"aika_users/{user_id}/balls_balance.txt"
            try:
                with open(points_path, "r") as points_file:
                    points = int(points_file.read())
                    if points < 89:
                        error_embed = discord.Embed( title="Ошибка", description="Недостаточно баллов.", color=discord.Color.red())
                        await interaction.followup.send(embed=error_embed, ephemeral=True)
                        return
                    new_points = points - 89
                with open(points_path, "w") as points_file:
                    points_file.write(str(new_points))
            except FileNotFoundError:
                error_embed = discord.Embed( title="Ошибка", description="Ваш баланс нельзя использовать.", color=discord.Color.red())
                await interaction.followup.send(embed=error_embed, ephemeral=True)
                return
            except ValueError:
                error_embed = discord.Embed( title="Ошибка", description="Неверный формат баланса.", color=discord.Color.red())
                await interaction.followup.send(embed=error_embed, ephemeral=True)
                return

        subscription_percentages = {
            "Ничего": 80,
            "Basic 1 мес": 5,
            "Basic 3 мес": 4,
            "Basic 6 мес": 3,
            "Basic 1 год": 2,
            "Standart 1 мес": 1,
            "Standart 3 мес": 1,
            "Standart 6 мес": 0.5,
            "Standart 1 год": 0.3,
            "Ultimate 1 мес": 0.5,
            "Ultimate 3 мес": 0.3,
            "Ultimate 6 мес": 0.2,
            "Ultimate 1 год": 0.1,
            "Excelsior 1 мес": 0.3,
            "Excelsior 3 мес": 0.2,
            "Excelsior 6 мес": 0.1,
            "Excelsior 1 год": 0.05,
        }

        chosen_subscription = random.choices(list(subscription_percentages.keys()), list(subscription_percentages.values()))[0]

        if chosen_subscription == "Ничего":
            await interaction.followup.send("К сожалению, вам ничего не выпало.", ephemeral=True)
        else:
            plus_path = f"aika_users/{user_id}/plus"
            os.makedirs(plus_path, exist_ok=True)
            with open(f"{plus_path}/buy_date.txt", "w") as buy_date_file:
                buy_date_file.write(datetime.now().strftime("%d.%m.%Y"))
            with open(f"{plus_path}/period.txt", "w") as period_file:
                if chosen_subscription.endswith("мес"):
                    period_file.write(f"{chosen_subscription.split()[1]}M")
                elif chosen_subscription.endswith("год"):
                    period_file.write("1Y")
            with open(f"{plus_path}/plan.txt", "w") as plan_file:
                plan_file.write(chosen_subscription.split(maxsplit=2)[0])

            user = interaction.user.name
            message = (f'Пользователь {user} открыл кейс. Сообщение было отправлено в канале `{interaction.channel.name if isinstance(interaction.channel, discord.TextChannel) else "Direct Message"}`.')
            channel_id = 000000000000000000
            channel = self.bot.get_channel(channel_id)
            await channel.send(message)

            success_embed = discord.Embed( title="Подписка успешно оформлена!", description=f"Вам выпало: {chosen_subscription}", color=0x00FF00)
            await interaction.followup.send(embed=success_embed, ephemeral=True)

    @app_commands.command(name="buy", description="Покупка подписки")
    @app_commands.choices(item=[
        app_commands.Choice(name="Basic (от 99 руб.)", value="Basic"),
        app_commands.Choice(name="Standart (от 199 руб.)", value="Standart"),
        app_commands.Choice(name="Ultimate (299 руб.)", value="Ultimate"),
        app_commands.Choice(name="Excelsior (от 399 руб.)", value="Excelsior"),
    ])
    @app_commands.choices(period=[
        app_commands.Choice(name="1 мес", value="1M"),
        app_commands.Choice(name="3 мес", value="3M"),
        app_commands.Choice(name="6 мес", value="6M"),
        app_commands.Choice(name="1 год", value="1Y"),
    ])
    @app_commands.choices(payment_type=[
        app_commands.Choice(name="Деньгами", value="money"),
        app_commands.Choice(name="Баллами", value="points"),
    ])
    async def buy_subscription(self, interaction: discord.Interaction, item: str, period: str, payment_type: str, pcode: str = None):
        await interaction.response.defer()

        try:
            user_id = interaction.user.id
            user_folder = os.path.join("aika_users", str(user_id))

            if str(user_id) in open("blocked_users.txt").read():
                error_embed = discord.Embed(title="Ошибка", description="Ваш аккаунт заблокирован.",color=discord.Color.red())
                await interaction.followup.send(embed=error_embed)
                return

            if not os.path.exists(user_folder):
                error_embed = discord.Embed(title="Ошибка", description="Хм, похоже я с вами еще не знакома. Пожалуйста, воспользуйтесь командой `/register` чтобы создать свой аккаунт", color=discord.Color.red())
                await interaction.response.send_message(embed=error_embed)
                return

            prices = {
                "Basic": {
                    "1M": (99, "1M"),
                    "3M": (299, "3M"),
                    "6M": (599, "6M"),
                    "1Y": (1199, "1Y")
                },
                "Standart": {
                    "1M": (199, "1M"),
                    "3M": (599, "3M"),
                    "6M": (1199, "6M"),
                    "1Y": (2399, "1Y")
                },
                "Ultimate": {
                    "1M": (299, "1M"),
                    "3M": (899, "3M"),
                    "6M": (1799, "6M"),
                    "1Y": (3599, "1Y")
                },
                "Excelsior": {
                    "1M": (399, "1M"),
                    "3M": (1199, "3M"),
                    "6M": (2399, "6M"),
                    "1Y": (4799, "1Y")
                }
            }

            if pcode:
                try:
                    with open(os.path.join("promo_codes", f"{pcode}.txt"), "r") as promo_file:
                        discount_percent = int(promo_file.read().strip())
                        if item in prices and period in prices[item]:
                            original_price, selected_period = prices[item][period]
                            discounted_price = original_price - (original_price * discount_percent / 100)
                        else:
                            not_found_embed = discord.Embed(title="Ошибка", description="Выбранная подписка или период не найдены.", color=discord.Color.red())
                            await interaction.followup.send(embed=not_found_embed)
                            return
                except FileNotFoundError:
                    not_found_embed = discord.Embed(title="Ошибка", description="Промокод не найден.", color=discord.Color.red())
                    await interaction.followup.send(embed=not_found_embed)
                    return
            else:
                if item in prices and period in prices[item]:
                    original_price, selected_period = prices[item][period]
                    discounted_price = original_price
                else:
                    not_found_embed = discord.Embed(title="Ошибка", description="Выбранная подписка или период не найдены.", color=discord.Color.red())
                    await interaction.followup.send(embed=not_found_embed)
                    return
            
            if discounted_price % 1 != 0:
                remainder = discounted_price % 1
                if remainder >= 0.5:
                    discounted_price = math.ceil(discounted_price)
                else:
                    discounted_price = math.floor(discounted_price)
            else:
                if item in prices and period in prices[item]:
                    original_price, selected_period = prices[item][period]
                    discounted_price = original_price
                else:
                    not_found_embed = discord.Embed(title="Ошибка", description="Выбранная подписка или период не найдены.", color=discord.Color.red())
                    await interaction.followup.send(embed=not_found_embed)
                    return

            if payment_type == "points":
                with open("blocked_apb_users.txt", "r") as blocked_users_file:
                    blocked_users = blocked_users_file.read().splitlines()
                if str(user_id) in blocked_users:
                    error_embed = discord.Embed(title="Ошибка", description="Ваш аккаунт заблокирован.", color=discord.Color.red())
                    await interaction.followup.send(embed=error_embed)
                    return
                else:
                    balance_file = "balls_balance.txt"
            else:
                balance_file = "balance.txt"

            confirmation_embed = discord.Embed(title="Подтверждение покупки", description=f"Вы собираетесь купить подписку {item} на {selected_period} за {discounted_price} рублей." if payment_type == "money" else f"Вы собираетесь купить подписку {item} на {selected_period} за {discounted_price} баллов.", color=0x921294)
            confirmation_embed.set_footer(text="Нажмите ✅, чтобы подтвердить покупку или ❌, чтобы отменить.")
            message = await interaction.followup.send(embed=confirmation_embed)

            await message.add_reaction("✅")
            await message.add_reaction("❌")

            def check(reaction, user):
                return user == interaction.user and str(reaction.emoji) in ["✅", "❌"]

            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=300.0, check=check)
            except asyncio.TimeoutError:
                timeout_embed = discord.Embed(title="Время истекло", description="Время ожидания истекло. Покупка отменена.", color=discord.Color.red())
                await interaction.followup.send(embed=timeout_embed)
                return

            if str(reaction.emoji) == "✅":
                try:
                    with open(os.path.join(user_folder, balance_file), "r") as f:
                        balance = int(f.read())
                        if balance < discounted_price:
                            error_message = "Ошибка: Недостаточно баллов." if payment_type == "points" else "Ошибка: Недостаточно средств."
                            error_embed = discord.Embed(title="Ошибка", description=error_message, color=discord.Color.red())
                            await interaction.followup.send(embed=error_embed)
                            return

                    with open(os.path.join(user_folder, balance_file), "w") as f:
                        remaining_balance = balance - discounted_price
                        f.write(str(remaining_balance))

                except Exception as e:
                    print(f"{e}")
                    error_embed = discord.Embed(title="Ошибка", description=f"При обработке платежа произошла ошибка: {e}", color=discord.Color.red())
                    await interaction.followup.send(embed=error_embed)
                    return

                plus_folder = os.path.join(user_folder, "plus")
                with open(os.path.join(plus_folder, "period.txt"), "w") as f:
                    f.write(selected_period)
                with open(os.path.join(plus_folder, "plan.txt"), "w") as f:
                    f.write(item)

                current_date = datetime.now().strftime("%d.%m.%Y")
                with open(os.path.join(plus_folder, "buy_date.txt"), "w") as f:
                    f.write(current_date)

                success_message = f'Подписка **{item}** успешно куплена!\n**Стоимость:** {discounted_price} баллов\n**Дата покупки:** {current_date}' if payment_type == "points" else f'**Подписка** {item} успешно куплена!\n**Стоимость:** {discounted_price} рублей\n**Дата покупки:** {current_date}.'
                success_embed = discord.Embed(title="Покупка успешно завершена", description=success_message, color=discord.Color.green())
                await interaction.followup.send(embed=success_embed)

                user = interaction.user.name
                message_content = (f'Пользователь {user} купил подписку `{item}` на `{selected_period}` за `{discounted_price}` рублей. Сообщение было отправлено в канале `{interaction.channel.name if isinstance(interaction.channel, discord.TextChannel) else "Direct Message"}`.' if payment_type == "money" else f'Пользователь {user} купил подписку `{item}` на `{selected_period}` за `{discounted_price}` баллов. Сообщение было отправлено в канале `{interaction.channel.name if isinstance(interaction.channel, discord.TextChannel) else "Direct Message"}`.')
                channel_id = 000000000000000000
                channel = self.bot.get_channel(channel_id)

                if channel is not None:
                    await channel.send(message_content)
                else:
                    print("Error: Channel not found or bot does not have permission to send messages to the channel.")

            if str(reaction.emoji) == "❌":
                cancellation_embed = discord.Embed(title="Покупка отменена", description="Оформление подписки было отменено", color=discord.Color.orange())
                await interaction.followup.send(embed=cancellation_embed)

        except Exception as e:
            print(f"{e}")
            error_embed = discord.Embed(title="Ошибка", description=f"При покупке подписки произошла ошибка: {e}", color=discord.Color.red())
            await interaction.followup.send(embed=error_embed, ephemeral=True)

    @app_commands.command(name="pbonus", description="О Aika Plus Bonus")
    async def infoaskills(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=False)
        user = interaction.user.name
        message = (f'Пользователь {user} использовал команду `/pbonus` в канале `{interaction.channel.name if isinstance(interaction.channel, discord.TextChannel) else "Direct Message"}`.')
        channel_id = 000000000000000000
        channel = self.bot.get_channel(channel_id)
        await channel.send(message)
        user_id = str(interaction.user.id)
        if str(user_id) in open("blocked_users.txt").read():
            error_embed = discord.Embed(title="Ошибка", description="Ваш аккаунт заблокирован.", color=discord.Color.red())
            await interaction.response.send_message(embed=error_embed, ephemeral=True)
            return
        embed = discord.Embed(title=f"Информация о Aika Plus Bonus:", color=0x921294)
        embed.add_field(name="🚀Пошаговый Гайд: Как Заработать Баллы🚀", value=f'**Шаг 1:** Апните Айку! Повысьте рейтинг Айки на мониторингах SD.C и/или Top.GG.\n\n**Шаг 2:** После успешного апгрейда убедитесь, что все прошло гладко.\n\n**Шаг 3:** Отправьте отчет о вашем апгрейде! Сделайте скриншот успешного поднятия уровня и отправьте его на проверку командой </up-report:1153372781518532609>.\n\n**Шаг 4:** Дождитесь нашей реакции! Мы проверим ваш отчет и начислим вам заслуженные ✨Баллы.✨\n\n**🌟Ваше Волшебное Путешествие начинается!🌟**\n\n***Теперь вы знаете, как взять на себя магию "Aika Plus Bonus"! Продолжайте апгрейдить Айка, зарабатывайте ✨Баллы✨ и погрузитесь в мир невероятных возможностей с "Aika Plus"!***', inline=False)
        await interaction.followup.send(embed=embed)
        return

    @app_commands.command(name="transfer", description="Перевод баллов на денежный счет")
    async def transfer_points(self, interaction: discord.Interaction, count: int):
        await interaction.response.defer()
        user = interaction.user.name
        message = (f'Пользователь {user} перевел {count} рублей на балловый счет. Сообщение было отправлено в канале `{interaction.channel.name if isinstance(interaction.channel, discord.TextChannel) else "Direct Message"}`.')
        channel_id = 00000000000000000
        channel = self.bot.get_channel(channel_id)
        await channel.send(message)

        try:
            user_id = interaction.user.id
            user_folder = os.path.join("aika_users", str(user_id))

            if not os.path.exists(user_folder):
                error_embed = discord.Embed(title="Ошибка", description="Хм, похоже я с вами еще не знакома. Пожалуйста, воспользуйтесь командой `/register` чтобы создать свой аккаунт", color=discord.Color.red())
                await interaction.followup.send(embed=error_embed, ephemeral=True)
                return

            if count <= 0:
                error_embed = discord.Embed(title="Ошибка", description="Ошибка: Сумма перевода должна быть положительным числом.", color=discord.Color.red())
                await interaction.followup.send(embed=error_embed, ephemeral=True)
                return

            points_balance_file = os.path.join(user_folder, "balls_balance.txt")
            money_balance_file = os.path.join(user_folder, "balance.txt")

            if not os.path.exists(points_balance_file) or not os.path.exists(money_balance_file):
                error_embed = discord.Embed(title="Ошибка", description="Ошибка: Один из балансов не найден.", color=discord.Color.red())
                await interaction.followup.send(embed=error_embed)
                return

            with open(points_balance_file, "r") as f:
                points_balance = int(f.read())

            with open(money_balance_file, "r") as f:
                money_balance = int(f.read())

            if count > money_balance:
                error_embed = discord.Embed(title="Ошибка", description="Ошибка: У вас недостаточно денежных средств для указанного перевода.", color=discord.Color.red())
                await interaction.followup.send(embed=error_embed)
                return

            points_balance += count
            money_balance -= count

            with open(points_balance_file, "w") as f:
                f.write(str(points_balance))

            with open(money_balance_file, "w") as f:
                f.write(str(money_balance))

            success_embed = discord.Embed(title="Успешно", description=f"Успешно переведено {count} руб. на балловый счет.", color=discord.Color.green())
            await interaction.followup.send(embed=success_embed)

        except Exception as e:
            print(f"{e}")
            error_embed = discord.Embed(title="Ошибка", description=f"При переводе баллов произошла ошибка",color=discord.Color.red())
            await interaction.followup.send(embed=error_embed, ephemeral=True)

    @app_commands.command(name="up-report", description="Отправить отчет об апе")
    async def up_report(self, interaction: discord.Interaction, image_url: str):
        user_id = interaction.user.id
        channel_id = 000000000000000000

        if not image_url.startswith("https://"):
            error_embed = discord.Embed(title="Ошибка", description="Вы указали неправильный URL адрес изображения.", color=discord.Color.red())
            await interaction.response.send_message(embed=error_embed, ephemeral=True)
            return

        if image_url.endswith((".png", ".jpeg", ".jpg")):
            await self.bot.get_channel(channel_id).send(f"Пользователь ({user_id}) отправил отчет об апе: {image_url}")
        else:
            error_embed = discord.Embed(title="Ошибка", description="Поддерживаемые форматы изображений: .png, .jpeg или .jpg", color=discord.Color.red())
            await interaction.response.send_message(embed=error_embed, ephemeral=True)
            return

        success_embed = discord.Embed(title="Успех", description="Отчет об апе успешно отправлен, ожидайте начисления награды😉.", color=discord.Color.green())
        await interaction.response.send_message(embed=success_embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Plus(bot))