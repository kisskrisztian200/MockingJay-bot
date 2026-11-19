import nextcord
import io
import random
from database import load_characters, save_characters, load_players, save_players
class CharacterRegistration(nextcord.ui.Modal):
    def __init__(self, review_channel_id: int):
        super().__init__(
            title="Panem – Karakterregisztráció"
        )
        self.review_channel_id = review_channel_id
        self.character_name = nextcord.ui.TextInput(
            label="Karakter teljes neve",
            placeholder="Pl. Katniss Everdeen",
            min_length=3,
            max_length=50,
            required=True
        )

        self.add_item(self.character_name)
        self.age = nextcord.ui.TextInput(
            label="Karakter életkora",
            placeholder="Pl. 16",
            min_length=1,
            max_length=2,
            required=True
        )

        self.add_item(self.age)

        self.gender = nextcord.ui.TextInput(
            label="Karakter neme",
            placeholder="Pl. Férfi / Nő",
            required=True
        )

        self.add_item(self.gender)
        
        self.backstory = nextcord.ui.TextInput(
            label="Karakter háttértörténete",
            placeholder="Meséld el a karaktered múltját...",
            style=nextcord.TextInputStyle.paragraph,
            min_length=20,
            max_length=4000,
            required=True
        )

        self.add_item(self.backstory)
        
    async def callback(self, interaction: nextcord.Interaction):
        characters = load_characters()
        user_id = str(interaction.user.id)

        

        try:
            age = int(self.age.value)
        except ValueError:
            await interaction.response.send_message(
                "❌ Az életkornak számnak kell lennie!",
                ephemeral=True
            )
            return

        if user_id not in characters:
            characters[user_id] = {}

        if "name" in characters[user_id]:
            characters[user_id] = {"1": characters[user_id]}

        character_id = str(len(characters[user_id]) + 1)
        district = random.randint(1, 13)
        characters[user_id][character_id] = {
            "name": self.character_name.value,
            "age": age,
            "gender": self.gender.value,
            "körzet": district,
            "backstory": self.backstory.value,
            "status": "pending",
            "image_status": "awaiting"
        }

        try:
            review_channel = await interaction.client.fetch_channel(
                self.review_channel_id
            )
        except (nextcord.NotFound, nextcord.Forbidden, nextcord.HTTPException):
            await interaction.response.send_message(
                "❌ Nem találom az adminellenőrző csatornát!",
                ephemeral=True
            )
            return


        try:
            await interaction.user.send(
                f"🖼️ **{self.character_name.value}** karaktered "
                "regisztrációja megérkezett!\n\n"
                f"🏘️ **Körzet:** {district}. körzet\n\n"
                "Most küldd el nekem privát üzenetben a karaktered "
                "profilképét!\n\n"
                "⚠️ Ha több karaktert is regisztráltál, "
                "a karakterek képeit a regisztráció sorrendjében küldd el. "
                "Először mindig a legrégebben regisztrált, még kép nélkül álló "
                "karaktered képét küldd."
            )
        except nextcord.Forbidden:
            await interaction.response.send_message(
                "❌ Nem tudok privát üzenetet küldeni neked. "
                "Engedélyezd a botoktól érkező DM-eket!",
                ephemeral=True
            )
            return
        
        save_characters(characters)

        await interaction.response.send_message(
            "🏹 **Sikeres karakterregisztráció!**\n\n"
            f"**Név:** {self.character_name.value}\n"
            f"**Életkor:** {age}\n"
            f"**Nem:** {self.gender.value}\n"
            f"**Körzet:** {district}. körzet",
            ephemeral=True
        )

class CharacterEditModal(nextcord.ui.Modal):
    def __init__(
        self,
        user_id: str,
        character_id: str,
        character: dict,
        review_channel_id: int
    ):
        super().__init__(title="Karakter szerkesztése")

        self.user_id = user_id
        self.character_id = character_id
        self.review_channel_id = review_channel_id

        self.character_name = nextcord.ui.TextInput(
            label="Karakter teljes neve",
            default_value=character["name"],
            min_length=3,
            max_length=50,
            required=True
        )
        self.add_item(self.character_name)

        self.age = nextcord.ui.TextInput(
            label="Karakter életkora",
            default_value=str(character["age"]),
            min_length=1,
            max_length=2,
            required=True
        )
        self.add_item(self.age)

        self.gender = nextcord.ui.TextInput(
            label="Karakter neme",
            default_value=character["gender"],
            required=True
        )
        self.add_item(self.gender)

        self.backstory = nextcord.ui.TextInput(
            label="Karakter háttértörténete",
            default_value=character["backstory"],
            style=nextcord.TextInputStyle.paragraph,
            min_length=20,
            max_length=4000,
            required=True
        )
        self.add_item(self.backstory)

    async def callback(self, interaction: nextcord.Interaction):
        characters = load_characters()
        user_characters = characters.get(self.user_id, {})
        character = user_characters.get(self.character_id)

        if not character or character.get("status") not in ("pending", "rejected"):
            await interaction.response.send_message(
                "❌ Ez a karakter már nem szerkeszthető!",
                ephemeral=True
            )
            return

        try:
            age = int(self.age.value)
            if age < 1 or age > 99:
                raise ValueError
        except ValueError:
            await interaction.response.send_message(
                "❌ Az életkornak 1 és 99 közötti számnak kell lennie!",
                ephemeral=True
            )
            return

        character["name"] = self.character_name.value
        character["age"] = age
        character["gender"] = self.gender.value
        character["backstory"] = self.backstory.value
        character["status"] = "pending"
        character.pop("rejection_reason", None)

        save_characters(characters)

        # Ha már van feltöltött profilkép, új ellenőrző üzenet készül
        if character.get("image_status") == "uploaded":
            try:
                review_channel = await interaction.client.fetch_channel(
                    self.review_channel_id
                )

                embed = nextcord.Embed(
                    title="🏹 Módosított karakter – Ellenőrzésre vár",
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
                    inline=False
                )
                embed.add_field(
                    name="Nem",
                    value=character["gender"],
                    inline=False
                )
                embed.add_field(
                    name="Háttértörténet",
                    value=character["backstory"][:1024],
                    inline=False
                )
                embed.add_field(
                    name="Játékos",
                    value=f"<@{self.user_id}>",
                    inline=False
                )

                embed.set_image(url=character["image_url"])

                review_message_id = character.get("review_message_id")

                try:
                    if review_message_id:
                        review_message = await review_channel.fetch_message(
                            int(review_message_id)
                        )

                        await review_message.edit(
                            embed=embed,
                            view=AdminReviewView(
                                self.user_id,
                                self.character_id
                            )
                        )
                    else:
                        review_message = await review_channel.send(
                            embed=embed,
                            view=AdminReviewView(
                                self.user_id,
                                self.character_id
                            )
                        )
                        character["review_message_id"] = str(review_message.id)

                    save_characters(characters)

                except nextcord.NotFound:
                    review_message = await review_channel.send(
                        embed=embed,
                        view=AdminReviewView(
                            self.user_id,
                            self.character_id
                        )
                    )
                    character["review_message_id"] = str(review_message.id)
                    save_characters(characters)

                except nextcord.HTTPException as error:
                    print(f"Adminellenőrzési hiba: {error}")

                    await interaction.response.send_message(
                        "⚠️ Az adatok mentve lettek, de az adminüzenet "
                        "elküldése nem sikerült.",
                        ephemeral=True
                    )
                    return

            except (nextcord.NotFound, nextcord.Forbidden, nextcord.HTTPException) as error:
                print(f"Adminellenőrzési hiba: {error}")

                await interaction.response.send_message(
                    "⚠️ Az adatok mentve lettek, de az adminüzenet "
                    "elküldése nem sikerült.",
                    ephemeral=True
                )
                return

            await interaction.response.send_message(
                "✅ A karaktered módosításai elmentve! "
                "Az adminok ismét ellenőrzik.",
                ephemeral=True
            )

        else:
            await interaction.response.send_message(
                "✅ Az adatok elmentve! Most küldd el privát üzenetben "
                "a karaktered profilképét.",
                ephemeral=True
            )
class CharacterEditView(nextcord.ui.View):
    def __init__(self, user_id: str, character_id: str, review_channel_id: int):
        super().__init__(timeout=180)

        self.user_id = user_id
        self.character_id = character_id
        self.review_channel_id = review_channel_id

        button = nextcord.ui.Button(
            label="Karakter szerkesztése",
            style=nextcord.ButtonStyle.primary
        )
        button.callback = self.edit_character
        self.add_item(button)

    async def edit_character(self, interaction: nextcord.Interaction):
        if str(interaction.user.id) != self.user_id:
            await interaction.response.send_message(
                "❌ Ez nem a te karaktered!",
                ephemeral=True
            )
            return

        characters = load_characters()
        user_characters = characters.get(self.user_id, {})
        character = user_characters.get(self.character_id)

        if not character or character.get("status") not in ("pending", "rejected"):
            await interaction.response.send_message(
                "❌ Ez a karakter már nem szerkeszthető!",
                ephemeral=True
            )
            return

        await interaction.response.send_modal(
            CharacterEditModal(
                self.user_id,
                self.character_id,
                character,
                self.review_channel_id
            )
        )


class AdminReviewView(nextcord.ui.View):
    def __init__(self, user_id: str, character_id: str):
        super().__init__(timeout=None)
        self.user_id = user_id
        self.character_id = character_id

        approve_button = nextcord.ui.Button(
            label="Elfogadás",
            style=nextcord.ButtonStyle.success,
            custom_id=f"character_approve:{user_id}:{character_id}"
        )
        approve_button.callback = self.approve

        reject_button = nextcord.ui.Button(
            label="Elutasítás",
            style=nextcord.ButtonStyle.danger,
            custom_id=f"character_reject:{user_id}:{character_id}"
        )
        reject_button.callback = self.reject

        self.add_item(approve_button)
        self.add_item(reject_button)

    async def approve(self, interaction: nextcord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "❌ Ehhez csak adminisztrátor férhet hozzá!",
                ephemeral=True
            )
            return

        characters = load_characters()
        user_characters = characters.get(self.user_id, {})
        character = user_characters.get(self.character_id)

        if not character or character["status"] != "pending":
            await interaction.response.send_message(
                "❌ Ez a karakter már el lett bírálva!",
                ephemeral=True
            )
            return

        character["status"] = "approved"
        save_characters(characters)

        try:
            player = await interaction.client.fetch_user(int(self.user_id))
            await player.send(
                f"✅ **{character['name']}** karakteredet "
                "az adminok elfogadták!"
            )
        except nextcord.HTTPException:
            pass

        for item in self.children:
            item.disabled = True

        await interaction.response.edit_message(
            content="✅ A karaktert az adminok elfogadták!",
            view=self
        )

    async def reject(self, interaction: nextcord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "❌ Ehhez csak adminisztrátor férhet hozzá!",
                ephemeral=True
            )
            return

        characters = load_characters()
        user_characters = characters.get(self.user_id, {})
        character = user_characters.get(self.character_id)

        if not character or character["status"] != "pending":
            await interaction.response.send_message(
                "❌ Ez a karakter már el lett bírálva!",
                ephemeral=True
            )
            return

        await interaction.response.send_modal(
            RejectReasonModal(
                self.user_id,
                self.character_id,
                interaction.channel_id,
                interaction.message.id
            )
        )


class RejectReasonModal(nextcord.ui.Modal):
    def __init__(
        self,
        user_id: str,
        character_id: str,
        channel_id: int,
        message_id: int
    ):
        super().__init__(title="Karakter elutasítása")
        self.user_id = user_id
        self.character_id = character_id
        self.channel_id = channel_id
        self.message_id = message_id
        self.reason = nextcord.ui.TextInput(
            label="Elutasítás indoka",
            placeholder="Írd le, miért utasítjátok el a karaktert...",
            style=nextcord.TextInputStyle.paragraph,
            min_length=5,
            max_length=1000,
            required=True
        )

        self.add_item(self.reason)

    async def callback(self, interaction: nextcord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "❌ Ehhez csak adminisztrátor férhet hozzá!",
                ephemeral=True
            )
            return

        characters = load_characters()
        user_characters = characters.get(self.user_id, {})
        character = user_characters.get(self.character_id)

        if not character or character["status"] != "pending":
            await interaction.response.send_message(
                "❌ Ez a karakter már el lett bírálva!",
                ephemeral=True
            )
            return

        character["status"] = "rejected"
        character["rejection_reason"] = self.reason.value
        save_characters(characters)

        try:
            player = await interaction.client.fetch_user(
                int(self.user_id)
            )
            await player.send(
                f"❌ **{character['name']}** karakteredet "
                "az adminok elutasították.\n\n"
                f"**Indok:** {self.reason.value}"
            )
        except nextcord.HTTPException:
            pass

        try:
            channel = await interaction.client.fetch_channel(self.channel_id)
            message = await channel.fetch_message(self.message_id)

            view = AdminReviewView(self.user_id, self.character_id)

            for item in view.children:
                item.disabled = True

            await message.edit(view=view)

        except nextcord.HTTPException as error:
            print(f"Az adminüzenet frissítése nem sikerült: {error}")

        await interaction.response.send_message(
            "❌ A karakter elutasítva. Az indoklás mentve.",
            ephemeral=True
        )


def register_persistent_views(bot):
    characters = load_characters()

    for user_id, user_characters in characters.items():
        # Régi karakteradatok kezelése
        if "name" in user_characters:
            user_characters = {"1": user_characters}

        for character_id, character in user_characters.items():
            if (
                character.get("status") == "pending"
                and character.get("image_status") == "uploaded"
                and character.get("review_message_id")
            ):
                bot.add_view(
                    AdminReviewView(user_id, character_id),
                    message_id=int(character["review_message_id"])
                )