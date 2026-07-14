// ══════════════════════════════════════════════
// NAME LIBRARY - Complete Global Game Names
// ══════════════════════════════════════════════

pub struct NameLibrary;

#[derive(Clone, Debug)]
pub struct GameName {
    pub english: &'static str,
    pub arabic: &'static str,
    pub category: &'static str,
    pub patterns: &'static [&'static str],
}

impl NameLibrary {
    pub fn all_names() -> Vec<GameName> {
        let mut names = Vec::new();
        names.extend(Self::keys());
        names.extend(Self::chests());
        names.extend(Self::currencies());
        names.extend(Self::tickets());
        names.extend(Self::materials());
        names.extend(Self::consumables());
        names.extend(Self::stats());
        names.extend(Self::hacks());
        names
    }

    // ═══ 1. المفاتيح (Keys) ═══
    fn keys() -> Vec<GameName> {
        vec![
            GameName { english: "Gold Key", arabic: "مفتاح ذهبي", category: "مفاتيح", patterns: &["GoldKey","gold_key","GOLD_KEY","goldenKey"] },
            GameName { english: "Silver Key", arabic: "مفتاح فضي", category: "مفاتيح", patterns: &["SilverKey","silver_key","SILVER_KEY"] },
            GameName { english: "Bronze Key", arabic: "مفتاح برونزي", category: "مفاتيح", patterns: &["BronzeKey","bronze_key"] },
            GameName { english: "Iron Key", arabic: "مفتاح حديدي", category: "مفاتيح", patterns: &["IronKey","iron_key"] },
            GameName { english: "Steel Key", arabic: "مفتاح فولاذي", category: "مفاتيح", patterns: &["SteelKey","steel_key"] },
            GameName { english: "Copper Key", arabic: "مفتاح نحاسي", category: "مفاتيح", patterns: &["CopperKey","copper_key"] },
            GameName { english: "Platinum Key", arabic: "مفتاح بلاتيني", category: "مفاتيح", patterns: &["PlatinumKey","platinum_key"] },
            GameName { english: "Diamond Key", arabic: "مفتاح ألماسي", category: "مفاتيح", patterns: &["DiamondKey","diamond_key"] },
            GameName { english: "Ruby Key", arabic: "مفتاح ياقوتي", category: "مفاتيح", patterns: &["RubyKey","ruby_key"] },
            GameName { english: "Emerald Key", arabic: "مفتاح زمردي", category: "مفاتيح", patterns: &["EmeraldKey","emerald_key"] },
            GameName { english: "Sapphire Key", arabic: "مفتاح صفيري", category: "مفاتيح", patterns: &["SapphireKey","sapphire_key"] },
            GameName { english: "Amethyst Key", arabic: "مفتاح جمشت", category: "مفاتيح", patterns: &["AmethystKey","amethyst_key"] },
            GameName { english: "Obsidian Key", arabic: "مفتاح سبجي", category: "مفاتيح", patterns: &["ObsidianKey","obsidian_key"] },
            GameName { english: "Master Key", arabic: "مفتاح رئيسي", category: "مفاتيح", patterns: &["MasterKey","master_key","MASTER_KEY"] },
            GameName { english: "Skeleton Key", arabic: "مفتاح الهيكل", category: "مفاتيح", patterns: &["SkeletonKey","skeleton_key"] },
            GameName { english: "Rusty Key", arabic: "مفتاح صدئ", category: "مفاتيح", patterns: &["RustyKey","rusty_key"] },
            GameName { english: "Dungeon Key", arabic: "مفتاح زنزانة", category: "مفاتيح", patterns: &["DungeonKey","dungeon_key"] },
            GameName { english: "Crypt Key", arabic: "مفتاح سرداب", category: "مفاتيح", patterns: &["CryptKey","crypt_key"] },
            GameName { english: "Tomb Key", arabic: "مفتاح مقبرة", category: "مفاتيح", patterns: &["TombKey","tomb_key"] },
            GameName { english: "Vault Key", arabic: "مفتاح خزنة", category: "مفاتيح", patterns: &["VaultKey","vault_key"] },
            GameName { english: "Safe Key", arabic: "مفتاح أمانات", category: "مفاتيح", patterns: &["SafeKey","safe_key"] },
            GameName { english: "Gate Key", arabic: "مفتاح بوابة", category: "مفاتيح", patterns: &["GateKey","gate_key"] },
            GameName { english: "Portal Key", arabic: "مفتاح انتقال", category: "مفاتيح", patterns: &["PortalKey","portal_key"] },
            GameName { english: "Ancient Key", arabic: "مفتاح أثري", category: "مفاتيح", patterns: &["AncientKey","ancient_key"] },
            GameName { english: "Relic Key", arabic: "مفتاح رفات", category: "مفاتيح", patterns: &["RelicKey","relic_key"] },
            GameName { english: "Mythic Key", arabic: "مفتاح خرافي", category: "مفاتيح", patterns: &["MythicKey","mythic_key"] },
            GameName { english: "Legendary Key", arabic: "مفتاح أسطوري", category: "مفاتيح", patterns: &["LegendaryKey","legendary_key"] },
            GameName { english: "Epic Key", arabic: "مفتاح ملحمي", category: "مفاتيح", patterns: &["EpicKey","epic_key"] },
            GameName { english: "Rare Key", arabic: "مفتاح نادر", category: "مفاتيح", patterns: &["RareKey","rare_key"] },
            GameName { english: "Celestial Key", arabic: "مفتاح سماوي", category: "مفاتيح", patterns: &["CelestialKey","celestial_key"] },
            GameName { english: "Void Key", arabic: "مفتاح الفراغ", category: "مفاتيح", patterns: &["VoidKey","void_key"] },
            GameName { english: "Shadow Key", arabic: "مفتاح الظل", category: "مفاتيح", patterns: &["ShadowKey","shadow_key"] },
            GameName { english: "Dragon Key", arabic: "مفتاح التنين", category: "مفاتيح", patterns: &["DragonKey","dragon_key"] },
            GameName { english: "Temple Key", arabic: "مفتاح المعبد", category: "مفاتيح", patterns: &["TempleKey","temple_key"] },
            GameName { english: "Boss Key", arabic: "مفتاح الزعيم", category: "مفاتيح", patterns: &["BossKey","boss_key"] },
            GameName { english: "Magic Key", arabic: "مفتاح سحري", category: "مفاتيح", patterns: &["MagicKey","magic_key"] },
            GameName { english: "Rune Key", arabic: "مفتاح روني", category: "مفاتيح", patterns: &["RuneKey","rune_key"] },
            GameName { english: "Cursed Key", arabic: "مفتاح ملعون", category: "مفاتيح", patterns: &["CursedKey","cursed_key"] },
            GameName { english: "Sacred Key", arabic: "مفتاح مقدس", category: "مفاتيح", patterns: &["SacredKey","sacred_key"] },
        ]
    }

    // ═══ 2. الصناديق (Chests) ═══
    fn chests() -> Vec<GameName> {
        vec![
            GameName { english: "Wooden Chest", arabic: "صندوق خشبي", category: "صناديق", patterns: &["WoodenChest","wooden_chest"] },
            GameName { english: "Iron Chest", arabic: "صندوق حديدي", category: "صناديق", patterns: &["IronChest","iron_chest"] },
            GameName { english: "Gold Chest", arabic: "صندوق ذهبي", category: "صناديق", patterns: &["GoldChest","gold_chest"] },
            GameName { english: "Silver Chest", arabic: "صندوق فضي", category: "صناديق", patterns: &["SilverChest","silver_chest"] },
            GameName { english: "Diamond Chest", arabic: "صندوق ألماسي", category: "صناديق", patterns: &["DiamondChest","diamond_chest"] },
            GameName { english: "Legendary Chest", arabic: "صندوق أسطوري", category: "صناديق", patterns: &["LegendaryChest","legendary_chest"] },
            GameName { english: "Epic Chest", arabic: "صندوق ملحمي", category: "صناديق", patterns: &["EpicChest","epic_chest"] },
            GameName { english: "Treasure Chest", arabic: "صندوق الكنز", category: "صناديق", patterns: &["TreasureChest","treasure_chest","treasureChest"] },
            GameName { english: "Loot Box", arabic: "صندوق الغنائم", category: "صناديق", patterns: &["LootBox","loot_box","lootBox","LootCrate"] },
            GameName { english: "Gacha Box", arabic: "كبسولة غاشا", category: "صناديق", patterns: &["GachaBox","gacha_box","GachaCapsule"] },
            GameName { english: "Supply Crate", arabic: "صندوق إمدادات", category: "صناديق", patterns: &["SupplyCrate","supply_crate"] },
            GameName { english: "Airdrop Crate", arabic: "صندوق إيردروب", category: "صناديق", patterns: &["AirdropCrate","airdrop","AirDrop"] },
            GameName { english: "Mystery Box", arabic: "صندوق غامض", category: "صناديق", patterns: &["MysteryBox","mystery_box"] },
            GameName { english: "Lucky Box", arabic: "صندوق الحظ", category: "صناديق", patterns: &["LuckyBox","lucky_box"] },
            GameName { english: "Boss Crate", arabic: "صندوق الزعيم", category: "صناديق", patterns: &["BossCrate","boss_crate"] },
            GameName { english: "Dungeon Chest", arabic: "صندوق زنزانة", category: "صناديق", patterns: &["DungeonChest","dungeon_chest"] },
            GameName { english: "Locked Chest", arabic: "صندوق مقفل", category: "صناديق", patterns: &["LockedChest","locked_chest"] },
            GameName { english: "Ancient Chest", arabic: "صندوق أثري", category: "صناديق", patterns: &["AncientChest","ancient_chest"] },
            GameName { english: "Enchanted Chest", arabic: "صندوق مسحور", category: "صناديق", patterns: &["EnchantedChest","enchanted_chest"] },
            GameName { english: "Frozen Chest", arabic: "صندوق مجمد", category: "صناديق", patterns: &["FrozenChest","frozen_chest"] },
        ]
    }

    // ═══ 3. العملات والموارد (Currencies) ═══
    fn currencies() -> Vec<GameName> {
        vec![
            GameName { english: "Gold", arabic: "ذهب", category: "عملات", patterns: &["Gold","gold","GOLD","goldCoins","GoldCoins","gold_coins","GoldAmount","goldAmount","get_Gold","set_Gold"] },
            GameName { english: "Silver", arabic: "فضة", category: "عملات", patterns: &["Silver","silver","SILVER","SilverCoins","silver_coins"] },
            GameName { english: "Copper", arabic: "نحاس", category: "عملات", patterns: &["Copper","copper","CopperCoins","copper_coins"] },
            GameName { english: "Gems", arabic: "جواهر", category: "عملات", patterns: &["Gems","gems","GEMS","GemCount","gemCount","gem_count","get_Gems","set_Gems","GemBalance","gemBalance"] },
            GameName { english: "Diamonds", arabic: "ألماس", category: "عملات", patterns: &["Diamonds","diamonds","DIAMONDS","DiamondCount","diamondCount","get_Diamonds","set_Diamonds"] },
            GameName { english: "Rubies", arabic: "ياقوت", category: "عملات", patterns: &["Rubies","rubies","RubyCount","rubyCount"] },
            GameName { english: "Emeralds", arabic: "زمرد", category: "عملات", patterns: &["Emeralds","emeralds","EmeraldCount"] },
            GameName { english: "Crystals", arabic: "بلورات", category: "عملات", patterns: &["Crystals","crystals","CrystalCount","crystalCount"] },
            GameName { english: "Shards", arabic: "شظايا", category: "عملات", patterns: &["Shards","shards","ShardCount","shardCount"] },
            GameName { english: "Dust", arabic: "غبار سحري", category: "عملات", patterns: &["Dust","dust","MagicDust","magicDust","DustAmount"] },
            GameName { english: "Cash", arabic: "كاش", category: "عملات", patterns: &["Cash","cash","CASH","Bucks","bucks","Dollars","dollars"] },
            GameName { english: "Credits", arabic: "أرصدة", category: "عملات", patterns: &["Credits","credits","CREDITS","CreditBalance"] },
            GameName { english: "Tokens", arabic: "توكنز", category: "عملات", patterns: &["Tokens","tokens","TOKENS","TokenCount","tokenCount"] },
            GameName { english: "Stars", arabic: "نجوم", category: "عملات", patterns: &["Stars","stars","STARS","StarCount","starCount","get_Stars"] },
            GameName { english: "Crowns", arabic: "تيجان", category: "عملات", patterns: &["Crowns","crowns","CrownCount"] },
            GameName { english: "Trophies", arabic: "كؤوس", category: "عملات", patterns: &["Trophies","trophies","TROPHIES","TrophyCount","trophyCount"] },
            GameName { english: "Medals", arabic: "ميداليات", category: "عملات", patterns: &["Medals","medals","MedalCount"] },
            GameName { english: "Badges", arabic: "شارات", category: "عملات", patterns: &["Badges","badges","BadgeCount"] },
            GameName { english: "Orbs", arabic: "كرات طاقة", category: "عملات", patterns: &["Orbs","orbs","OrbCount","orbCount"] },
            GameName { english: "Runes", arabic: "رونات", category: "عملات", patterns: &["Runes","runes","RuneCount","runeCount"] },
            GameName { english: "Points", arabic: "نقاط", category: "عملات", patterns: &["Points","points","POINTS","PointCount","pointCount","Score","score","SCORE"] },
            GameName { english: "Soul Points", arabic: "نقاط الأرواح", category: "عملات", patterns: &["SoulPoints","soulPoints","soul_points"] },
            GameName { english: "Honor Points", arabic: "نقاط الشرف", category: "عملات", patterns: &["HonorPoints","honorPoints","honor_points"] },
            GameName { english: "Arena Points", arabic: "نقاط الحلبة", category: "عملات", patterns: &["ArenaPoints","arenaPoints","arena_points"] },
            GameName { english: "Guild Coins", arabic: "عملات التحالف", category: "عملات", patterns: &["GuildCoins","guildCoins","guild_coins","ClanCoins","clanCoins"] },
            GameName { english: "Alliance Points", arabic: "نقاط التحالف", category: "عملات", patterns: &["AlliancePoints","alliancePoints","alliance_points"] },
            GameName { english: "Karma Points", arabic: "نقاط الكارما", category: "عملات", patterns: &["KarmaPoints","karmaPoints","karma_points"] },
            GameName { english: "Valor Points", arabic: "نقاط البسالة", category: "عملات", patterns: &["ValorPoints","valorPoints","valor_points"] },
            GameName { english: "Glory Points", arabic: "نقاط المجد", category: "عملات", patterns: &["GloryPoints","gloryPoints","glory_points"] },
            GameName { english: "Pearls", arabic: "لآلئ", category: "عملات", patterns: &["Pearls","pearls","PearlCount"] },
            GameName { english: "Ancient Coins", arabic: "عملات قديمة", category: "عملات", patterns: &["AncientCoins","ancientCoins","ancient_coins"] },
            GameName { english: "Event Coins", arabic: "عملات فعاليات", category: "عملات", patterns: &["EventCoins","eventCoins","event_coins"] },
            GameName { english: "Season Points", arabic: "نقاط الموسم", category: "عملات", patterns: &["SeasonPoints","seasonPoints","season_points"] },
            GameName { english: "VIP Points", arabic: "نقاط VIP", category: "عملات", patterns: &["VIPPoints","vipPoints","vip_points"] },
            GameName { english: "Money", arabic: "فلوس", category: "عملات", patterns: &["Money","money","MONEY","MoneyAmount","moneyAmount","get_Money","set_Money","AddMoney","addMoney"] },
            GameName { english: "Coins", arabic: "عملات", category: "عملات", patterns: &["Coins","coins","COINS","CoinCount","coinCount","get_Coins","set_Coins","AddCoins","addCoins","CoinBalance"] },
        ]
    }

    // ═══ 4. التذاكر والتصاريح (Tickets) ═══
    fn tickets() -> Vec<GameName> {
        vec![
            GameName { english: "Summon Ticket", arabic: "تذكرة استدعاء", category: "تذاكر", patterns: &["SummonTicket","summonTicket","summon_ticket"] },
            GameName { english: "Gacha Ticket", arabic: "تذكرة غاشا", category: "تذاكر", patterns: &["GachaTicket","gachaTicket","gacha_ticket"] },
            GameName { english: "Spin Ticket", arabic: "تذكرة لف", category: "تذاكر", patterns: &["SpinTicket","spinTicket","spin_ticket"] },
            GameName { english: "Battle Pass", arabic: "باتل باس", category: "تذاكر", patterns: &["BattlePass","battlePass","battle_pass"] },
            GameName { english: "Season Pass", arabic: "ممر الموسم", category: "تذاكر", patterns: &["SeasonPass","seasonPass","season_pass"] },
            GameName { english: "VIP Pass", arabic: "ممر VIP", category: "تذاكر", patterns: &["VIPPass","vipPass","vip_pass"] },
            GameName { english: "Royal Pass", arabic: "ممر ملكي", category: "تذاكر", patterns: &["RoyalPass","royalPass","royal_pass"] },
            GameName { english: "Dungeon Ticket", arabic: "تذكرة زنزانة", category: "تذاكر", patterns: &["DungeonTicket","dungeonTicket","dungeon_ticket"] },
            GameName { english: "Raid Ticket", arabic: "تذكرة غارة", category: "تذاكر", patterns: &["RaidTicket","raidTicket","raid_ticket"] },
            GameName { english: "Arena Ticket", arabic: "تذكرة حلبة", category: "تذاكر", patterns: &["ArenaTicket","arenaTicket","arena_ticket"] },
            GameName { english: "Challenge Ticket", arabic: "تذكرة تحدي", category: "تذاكر", patterns: &["ChallengeTicket","challengeTicket"] },
            GameName { english: "Reset Ticket", arabic: "تذكرة إعادة", category: "تذاكر", patterns: &["ResetTicket","resetTicket","reset_ticket"] },
            GameName { english: "Skip Ticket", arabic: "تذكرة تخطي", category: "تذاكر", patterns: &["SkipTicket","skipTicket","skip_ticket"] },
            GameName { english: "Sweep Ticket", arabic: "تذكرة كنس", category: "تذاكر", patterns: &["SweepTicket","sweepTicket","sweep_ticket"] },
        ]
    }

    // ═══ 5. المواد (Materials) ═══
    fn materials() -> Vec<GameName> {
        vec![
            GameName { english: "Iron Ore", arabic: "خام حديد", category: "مواد", patterns: &["IronOre","ironOre","iron_ore"] },
            GameName { english: "Gold Ore", arabic: "خام ذهب", category: "مواد", patterns: &["GoldOre","goldOre","gold_ore"] },
            GameName { english: "Wood", arabic: "خشب", category: "مواد", patterns: &["Wood","wood","WOOD","Lumber","lumber","WoodCount","woodCount"] },
            GameName { english: "Stone", arabic: "حجر", category: "مواد", patterns: &["Stone","stone","STONE","Rock","rock","StoneCount"] },
            GameName { english: "Leather", arabic: "جلد", category: "مواد", patterns: &["Leather","leather","LeatherCount"] },
            GameName { english: "Cloth", arabic: "قماش", category: "مواد", patterns: &["Cloth","cloth","Fabric","fabric","ClothCount"] },
            GameName { english: "Silk", arabic: "حرير", category: "مواد", patterns: &["Silk","silk","SilkCount"] },
            GameName { english: "Herbs", arabic: "أعشاب", category: "مواد", patterns: &["Herbs","herbs","HerbCount"] },
            GameName { english: "Bones", arabic: "عظام", category: "مواد", patterns: &["Bones","bones","BoneCount"] },
            GameName { english: "Scales", arabic: "حراشف", category: "مواد", patterns: &["Scales","scales","ScaleCount"] },
            GameName { english: "Souls", arabic: "أرواح", category: "مواد", patterns: &["Souls","souls","SoulCount","soulCount"] },
            GameName { english: "Essence", arabic: "جوهر", category: "مواد", patterns: &["Essence","essence","EssenceCount"] },
            GameName { english: "Catalyst", arabic: "محفز", category: "مواد", patterns: &["Catalyst","catalyst","CatalystCount"] },
            GameName { english: "Elixir", arabic: "إكسير", category: "مواد", patterns: &["Elixir","elixir","ElixirCount"] },
            GameName { english: "Energy Core", arabic: "نواة طاقة", category: "مواد", patterns: &["EnergyCore","energyCore","PowerCore","powerCore"] },
            GameName { english: "Fragment", arabic: "شظية", category: "مواد", patterns: &["Fragment","fragment","FragmentCount","fragmentCount"] },
            GameName { english: "Scrap", arabic: "خردة", category: "مواد", patterns: &["Scrap","scrap","ScrapMetal","scrapMetal"] },
            GameName { english: "Blueprint", arabic: "مخطط", category: "مواد", patterns: &["Blueprint","blueprint","BlueprintCount"] },
            GameName { english: "Mithril", arabic: "ميثريل", category: "مواد", patterns: &["Mithril","mithril","MithrilCount"] },
            GameName { english: "Dark Matter", arabic: "مادة مظلمة", category: "مواد", patterns: &["DarkMatter","darkMatter","dark_matter"] },
            GameName { english: "Food", arabic: "طعام", category: "مواد", patterns: &["Food","food","FOOD","FoodCount","foodCount","Meal","meal"] },
            GameName { english: "Water", arabic: "ماء", category: "مواد", patterns: &["Water","water","WaterCount"] },
        ]
    }

    // ═══ 6. المستهلكات (Consumables) ═══
    fn consumables() -> Vec<GameName> {
        vec![
            GameName { english: "Health Potion", arabic: "جرعة صحة", category: "مستهلكات", patterns: &["HealthPotion","healthPotion","health_potion","HealPotion","healPotion"] },
            GameName { english: "Mana Potion", arabic: "جرعة مانا", category: "مستهلكات", patterns: &["ManaPotion","manaPotion","mana_potion"] },
            GameName { english: "Stamina Potion", arabic: "جرعة لياقة", category: "مستهلكات", patterns: &["StaminaPotion","staminaPotion"] },
            GameName { english: "Energy Drink", arabic: "مشروب طاقة", category: "مستهلكات", patterns: &["EnergyDrink","energyDrink"] },
            GameName { english: "Antidote", arabic: "ترياق", category: "مستهلكات", patterns: &["Antidote","antidote"] },
            GameName { english: "Revive Stone", arabic: "حجر إنعاش", category: "مستهلكات", patterns: &["ReviveStone","reviveStone","PhoenixDown","phoenixDown"] },
            GameName { english: "Teleport Scroll", arabic: "لفافة انتقال", category: "مستهلكات", patterns: &["TeleportScroll","teleportScroll"] },
            GameName { english: "Bandage", arabic: "ضمادة", category: "مستهلكات", patterns: &["Bandage","bandage","BandageCount"] },
            GameName { english: "Medkit", arabic: "حقيبة طبية", category: "مستهلكات", patterns: &["Medkit","medkit","FirstAidKit","firstAidKit"] },
            GameName { english: "Stimpack", arabic: "إبرة منشطة", category: "مستهلكات", patterns: &["Stimpack","stimpack","StimPack"] },
            GameName { english: "Shield Battery", arabic: "بطارية درع", category: "مستهلكات", patterns: &["ShieldBattery","shieldBattery","ShieldCell","shieldCell"] },
        ]
    }

    // ═══ 7. الإحصائيات (Stats) ═══
    fn stats() -> Vec<GameName> {
        vec![
            GameName { english: "HP", arabic: "الصحة", category: "إحصائيات", patterns: &["HP","hp","Health","health","HEALTH","HealthPoints","healthPoints","get_Health","set_Health","GetHealth","SetHealth","MaxHP","maxHP","CurrentHP","currentHP","HitPoints","hitPoints"] },
            GameName { english: "MP", arabic: "المانا", category: "إحصائيات", patterns: &["MP","mp","Mana","mana","MANA","ManaPoints","manaPoints","get_Mana","set_Mana","GetMana","MaxMP","maxMP","CurrentMP"] },
            GameName { english: "SP", arabic: "اللياقة", category: "إحصائيات", patterns: &["SP","sp","Stamina","stamina","STAMINA","StaminaPoints","staminaPoints","get_Stamina","set_Stamina","MaxStamina","maxStamina"] },
            GameName { english: "Energy", arabic: "الطاقة", category: "إحصائيات", patterns: &["Energy","energy","ENERGY","EnergyPoints","energyPoints","get_Energy","set_Energy","MaxEnergy","maxEnergy","CurrentEnergy"] },
            GameName { english: "Rage", arabic: "الغضب", category: "إحصائيات", patterns: &["Rage","rage","RAGE","Fury","fury","RagePoints","ragePoints"] },
            GameName { english: "Attack", arabic: "الهجوم", category: "إحصائيات", patterns: &["ATK","atk","Attack","attack","ATTACK","AttackPower","attackPower","get_Attack","set_Attack","GetAttack","BaseAttack","baseAttack","PhysicalAttack","physicalAttack","TotalAttack"] },
            GameName { english: "Defense", arabic: "الدفاع", category: "إحصائيات", patterns: &["DEF","def","Defense","defense","DEFENSE","DefensePower","defensePower","get_Defense","set_Defense","GetDefense","PhysicalDefense","physicalDefense","MagicDefense","magicDefense","TotalDefense"] },
            GameName { english: "Strength", arabic: "القوة", category: "إحصائيات", patterns: &["STR","str","Strength","strength","STRENGTH","get_Strength","set_Strength","GetStrength","Power","power","POWER"] },
            GameName { english: "Agility", arabic: "الرشاقة", category: "إحصائيات", patterns: &["AGI","agi","Agility","agility","AGILITY","get_Agility","set_Agility"] },
            GameName { english: "Dexterity", arabic: "البراعة", category: "إحصائيات", patterns: &["DEX","dex","Dexterity","dexterity","DEXTERITY","get_Dexterity"] },
            GameName { english: "Intelligence", arabic: "الذكاء", category: "إحصائيات", patterns: &["INT","int","Intelligence","intelligence","INTELLIGENCE","get_Intelligence"] },
            GameName { english: "Wisdom", arabic: "الحكمة", category: "إحصائيات", patterns: &["WIS","wis","Wisdom","wisdom","WISDOM","get_Wisdom"] },
            GameName { english: "Vitality", arabic: "الحيوية", category: "إحصائيات", patterns: &["VIT","vit","Vitality","vitality","VITALITY","get_Vitality"] },
            GameName { english: "Luck", arabic: "الحظ", category: "إحصائيات", patterns: &["LCK","lck","Luck","luck","LUCK","get_Luck","set_Luck","Lucky","lucky"] },
            GameName { english: "Speed", arabic: "السرعة", category: "إحصائيات", patterns: &["SPD","spd","Speed","speed","SPEED","MoveSpeed","moveSpeed","MovementSpeed","movementSpeed","get_Speed","set_Speed","GetSpeed","RunSpeed","runSpeed"] },
            GameName { english: "Attack Speed", arabic: "سرعة الهجوم", category: "إحصائيات", patterns: &["ATKSPD","atkSpd","AttackSpeed","attackSpeed","ATK_SPD","get_AttackSpeed"] },
            GameName { english: "Critical Rate", arabic: "معدل الحرجة", category: "إحصائيات", patterns: &["CRIT","crit","CritRate","critRate","CriticalRate","criticalRate","CritChance","critChance","CriticalChance"] },
            GameName { english: "Critical Damage", arabic: "ضرر الحرجة", category: "إحصائيات", patterns: &["CRITDMG","critDmg","CritDamage","critDamage","CriticalDamage","criticalDamage"] },
            GameName { english: "Evasion", arabic: "المراوغة", category: "إحصائيات", patterns: &["EVA","eva","Evasion","evasion","EVASION","Dodge","dodge","DodgeRate","dodgeRate"] },
            GameName { english: "Accuracy", arabic: "الدقة", category: "إحصائيات", patterns: &["ACC","acc","Accuracy","accuracy","ACCURACY","HitRate","hitRate","Precision","precision"] },
            GameName { english: "Armor", arabic: "الدرع", category: "إحصائيات", patterns: &["Armor","armor","ARMOR","ArmorValue","armorValue","get_Armor","set_Armor","Shield","shield","SHIELD"] },
            GameName { english: "Penetration", arabic: "الاختراق", category: "إحصائيات", patterns: &["Penetration","penetration","ArmorPen","armorPen","MagicPen","magicPen"] },
            GameName { english: "Lifesteal", arabic: "سرقة الحياة", category: "إحصائيات", patterns: &["Lifesteal","lifesteal","LIFESTEAL","Vampirism","vampirism","LifeSteal"] },
            GameName { english: "Health Regen", arabic: "تجدد الصحة", category: "إحصائيات", patterns: &["HealthRegen","healthRegen","HPRegen","hpRegen","HealRate","healRate","Regeneration","regeneration"] },
            GameName { english: "Cooldown Reduction", arabic: "تقليل الانتظار", category: "إحصائيات", patterns: &["CDR","cdr","CooldownReduction","cooldownReduction","Cooldown","cooldown","COOLDOWN"] },
            GameName { english: "Level", arabic: "المستوى", category: "إحصائيات", patterns: &["Level","level","LEVEL","PlayerLevel","playerLevel","HeroLevel","heroLevel","CharLevel","get_Level","set_Level","GetLevel","CurrentLevel","MaxLevel"] },
            GameName { english: "Experience", arabic: "الخبرة", category: "إحصائيات", patterns: &["EXP","exp","XP","xp","Experience","experience","EXPERIENCE","PlayerEXP","playerEXP","HeroEXP","get_Experience","set_Experience","CurrentEXP","RequiredEXP","ExpMultiplier"] },
            GameName { english: "Ammo", arabic: "الذخيرة", category: "إحصائيات", patterns: &["Ammo","ammo","AMMO","AmmoCount","ammoCount","Bullets","bullets","BulletCount","Magazine","magazine","Clip","clip","get_Ammo","set_Ammo"] },
            GameName { english: "Damage", arabic: "الضرر", category: "إحصائيات", patterns: &["Damage","damage","DAMAGE","get_Damage","set_Damage","GetDamage","SetDamage","DealDamage","dealDamage","TakeDamage","takeDamage","CalculateDamage","DamageMultiplier","damageMultiplier","BaseDamage","baseDamage"] },
        ]
    }

    // ═══ 8. الهاكات (Hacks) ═══
    fn hacks() -> Vec<GameName> {
        vec![
            GameName { english: "God Mode", arabic: "وضع الإله", category: "هاكات", patterns: &["GodMode","godMode","god_mode","GOD_MODE","Invincible","invincible","IsInvincible","isGodMode"] },
            GameName { english: "Infinite Health", arabic: "صحة لا نهائية", category: "هاكات", patterns: &["InfiniteHealth","infiniteHealth","infinite_health","UnlimitedHP","unlimitedHP"] },
            GameName { english: "Infinite Mana", arabic: "مانا لا نهائية", category: "هاكات", patterns: &["InfiniteMana","infiniteMana","infinite_mana","UnlimitedMP","unlimitedMP"] },
            GameName { english: "Infinite Energy", arabic: "طاقة لا نهائية", category: "هاكات", patterns: &["InfiniteEnergy","infiniteEnergy","infinite_energy"] },
            GameName { english: "Infinite Ammo", arabic: "ذخيرة لا نهائية", category: "هاكات", patterns: &["InfiniteAmmo","infiniteAmmo","infinite_ammo","UnlimitedAmmo","unlimitedAmmo","NoReload","noReload"] },
            GameName { english: "No Recoil", arabic: "بدون ارتداد", category: "هاكات", patterns: &["NoRecoil","noRecoil","no_recoil","Recoil","recoil","RemoveRecoil","removeRecoil"] },
            GameName { english: "No Spread", arabic: "بدون انتشار", category: "هاكات", patterns: &["NoSpread","noSpread","no_spread","Spread","spread","RemoveSpread"] },
            GameName { english: "Aimbot", arabic: "تصويب تلقائي", category: "هاكات", patterns: &["Aimbot","aimbot","AIMBOT","AutoAim","autoAim","auto_aim","SilentAim","silentAim"] },
            GameName { english: "Wallhack", arabic: "رؤية خلف الجدران", category: "هاكات", patterns: &["Wallhack","wallhack","WALLHACK","WallHack","wall_hack","SeeThroughWalls"] },
            GameName { english: "ESP", arabic: "كشف الأعداء", category: "هاكات", patterns: &["ESP","esp","ExtraSensory","extraSensory","PlayerESP","playerESP"] },
            GameName { english: "Speedhack", arabic: "هكر السرعة", category: "هاكات", patterns: &["Speedhack","speedhack","SpeedHack","speed_hack","SpeedMultiplier","speedMultiplier"] },
            GameName { english: "Fly Hack", arabic: "هكر الطيران", category: "هاكات", patterns: &["FlyHack","flyHack","fly_hack","CanFly","canFly","IsFlying","isFlying"] },
            GameName { english: "No Clip", arabic: "اختراق الجدران", category: "هاكات", patterns: &["NoClip","noClip","no_clip","Noclip","noclip","ClipThrough","clipThrough"] },
            GameName { english: "One-Hit Kill", arabic: "قتل بضربة", category: "هاكات", patterns: &["OneHitKill","oneHitKill","one_hit_kill","InstantKill","instantKill","instant_kill","KillAll","killAll"] },
            GameName { english: "Damage Multiplier", arabic: "مضاعف الضرر", category: "هاكات", patterns: &["DamageMultiplier","damageMultiplier","damage_multiplier","DamageHack","damageHack"] },
            GameName { english: "XP Multiplier", arabic: "مضاعف الخبرة", category: "هاكات", patterns: &["XPMultiplier","xpMultiplier","xp_multiplier","EXPMultiplier","expMultiplier","EXPBoost","expBoost"] },
            GameName { english: "Gold Multiplier", arabic: "مضاعف الذهب", category: "هاكات", patterns: &["GoldMultiplier","goldMultiplier","gold_multiplier","MoneyMultiplier","moneyMultiplier"] },
            GameName { english: "Drop Rate Hack", arabic: "زيادة اللوت", category: "هاكات", patterns: &["DropRate","dropRate","drop_rate","DropRateHack","LootMultiplier","lootMultiplier"] },
            GameName { english: "No Cooldown", arabic: "بدون انتظار", category: "هاكات", patterns: &["NoCooldown","noCooldown","no_cooldown","CooldownReset","cooldownReset","ZeroCooldown","zeroCooldown","InstantCooldown"] },
            GameName { english: "Map Hack", arabic: "كشف الخريطة", category: "هاكات", patterns: &["MapHack","mapHack","map_hack","RevealMap","revealMap","FogRemover","fogRemover","RemoveFog","removeFog"] },
            GameName { english: "Dumb AI", arabic: "أعداء أغبياء", category: "هاكات", patterns: &["DumbAI","dumbAI","dumb_ai","DisableAI","disableAI","AIDisable","NoAI","noAI"] },
            GameName { english: "Unlock All", arabic: "فتح الكل", category: "هاكات", patterns: &["UnlockAll","unlockAll","unlock_all","UnlockEverything","IsUnlocked","isUnlocked","SetUnlocked"] },
            GameName { english: "Anti-Ban", arabic: "مضاد الحظر", category: "هاكات", patterns: &["AntiBan","antiBan","anti_ban","AntiCheatBypass","antiCheatBypass","BypassBan","bypassBan"] },
            GameName { english: "Free Shopping", arabic: "تسوق مجاني", category: "هاكات", patterns: &["FreeShopping","freeShopping","free_shopping","FreePurchase","freePurchase","NoCost","noCost","IsFree","isFree","ZeroCost","zeroCost"] },
            GameName { english: "No Ads", arabic: "بدون إعلانات", category: "هاكات", patterns: &["NoAds","noAds","no_ads","RemoveAds","removeAds","DisableAds","disableAds","AdFree","adFree","isAdFree","hasNoAds","LoadAd","ShowAd","showInterstitial","loadRewardedVideo"] },
            GameName { english: "Packet Injection", arabic: "حقن الحزم", category: "هاكات", patterns: &["PacketInjection","packetInjection","ModifyPacket","modifyPacket","InterceptPacket","interceptPacket"] },
            GameName { english: "Memory Freeze", arabic: "تجميد الذاكرة", category: "هاكات", patterns: &["FreezeValues","freezeValues","FreezeHP","freezeHP","FreezeCoins","freezeCoins"] },
            GameName { english: "HWID Spoofer", arabic: "تزييف الهوية", category: "هاكات", patterns: &["HWIDSpoofer","hwidSpoofer","SpoofHWID","spoofHWID","DeviceID","deviceID","FakeID","fakeID"] },
        ]
    }

    // ═══ Match a found string to a known name ═══
    pub fn match_string(found: &str) -> Option<GameName> {
        let found_lower = found.to_lowercase();
        for name in Self::all_names() {
            for pattern in name.patterns {
                if found_lower.contains(&pattern.to_lowercase()) {
                    return Some(name);
                }
            }
        }
        None
    }

    pub fn get_categories() -> Vec<String> {
        vec![
            "عملات".into(), "إحصائيات".into(), "هاكات".into(),
            "مفاتيح".into(), "صناديق".into(), "تذاكر".into(),
            "مواد".into(), "مستهلكات".into(),
        ]
    }
}
