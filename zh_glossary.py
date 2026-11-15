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
}
