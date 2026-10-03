from pathlib import Path
from fontTools import subset
from fontTools.ttLib import TTFont
R=Path(__file__).resolve().parent.parent
font=TTFont('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',fontNumber=1)
options=subset.Options();options.set(flavor='woff',name_IDs=['*'],name_languages=['*']);s=subset.Subsetter(options=options)
chars=set()
for a,b in [(0x20,0x100),(0x1100,0x1200),(0x2000,0x2070),(0x2190,0x2300),(0x3000,0x3040),(0x3130,0x3190),(0xAC00,0xD7A4)]:chars.update(range(a,b))
s.populate(unicodes=chars);s.subset(font);font.flavor='woff';dest=R/'study/noto-study.woff';font.save(dest)
cmap=font.getBestCmap();assert cmap is not None;assert all(x in cmap for x in range(0xAC00,0xD7A4));print({'font':dest.name,'bytes':dest.stat().st_size,'full_hangul_syllables':True})
