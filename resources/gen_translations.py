#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Regenerate resources/translations.json from this authoritative source.

WHY: element/tool descriptions live in C++ files; typing their English text
again by hand risks key mismatch (=> silently unused translation). This script
reads the exact English `Description = "..."` from the source by identifier and
pairs it with the Chinese below, so every key is guaranteed to match.

Run:  python resources/gen_translations.py
"""
import glob, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # repo root
SRC = os.path.join(ROOT, "src")

# Menus and any fixed UI strings keyed by their exact English text.
FIXED = {
  "Walls": "墙体", "Electronics": "电子", "Powered Materials": "需电材料",
  "Sensors": "传感器", "Force": "力场", "Explosives": "爆炸物", "Gases": "气体",
  "Liquids": "液体", "Powders": "粉末", "Solids": "固体", "Radioactive": "放射性",
  "Special": "特殊", "Game Of Life": "生命游戏", "Tools": "工具",
  "Favorites": "收藏", "Decoration tools": "装饰工具",

  # Wall tool descriptions (LoadWalls)
  "Erases walls.": "擦除墙体。",
  "Blocks everything. Conductive.": "阻挡一切,导电。",
  "E-Wall. Becomes transparent when electricity is connected.": "E-Wall 电子墙。通电时变透明。",
  "Detector. Generates electricity when a particle is inside.": "探测器。粒子进入时产生电。",
  "Streamline. Creates a line that follows air movement.": "流线墙。沿气流方向形成流线。",
  "Fan. Accelerates air. Use the line tool to set direction and strength.": "风扇。加速空气,用直线工具设定方向与强度。",
  "Allows liquids, blocks all other particles. Conductive.": "只许液体通过,阻挡其他粒子,导电。",
  "Absorbs particles but lets air currents through.": "吸收粒子但让气流通过。",
  "Basic wall, blocks everything.": "基础墙,阻挡一切。",
  "Allows air, but blocks all particles.": "只许空气通过,阻挡所有粒子。",
  "Allows powders, blocks all other particles.": "只许粉末通过,阻挡其他粒子。",
  "Conductor. Allows all particles to pass through and conducts electricity.": "导体。允许所有粒子通过并导电。",
  "E-Hole. absorbs particles, releases them when powered.": "E-Hole 电子洞。吸收粒子,通电时释放。",
  "Allows gases, blocks all other particles.": "只许气体通过,阻挡其他粒子。",
  "Gravity wall. Newtonian Gravity has no effect inside a box drawn with this.": "重力墙。其内部牛顿引力无效。",
  "Allows energy particles, blocks all other particles.": "只许能量粒子通过,阻挡其他粒子。",
  "Allows all particles, but blocks air.": "允许所有粒子,但阻挡空气。",
  "Erases walls, particles, and signs.": "擦除墙体、粒子与标记。",
  "Freezes particles inside the wall in place until powered.": "使墙内粒子冻结在原处,直至通电。",

  # Decoration tool descriptions
  "Colour blending: Add.": "颜色混合:叠加(ADD)。",
  "Colour blending: Subtract.": "颜色混合:减去(SUB)。",
  "Colour blending: Multiply.": "颜色混合:相乘(MUL)。",
  "Colour blending: Divide.": "颜色混合:相除(DIV)。",
  "Smudge tool, blends surrounding deco together.": "涂抹工具,把周围的装饰混合在一起。",
  "Erase any set decoration.": "擦除任何已设置的装饰。",
  "Draw decoration (No blending).": "绘制装饰（不混合）。",

  # Wall type names (HUD / wall names)
  "ERASE": "橡皮擦",
  "CONDUCTIVE WALL": "导体墙",
  "EWALL": "电子墙",
  "DETECTOR": "探测器",
  "STREAMLINE": "流线墙",
  "FAN": "风扇",
  "LIQUID WALL": "液体墙",
  "ABSORB WALL": "吸收墙",
  "WALL": "普通墙",
  "AIRONLY WALL": "气孔墙",
  "POWDER WALL": "粉末墙",
  "CONDUCTOR": "导体",
  "EHOLE": "电子洞",
  "GAS WALL": "气体墙",
  "GRAVITY WALL": "重力墙",
  "ENERGY WALL": "能量墙",
  "AIRBLOCK WALL": "阻气墙",
  "ERASEALL": "全部擦除",
  "STASIS WALL": "停滞墙",

  # Game-of-Life type descriptions (rule codes kept)
  "Game Of Life: Begin 3/Stay 23": "生命游戏:出生(B)3/存活(S)23",
  "High Life: B36/S23": "高生命(High Life):B36/S23",
  "Assimilation: B345/S4567": "同化(Assimilation):B345/S4567",
  "2X2: B36/S125": "2X2:B36/S125",
  "Day and Night: B3678/S34678": "昼夜(Day and Night):B3678/S34678",
  "Amoeba: B357/S1358": "变形虫(Amoeba):B357/S1358",
  "'Move' particles. Does not move things.. it is a life type: B368/S245": "移动(Move)粒子。它并不移动物体,只是一种生命类型:B368/S245",
  "Pseudo Life: B357/S238": "伪生命(Pseudo Life):B357/S238",
  "Diamoeba: B35678/S5678": "迪阿莫巴(Diamoeba):B35678/S5678",
  "3-4: B34/S34": "3-4:B34/S34",
  "Long Life: B345/S5": "长生命(Long Life):B345/S5",
  "Stains: B3678/S235678": "污渍(Stains):B3678/S235678",
  "Seeds: B2/S": "种子(Seeds):B2/S",
  "Maze: B3/S12345": "迷宫(Maze):B3/S12345",
  "Coagulations: B378/S235678": "凝固(Coagulations):B378/S235678",
  "Walled cities: B45678/S2345": "围城(Walled cities):B45678/S2345",
  "Gnarl: B1/S1": "节瘤(Gnarl):B1/S1",
  "Replicator: B1357/S1357": "复制者(Replicator):B1357/S1357",
  "Mystery: B3458/S05678": "谜(Mystery):B3458/S05678",
  "Living on the Edge: B37/S3458/4": "边缘生命(Living on the Edge):B37/S3458/4",
  "Like Frogs rule: B3/S124/3": "类青蛙规则(Like Frogs rule):B3/S124/3",
  "Like Star Wars rule: B278/S3456/6": "类星球大战规则(Like Star Wars rule):B278/S3456/6",
  "Frogs: B34/S12/3": "青蛙(Frogs):B34/S12/3",
  "Brian 6: B246/S6/3": "布莱恩6(Brian 6):B246/S6/3",
}

# Element identifier -> Simplified Chinese description
ELEMENT_ZH = {
  "ACEL": "加速器。使附近的元素加速运动。",
  "ACID": "几乎能溶解一切物质。",
  "AMTR": "反物质。摧毁绝大多数粒子。",
  "ANAR": "反空气尘。极轻且不受重力影响。燃烧时产生的是冷而非热。",
  "ARAY": "射线发射器。射线碰撞处会产生光点。",
  "BANG": "TNT。一次性全部爆炸。",
  "BASE": "腐蚀性液体。使导电固体生锈,可中和酸。",
  "BCLN": "可破碎的克隆。",
  "BCOL": "碎煤。较重的颗粒,燃烧缓慢。",
  "BGLA": "碎玻璃。玻璃受压碎裂形成的较重颗粒,可熔化。",
  "BHOL": "真空。吸入其他粒子并升温。",
  "BIZR": "奇异物质,行为违背常规相变规律,还会用其装饰色给其他元素上色。",
  "BIZRG": "奇异气体。",
  "BIZRS": "奇异固体。",
  "BMTL": "可破碎金属。常用导电建材,可熔化并受压破碎。",
  "BOMB": "炸弹。触碰到物体时爆炸并摧毁周围粒子。",
  "BOYL": "玻义耳气体。压强可变,受热膨胀。",
  "BRAY": "射线点。射线碰撞处会产生光点。",
  "BRCK": "砖块。可破碎的建筑材料。",
  "BREC": "损坏的电子元件。由电磁脉冲爆炸产生;持续被电击且受压时会转化为奇异物质(EXOT)。",
  "BRMT": "损坏金属。铁生锈或金属受压碎裂时产生。",
  "BTRY": "电池。产生无限电能。",
  "BVBR": "损坏的振金。",
  "C5": "冷炸药。任何低温都会引爆它。",
  "CAUS": "腐蚀性气体。作用同 ACID(酸)。",
  "CBNW": "碳酸水。缓慢释放二氧化碳(CO2)。",
  "CFLM": "零下火焰。",
  "CLNE": "克隆。复制它接触到的任何粒子。",
  "CLST": "黏土粉。与水混合会产生糊状物(PSTE)。",
  "CNCT": "混凝土。可堆叠在自身或 ROCK 上,受压坍塌。",
  "CO2": "二氧化碳。较重的气体,向下飘。使水碳酸化,遇冷变成干冰。",
  "COAL": "煤炭。燃烧很慢,受热会变红。",
  "CONV": "转换器。把一切转化为它首次接触到的物质。",
  "CRAY": "粒子射线发射器。发射由 ctype 指定的粒子束,射程由 tmp 决定。",
  "CRMC": "陶瓷。受压时变得更坚固。",
  "DCEL": "减速器。使附近的元素减速。",
  "DESL": "液态柴油。在高压与高温下爆炸。",
  "DEST": "更强力的炸弹。几乎能炸穿任何东西。",
  "DEUT": "氧化氘(重水)。低温下更浓缩,遇中子或质子即爆炸。",
  "DLAY": "温控延迟导体(用 HEAT/COOL 控制)。",
  "DMG": "产生破坏性压力,击碎所触及的元素。",
  "DMND": "钻石。不可摧毁。",
  "DRAY": "复制射线。在其前方复制一排粒子。",
  "DRIC": "干冰。CO2 冷却后形成。",
  "DSTW": "蒸馏水。不导电。",
  "DTEC": "探测器。当附近有与其 ctype 匹配的物质时产生电火花。",
  "DUST": "极轻的尘埃,易燃。",
  "DYST": "死亡酵母。",
  "E116": "一次失败的同速测试。",
  "ELEC": "电子。激发电子元件,与 NEUT 和 WATR 反应。",
  "EMBR": "火花。由爆炸产生。",
  "EMP": "电磁脉冲。摧毁已激活的电子元件。",
  "ETRD": "电极。用电产生等离子电弧(请谨慎使用)。",
  "EXOT": "奇异物质。接触过量电子会爆炸,还有许多奇特反应。",
  "FIGH": "斗士。试图击杀小人,需先给它一种元素作为武器。",
  "FILT": "滤光器。改变 PHOT 与 BIZR 的颜色,颜色随温度变化。",
  "FIRE": "点燃易燃物,并使空气升温。",
  "FIRW": "烟花!五彩缤纷,遇火点燃。",
  "FOG": "雾。电流通过 RIME(霜)时产生。",
  "FRAY": "力场发射器。依自身温度推或拉物体,用法同 ARAY。",
  "FRME": "框架。可与活塞配合推动大量粒子。",
  "FRZW": "冻水。Freeze 粉末熔化形成的混合液体。",
  "FRZZ": "Freeze 粉末。熔化后形成持续降温的冰,可随普通水蔓延。",
  "FSEP": "Fuse 粉末。像 FUSE 一样缓慢燃烧。",
  "FUSE": "缓慢燃烧。极高温度或被电击时点燃。",
  "FWRK": "烟花原版。由热量或中子触发。",
  "GAS": "气体。扩散快且易燃,受压液化成油(OIL)。",
  "GBMB": "重力炸弹。粘住首个接触物后产生强重力推斥。",
  "GEL": "凝胶。黏度与导热性可变的液体,会吸水。",
  "GLAS": "玻璃。可熔化。受压碎裂,折射光子。",
  "GLOW": "荧光。受压发光。",
  "GOLD": "金。耐腐蚀金属,可逆转铁的生锈,是优良导体。",
  "GOO": "软泥。受压变形并消失。",
  "GPMP": "重力泵。激活后把重力改变为与其温度对应(用 HEAT/COOL)。",
  "GRAV": "极轻尘埃。颜色随速度变化。",
  "GRVT": "引力子。产生牛顿引力。",
  "GUNP": "火药。轻尘,遇火或火花即爆。",
  "H2": "氢。与 OXYG 燃烧生成 WATR,高温高压下发生聚变。",
  "HEAC": "快速导热体。",
  "HSWC": "热开关。仅在激活时导热。",
  "ICEI": "冰。受压碎裂,使空气降温。",
  "IGNT": "引燃绳。遇火与火花缓慢燃烧。",
  "INSL": "绝缘体。隔绝热、电与辐射。",
  "INST": "瞬时导体。PSCN 充电,NSCN 放电。",
  "INVIS": "隐形墙。受压时隐形,允许粒子穿过。",
  "INWR": "绝缘导线。只向 PSCN、NSCN、WIFI 与 SWCH 导电。",
  "IRON": "铁。遇盐生锈,可用于电解 WATR(水)。",
  "ISOZ": "同位素 Z。放射性液体,接触 PHOT 或处于负压时衰变为光子。",
  "ISZS": "同位素 Z 的固态,缓慢衰变为 PHOT。",
  "LAVA": "熔岩。可点燃易燃物。金属等物质熔化时生成,冷却后凝固。",
  "LCRY": "液晶。带电时变色(PSCN 充电,NSCN 放电)。",
  "LDTC": "线性探测器。朝 8 个方向扫描与其 ctype 匹配的粒子,并在对侧产生火花。",
  "LIFE": "生命游戏!B3/S23",
  "LIGH": "闪电。用笔刷大小设定闪电尺寸。",
  "LITH": "锂。活泼元素,遇水爆炸。",
  "LNTG": "液氮。极冷,接触任何较暖物体即消失。",
  "LO2": "液氧。极冷,遇火反应。",
  "LOLZ": "哈哈(玩笑元素)。",
  "LOVE": "爱,一种抽象的情感。",
  "LRBD": "液态铷。",
  "LSNS": "生命传感器。附近存在 life 高于其温度的粒子时产生火花。",
  "MERC": "汞。体积随温度变化,导电。",
  "METL": "金属。基础导体,可熔化。",
  "MORT": "蒸汽火车。",
  "MWAX": "液态蜡。45 度时凝固成 WAX(蜡)。",
  "NBHL": "黑洞。借引力吸入粒子(需开启牛顿引力)。",
  "NBLE": "稀有气体。被电击时电离成等离子体,会扩散。",
  "NEUT": "中子。与物质以奇特方式相互作用。",
  "NICE": "氮冰。极冷,略微受热即熔化为液氮(LN2)。",
  "NITR": "硝化甘油。对压力敏感的炸药。与 CLST 混合可制成 TNT。",
  "NONE": "擦除粒子。",
  "NSCN": "N 型硅。不向 P 型硅(PSCN)传导电流,可关闭需电材料。",
  "NTCT": "NTC 热敏电阻。与 PSCN/NSCN 导通,但仅在加热到 100℃ 以上时。",
  "NWHL": "白洞。借引力推开其他粒子(需开启牛顿引力)。",
  "O2": "氧气。极易点燃。",
  "OIL": "易燃。在低压或高温下转化为气体(GAS)。",
  "PBCN": "需电的可破碎克隆。",
  "PCLN": "需电克隆。激活后复制它接触到的任何粒子。",
  "PHOT": "光子。穿过玻璃时折射,不同元素会改变其颜色,可点燃易燃物。",
  "PIPE": "管道。搬运粒子。BRCK(砖)生成后,挖掉一部分作为出口,PIPE 便可使用。",
  "PLEX": "固态压敏炸药。",
  "PLNT": "植物。吸收水分生长。",
  "PLSM": "等离子体。极热。",
  "PLUT": "钚。重的可裂变粒子,受压产生中子。",
  "POLO": "钋。强放射性,衰变为 NEUT 并发热。",
  "PPIP": "PIPE 的需电版。用 PSCN/NSCN 激活或停用。",
  "PQRT": "石英粉。QRTZ(石英)的破碎形态。",
  "PROT": "质子。向材料传热并消除火花。",
  "PRTI": "传送门入口。粒子从此进入,亦具随温度变化的信道(同 WIFI)。",
  "PRTO": "传送门出口。粒子从此出来,亦具随温度变化的信道(同 WIFI)。",
  "PSCN": "P 型硅。向任意导体传导电流,可激活需电材料。",
  "PSNS": "压力传感器。当压力大于其温度时产生火花。",
  "PSTE": "糊状胶体。受压变硬。",
  "PSTN": "活塞。推动粒子。PSCN 伸出,NSCN 缩回。",
  "PSTS": "PSTE(糊状胶体)的固态。",
  "PTCT": "PTC 热敏电阻。与 PSCN/NSCN 导通,但仅在冷却到 100℃ 以下时。",
  "PTNM": "铂。催化某些反应。",
  "PUMP": "压力泵。激活后把压力改变为与其温度对应(用 HEAT/COOL)。",
  "PVOD": "需电虚空(VOID)。激活时摧毁进入的粒子。",
  "QRTZ": "石英。可破碎矿物。导电,但遇冷变脆,会散射光子。",
  "RBDM": "铷。易爆,尤其遇水。熔点低。",
  "RFGL": "液态制冷剂。",
  "RFRG": "制冷剂。受压升温并液化。",
  "RIME": "霜。水蒸气急速冷却时凝华生成,跳过液相。",
  "ROCK": "岩石。固体,熔化成多种元素。",
  "RPEL": "依温度排斥或吸引粒子。",
  "RSSS": "凝固的抗蚀剂。阻挡压力并绝缘,接触中子会液化。",
  "RSST": "抗蚀剂。接触光子会凝固,被电子与火花摧毁。",
  "SALT": "盐。溶于水。",
  "SAND": "沙。较重的颗粒,熔化后成为玻璃。",
  "SAWD": "锯末。漂浮在水上。",
  "SEED": "种子。种在沙上并加水即可长成树。",
  "SHLD1": "护盾。围绕火花生长,受压破碎。",
  "SHLD2": "2 级护盾。",
  "SHLD3": "3 级护盾。",
  "SHLD4": "4 级护盾。",
  "SING": "奇点。产生巨大负压并摧毁一切。",
  "SLCN": "硅粉。制造多种材料的关键原料。",
  "SLTW": "盐水。导电,难以冻结。",
  "SMKE": "烟。由火产生。",
  "SNOW": "雪花。轻颗粒,由 ICE(冰)受压碎裂产生。",
  "SOAP": "肥皂。产生气泡,可洗去装饰色并治愈病毒。",
  "SPAWN": "小人(STKM)出生点。",
  "SPAWN2": "小人 2(STK2)出生点。",
  "SPNG": "海绵。吸水,不是可移动固体。",
  "SPRK": "电流。TPT 中一切电子元件的基础,沿导电元素传播。",
  "STKM": "小人。别杀他!用方向键控制。",
  "STKM2": "第二个小人。别杀他!用 WASD 控制。",
  "STNE": "石头。较重的颗粒,可熔化。",
  "STOR": "存储。捕获并保存单个粒子,由 PSCN 充电时释放,亦可传给 PIPE。",
  "SWCH": "开关。仅在开启时导电(PSCN 开,NSCN 关)。",
  "TESC": "特斯拉线圈!被电击时产生闪电。",
  "THDR": "闪电!极热,对多数材料造成伤害,并向金属传导电流。",
  "THRM": "铝热剂。燃烧成极热的熔融金属。",
  "TRON": "智能粒子。沿直线行进并避障,随时间增长。",
  "TSNS": "温度传感器。附近存在温度更高的粒子时产生火花。",
  "TTAN": "钛。熔点高于多数金属,可阻挡全部空气压力。",
  "TUNG": "钨。熔点极高的脆性金属。",
  "URAN": "铀。重颗粒,受压产热。",
  "VIBR": "振金。储存能量并以猛烈爆炸释放。",
  "VINE": "藤蔓。可沿 WOOD(木头)生长。",
  "VIRS": "病毒。把接触的一切转化为病毒。",
  "VOID": "虚空。排走任何粒子。",
  "VRSG": "气体病毒。把接触的一切转化为病毒。",
  "VRSS": "固体病毒。把接触的一切转化为病毒。",
  "VSNS": "速度传感器。附近存在速度高于其温度的粒子时产生火花。",
  "WARP": "使其他元素位移。",
  "WATR": "水。可导电、会结冰,并能灭火。",
  "WAX": "蜡。易燃,在较高温度下熔化。",
  "WHOL": "排气口。产生压力并推开其他粒子。",
  "WIFI": "无线发射器。把电流传给同温度信道上的其他WIFI。（TPT 以温度值充当频道号）",
  "WIRE": "WireWorld 导线。按类生命游戏的规则导电。",
  "WOOD": "木头,易燃。",
  "WTRV": "水蒸气。由热水产生。",
  "YEST": "酵母。温暖(约37°C)时生长。",
}

TOOL_ZH = {
  "AIR": "风。制造气流与气压。",
  "AMBM": "降低环境气温。",
  "AMBP": "升高环境气温。",
  "COOL": "冷却目标元素。",
  "CYCL": "旋风。产生旋转气流。",
  "HEAT": "加热目标元素。",
  "MIX": "混合粒子。",
  "NGRV": "短暂制造负引力场。",
  "PGRV": "短暂制造引力场。",
  "VAC": "真空。降低气压。",
  "WIND": "制造空气流动。",
}

# Half-width punctuation inside Chinese -> full width; ℃ -> °C (font lacks ℃ but has °).
ASCII2FULL = {
    ",": "，", "!": "！", "?": "？", ";": "；", ":": "：",
    "(": "（", ")": "）", "[": "【", "]": "】", "~": "～",
}

def zh_norm(s):
    s = s.replace("℃", "°C")
    return "".join(ASCII2FULL.get(ch, ch) for ch in s)

GLOSS = {}
_gloss_path = os.path.join(ROOT, "resources", "glossary.json")
if os.path.isfile(_gloss_path):
    _gd = json.load(open(_gloss_path, encoding="utf-8"))
    for _code, _obj in _gd.items():
        if isinstance(_obj, dict) and isinstance(_obj.get("zh"), str):
            GLOSS[_code] = _obj["zh"]


def gloss_crossref(s):
    """Replace bare element codes (outside full-width parentheses) with 中文（CODE）.
    If a code is immediately followed by a （中文） annotation, that annotation is
    dropped and the code is glossed instead (avoids 中文（CODE）（中文） redundancy)."""
    out = []
    depth = 0
    i, n = 0, len(s)
    while i < n:
        c = s[i]
        if c == "（":
            depth += 1
            out.append(c)
            i += 1
        elif c == "）":
            depth = max(0, depth - 1)
            out.append(c)
            i += 1
        elif ("A" <= c <= "Z" or "0" <= c <= "9") and depth == 0:
            j = i
            while j < n and ("A" <= s[j] <= "Z" or "0" <= s[j] <= "9"):
                j += 1
            tok = s[i:j]
            if len(tok) >= 2 and tok in GLOSS:
                k = j
                if k < n and s[k] == "（":
                    # drop the trailing full-width parenthesised annotation
                    e = k + 1
                    dd = 1
                    while e < n and dd > 0:
                        if s[e] == "（":
                            dd += 1
                        elif s[e] == "）":
                            dd -= 1
                        e += 1
                    j = e
                out.append(GLOSS[tok] + "（" + tok + "）")
            else:
                out.append(tok)
            i = j
        else:
            out.append(c)
            i += 1
    return "".join(out)

def grab(field, text):
    m = re.search(field + r'\s*=\s*"((?:[^"\\]|\\.)*)"', text)
    return m.group(1) if m else None

def main():
    out = dict(FIXED)
    missing = []

    elem_dir = os.path.join(SRC, "simulation", "elements")
    for path in sorted(glob.glob(os.path.join(elem_dir, "*.cpp"))):
        ident = os.path.basename(path)[:-4]
        if ident not in ELEMENT_ZH:
            missing.append("ELEMENT " + ident + " (no zh)")
            continue
        text = open(path, encoding="utf-8").read()
        en = grab("Description", text)
        if en is None:
            missing.append("ELEMENT " + ident + " (no English description found)")
            continue
        out[en] = ELEMENT_ZH[ident]

    tool_dir = os.path.join(SRC, "simulation", "simtools")
    for path in sorted(glob.glob(os.path.join(tool_dir, "*.cpp"))):
        ident = os.path.basename(path)[:-4]
        if ident not in TOOL_ZH:
            continue
        text = open(path, encoding="utf-8").read()
        en = grab("Description", text)
        if en:
            out[en] = TOOL_ZH[ident]

    out = {k: gloss_crossref(zh_norm(v)) for k, v in out.items()}
    out_path = os.path.join(ROOT, "resources", "translations.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("wrote", out_path, "entries:", len(out))
    if missing:
        print("MISSING zh for:")
        for m in missing:
            print(" -", m)
    else:
        print("all element identifiers covered")

if __name__ == "__main__":
    main()
