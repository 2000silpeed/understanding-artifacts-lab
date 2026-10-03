// Positions computed from canonical educational data-model.js, not empirical measurements.
const aggregate=[[516,765.8,"blue"],[558.5494505494506,695.710085054678,"blue"],[606.4175824175825,738.3735115431348,"blue"],[648.967032967033,683.5205346294046,"blue"],[542.5934065934066,720.0891859052247,"blue"],[670.2417582417584,750.5630619684082,"blue"],[651.6263736263736,695.9132442284325,"teal"],[694.1758241758242,625.8233292831105,"teal"],[742.0439560439561,668.4867557715673,"teal"],[784.5934065934066,613.6337788578371,"teal"],[678.2197802197802,650.2024301336573,"teal"],[805.868131868132,680.6763061968408,"teal"],[787.2527472527472,626.0264884568651,"yellow"],[829.802197802198,555.936573511543,"yellow"],[877.6703296703298,598.5999999999999,"yellow"],[920.2197802197803,543.7470230862698,"yellow"],[813.8461538461539,580.3156743620898,"yellow"],[941.4945054945056,610.7895504252733,"yellow"],[922.8791208791208,556.1397326852975,"green"],[965.4285714285714,486.04981773997565,"green"],[1013.2967032967034,528.7132442284326,"green"],[1055.846153846154,473.86026731470236,"green"],[949.4725274725276,510.4289185905224,"green"],[1077.1208791208792,540.9027946537059,"green"],[1058.5054945054949,486.25297691373015,"purple"],[1101.054945054945,416.1630619684082,"purple"],[1148.9230769230771,458.82648845686504,"purple"],[1191.4725274725279,403.97351154313475,"purple"],[1085.0989010989013,440.542162818955,"purple"],[1212.747252747253,471.01603888213845,"purple"],[1194.1318681318685,416.3662211421627,"pink"],[1236.6813186813188,346.2763061968408,"pink"],[1284.5494505494507,388.9397326852976,"pink"],[1327.0989010989015,334.08675577156737,"pink"],[1220.725274725275,370.6554070473875,"pink"],[1348.3736263736268,401.1292831105709,"pink"],[1329.758241758242,346.47946537059534,"orange"],[1372.3076923076922,276.38955042527334,"orange"],[1420.1758241758243,319.0529769137302,"orange"],[1462.725274725275,264.19999999999993,"orange"],[1356.3516483516485,300.76865127582005,"orange"],[1484,331.2425273390036,"orange"]];
const groupAggregate=[[302.4,677.2,"blue"],[323.2879120879121,630.473390036452,"blue"],[346.7868131868132,658.9156743620899,"blue"],[367.6747252747253,622.3470230862697,"blue"],[315.45494505494503,646.7261239368165,"blue"],[378.11868131868135,667.0420413122722,"blue"],[368.9802197802198,630.6088294856218,"teal"],[389.86813186813185,583.8822195220737,"teal"],[413.36703296703297,612.3245038477116,"teal"],[434.25494505494504,575.7558525718914,"teal"],[382.03516483516484,600.1349534224382,"teal"],[444.6989010989011,620.4508707978939,"teal"],[435.5604395604396,584.0176589712433,"yellow"],[456.4483516483517,537.2910490076954,"yellow"],[479.94725274725283,565.7333333333332,"yellow"],[500.83516483516485,529.1646820575131,"yellow"],[448.61538461538464,553.5437829080599,"yellow"],[511.2791208791209,573.8597002835155,"yellow"],[502.14065934065934,537.4264884568651,"green"],[523.0285714285715,490.6998784933171,"green"],[546.5274725274726,519.1421628189551,"green"],[567.4153846153847,482.5735115431349,"green"],[515.1956043956045,506.95261239368165,"green"],[577.8593406593407,527.2685297691373,"green"],[568.7208791208793,490.83531794248677,"purple"],[589.6087912087912,444.1087079789388,"purple"],[613.1076923076923,472.5509923045767,"purple"],[633.9956043956045,435.9823410287565,"purple"],[581.7758241758243,460.36144187930336,"purple"],[644.4395604395605,480.677359254759,"purple"],[635.3010989010991,444.2441474281085,"pink"],[656.189010989011,397.5175374645605,"pink"],[679.6879120879122,425.9598217901984,"pink"],[700.5758241758243,389.39117051437825,"pink"],[648.356043956044,413.77027136492495,"pink"],[711.0197802197804,434.08618874038063,"pink"],[701.8813186813188,397.6529769137302,"orange"],[722.7692307692307,350.9263669501822,"orange"],[746.2681318681321,379.3686512758201,"orange"],[767.1560439560441,342.79999999999995,"orange"],[714.9362637362638,367.1791008505467,"orange"],[777.5999999999999,387.49501822600234,"orange"]];
const group22=[[1402.1406593406593,537.4264884568651,"yellow"],[1423.0285714285715,490.6998784933171,"yellow"],[1446.5274725274726,519.1421628189551,"yellow"],[1467.4153846153847,482.5735115431349,"yellow"],[1415.1956043956045,506.95261239368165,"yellow"],[1477.8593406593407,527.2685297691373,"yellow"]];
const intervention=[[486,863.8,"teal"],[647.3333333333334,661.3999999999999,"teal"],[808.6666666666667,784.6,"teal"],[970,626.1999999999999,"teal"],[1131.3333333333335,731.8,"teal"],[1292.6666666666667,819.8,"teal"],[1454,863.8,"teal"]];
function plus(at, seconds) {
  return typeof at === 'string' ? at : at + seconds;
}

function axes(s, x = 450, y = 230, w = 1100, h = 570, at = 0.2, labels = true) {
  s.line([[x, y + h], [x + w, y + h]], { at, color: 'muted', width: 5 });
  s.line([[x, y + h], [x, y]], { at, color: 'muted', width: 5 });
  if (labels) {
    s.text('아이스크림 판매량', { x: x + w / 2, y: y + h + 58, size: 34, align: 'center', at: plus(at, 0.15), color: 'muted' });
    s.text('수영·사고위험 대표값', { x: x - 32, y: y + h / 2, size: 30, align: 'right', at: plus(at, 0.2), color: 'muted' });
  }
}
function dots(s, points, at, step = 0.08, radius = 14) {
  points.forEach(([x, y, color], i) => s.circle({ x, y, r: radius, color, at: typeof at === 'number' ? at + i * step : `${at}`, sfx: false }));
}
function chart(s, title, points, at, opts = {}) {
  s.box(title, { x: 980, y: 135, w: opts.w || 1250, h: opts.h || 760, color: opts.color || 'blue', at, size: 34 });
  axes(s, 480, 240, 1050, 520, at + 0.2);
  dots(s, points, at + 0.4, 0.06, opts.radius || 13);
}

export default {
  hook(s) {
    s.title('상관관계 ≠ 인과관계', { at: 0.1 });
    s.subtitle('A synthetic case about ice cream, temperature, and pool visits', { at: 0.5, size: 34 });
    s.box('아이스크림 판매 X', { id: 'ice', x: 560, y: 570, w: 420, icon: 'ice-cream-bowl', color: 'blue', at: '#question', size: 38 });
    s.box('수영·사고위험 대표값 Y', { id: 'pool', x: 1370, y: 570, w: 520, icon: 'waves', color: 'green', at: '#question', size: 34 });
    s.arrow('ice', 'pool', { at: '#question', dashed: true, color: 'muted', width: 4 });
    s.text('함께 움직인다고 원인은 아니다', { y: 960, size: 48, align: 'center', at: '#question', color: 'red' });
    s.note('illustrative synthetic data', { y: 1000, at: 1.5, color: 'muted' });
  },
  pattern(s) {
    s.text('전체 온도를 섞으면', { x: 960, y: 100, size: 62, font: 'display', align: 'center', at: 0.1 });
    s.text('관찰된 점들의 상승 패턴', { x: 980, y: 190, size: 32, align: 'center', at: '#mix', color: 'muted' });
    axes(s, 450, 230, 1100, 540, '#mix');
    dots(s, aggregate, '#pattern', 0.07, 15);
    s.annotate({ x: 780, y: 250, w: 760, h: 560 }, { type: 'bracket', color: 'red', at: '#pattern' });
    s.text('높은 상관처럼 보임', { x: 1130, y: 300, size: 42, align: 'center', at: '#pattern', color: 'red' });
    s.note('색은 서로 다른 기온 그룹을 뜻함', { x: 970, y: 900, at: 6.5, color: 'muted' });
    s.text('색 그룹을 분리해 읽기', { x: 980, y: 950, size: 34, align: 'center', at: 5.5, color: 'teal' });
  },
  dag(s) {
    s.text('공통 원인을 먼저 묻기', { x: 960, y: 100, size: 62, font: 'display', align: 'center', at: 0.1 });
    s.circle({ id: 'temp', x: 980, y: 310, r: 105, label: 'T\n기온', color: 'yellow', at: '#common', labelSize: 38 });
    s.box('아이스크림 판매 X', { id: 'x', x: 520, y: 680, w: 420, color: 'blue', at: '#arrows', size: 36 });
    s.box('수영·사고위험 Y', { id: 'y', x: 1440, y: 680, w: 420, color: 'green', at: '#arrows', size: 36 });
    s.arrow('temp', 'x', { at: '#arrows', color: 'yellow', width: 7, label: '공통 원인', labelColor: 'yellow', bend: -0.1 });
    s.arrow('temp', 'y', { at: '#arrows', color: 'yellow', width: 7, label: '공통 원인', labelColor: 'yellow', bend: 0.1 });
    s.text('X ← T → Y', { y: 900, size: 60, font: 'mono', align: 'center', at: '#arrows', color: 'teal' });
  },
  missing(s) {
    s.text('관찰된 패턴이 화살표를 만들지는 않습니다', { x: 960, y: 100, size: 58, font: 'display', align: 'center', at: 0.1 });
    s.circle({ id: 'temp2', x: 720, y: 330, r: 100, label: 'T\n기온', color: 'yellow', at: '#graph', labelSize: 36 });
    s.box('판매 X', { id: 'x2', x: 420, y: 700, w: 300, color: 'blue', at: '#graph', size: 38 });
    s.box('결과 Y', { id: 'y2', x: 1260, y: 700, w: 300, color: 'green', at: '#graph', size: 38 });
    s.arrow('temp2', 'x2', { at: '#graph', color: 'yellow', width: 7 });
    s.arrow('temp2', 'y2', { at: '#graph', color: 'yellow', width: 7 });
    s.arrow('x2', 'y2', { at: '#missing', color: 'red', dashed: true, label: '선언하지 않음', labelColor: 'red', width: 5, bend: -0.1 });
    s.line([[800,630],[880,710]],{at:'#missing',color:'red',width:7});s.line([[800,710],[880,630]],{at:'#missing',color:'red',width:7});
    s.text('상관관계 ≠ 인과관계', { y: 930, size: 58, align: 'center', at: '#missing', color: 'red' });
  },
  group(s) {
    s.text('기온 그룹을 나눠 비교하기', { x: 960, y: 100, size: 56, font: 'display', align: 'center', at: 0.1 });
    s.box('전체 온도 혼합', { x: 520, y: 210, w: 600, h: 120, color: 'muted', at: '#hold', size: 36 });
    s.box('T = 22°C 그룹', { x: 1430, y: 210, w: 600, h: 120, color: 'yellow', at: '#hold', size: 36 });
    axes(s, 270, 320, 540, 380, '#hold', false);
    dots(s, groupAggregate, '#hold', 0.06, 11);
    axes(s, 1170, 320, 540, 380, '#group', false);
    dots(s, group22, '#group', 0.15, 18);
    s.text('전체 r = 0.97', { x: 545, y: 820, size: 42, align: 'center', at: '#hold', color: 'red' });
    s.text('같은 T의 r = 0.21', { x: 1440, y: 820, size: 42, align: 'center', at: '#group', color: 'teal' });
    s.note('계산된 합성값, 실제 자료 아님', { y: 980, at: 2.5, color: 'muted' });
    s.text('같은 기온 안에서는 상승이 약해짐', { x: 1440, y: 910, size: 30, align: 'center', at: 4.5, color: 'teal' });
  },
  intervention(s) {
    s.text('무엇을 바꾸고 무엇을 고정했나요?', { x: 960, y: 100, size: 58, font: 'display', align: 'center', at: 0.1 });
    s.box('T = 22°C로 고정', { id: 'fixed', x: 540, y: 320, w: 500, h: 170, color: 'yellow', at: '#change', icon: 'thermometer', size: 40 });
    s.box('X만 시뮬레이션으로 변경', { id: 'change', x: 1400, y: 320, w: 550, h: 170, color: 'blue', at: '#change', icon: 'sliders-horizontal', size: 36 });
    s.arrow('fixed', 'change', { at: '#change', color: 'teal', width: 7, label: '조건 설정', labelColor: 'teal' });
    axes(s, 420, 610, 1100, 270, '#outcome');
    dots(s, intervention, '#outcome', 0.12, 17);
    s.line([[420, 755], [1520, 755]], { at: '#outcome', color: 'red', dashed: true, width: 4 });
    s.note('Y 생성 규칙은 그대로', { x: 1500, y: 560, at: '#outcome', color: 'red' });
    s.text('실제 사람에 대한 효과 추정 아님', { y: 1000, size: 42, align: 'center', at: 2.5, color: 'muted' });

  },
  questions(s) {
    s.text('관찰과 개입은 다른 질문입니다', { x: 960, y: 100, size: 58, font: 'display', align: 'center', at: 0.1 });
    s.box('관찰', { id: 'observe', x: 530, y: 570, w: 560, h: 270, color: 'teal', at: '#observe', size: 54 });
    s.text('큰 X와 큰 Y가 함께 보이는가?', { x: 530, y: 740, size: 32, align: 'center', at: '#observe', color: 'muted' });
    s.box('개입', { id: 'intervene', x: 1430, y: 570, w: 560, h: 270, color: 'orange', at: '#intervene', size: 54 });
    s.text('X를 바꾸면 Y가 달라지는가?', { x: 1430, y: 740, size: 32, align: 'center', at: '#intervene', color: 'muted' });
    s.arrow('observe', 'intervene', { at: '#intervene', color: 'muted', dashed: true, label: '질문을 바꿔야 함', labelColor: 'muted' });
    s.text('서로 다른 증거와 가정이 필요합니다', { y: 930, size: 46, align: 'center', at: 2.0, color: 'teal' });
    s.text('질문을 분리해서 검토합니다', { y: 870, size: 30, align: 'center', at: 8.0, color: 'muted' });

  },
  outro(s) {
    s.text('상관관계는 질문을 시작하게 합니다', { x: 960, y: 100, size: 58, font: 'display', align: 'center', at: 0.1 });
    s.box('T', { id: 't3', x: 700, y: 560, w: 180, h: 150, color: 'yellow', at: '#controls', size: 60 });
    s.box('X', { id: 'x3', x: 430, y: 820, w: 180, h: 150, color: 'blue', at: '#controls', size: 60 });
    s.box('Y', { id: 'y3', x: 990, y: 820, w: 180, h: 150, color: 'green', at: '#controls', size: 60 });
    s.arrow('t3', 'x3', { at: '#controls', color: 'yellow', width: 7 });
    s.arrow('t3', 'y3', { at: '#controls', color: 'yellow', width: 7 });
    s.text('T는 시뮬레이션 변수', { x: 1450, y: 620, size: 40, at: '#controls', color: 'muted' });
    s.text('인과관계에는 설계와 가정이 필요합니다', { y: 980, size: 50, align: 'center', at: '#lesson', color: 'red' });
    s.text('먼저 질문하고, 그다음 설계합니다', { y: 880, size: 30, align: 'center', at: 7.0, color: 'muted' });

  },
};
