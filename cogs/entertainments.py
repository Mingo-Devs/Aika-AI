import os
from core.classes import Cog_Extension
import openai
import discord
import random
import time
from discord import app_commands

api_key = os.getenv("OPENAI_API_KEY")

context_store = {}
cooldowns_meme = {}

cooldowns = {}

cooldowns_ai = {}

class Entertainments(Cog_Extension):
    @app_commands.command(name="meme", description="Айка сгенерирует мем")
    async def meme(self, interaction: discord.Interaction):
        await interaction.response.defer()

        try:
            user_id = interaction.user.id
            user_folder = os.path.join("aika_users", str(user_id))
            plan_file_path = os.path.join(user_folder, "plus", "plan.txt")

            current_time = time.time()
            last_used_time = cooldowns_meme.get(user_id, 0)

            if str(user_id) in open("blocked_users.txt").read():
                error_embed = discord.Embed(title="Ошибка", description="Ваш аккаунт заблокирован.", color=discord.Color.red())
                await interaction.followup.send(embed=error_embed, ephemeral=True)
                return

            if not os.path.exists(user_folder):
                error_embed = discord.Embed(title="Ошибка", description="Хм, похоже я с вами еще не знакома. Пожалуйста, воспользуйтесь командой `/register` чтобы создать свой аккаунт", color=discord.Color.red())
                await interaction.followup.send(embed=error_embed, ephemeral=True)
                return

            if not os.path.exists(plan_file_path):
                cooldown = 600
            else:
                with open(plan_file_path, "r") as plan_file:
                    plan_text = plan_file.read().strip()

                if plan_text in ["Basic", "Standart", "Ultimate", "Excelsior"]:
                    cooldown = 0
                else:
                    cooldown = 600

            if current_time - last_used_time < cooldown:
                error_embed = discord.Embed(title="Ошибка", description=f"Ваш тарифный план не позволяет использовать эту команду чаще 1 раза в {int(cooldown / 60)} минут. Подробнее по команде `/plus`", color=discord.Color.red())
                await interaction.followup.send(embed=error_embed, ephemeral=True)
                return

            prompt = f'сгенерируй смешной мем оформленный в рамке и заключенный в ``` ```'
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": " "},
                    {"role": "user", "content": prompt}
                ],
                api_key=api_key
            )
            meme = response.choices[0].message.content.strip()

            log_embed = discord.Embed(title="Aika Meme Gen Log", color=0x00ff00)
            log_embed.add_field(name="User", value=interaction.user.display_name, inline=False)
            log_embed.add_field(name="User ID", value=interaction.user.id, inline=False)
            log_embed.add_field(name="Server", value=interaction.guild.name if interaction.guild else "Direct Message", inline=False)
            log_embed.add_field(name="Server ID", value=interaction.guild.id if interaction.guild else "N/A", inline=False)
            log_embed.add_field(name="Channel", value=interaction.channel.name if isinstance(interaction.channel, discord.TextChannel) else "Direct Message", inline=False)
            log_embed.add_field(name="Meme", value=meme, inline=False)
            channel_id = 000000000000000000
            channel = self.bot.get_channel(channel_id)
            if channel:
                await channel.send(embed=log_embed)

            embed = discord.Embed(title="Aika Meme Generator", color=0x921294)
            embed.add_field(name="Мем", value=meme, inline=False)
            await interaction.followup.send(embed=embed)
            cooldowns_meme[user_id] = current_time
        except Exception as e:
            print(f"{e}")
            error_embed = discord.Embed(title="Ошибка", description=f"Извините за неудобства. В настоящее время Айка не может обработать ваш запрос из-за технических проблем. Мы работаем над их устранением и ожидаем, что проблема будет решена в ближайшее время. Просим вас не удалять Айку с сервера. Спасибо за понимание.", color=discord.Color.red())
            await interaction.followup.send(embed=error_embed, ephemeral=True)

    @app_commands.command(name="shoot", description="Выстрелить в бота")
    async def shoot(self, interaction: discord.Interaction):
        user = interaction.user.name
        message = f'Пользователь {user} использовал команду `/shoot` в канале `{interaction.channel.name if isinstance(interaction.channel, discord.TextChannel) else "Direct Message"}`.'
        channel_id = 000000000000000000
        channel = self.bot.get_channel(channel_id)
        await channel.send(message)

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

        hit = random.choice(["попали", "не попали"])

        if hit == "попали":
            await interaction.response.send_message("Вы попали в меня! Я признаю своё поражение.")
        else:
            outcome = random.choice(["попала", "не попала"])
            end = "не победила"
            if outcome == "попала":
                end = "я победила"
            response_text = f"Вы не попали в меня! Я {outcome} и {end}."
            await interaction.response.send_message(response_text)

    @app_commands.command(name="lucky", description="Испытайте свою удачу")
    async def lucky(self, interaction: discord.Interaction, *, phrase: str):
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

        responses = ["успешным", "неуспешным"]
        random_response = random.choice(responses)
        respone_text = f"Я думаю, что '{phrase}' будет {random_response}."

        await interaction.response.send_message(respone_text)
        user = interaction.user.name
        message = f'Пользователь {user} использовал команду `/lucky` в канале `{interaction.channel.name if isinstance(interaction.channel, discord.TextChannel) else "Direct Message"}`. Результат `{respone_text}`'
        channel_id = 000000000000000000
        channel = self.bot.get_channel(channel_id)
        await channel.send(message)

    @app_commands.command(name="horoscope", description="Айка расскажет вам гороскоп на выбранный вами день и знак зодиака")
    @app_commands.choices(day=[
        app_commands.Choice(name="Сегодня", value="TODAY"),
        app_commands.Choice(name="Завтра", value="TOMORROW"),
        app_commands.Choice(name="Послезавтра", value="AFTER_TOMORROW"),
    ])
    @app_commands.choices(zodiac_sign=[
        app_commands.Choice(name="Овен", value="ARIES"),
        app_commands.Choice(name="Телец", value="TAURUS"),
        app_commands.Choice(name="Близнецы", value="GEMINI"),
        app_commands.Choice(name="Рак", value="CANCER"),
        app_commands.Choice(name="Лев", value="LEO"),
        app_commands.Choice(name="Дева", value="VIRGO"),
        app_commands.Choice(name="Весы", value="LIBRA"),
        app_commands.Choice(name="Скорпион", value="SCORPIO"),
        app_commands.Choice(name="Стрелец", value="SAGITTARIUS"),
        app_commands.Choice(name="Козерог", value="CAPRICORN"),
        app_commands.Choice(name="Водолей", value="AQUARIUS"),
        app_commands.Choice(name="Рыбы", value="PISCES"),
    ])
    async def horoscope(self, interaction: discord.Interaction, day: str, zodiac_sign: str):
        await interaction.response.defer()

        try:
            user_id = interaction.user.id
            user_folder = os.path.join("aika_users", str(user_id))
            plan_file_path = os.path.join(user_folder, "plus", "plan.txt")

            if str(user_id) in open("blocked_users.txt").read():
                error_embed = discord.Embed(title="Ошибка", description="Ваш аккаунт заблокирован.", color=discord.Color.red())
                await interaction.followup.send(embed=error_embed, ephemeral=True)
                return

            if not os.path.exists(user_folder):
                error_embed = discord.Embed(title="Ошибка", description="Хм, похоже я с вами еще не знакома. Пожалуйста, воспользуйтесь командой `/register` чтобы создать свой аккаунт", color=discord.Color.red())
                await interaction.followup.send(embed=error_embed, ephemeral=True)
                return

            if not os.path.exists(plan_file_path):
                error_embed = discord.Embed(title="Ошибка", description="Доступ к этой команде разрешен только для пользователей с тарифами Ultimate и Excelsior.", color=discord.Color.red())
                await interaction.followup.send(embed=error_embed, ephemeral=True)
                return

            with open(plan_file_path, "r") as plan_file:
                plan_text = plan_file.read().strip()

            if plan_text not in ["Ultimate", "Excelsior"]:
                error_embed = discord.Embed(title="Ошибка", description="Доступ к этой команде разрешен только для пользователей с тарифами Ultimate и Excelsior.", color=discord.Color.red())
                await interaction.followup.send(embed=error_embed, ephemeral=True)
                return

            prompt = f'Гороскоп на {day} для {zodiac_sign}'
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system",
                     "content": "You are a friendly astrologer. Also answer the user only with the horoscope without any preface and words not related to the horoscope. Also you must using emoji in every message."},
                    {"role": "user", "content": prompt}
                ],
                api_key=api_key
            )
            horoscope_text = response.choices[0].message.content.strip()

            log_embed = discord.Embed(title="Aika Horoscope Log", color=0x00ff00)
            log_embed.add_field(name="User", value=interaction.user.display_name, inline=False)
            log_embed.add_field(name="User ID", value=interaction.user.id, inline=False)
            log_embed.add_field(name="Server", value=interaction.guild.name if interaction.guild else "Direct Message", inline=False)
            log_embed.add_field(name="Server ID", value=interaction.guild.id if interaction.guild else "N/A", inline=False)
            log_embed.add_field(name="Channel", value=interaction.channel.name if isinstance(interaction.channel, discord.TextChannel) else "Direct Message", inline=False)
            log_embed.add_field(name="Day", value=day, inline=False)
            log_embed.add_field(name="Zodiag Sign", value=zodiac_sign, inline=False)
            log_embed.add_field(name="Horoscope", value=horoscope_text, inline=False)
            channel_id = 000000000000000000
            channel = self.bot.get_channel(channel_id)
            if channel:
                await channel.send(embed=log_embed)

            embed = discord.Embed(title="Айка Гороскоп", color=0x921294)
            embed.add_field(name="День:", value=day, inline=False)
            embed.add_field(name="Знак зодиака:", value=zodiac_sign, inline=False)
            embed.add_field(name="Гороскоп:", value=horoscope_text, inline=False)
            await interaction.followup.send(embed=embed)
        except Exception as e:
            print(f"{e}")
            error_embed = discord.Embed(title="Ошибка", description="Извините за неудобства. В настоящее время Айка не может обработать ваш запрос из-за технических проблем. Мы работаем над их устранением и ожидаем, что проблема будет решена в ближайшее время. Просим вас не удалять Айку с сервера. Спасибо за понимание.", color=discord.Color.red())
            await interaction.followup.send(embed=error_embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Entertainments(bot))