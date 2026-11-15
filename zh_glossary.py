"""App 中文版的武器／裝備名 → 英文名（資料庫只有英文）。官方沒有中英對照的來源，這份是照意思對、再跟該單位資料卡上的武器清單核對過的。
沒在這裡的中文武器名，程式會在註記裡列出來，並記到 unknown_zh.txt，之後再補。
2026-11-15：使用者貼的禁軍表。"""
WEAPONS = {
    '守望者之斧': "Watcher's Axe",
    '雄鹰之啸': "Eagle's Scream",
    '卫戍盾': 'Praesidium Shield',
    '哨戒之刃': 'Sentinel Blade',
    '旗徽': 'Vexilla',
    '枪托': 'Gun Stock',
    '爆矢枪': 'Boltgun',
    '火焰喷射器': 'Flamer',
    '双联中子级联投射器': 'Twin Neutronium Cascade Projectors',
    '双重拳套': 'Dual Caestus Fists',
    '斯皮库鲁斯型爆矢发射器': 'Spiculus Bolt Launcher',
    '战刃': 'Warblade',
    '守护之矛': 'Guardian Spear',
    '强弩榴弹发射器': 'Balistus Grenade Launcher',
    # 2026-11-15 下午：使用者貼的極限戰士表（App 匯出「(180点)」沒空格那版），逐一對過資料卡武器清單
    '奥特拉玛臂铠': 'Gauntlets of Ultramar',
    '大师级动力武器': 'Master-crafted Power Weapon',
    '重型爆矢手枪': 'Heavy Bolt Pistol',
    '爆矢步枪': 'Bolt Rifle',
    '陶钢铁拳': 'Ceramite Fists',
    '动力武器': 'Power Weapon',
    '远古科技激光手枪': 'Archeotech Laspistol',
    '星语爆炸': 'Astropathic Blast',
    '灵能法杖': 'Force Stave',
    '奥特拉玛格斗武器': 'Ultramarian Combat Weapons',
    '大师级动力剑': 'Master-crafted Power Sword',
    '等离子手枪': 'Plasma Pistol',
    '帝皇之剑': "Emperor's Sword",
    '统御之手': 'Hand of Dominion',
    '装甲外壳': 'Armoured Hull',
    '铁雨重机枪': 'Ironhail Heavy Stubber',
    '风暴爆矢枪': 'Storm Bolter',
    '战斗刀': 'Combat Knife',
    '爆矢手枪': 'Bolt Pistol',
    '狙击步枪': 'Sniper Rifle',
    '链锯剑': 'Chainsword',
    '单分子战斗刀': 'Monomolecular Combat Knife',
    '爆矢卡宾枪': 'Bolt Carbine',
    '特制爆矢手枪': 'Special-issue Bolt Pistol',
    '救赎者铁拳': 'Redemptor Fist',
    '破片风暴榴弹发射器': 'Fragstorm Grenade Launcher',
    '重型火焰喷射器': 'Heavy Flamer',
    '伊卡洛斯火箭巢': 'Icarus Rocket Pod',
    '动力拳': 'Power Fist',
    '雷霆锤': 'Thunder Hammer',
    '热熔步枪': 'Melta Rifle',
    '导弹发射器': 'Missile Launcher',          # 官方點數頁的「导弹发射器」是終結者的 Cyclone，兩個都會試
    # 不是武器的裝備（對到英文就不會被當成「沒有對照」，但也不算傷害）
    '风暴盾': 'Storm Shield',
    '穹顶护盾': 'Shield Dome',
}

# 模型名（中文 → 資料卡上的模型名）。對不到時程式用資料卡第一個模型。
MODELS = {
    '老兵军士梅陶露斯': 'Veteran Sergeant Metaurus',
    '旗手加德里尔': 'Ancient Gadriel',
    '盖乌斯·席尔瓦': 'Gaius Silva',
    '丹尼尔·科内留斯': 'Dainal Komelius',
    '埃米莉亚·密涅瓦斯': 'Aemelia Minervas',
    '露西娅·维萨': 'Lucia Vestha',
    '剑卫老兵军士': 'Bladeguard Veteran Sergeant',
    '剑卫老兵': 'Bladeguard Veteran',
    '侦察兵军士': 'Scout Sergeant',
    '侦察兵': 'Scout',
    '掠夺者军士': 'Reiver Sergeant',
    '掠夺者': 'Reiver',
    '根除者军士': 'Eradicator Sergeant',
    '根除者': 'Eradicator',
}

# 2026-11-15 傍晚（使用者要「補常見陣營的中文武器名」）：沒有官方中英對照，逐一列不完，
# 改成「拆字對照」：把中文武器名拆成常見字詞（爆矢＝bolt、手枪＝pistol…），再跟「這張資料卡上」的英文武器逐一比，
# 只在一張卡的幾把武器之間挑最像的，而且要明顯勝出才採用；採用的會在網頁註記標「推測」。
# 值的寫法：「/」分開的是可以互換的英文，空格連起來的是一整個詞組（要整組都在才算）。
MORPH = {
    '远古科技': 'archeotech', '手持': 'hand', '爆矢枪': 'boltgun/bolter', '陶钢': 'ceramite', '救赎者': 'redemptor',
    '装甲': 'armoured', '外壳': 'hull', '盾牌': 'shield', '单分子': 'monomolecular', '大师级': 'master crafted', '特制': 'special issue',
    '火焰喷射器': 'flamer', '喷火器': 'flamer', '卡宾枪': 'carbine', '霰弹枪': 'shotgun', '自动炮': 'autocannon',
    '加农炮': 'cannon', '重机枪': 'heavy stubber', '机枪': 'stubber', '发射器': 'launcher', '发射架': 'launcher',
    '格斗武器': 'combat weapon', '近战武器': 'close combat weapon', '加特林': 'gatling', '迫击炮': 'mortar',
    '爆矢': 'bolt', '手枪': 'pistol', '步枪': 'rifle', '重型': 'heavy', '双联': 'twin', '动力': 'power',
    '等离子': 'plasma', '热熔': 'melta', '多管': 'multi', '激光': 'las/laser', '导弹': 'missile', '榴弹': 'grenade',
    '破片': 'frag', '穿甲': 'krak', '狙击': 'sniper', '突击': 'assault', '战斗': 'combat/battle', '风暴': 'storm',
    '旋风': 'cyclone', '飓风': 'hurricane', '雷霆': 'thunder', '闪电': 'lightning', '链锯': 'chain', '灵能': 'force/psychic',
    '法杖': 'stave/staff', '火箭': 'rocket', '焚化': 'incinerator', '巨型': 'macro', '铁雨': 'ironhail',
    '伊卡洛斯': 'icarus', '死神': 'reaper', '收割者': 'reaper', '幽冥': 'wraith', '光矛': 'lance', '光束': 'beam',
    '离子': 'ion', '脉冲': 'pulse', '磁轨': 'rail', '轨道': 'rail', '高斯': 'gauss', '特斯拉': 'tesla', '粒子': 'particle',
    '毁灭者': 'destroyer', '破坏者': 'demolisher', '净化': 'purgation', '辐射': 'radium', '电弧': 'arc', '虚空': 'void',
    '臂铠': 'gauntlets', '拳套': 'gauntlet', '铁拳': 'fist', '爪': 'claw/claws', '锤': 'hammer', '剑': 'sword',
    '刃': 'blade', '斧': 'axe', '矛': 'spear', '戟': 'halberd', '鞭': 'whip', '镰': 'scythe', '刀': 'knife',
    '匕首': 'knife/dagger', '拳': 'fist', '锯': 'saw', '钻': 'drill', '弩': 'crossbow', '弓': 'bow', '盾': 'shield',
    '炮': 'cannon', '枪': 'gun', '舱': 'pod', '巢': 'pod', '军士': 'sergeant', '冠军': 'champion', '老兵': 'veteran',
    '武器': 'weapon/weapons', '链': 'chain', '毒': 'toxin/poison', '尖刺': 'spike', '刺': 'stinger/spike',
}
