import nextcord
import json
from pathlib import Path
from nextcord.ui import View, Button

CARTS_FILE = Path(__file__).parent / "carts.json"
INVENTORY_FILE = Path(__file__).parent / "inventory.json"

def load_carts():
    if not CARTS_FILE.exists():
        return {}

    with open(CARTS_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def save_carts(carts):
    with open(CARTS_FILE, "w", encoding="utf-8") as file:
        json.dump(carts, file, ensure_ascii=False, indent=4)


def add_to_cart(user_id, category_id, item_id, quantity):
    carts = load_carts()

    user_id = str(user_id)

    if user_id not in carts:
        carts[user_id] = {}

    cart_key = f"{category_id}:{item_id}"

    if cart_key not in carts[user_id]:
        carts[user_id][cart_key] = 0

    carts[user_id][cart_key] += quantity

    save_carts(carts)

def remove_from_cart(user_id, cart_key):
    carts = load_carts()
    user_id = str(user_id)

    if user_id not in carts:
        return False

    if cart_key not in carts[user_id]:
        return False

    del carts[user_id][cart_key]

    if not carts[user_id]:
        del carts[user_id]

    save_carts(carts)
    return True

def load_inventory():
    if not INVENTORY_FILE.exists():
        return {}

    with open(INVENTORY_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def save_inventory(inventory):
    with open(INVENTORY_FILE, "w", encoding="utf-8") as file:
        json.dump(inventory, file, ensure_ascii=False, indent=4)

SHOP_CATEGORIES = {
    "etelek": {
        "name": "🍞 Ételek",
        "items": {
            "kenyer": {
                "name": "Kenyér",
                "description": "Egyszerű, tápláló kenyér.",
                "price": 20
            },
            "alma": {
                "name": "Alma",
                "description": "Friss alma.",
                "price": 15
            },
            "hus": {
                "name": "Hús / Vadhús",
                "description": "Friss hús és vadon élő állatok húsa.",
                "price": 40
            },
            "gyumolcs": {
                "name": "Gyümölcs",
                "description": "Válogatott gyümölcsök.",
                "price": 25
            }
        }
    },
    "italok": {
        "name": "🥤 Italok",
        "items": {
            "ivoviz": {
                "name": "Ivóvíz",
                "description": "Egy palack tiszta ivóvíz.",
                "price": 15
            },
            "gyumolcsle": {
                "name": "Gyümölcslé",
                "description": "Frissen készített gyümölcslé.",
                "price": 30
            },
            "tej": {
                "name": "Tej",
                "description": "Friss tej.",
                "price": 25
            },
            "tea": {
                "name": "Tea",
                "description": "Melegítő ital a hideg napokra.",
                "price": 20
            }
        }
    },
    "fegyverek": {
        "name": "⚔️ Fegyverek",
        "items": {
            "fakard": {
                "name": "Fakard",
                "description": "Edzéshez használható gyakorlókard.",
                "price": 80
            },
            "gyakorloij": {
                "name": "Gyakorlóíj",
                "description": "Edzéshez készült gyakorlóíj.",
                "price": 100
            },
            "gyakorlotőr": {
                "name": "Gyakorlótőr",
                "description": "Tompa gyakorlóeszköz.",
                "price": 60
            },
            "gyakorlolándzsa": {
                "name": "Gyakorlólándzsa",
                "description": "Edzéshez használható gyakorlóeszköz.",
                "price": 90
            }
        }
    },
    "gyakorlofelszereles": {
        "name": "🥋 Gyakorlófelszerelés",
        "items": {
            "gyakorlopajzs": {
                "name": "Gyakorlópajzs",
                "description": "Edzéshez használható védőfelszerelés.",
                "price": 70
            },
            "edzokesztyu": {
                "name": "Edzőkesztyű",
                "description": "Kényelmes kesztyű gyakorláshoz.",
                "price": 50
            },
            "vedosisak": {
                "name": "Védősisak",
                "description": "Fejvédő felszerelés edzésekhez.",
                "price": 90
            },
            "gyakorloruha": {
                "name": "Gyakorlóruha",
                "description": "Kényelmes öltözet az edzésekhez.",
                "price": 60
            },
            "edzobabu": {
                "name": "Edzőbábu",
                "description": "Gyakorláshoz használható edzőeszköz.",
                "price": 120
            }
        }
    },
    "ruhazat": {
        "name": "👕 Ruházat",
        "items": {
            "hetkoznapi_ruha": {
                "name": "Hétköznapi ruha",
                "description": "Egyszerű, kényelmes öltözet.",
                "price": 50
            },
            "kabát": {
                "name": "Kabát",
                "description": "Meleg kabát a hideg időkre.",
                "price": 100
            },
            "csizma": {
                "name": "Csizma",
                "description": "Tartós lábbeli a mindennapokra.",
                "price": 75
            },
            "kesztyu": {
                "name": "Kesztyű",
                "description": "Egyszerű védőkesztyű.",
                "price": 35
            },
            "elegans_ruha": {
                "name": "Elegáns ruha",
                "description": "Különleges alkalmakra készült öltözet.",
                "price": 180
            }
        }
    },
    "egyeb": {
        "name": "🎒 Egyéb",
        "items": {
            "hatizsak": {
                "name": "Hátizsák",
                "description": "Praktikus táska a személyes tárgyak tárolására.",
                "price": 75
            },
            "kotel": {
                "name": "Kötél",
                "description": "Általános célokra használható kötél.",
                "price": 30
            },
            "jegyzetfuzet": {
                "name": "Jegyzetfüzet",
                "description": "Jegyzetek és feljegyzések készítéséhez.",
                "price": 20
            },
            "zseblampa": {
                "name": "Zseblámpa",
                "description": "Hordozható fényforrás.",
                "price": 60
            },
            "var keszlet": {
                "name": "Varrókészlet",
                "description": "Alapvető eszközök ruhák javításához.",
                "price": 45
            }
        }
    },
    "korzeti": {
        "name": "🏛️ Körzeti különlegességek",
        "items": {
            "korzet_1": {
                "name": "Luxusékszer",
                "description": "Az 1. körzet híres, elegáns ékszere.",
                "price": 300,
                "district": 1
            },
            "korzet_2": {
                "name": "Díszes ruha",
                "description": "A 2. körzet kézműveseinek különleges ruhája.",
                "price": 250,
                "district": 2
            },
            "korzet_3": {
                "name": "Elektronikai alkatrész",
                "description": "A 3. körzet technológiai terméke.",
                "price": 180,
                "district": 3
            },
            "korzet_4": {
                "name": "Különleges halétel",
                "description": "A 4. körzet halászainak válogatott portékája.",
                "price": 100,
                "district": 4
            },
            "korzet_5": {
                "name": "Energiakristály",
                "description": "Az 5. körzet energiatermeléséhez kapcsolódó különlegesség.",
                "price": 200,
                "district": 5
            },
            "korzet_6": {
                "name": "Járműalkatrész",
                "description": "A 6. körzet közlekedési iparából származó termék.",
                "price": 150,
                "district": 6
            },
            "korzet_7": {
                "name": "Faragott fatárgy",
                "description": "A 7. körzet mestereinek kézzel készített dísztárgya.",
                "price": 120,
                "district": 7
            },
            "korzet_8": {
                "name": "Különleges szövet",
                "description": "A 8. körzet textiliparának minőségi terméke.",
                "price": 130,
                "district": 8
            },
            "korzet_9": {
                "name": "Gabonacsomag",
                "description": "A 9. körzet terméséből összeállított csomag.",
                "price": 90,
                "district": 9
            },
            "korzet_10": {
                "name": "Füstölt húskülönlegesség",
                "description": "A 10. körzet jellegzetes élelmiszere.",
                "price": 110,
                "district": 10
            },
            "korzet_11": {
                "name": "Friss gyümölcskosár",
                "description": "A 11. körzet gyümölcseiből összeállítva.",
                "price": 100,
                "district": 11
            },
            "korzet_12": {
                "name": "Kézzel készített szénmedál",
                "description": "A 12. körzet bányászati hagyományait idéző medál.",
                "price": 140,
                "district": 12
            },
            "korzet_12_vadhus": {
                "name": "Vadhús",
                "description": "A 12. körzet erdeiből származó friss vadhús.",
                "price": 50,
                "district": 12
            },
            "korzet_13": {
                "name": "Precíziós műszer",
                "description": "A 13. körzet technikai szakértelmével készült eszköz.",
                "price": 350,
                "district": 13
            }
        }
    },
    "ritka": {
        "name": "💎 Ritka tárgyak",
        "items": {
            "arany_medal": {
                "name": "Aranymedál",
                "description": "Ritka, díszes aranymedál.",
                "price": 500
            },
            "luxusora": {
                "name": "Luxusóra",
                "description": "Különleges, elegáns karóra.",
                "price": 750
            },
            "ritka_konyv": {
                "name": "Ritka könyv",
                "description": "Nehezen beszerezhető, értékes könyv.",
                "price": 400
            },
            "antik_ekszer": {
                "name": "Antik ékszer",
                "description": "Régi korokból származó különleges ékszer.",
                "price": 650
            },
            "gyujtoi_ermek": {
                "name": "Gyűjtői érme",
                "description": "Különleges Panem-érme gyűjtők számára.",
                "price": 350
            },
            "luxus_parfum": {
                "name": "Luxusparfüm",
                "description": "Ritka, különleges illat.",
                "price": 450
            },
            "fecsegoposzata_kituzo": {
                "name": "Fecsegőposzáta kitűző",
                "description": "A 12. körzet híres fecsegőposzátájának kitűzője.",
                "price": 300
            }
        }
    }
}

def create_inventory_embed(user_id):
    inventory = load_inventory()
    user_inventory = inventory.get(str(user_id), {})

    embed = nextcord.Embed(
        title="🎒 Felszerelés",
        color=nextcord.Color.gold()
    )

    if not user_inventory:
        embed.description = "Még nincs egyetlen tárgyad sem."
        return embed

    for cart_key, quantity in user_inventory.items():
        category_id, item_id = cart_key.split(":", 1)

        item = SHOP_CATEGORIES[category_id]["items"][item_id]

        embed.add_field(
            name=f"📦 {item['name']}",
            value=f"Darabszám: **{quantity} db**",
            inline=False
        )

    return embed

class QuantityModal(nextcord.ui.Modal):
    def __init__(self, user_id, category_id, item_id):
        super().__init__(title="🛒 Termék hozzáadása")

        self.user_id = user_id
        self.category_id = category_id
        self.item_id = item_id

        self.quantity = nextcord.ui.TextInput(
            label="Hány darabot szeretnél?",
            placeholder="Például: 5",
            min_length=1,
            max_length=4,
            required=True
        )

        self.add_item(self.quantity)

    async def callback(self, interaction: nextcord.Interaction):
        if str(interaction.user.id) != str(self.user_id):
            await interaction.response.send_message(
                "❌ Ez nem a te vásárlási ablakod!",
                ephemeral=True
            )
            return

        try:
            quantity = int(self.quantity.value)

            if quantity <= 0:
                raise ValueError

        except ValueError:
            await interaction.response.send_message(
                "❌ Érvényes, pozitív darabszámot adj meg!",
                ephemeral=True
            )
            return

        add_to_cart(
            self.user_id,
            self.category_id,
            self.item_id,
            quantity
        )

        await interaction.response.send_message(
            f"✅ **{quantity} db** termék bekerült a kosaradba!",
            ephemeral=True
        )


class ShopItemButton(Button):
    def __init__(self, category_id, item_id, item):
        super().__init__(
            label=f"🛒 {item['name']}",
            style=nextcord.ButtonStyle.success
        )

        self.category_id = category_id
        self.item_id = item_id

    async def callback(self, interaction: nextcord.Interaction):
        modal = QuantityModal(
            interaction.user.id,
            self.category_id,
            self.item_id
        )

        await interaction.response.send_modal(modal)


class ShopCategoryButton(Button):
    def __init__(self, category_id):
        category = SHOP_CATEGORIES[category_id]

        super().__init__(
            label=category["name"],
            style=nextcord.ButtonStyle.primary
        )

        self.category_id = category_id

    async def callback(self, interaction: nextcord.Interaction):
        category = SHOP_CATEGORIES[self.category_id]

        embed = nextcord.Embed(
            title=f"🛒 Panem Bolt – {category['name']}",
            description="Válaszd ki a megvásárolni kívánt terméket!",
            color=nextcord.Color.gold()
        )

        for item in category["items"].values():
            embed.add_field(
                name=f"{item['name']} – {item['price']} Panem-kredit",
                value=item["description"],
                inline=False
            )

        view = self.view

        for child in list(view.children):
            if isinstance(child, ShopItemButton):
                view.remove_item(child)

        for item_id, item in category["items"].items():
            view.add_item(
                ShopItemButton(
                    self.category_id,
                    item_id,
                    item
                )
            )

        await interaction.response.edit_message(
            embed=embed,
            view=view
        )


def purchase_items(user_id):
    user_id = str(user_id)

    carts = load_carts()
    inventory = load_inventory()

    user_cart = carts.get(user_id, {})

    if not user_cart:
        return False, "A kosarad üres!"

    total_price = 0

    for cart_key, quantity in user_cart.items():
        category_id, item_id = cart_key.split(":", 1)
        item = SHOP_CATEGORIES[category_id]["items"][item_id]

        total_price += item["price"] * quantity

    players_file = Path(__file__).parent / "players.json"

    if not players_file.exists():
        return False, "Nem található a játékosadatbázis!"

    with open(players_file, "r", encoding="utf-8") as file:
        players = json.load(file)

    if user_id not in players:
        return False, "Nem található a játékosprofilod!"

    player = players[user_id]
    balance = player.get("kredit", 0)

    if balance < total_price:
        return False, (
            f"Nincs elegendő Panem-kredited! "
            f"Szükséges: {total_price}, egyenleg: {balance}."
        )

    player["kredit"] -= total_price

    if user_id not in inventory:
        inventory[user_id] = {}

    for cart_key, quantity in user_cart.items():
        inventory[user_id][cart_key] = (
            inventory[user_id].get(cart_key, 0) + quantity
        )

    save_inventory(inventory)

    with open(players_file, "w", encoding="utf-8") as file:
        json.dump(players, file, ensure_ascii=False, indent=4)

    del carts[user_id]
    save_carts(carts)

    return True, f"Sikeres vásárlás! Levont összeg: {total_price} Panem-kredit."

class RemoveCartItemButton(Button):
    def __init__(self, cart_key, user_id):
        super().__init__(
            label="🗑️ Eltávolítás",
            style=nextcord.ButtonStyle.danger
        )

        self.cart_key = cart_key
        self.user_id = str(user_id)

    async def callback(self, interaction: nextcord.Interaction):
        if str(interaction.user.id) != self.user_id:
            await interaction.response.send_message(
                "❌ Ez nem a te kosarad!",
                ephemeral=True
            )
            return

        success = remove_from_cart(
            self.user_id,
            self.cart_key
        )

        if success:
            await interaction.response.send_message(
                "🗑️ A terméket eltávolítottad a kosaradból! "
                "Nyisd meg újra a kosaradat a friss tartalomért.",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "❌ Ez a termék már nincs a kosaradban!",
                ephemeral=True
            )

class PurchaseButton(Button):
    def __init__(self):
        super().__init__(
            label="💳 Vásárlás",
            style=nextcord.ButtonStyle.success
        )

    async def callback(self, interaction: nextcord.Interaction):
        success, message = purchase_items(interaction.user.id)

        await interaction.response.send_message(
            message,
            ephemeral=True
        )


class CartButton(Button):
    def __init__(self):
        super().__init__(
            label="🛒 Kosaram",
            style=nextcord.ButtonStyle.success
        )

    async def callback(self, interaction: nextcord.Interaction):
        carts = load_carts()
        user_cart = carts.get(str(interaction.user.id), {})

        if not user_cart:
            await interaction.response.send_message(
                "🛒 A kosarad jelenleg üres!",
                ephemeral=True
            )
            return

        embed = nextcord.Embed(
            title="🛒 Saját kosarad",
            description="A kosaradban lévő termékek:",
            color=nextcord.Color.gold()
        )

        total_price = 0

        for cart_key, quantity in user_cart.items():
            category_id, item_id = cart_key.split(":", 1)

            item = SHOP_CATEGORIES[category_id]["items"][item_id]

            item_total = item["price"] * quantity
            total_price += item_total

            embed.add_field(
                name=item["name"],
                value=(
                    f"Darabszám: **{quantity} db**\n"
                    f"Egységár: **{item['price']} Panem-kredit**\n"
                    f"Összesen: **{item_total} Panem-kredit**"
                ),
                inline=False
            )

        embed.add_field(
            name="💰 Végösszeg",
            value=f"**{total_price} Panem-kredit**",
            inline=False
        )

        view = View()

        for cart_key in user_cart:
            view.add_item(
                RemoveCartItemButton(
                    cart_key,
                    interaction.user.id
                )
            )

        view.add_item(PurchaseButton())

        await interaction.response.send_message(
            embed=embed,
            view=view,
            ephemeral=True
        )


class ShopView(View):
    def __init__(self):
        super().__init__(timeout=None)

        for category_id in SHOP_CATEGORIES:
            self.add_item(ShopCategoryButton(category_id))

        self.add_item(CartButton())

def create_shop_embed():
    embed = nextcord.Embed(
        title="🛒 Panem Bolt",
        description=(
            "Üdvözöllek Panem boltjában!\n\n"
            "Válassz egy kategóriát az alábbi gombok közül, "
            "és nézd meg a kínálatot!\n\n"
            "💰 Fizetőeszköz: Panem-kredit"
        ),
        color=nextcord.Color.gold()
    )

    embed.set_footer(text="Panem – A 13 körzet világa")

    return embed
    