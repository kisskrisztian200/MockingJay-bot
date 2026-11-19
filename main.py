import os
import nextcord
import io
from urllib.parse import urlparse
from nextcord.ext import commands
from dotenv import load_dotenv
from bolt import ShopView, create_shop_embed, create_inventory_embed
from map.map import get_map_path
from map.körzetek import DISTRICTS
from karakterek import (
    CharacterRegistration,
    CharacterEditView,
    AdminReviewView,
    register_persistent_views,
)

from database import (
    load_characters,
    save_characters,
    load_players,
    save_players,
)

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
CHARACTER_REVIEW_CHANNEL_ID = 1570022745779998740

intents = nextcord.Intents.default()
intents.members = True
intents.dm_messages = True

GUILD_ID = 1466849151126864078

bot = commands.Bot(
    command_prefix=commands.when_mentioned,
    intents=intents
)



class DistrictSelect(nextcord.ui.Select):
    def __init__(self):
        options = [
            nextcord.SelectOption(
                label=DISTRICTS[number]["name"],
                value=str(number),
                description=DISTRICTS[number]["specialty"][:100]
            )
            for number in DISTRICTS
        ]

        super().__init__(
            placeholder="Válassz egy körzetet...",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="district_select"
        )
        

    async def callback(self, interaction: nextcord.Interaction):
        number = int(self.values[0])
        district = DISTRICTS[number]

        embed = nextcord.Embed(
            title=district["name"],
            description=district["description"],
            color=nextcord.Color.dark_red()
        )

        embed.add_field(
            name="Iparág",
            value=district["specialty"],
            inline=False
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )


class DistrictView(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(DistrictSelect())


@bot.event
async def on_message(message: nextcord.Message):
    if message.author.bot:
        return

    if isinstance(message.channel, nextcord.DMChannel) and message.attachments:
        user_id = str(message.author.id)
        characters = load_characters()

        user_characters = characters.get(user_id, {})

        # Régi karakteradatok átalakítása az új rendszerhez
        if user_characters and "name" in user_characters:
            user_characters = {"1": user_characters}
            characters[user_id] = user_characters

        character_id, character = next(
            (
                (cid, char)
                for cid, char in user_characters.items()
                if char.get("image_status") == "awaiting"
            ),
            (None, None)
        )

        if not character:
            await message.author.send(
                "❌ Nincs függőben lévő karakterregisztrációd."
            )
            return

        attachment = message.attachments[0]

        if not attachment.content_type or not attachment.content_type.startswith("image/"):
            await message.author.send(
                "❌ Kérlek, valódi képfájlt küldj!"
            )
            return

        try:
            image_data = await attachment.read()

            image_file = nextcord.File(
                io.BytesIO(image_data),
                filename=attachment.filename
            )

            profile_message = await message.author.send(
                f"🖼️ **{character['name']}** RP-profilképe. "
                "Ezt az üzenetet ne töröld, innen használja a bot.",
                file=image_file
            )

            character["image_status"] = "uploaded"
            character["image_message_id"] = str(profile_message.id)
            character["image_channel_id"] = str(profile_message.channel.id)
            character["image_url"] = profile_message.attachments[0].url

            save_characters(characters)

            review_channel = await bot.fetch_channel(
                CHARACTER_REVIEW_CHANNEL_ID
            )

            embed = nextcord.Embed(
                title="🏹 Új karakter – Ellenőrzésre vár",
                color=nextcord.Color.dark_red()
            )

            embed.add_field(
                name="Karakter neve",
                value=character["name"],
                inline=False
            )

            embed.add_field(
                name="Életkor",
                value=str(character["age"]),
                inline=True
            )

            embed.add_field(
                name="Nem",
                value=character["gender"],
                inline=True
            )

            embed.add_field(
                name="Háttértörténet",
                value=character["backstory"][:1024],
                inline=False
            )

            embed.add_field(
                name="Játékos",
                value=message.author.mention,
                inline=False
            )

            embed.set_image(url=character["image_url"])

            review_message = await review_channel.send(
                embed=embed,
                view=AdminReviewView(user_id, character_id)
            )

            character["review_message_id"] = str(review_message.id)
            save_characters(characters)

            await message.author.send(
                "✅ A karakterképed megérkezett! "
                "A regisztrációdat most már az adminok ellenőrzik."
            )

        except Exception as error:
            print(f"Karakterkép feldolgozási hiba: {error}")
            await message.author.send(
                "❌ Hiba történt a kép feldolgozásakor. "
                "Kérlek, jelezd az adminoknak!"
            )

    await bot.process_commands(message)


@bot.event
async def on_ready():
    register_persistent_views(bot)

    try:
        synced = await bot.sync_application_commands()
        print("Globális parancsok szinkronizálása lefutott.")    
        print("Szerverparancsok szinkronizálása befejeződött.")     
        print("Helyi parancsok:", [
            (cmd.name, cmd.guild_ids)
            for cmd in bot.get_all_application_commands()
        ])
        print("Slash parancsok szinkronizálva!")
        print("Teszt szerver parancsai:", [
            cmd.name for cmd in bot.get_all_application_commands()
            ])
    except Exception as error:
        print(f"Szinkronizálási hiba: {error}")

    print("--------------------------------")
    print(f"Mockingjay elindult: {bot.user}")
    print("Panem rendszere online.")
    print("--------------------------------")

@bot.slash_command(
    name="regisztracio",
    description="Karakter regisztrálása Panemben"
)
async def regisztracio(interaction: nextcord.Interaction):
    print("1. REGISZTRÁCIÓS PARANCS ELINDULT")

    modal = CharacterRegistration(
        review_channel_id=CHARACTER_REVIEW_CHANNEL_ID
    )

    print("2. MODAL LÉTREHOZVA")

    await interaction.response.send_modal(modal)

    print("3. MODAL ELKÜLDVE")


@bot.slash_command(
    name="karakter_szerkesztes",
    description="Saját karakter szerkesztése"
)
async def karakter_szerkesztes(interaction: nextcord.Interaction):
    characters = load_characters()
    user_id = str(interaction.user.id)

    user_characters = characters.get(user_id, {})

    # Régi karakteradatok kezelése
    if user_characters and "name" in user_characters:
        user_characters = {"1": user_characters}
        characters[user_id] = user_characters
        save_characters(characters)

    editable_characters = [
        (character_id, character)
        for character_id, character in user_characters.items()
        if character.get("status") in ("pending", "rejected")
    ]

    if not editable_characters:
        await interaction.response.send_message(
            "❌ Nincs szerkeszthető karaktered. "
            "Az elfogadott karakterek már nem módosíthatók.",
            ephemeral=True
        )
        return

    for index, (character_id, character) in enumerate(editable_characters):
        status = (
            "Elutasított"
            if character["status"] == "rejected"
            else "Ellenőrzés alatt"
        )

        message = (
            f"🏹 **{character['name']}**\n"
            f"Állapot: {status}\n"
            "A szerkesztéshez kattints a gombra:"
        )

        view = CharacterEditView(
            user_id,
            character_id,
            CHARACTER_REVIEW_CHANNEL_ID
        )
        if index == 0:
            await interaction.response.send_message(
                message,
                view=view,
                ephemeral=True
            )
        else:
            await interaction.followup.send(
                message,
                view=view,
                ephemeral=True
            )

@bot.slash_command(
    name="terkep",
    description="Panem interaktív térképének megnyitása"
)
async def terkep(interaction: nextcord.Interaction):

    await interaction.response.defer()

    try:
        map_path = get_map_path()

        print(f"Térkép elérési útja: {map_path}")
        print(f"Létezik a fájl: {map_path.exists()}")

        file = nextcord.File(
            map_path,
            filename="panem_map.jpeg"
        )

        embed = nextcord.Embed(
            title="🗺️ Panem térképe",
            description=(
                "Üdvözlünk Panemben!\n"
                "Válaszd ki a körzetet, amelyről információt szeretnél."
            ),
            color=nextcord.Color.dark_red()
        )

        embed.set_image(
            url="attachment://panem_map.jpeg"
        )

        await interaction.followup.send(
            embed=embed,
            file=file,
            view=DistrictView()
        )

    except Exception as error:
        print(f"Térkép hiba: {error}")

        await interaction.followup.send(
            "❌ Hiba történt a térkép betöltésekor. "
            "Nézd meg a bot terminálját!"
        )


@bot.slash_command(
    name="ping",
    description="A Mockingjay működésének ellenőrzése"
)
async def ping(interaction: nextcord.Interaction):
    await interaction.response.defer()

    await interaction.followup.send(
        "🏹 Mockingjay működik! Panem vár rád."
    )


@bot.slash_command(
    name="korzet_beallitas",
    description="Egy karakter körzetének módosítása"
)
async def korzet_beallitas(
    interaction: nextcord.Interaction,
    jatekos: nextcord.Member,
    karakter: str,
    korzet: int
):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "❌ Ehhez adminisztrátori jogosultság szükséges!",
            ephemeral=True
        )
        return

    characters = load_characters()
    user_id = str(jatekos.id)
    
    players = load_players()

    if user_id not in players:
        players[user_id] = {
    "szint": 1,
    "xp": 0,
    "kredit": 0
}
        save_players(players)

    player_data = players[user_id]

    user_characters = characters.get(user_id, {})

    # Régi karakteradatok kezelése
    if "name" in user_characters:
        user_characters = {"1": user_characters}
        characters[user_id] = user_characters

    # Karakter megkeresése
    character = next(
        (
            char for char in user_characters.values()
            if char["name"].lower() == karakter.lower()
        ),
        None
    )

    if not character:
        await interaction.response.send_message(
            "❌ Nem található ilyen karakter ennél a játékosnál!",
            ephemeral=True
        )
        return

    # Körzet ellenőrzése
    if korzet not in range(1, 14):
        await interaction.response.send_message(
            "❌ Csak az 1–13. körzet választható!",
            ephemeral=True
        )
        return

    # Körzet módosítása és mentése
    character["körzet"] = korzet
    save_characters(characters)

    await interaction.response.send_message(
        f"✅ **{character['name']}** körzete sikeresen módosult: "
        f"**{korzet}. körzet**!"
    )


@bot.slash_command(
    name="profil",
    description="Saját vagy másik játékos profiljának megtekintése"
)
async def profil(
    interaction: nextcord.Interaction,
    jatekos: nextcord.Member = None
):
    if jatekos is None:
        jatekos = interaction.user

    user_id = str(jatekos.id)

    characters = load_characters()
    user_characters = characters.get(user_id, {})

    # Régi karakteradatok kezelése
    if "name" in user_characters:
        user_characters = {"1": user_characters}

    players = load_players()
    player_data = players.get(user_id, {"szint": 1, "xp": 0})

    approved_characters = [
        char for char in user_characters.values()
        if char.get("status") == "approved"
    ]

    embed = nextcord.Embed(
        title=f"🏹 {jatekos.display_name} – Profil",
        color=nextcord.Color.dark_red()
    )

    embed.set_thumbnail(url=jatekos.display_avatar.url)

    szint = player_data["szint"]
    xp = player_data["xp"]
    if szint < 100:
        kovetkezo_szint_xp = szint * 1000
    elif szint < 300:
        kovetkezo_szint_xp = 100000
    elif szint < 600:
        kovetkezo_szint_xp = 300000
    elif szint < 1000:
        kovetkezo_szint_xp = 600000
    else:
        kovetkezo_szint_xp = 0

    if szint >= 1000:
        rang = "🏆 Bajnok"
    elif szint >= 900:
        rang = "🥇 Bajnokjelölt"
    elif szint >= 800:
        rang = "👑 Vezéralak"
    elif szint >= 700:
        rang = "🎓 Mentor"
    elif szint >= 600:
        rang = "🌟 Legenda"
    elif szint >= 500:
        rang = "🛡️ Hős"
    elif szint >= 400:
        rang = "⚔️ Veterán"
    elif szint >= 300:
        rang = "🔥 Elit"
    elif szint >= 200:
        rang = "🎯 Kiválasztott"
    elif szint >= 100:
        rang = "🏹 Harcos"
    elif szint >= 50:
        rang = "🪓 Túlélő"
    else:
        rang = "🌱 Újonc"

    embed.add_field(
        name="🏅 Szint",
        value=f"**{szint}. szint**",
        inline=True
    )

    embed.add_field(
        name="🎖️ Rang",
        value=f"**{rang}**",
        inline=True
    )

    embed.add_field(
        name="⭐ XP",
        value=f"**{xp} / {kovetkezo_szint_xp} XP**",
        inline=True
    )

    if szint >= 1000:
        xp_csik = "🟩" * 10
        szint_info = "🏆 Maximális szint elérve!"
    else:
        szazalek = min(100, int((xp / kovetkezo_szint_xp) * 100))

        tele = int(szazalek / 10)
        ures = 10 - tele

        xp_csik = "🟩" * tele + "⬜" * ures
        szint_info = f"{xp_csik} **{szazalek}%**"

    embed.add_field(
        name="📊 Szintlépés",
        value=szint_info,
        inline=False
    )

    if approved_characters:
        character_names = "\n".join(
            f"🏹 {char['name']}"
            for char in approved_characters
        )
    else:
        character_names = "Még nincs elfogadott karakter."

    embed.add_field(
        name=f"📜 Karakterek ({len(approved_characters)})",
        value=character_names,
        inline=False
    )

    await interaction.response.send_message(
        embed=embed
    )

@bot.slash_command(
    name="panembolt",
    description="Panem boltjának megnyitása"
)
async def bolt(interaction: nextcord.Interaction):
    embed = create_shop_embed()
    view = ShopView()

    await interaction.response.send_message(
        embed=embed,
        view=view,
        ephemeral=True
    )

@bot.slash_command(
    name="felszereles",
    description="A megvásárolt tárgyaid megtekintése"
)
async def felszereles(interaction: nextcord.Interaction):
    embed = create_inventory_embed(interaction.user.id)

    await interaction.response.send_message(
        embed=embed,
        ephemeral=True
    )

@bot.slash_command(
    name="xp_ad",
    description="XP adása egy játékosnak"
)
async def xp_ad(
    interaction: nextcord.Interaction,
    jatekos: nextcord.Member,
    mennyiseg: int
):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "❌ Ehhez a parancshoz adminisztrátori jogosultság szükséges!",
            ephemeral=True
        )
        return
    if mennyiseg <= 0:
        await interaction.response.send_message(
            "❌ Az XP mennyiségének pozitív számnak kell lennie!",
            ephemeral=True
        )
        return
    players = load_players()
    user_id = str(jatekos.id)

    if user_id not in players:
        players[user_id] = {"szint": 1, "xp": 0}

    player_data = players[user_id]
    regi_szint = player_data["szint"]
    player_data["xp"] += mennyiseg

    while player_data["szint"] < 1000:
        szint = player_data["szint"]

        if szint < 100:
            kovetkezo_szint_xp = szint * 1000
        elif szint < 300:
            kovetkezo_szint_xp = 100000
        elif szint < 600:
            kovetkezo_szint_xp = 300000
        else:
            kovetkezo_szint_xp = 600000

        if player_data["xp"] < kovetkezo_szint_xp:
            break

        player_data["xp"] -= kovetkezo_szint_xp
        player_data["szint"] += 1

    if player_data["szint"] >= 1000:
        player_data["szint"] = 1000
        player_data["xp"] = 0

    save_players(players)

    if player_data["szint"] > regi_szint:
        message = (
            f"✅ {jatekos.mention} kapott **{mennyiseg} XP-t**!\n"
            f"🏅 Új szint: **{player_data['szint']}**\n"
            f"📈 Szintlépések: **{player_data['szint'] - regi_szint}**"
        )
    else:
        message = f"✅ {jatekos.mention} kapott {mennyiseg} XP-t!"
        
        
@bot.slash_command(
    name="xp_levonas",
    description="XP levonása egy játékostól"
)
async def xp_levonas(
    interaction: nextcord.Interaction,
    jatekos: nextcord.Member,
    mennyiseg: int
):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "❌ Ehhez a parancshoz adminisztrátori jogosultság szükséges!",
            ephemeral=True
        )
        return

    if mennyiseg <= 0:
        await interaction.response.send_message(
            "❌ Az XP mennyiségének pozitív számnak kell lennie!",
            ephemeral=True
        )
        return

    players = load_players()
    user_id = str(jatekos.id)

    if user_id not in players:
        players[user_id] = {"szint": 1, "xp": 0}

    player_data = players[user_id]
    regi_xp = player_data["xp"]

    player_data["xp"] = max(0, regi_xp - mennyiseg)

    levont_xp = regi_xp - player_data["xp"]

    save_players(players)

    await interaction.response.send_message(
        f"✅ {jatekos.mention} XP-jéből **{levont_xp} XP** levonva!\n"
        f"📈 Jelenlegi XP: **{player_data['xp']}**\n"
        f"🏅 Szint: **{player_data['szint']}**",
        ephemeral=True
    )

if not TOKEN:
    raise ValueError(
        "A DISCORD_TOKEN hiányzik a .env fájlból!"
    )


@bot.slash_command(
    name="help",
    description="A Mockingjay bot parancsainak megtekintése"
)
async def help_command(interaction: nextcord.Interaction):
    embed = nextcord.Embed(
        title="📖 Mockingjay – Súgó",
        description="A bot jelenleg elérhető parancsai:",
        color=nextcord.Color.gold()
    )

    for command in sorted(bot.get_all_application_commands(), key=lambda c: c.name):
        embed.add_field(
            name=f"/{command.name}",
            value=command.description or "Nincs leírás.",
            inline=False
        )

    embed.set_footer(text="Panem vár rád! 🏹")

    await interaction.response.send_message(
        embed=embed,
        ephemeral=True
    )


bot.run(TOKEN)