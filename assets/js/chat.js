/* Ask HST: the HST Medical shop assistant.
   Rule-based and 100% in the browser: no backend, no API key, no external AI service. It answers from
   assets/data/chat-kb.json (generated on every build from the same data as the pages, see _src/chat_kb.py),
   keeps its conversation in sessionStorage and a little learning in localStorage (hst-chat-mem), and adds to the
   site's own bag (localStorage hst-bag, through window.HSTBag from site.js). Payment is never taken in chat.
   Layout of this file: 1 core + knowledge index, 2 language understanding, 3 dialogue + answers, 4 bag, 5 UI + API. */
(function () {
  'use strict';
  var d = document, w = window;
  var MEM_KEY = 'hst-chat-mem', SESS_KEY = 'hst-chat-sess', BAG_KEY = 'hst-bag';
  var me = d.currentScript || d.querySelector('script[src*="assets/js/chat.js"]');
  var SRC = (me && me.src) || '';
  var ROOT = SRC.replace(/assets\/js\/chat\.js[\s\S]*$/, '') || '/';
  var VER = (SRC.match(/[?&]v=([^&#]+)/) || [])[1] || '';
  var KB_URL = ROOT + 'assets/data/chat-kb.json' + (VER ? '?v=' + VER : '');
  var KB = null, IDX = null, loading = null;
  var reduce = false;
  try { reduce = w.matchMedia('(prefers-reduced-motion: reduce)').matches; } catch (e) { reduce = false; }
  var MAXQ = 20, ASKQ = 10;

  /* ------------------------------------------------------------------ small helpers */
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  function money(n) { return 'S$' + Number(n).toFixed(2); }
  function clone(o) { return o == null ? o : JSON.parse(JSON.stringify(o)); }
  function uniq(a) { var s = {}, o = []; for (var i = 0; i < a.length; i++) if (!s[a[i]]) { s[a[i]] = 1; o.push(a[i]); } return o; }
  function fold(s) { return String(s).normalize('NFKD').replace(/[\u0300-\u036f]/g, '').replace(/[\u00ae\u2122\u00a9]/g, '').toLowerCase(); }
  function cap1(s) { s = String(s || ''); return s.charAt(0).toUpperCase() + s.slice(1); }
  function lsGet(k) { try { return JSON.parse(w.localStorage.getItem(k) || 'null'); } catch (e) { return null; } }
  function lsSet(k, v) { try { w.localStorage.setItem(k, JSON.stringify(v)); return true; } catch (e) { return false; } }
  function lsDel(k) { try { w.localStorage.removeItem(k); } catch (e) { /* ignore */ } }
  function ssGet(k) { try { return JSON.parse(w.sessionStorage.getItem(k) || 'null'); } catch (e) { return null; } }
  function ssSet(k, v) { try { w.sessionStorage.setItem(k, JSON.stringify(v)); } catch (e) { /* ignore */ } }
  function ssDel(k) { try { w.sessionStorage.removeItem(k); } catch (e) { /* ignore */ } }

  /* Damerau-Levenshtein (optimal string alignment) with an early exit above `max` */
  function dl(a, b, max) {
    var la = a.length, lb = b.length, i, j;
    if (Math.abs(la - lb) > max) return max + 1;
    var p2 = null, p = [], c;
    for (j = 0; j <= lb; j++) p[j] = j;
    for (i = 1; i <= la; i++) {
      c = [i]; var rm = i;
      for (j = 1; j <= lb; j++) {
        var cost = a.charCodeAt(i - 1) === b.charCodeAt(j - 1) ? 0 : 1;
        var v = Math.min(p[j] + 1, c[j - 1] + 1, p[j - 1] + cost);
        if (i > 1 && j > 1 && a.charCodeAt(i - 1) === b.charCodeAt(j - 2) && a.charCodeAt(i - 2) === b.charCodeAt(j - 1)) v = Math.min(v, p2[j - 2] + 1);
        c[j] = v; if (v < rm) rm = v;
      }
      if (rm > max) return max + 1;
      p2 = p; p = c;
    }
    return p[lb];
  }
  /* edits we forgive: 4-6 letters 1, 7-13 letters 2, longer 3 (never for 3 letters or fewer) */
  function maxEdits(n) { return n <= 3 ? 0 : n <= 6 ? 1 : n <= 13 ? 2 : 3; }

  /* crude stem, applied identically to the shopper's words and to the vocabulary */
  function stem(w_) {
    if (w_.length < 4) return w_;
    if (/ies$/.test(w_) && w_.length > 4) return w_.replace(/ies$/, 'y');
    if (/(ss|us|is|ous)$/.test(w_)) return w_;
    if (/(ch|sh|x|z)es$/.test(w_)) return w_.replace(/es$/, '');
    if (/ing$/.test(w_) && w_.length > 5) { var b = w_.slice(0, -3); if (/(.)\1$/.test(b) && !/(ll|ss)$/.test(b)) b = b.slice(0, -1); return b; }
    if (/ed$/.test(w_) && w_.length > 5) return w_.replace(/ed$/, '');
    if (/s$/.test(w_)) return w_.slice(0, -1);
    return w_;
  }
  function singular(w_) { return w_.length > 3 ? w_.replace(/ies$/, 'y').replace(/(ch|sh|x)es$/, '$1').replace(/([^s])s$/, '$1') : w_; }

  /* ------------------------------------------------------------------ language data */
  var NUMW = { one: 1, two: 2, three: 3, four: 4, five: 5, six: 6, seven: 7, eight: 8, nine: 9, ten: 10, eleven: 11, twelve: 12, thirteen: 13, fourteen: 14, fifteen: 15, twenty: 20,
    dozen: 12, couple: 2, pair: 2, twice: 2, thrice: 3, single: 1, once: 1 };
  var ORD = { first: 0, '1st': 0, second: 1, '2nd': 1, third: 2, '3rd': 2, fourth: 3, '4th': 3, fifth: 4, '5th': 4, last: -1, latter: -1, former: 0 };
  /* chat shorthand and contractions (apostrophes are removed before this) */
  var SHORT = { pls: 'please', plz: 'please', pliz: 'please', plss: 'please', thx: 'thanks', tq: 'thanks', ty: 'thanks', tks: 'thanks', thks: 'thanks', thanx: 'thanks', thankyou: 'thanks', u: 'you', ur: 'your', r: 'are',
    abt: 'about', wat: 'what', wut: 'what', hw: 'how', wanna: 'want to', gonna: 'going to', gotta: 'got to', wan: 'want', nid: 'need', ned: 'need', oso: 'also', bout: 'about', cos: 'because', coz: 'because',
    dis: 'this', dat: 'that', lemme: 'let me', gimme: 'give me', cant: 'cannot', wont: 'will not', dont: 'do not', doesnt: 'does not', didnt: 'did not', isnt: 'is not', arent: 'are not', wasnt: 'was not',
    shouldnt: 'should not', couldnt: 'could not', wouldnt: 'would not', cannot: 'cannot', whats: 'what is', hows: 'how is', wheres: 'where is', whos: 'who is', thats: 'that is', theres: 'there is', lets: 'let us',
    im: 'i am', ive: 'i have', ill: 'i will', youre: 'you are', youll: 'you will', theyre: 'they are', itll: 'it will', its: 'it is', id: 'i would', hv: 'have', tmr: 'tomorrow', tmrw: 'tomorrow', abit: 'a bit',
    okie: 'ok', okey: 'ok', okayy: 'okay', okk: 'ok', yeah: 'yes', yep: 'yes', yup: 'yes', yea: 'yes', ya: 'yes', yah: 'yes', yass: 'yes', sure: 'sure', nope: 'no', nah: 'no', mins: 'minutes', pcs: 'pieces',
    pc: 'piece', qty: 'quantity', nos: 'pieces', bag: 'bag', bags: 'bag', basket: 'bag', cart: 'bag', trolley: 'bag', carts: 'bag', baskets: 'bag', stuff: 'things', somethin: 'something', anythin: 'anything',
    kena: 'got', ada: 'got', tak: 'not', mahu: 'want', mau: 'want', nak: 'want', berapa: 'how much', boleh: 'can', tolong: 'please', sakit: 'pain', batuk: 'cough', demam: 'fever', pening: 'dizzy', 'sakit kepala': 'headache' };
  /* discourse particles and filler that carry no meaning (Singlish and friends) */
  var DROP = { lah: 1, leh: 1, lor: 1, meh: 1, sia: 1, hor: 1, ah: 1, ahh: 1, mah: 1, liao: 1, loh: 1, hmm: 1, hmmm: 1, umm: 1, um: 1, uh: 1, erm: 1, haha: 1, hehe: 1, lol: 1, wah: 1, aiyo: 1, aiyah: 1, alamak: 1, eh: 1, oh: 1, ok: 0, okay: 0 };
  /* never "corrected": everyday words that sit one edit away from catalogue words */
  var STOP = {};
  ('that this with have from they will would there their what when where which while about after again against also because been before being between both could does doing down during each '
    + 'further here hers himself into just more most myself nothing only other ours ourselves over same should some such than then these those through under until very were whom your yours yourself '
    + 'main mail rain gain game name came home hope hole hold held hand hard hear heat half hall halt hang hike hill hint hire horn host hour huge hunt hurt idea inch iron item jail join joke jump '
    + 'keep kick kill kind king kiss knee know lack lady lake lamp land lane last late lazy lead leaf lean left lend less life lift like line link lion list live load loan lock long look loop lose loss '
    + 'lost loud love luck lunch mind mine miss mode mood moon more move much must myth nail near neat need news next nice nine none nose note noun nuts once open oral pace pack page paid pair palm park '
    + 'part pass past path peak peel pick pile pill pine pink pipe plan play plot plus pole pool poor port post pour pray pull pump pure push quit race rank rare rate read real rely rent rest rice rich '
    + 'ride ring rise risk road rock role roll roof room root rope rose ruin rule rush sack safe sail salt sand save seat seed seek seem seen self sell send sent sets shop show shut sick side sign silk '
    + 'sing sink site size skip slip slow snap snow soap sock soft soil sold sole some song soon sort soul soup spot star stay step stop such suit sure swim tail take tale talk tall tank tape task '
    + 'team tear tell tend tent term test text than thin tide tidy tile till time tiny tips tire told tone tool tops tour town trap tree trip true tube tune turn twin type ugly unit upon used user vast '
    + 'very view vote wage wait wake walk wall want warm wash wave weak wear week well went west what when whom wide wife wild will wind wine wing wipe wire wise wish with wood word wore work worn yard '
    + 'yeah year zero zone black blank blind block board bonus brain brand bread break bring broad brown build burst cable candy carry catch cause chain chair chart cheap check chest chief child claim '
    + 'class clean clear click clock close cloud coach coast could count court cover craft crash cream crime cross crowd crown cycle daily dance dealt death delay depth doubt draft drama dream dress '
    + 'drink drive early earth eight empty enemy enjoy enter entry equal error event every exact exist extra faith false fault fiber field fifth fifty fight final first flash fleet floor focus force '
    + 'forth forty found frame frank fresh front fruit fully glass globe going grace grade grand grant grass great green gross group grown guard guess guest guide happy harsh heart heavy hence horse '
    + 'hotel house human ideal image index inner input issue joint judge juice known label large laser later laugh layer learn lease least leave legal level light limit local logic loose lower lucky '
    + 'lunch magic major maker march match maybe mayor meant media metal might minor minus mixed model money month moral motor mount mouse mouth movie music needs never newly night noise north noted '
    + 'novel nurse occur ocean offer often order other ought outer owner paint panel paper party pause peace phase phone photo piano piece pilot pitch place plain plane plant plate point pound power '
    + 'press price pride prime print prior prize proof proud prove queen quick quiet quite radio raise range rapid ratio reach ready refer relax reply right rival river rough round route royal rural '
    + 'scale scene scope score sense serve seven shade shake shall shape share sharp sheet shelf shell shift shine shirt shock shoot short shown sight since sixth sixty skill sleep slide small smart '
    + 'smile smoke solid solve sorry sound south space spare speak speed spend spent split spoke sport staff stage stake stand start state steam steel stick still stock stone stood store storm story '
    + 'strip stuck study stuff style sugar suite super sweet table taken taste taxes teach teeth thank theme there thick thing think third those three threw throw tight times tired title today '
    + 'topic total touch tough tower track trade train treat trend trial tried tries truck truly trust truth twice under union unity until upper upset urban usage usual valid value video virus visit '
    + 'vital voice waste watch water wheel where which while white whole whose woman women world worry worse worst worth would wound write wrong wrote young youth').split(/\s+/).forEach(function (x) { if (x) STOP[x] = 1; });

  /* words the assistant itself understands (so typos of them get repaired): commands, topics, health words */
  var LEXICON = ('add buy purchase order checkout check out pay payment proceed remove delete clear empty cancel change update show view display list open bag cart basket total subtotal price prices cost how much cheap cheaper cheapest '
    + 'expensive free delivery deliver shipping ship courier postage island overseas international gst tax stock available availability recommend suggest suggestion help helpful need want looking find search have got '
    + 'sell stock carry compare comparison difference different versus better best good ingredients ingredient contain contains usage use apply dosage dose daily twice instructions directions caution warning safe side effect '
    + 'effects allergy allergic pregnant pregnancy breastfeeding medication medicine tablet capsule capsules softgel gummy gummies jelly lozenge lozenges syrup drops oil balm creme cream liniment patch plaster stick inhaler '
    + 'powder sachet sachets bottle bottles pack packs twin triple value travel bundle single size sizes halal vegan vegetarian gmp certified quality genuine authentic fake counterfeit origin made singapore store stores '
    + 'stockist stockists guardian watsons nhgp polyclinic pharmacy pharmacies fairprice online shop shopping contact email phone call hotline telegram address trade reseller wholesale distributor about company kowa brand '
    + 'brands catalogue catalog flipbook book page pages sheet product products health notes blog article articles privacy policy refund return returns promotion promo discount offer voucher coupon code thanks thank hello '
    + 'please sorry yes no maybe okay continue another more less extra instead both first second third last cheapest same usual before after meals night morning evening bedtime twice thrice often long short pain relief ache '
    + 'aches sore tired weak stress sleep sleeping insomnia cough cold flu fever throat phlegm nose blocked sinus headache migraine dizzy giddy joint joints knee knees back neck shoulder muscle muscles sprain strain bruise '
    + 'swelling arthritis rheumatism immunity immune energy stamina vitality eyes vision memory brain skin hair beauty digestion liver kidney urinary bladder heart cholesterol bones calcium kids children child baby infant '
    + 'toddler elderly women men vitamin vitamins supplement supplements herbal tonic ginseng cordyceps lingzhi melatonin magnesium omega probiotic collagen pearl squalene turmeric ginkgo glucosamine elderberry lutein '
    + 'rheuma salve alievaid lintus gard zoo vite ivy leaf sinus clear boost rosehips therra synbioten curqmax algaomega neuro arthro libi maxi cal flugard minigels penguin panda skippy charley safari').split(/\s+/);

  /* ------------------------------------------------------------------ tokenising */
  var UNITW = 'pieces|piece|boxes|box|packs|pack|tubes|tube|jars|jar|bottles|bottle|sachets|sachet|sets|set|units|unit|strips|strip|caps|tabs|capsules|capsule|tablets|tablet|gummies|gummy|sticks|stick|patches|patch|softgels|vegicaps|lozenges|drops|pcs|pc|bags|bag';
  var RE_NUMUNIT = new RegExp('^(\\d+)(' + UNITW + ')$');
  function tokenize(raw) {
    var s = fold(raw);
    s = s.replace(/[\u2018\u2019\u02bc`']/g, '').replace(/\u00d7/g, ' x ');
    s = s.replace(/(?:s\$|sgd|usd|\$)\s*(\d+(?:\.\d+)?)/g, ' \u00a4$1 ').replace(/(\d+(?:\.\d+)?)\s*(?:dollars?|bucks)\b/g, ' \u00a4$1 ');
    s = s.replace(/&/g, ' and ').replace(/\+/g, ' ').replace(/(\d),(\d{3})/g, '$1$2').replace(/;/g, ',');
    var m = s.match(/\u00a4\d+(?:\.\d+)?|[a-z]+\d*[a-z]*|\d+(?:\.\d+)?[a-z]*|,/g) || [], out = [], x, i;
    for (i = 0; i < m.length; i++) {
      var t = m[i];
      if ((x = /^(\d+(?:\.\d+)?)x$/.exec(t))) { out.push(x[1], 'x'); continue; }
      if ((x = /^x(\d+)$/.exec(t))) { out.push('x', x[1]); continue; }
      if ((x = RE_NUMUNIT.exec(t))) { out.push(x[1], x[2]); continue; }
      out.push(t);
    }
    var o2 = [];
    for (i = 0; i < out.length; i++) {
      if (/^\d+(?:\.\d+)?$/.test(out[i]) && /^(g|mg|ml|mcg|iu|kg|cm)$/.test(out[i + 1] || '')) { o2.push(out[i] + out[i + 1]); i++; } else o2.push(out[i]);
    }
    return o2;
  }
  function expand(tokens, spell) {
    var out = [], sp = spell && KB && KB.spell;
    tokens.forEach(function (t) {
      if (DROP[t]) return;
      var r = SHORT[t];
      if (r === undefined && sp && sp[t] !== undefined) r = sp[t];
      if (r !== undefined) { if (r) r.split(' ').forEach(function (z) { out.push(z); }); return; }
      out.push(t);
    });
    return out;
  }
  function lite(phrase) { return expand(tokenize(phrase), false); }

  /* ------------------------------------------------------------------ the knowledge index (built once, after the KB is fetched) */
  var GENERIC_STEMS = {};
  'pain relief herbal remedy health care plus forte formula advanced high strength daily support supplement product products help helps promote promotes maintain maintains healthy natural take use used also may can for the and with from your you our not'.split(' ').forEach(function (x) { GENERIC_STEMS[stem(x)] = 1; });

  function parseVariant(v, p, i) {
    var l = fold(v.l), o = { i: i, l: v.l, p: v.p, c: v.c, size: [], mult: 0, words: {} }, m;
    (l.match(/\d+(?:\.\d+)?\s?(?:g|ml|mg)\b/g) || []).forEach(function (z) { o.size.push(z.replace(/\s/g, '')); });
    m = /[\u00d7x]\s?(\d+)|bundle of (\d+)|(\d+)\s?(?:bottles|sachets|packs?)\b/.exec(l);
    if (m) o.mult = +(m[1] || m[2] || m[3]);
    ['single', 'twin', 'triple', 'value', 'travel', 'bundle', 'sachet', 'bottle', 'tablets', 'effervescent'].forEach(function (k) { if (l.indexOf(k) > -1) o.words[k] = 1; });
    if (/buy 1 get 1|bogo/.test(l)) o.words.bogo = 1;
    if (i === 0 && !o.size.length) { var bs = /\d+(?:\.\d+)?\s?(?:g|ml|mg)\b/.exec(fold(p.sz || '')); if (bs) o.baseSize = bs[0].replace(/\s/g, ''); }
    return o;
  }

  function buildIndex(kb) {
    var I = { P: {}, alias: {}, aliasBy: {}, catAlias: {}, pageAlias: {}, vocab: {}, vp: {}, vbl: {}, needs: [], idf: {}, cidf: {}, chains: {}, areas: [] };
    var i, j;
    function addVocab(tok, pr) {
      if (!tok || tok.length < 2 || /\d/.test(tok)) return;
      if (!I.vocab[tok]) { I.vocab[tok] = 1; (I.vbl[tok.length] = I.vbl[tok.length] || []).push(tok); }
      if ((I.vp[tok] || 0) < pr) I.vp[tok] = pr;
    }
    LEXICON.forEach(function (x) { addVocab(x, 3); });
    kb.products.forEach(function (p) {
      I.P[p.id] = p;
      p.vk = p.v.map(function (v, k) { return parseVariant(v, p, k); });
      p.buy = p.v.some(function (v) { return v.p; });
      p.min = p.v.reduce(function (m, v) { return v.p && (m == null || v.p < m) ? v.p : m; }, null);
      var bag = {}, txt = [p.n, p.sn, p.tg, p.f, p.need, (p.ben || []).join(' '), (p.ind || []).join(' '), (p.d || '').slice(0, 200), p.fm].join(' ');
      lite(txt).forEach(function (t) { if (t.length > 2 && !/\d/.test(t)) { var s = stem(t); if (!GENERIC_STEMS[s] && !STOP[t]) bag[s] = 1; } });
      p.bag = bag;
    });
    Object.keys(kb.alias).forEach(function (phrase) {
      var toks = lite(phrase);
      if (!toks.length) return;
      var sq = toks.join('');
      if (sq.length < 2) return;
      var e = I.alias[sq] || (I.alias[sq] = { sq: sq, n: toks.length, owners: [] });
      kb.alias[phrase].forEach(function (o) { if (e.owners.indexOf(o) < 0) e.owners.push(o); });
      toks.forEach(function (t) { addVocab(t, 2); });
    });
    Object.keys(I.alias).forEach(function (sq) { (I.aliasBy[sq.length] = I.aliasBy[sq.length] || []).push(sq); });
    kb.cats.forEach(function (c) {
      (c.al || []).forEach(function (a) { var t = lite(a); if (t.length) { I.catAlias[t.join('')] = c.id; t.forEach(function (x) { addVocab(x, 2); }); } });
    });
    kb.pages.forEach(function (pg) {
      (pg.al || []).forEach(function (a) { var t = lite(a); if (t.length) { I.pageAlias[t.join('')] = pg.id; t.forEach(function (x) { addVocab(x, 1); }); } });
    });
    kb.needs.forEach(function (n) {
      var ph = n.ph.map(function (s) { var t = lite(s); t.forEach(function (x) { addVocab(x, 2); }); return { t: t, st: t.map(stem), txt: t.join(' ') }; });
      I.needs.push({ id: n.id, l: n.l, ph: ph, p: n.p, cats: n.cats, note: n.note });
    });
    Object.keys(kb.spell || {}).forEach(function (k) { lite(kb.spell[k]).forEach(function (x) { addVocab(x, 2); }); });
    kb.chains.forEach(function (c) { c.w.forEach(function (wd) { var t = lite(wd); I.chains[t.join('')] = c.id; t.forEach(function (x) { addVocab(x, 2); }); }); });
    kb.areas.forEach(function (a) { var t = lite(a.n); I.areas.push({ n: a.n, sq: t.join(''), t: t, ll: a.ll }); t.forEach(function (x) { addVocab(x, 1); }); });
    kb.stores.forEach(function (s, k) {
      s.k = k;
      var STW = { singapore: 1, road: 1, street: 1, avenue: 1, central: 0, shopping: 1, centre: 1, center: 1, building: 1, level: 1, boulevard: 1, terminal: 0, airport: 0, link: 1, lorong: 1, complex: 1, the: 1 };
      var toks = lite(s.n + ' ' + s.a.replace(/#[\w\-\/]+/g, ' ').replace(/\d{6}/, ' '));
      s.st = {};
      toks.forEach(function (t) { if (t.length > 2 && !STW[t] && !/\d/.test(t)) { s.st[stem(t)] = 1; addVocab(t, 1); } });
      s.nt = lite(s.n).filter(function (t) { return t.length > 1 && !STW[t]; }).map(stem);
    });
    // text index for "closest matches" and answers from the site's own text
    var df = {}, N = kb.products.length;
    kb.products.forEach(function (p) { Object.keys(p.bag).forEach(function (s) { df[s] = (df[s] || 0) + 1; }); });
    Object.keys(df).forEach(function (s) { I.idf[s] = Math.log(1 + N / df[s]); });
    var cdf = {}, docs = [];
    kb.chunks.forEach(function (c) {
      var st = {}; lite(c.t + ' ' + c.s + ' ' + c.x).forEach(function (t) { if (t.length > 2 && !STOP[t]) st[stem(t)] = 1; });
      var sh = {}; lite(c.t + ' ' + c.s).forEach(function (t) { if (t.length > 2) sh[stem(t)] = 1; });
      c.st = st; c.sh = sh; docs.push(c);
      Object.keys(st).forEach(function (s) { cdf[s] = (cdf[s] || 0) + 1; });
    });
    Object.keys(cdf).forEach(function (s) { I.cidf[s] = Math.log(1 + docs.length / cdf[s]); });
    return I;
  }

  function load() {
    if (KB) return Promise.resolve(KB);
    if (!loading) {
      loading = fetch(KB_URL, { cache: 'no-cache' }).then(function (r) { if (!r.ok) throw new Error('kb ' + r.status); return r.json(); })
        .then(function (j) { KB = j; IDX = buildIndex(j); return j; })
        .catch(function (e) { loading = null; throw e; });
    }
    return loading;
  }
  function prod(id) { return IDX && IDX.P[id] || null; }
  function catOf(id) { for (var i = 0; i < KB.cats.length; i++) if (KB.cats[i].id === id) return KB.cats[i]; return null; }
  function pageOf(id) { for (var i = 0; i < KB.pages.length; i++) if (KB.pages[i].id === id) return KB.pages[i]; return null; }
  function chainOf(id) { for (var i = 0; i < KB.chains.length; i++) if (KB.chains[i].id === id) return KB.chains[i]; return null; }
  function href(rel) { return ROOT + rel; }

  /* spelling repair of one word against the vocabulary (same first letter, edits scaled to length) */
  function correctToken(t) {
    if (t.length < 4 || /[\d\u00a4]/.test(t) || IDX.vocab[t] || STOP[t]) return t;
    var sg = singular(t);
    if (sg !== t && IDX.vocab[sg]) return sg;
    var max = maxEdits(t.length), best = null, bd = 9, bp = -1, tie = false, L, k, arr, v, dd, pr;
    for (L = t.length - max; L <= t.length + max; L++) {
      arr = IDX.vbl[L];
      if (!arr) continue;
      for (k = 0; k < arr.length; k++) {
        v = arr[k];
        if (v.charCodeAt(0) !== t.charCodeAt(0)) continue;
        dd = dl(t, v, max);
        if (dd > max) continue;
        pr = IDX.vp[v] || 0;
        if (dd < bd || (dd === bd && pr > bp)) { bd = dd; best = v; bp = pr; tie = false; }
        else if (dd === bd && pr === bp && v !== best) tie = true;
      }
    }
    return best && !tie ? best : t;
  }
  function normalize(raw) {
    var toks = expand(tokenize(raw), true).map(correctToken);
    return toks;
  }

  /* ================================================================== 2. LANGUAGE UNDERSTANDING */
  var CONNECT = { and: 1, also: 1, then: 1, plus: 1, ',': 1, n: 1 };
  var FILL = { the: 1, a: 1, an: 1, of: 1, my: 1, your: 1, some: 1, any: 1, new: 1, big: 1, small: 1, little: 1, bit: 1, for: 0 };
  var UNITWORD = { piece: 1, pieces: 1, box: 1, boxes: 1, pack: 1, packs: 1, tube: 1, tubes: 1, jar: 1, jars: 1, bottle: 1, bottles: 1, sachet: 1, sachets: 1, set: 1, sets: 1, unit: 1, units: 1, strip: 1, strips: 1,
    bag: 1, bags: 1, capsules: 1, capsule: 1, tablets: 1, tablet: 1, gummies: 1, gummy: 1, sticks: 1, stick: 1, patches: 1, patch: 1, softgels: 1, vegicaps: 1, lozenges: 1, drops: 1, caps: 1, tabs: 1 };
  var NOT_QTY_AFTER = { year: 1, years: 1, yr: 1, yrs: 1, yo: 1, month: 1, months: 1, week: 1, weeks: 1, day: 1, days: 1, hour: 1, hours: 1, minute: 1, minutes: 1, min: 1, time: 1, times: 1, percent: 1, kg: 1, cm: 1, old: 1, am: 1, pm: 1, st: 1, nd: 1, rd: 1, th: 1 };
  var AUD = { kid: 'child', kids: 'child', child: 'child', children: 'child', childs: 'child', son: 'child', daughter: 'child', toddler: 'child', toddlers: 'child', baby: 'baby', babies: 'baby', infant: 'baby', newborn: 'baby',
    boy: 'child', girl: 'child', teen: 'child', teenager: 'child', grandson: 'child', granddaughter: 'child', nephew: 'child', niece: 'child', elderly: 'elder', senior: 'elder', seniors: 'elder', parents: 'elder',
    grandmother: 'elder', grandfather: 'elder', grandma: 'elder', grandpa: 'elder', mother: 'elder', father: 'elder', mum: 'elder', mom: 'elder', dad: 'elder', pregnant: 'preg', pregnancy: 'preg', expecting: 'preg', breastfeeding: 'preg', nursing: 'preg', lactating: 'preg' };
  var RE_CAUTION = /\b(pregnan\w*|expecting a baby|breast ?feed\w*|nursing|lactating|baby|babies|infant|newborn|toddler|under (2|two|3|three|12|twelve|6|six)|(kid|kids|child|children|son|daughter)\b|medication|meds|blood thinners?|warfarin|antibiotics?|diabet\w*|blood pressure|hypertension|heart (disease|condition|problem|patient)|kidney (disease|problem|failure)|liver (disease|problem)|cancer|asthma|epilepsy|surgery|operation|elderly|senior|allergic to|allergy to|chronic|sensitive skin|on (other )?(medicine|medication|meds|pills)|taking (medicine|medication|meds|pills)|g6pd|ulcer|stroke patient|high cholesterol)\b/;

  function stemsOf(T) { return T.filter(function (x) { return x !== ','; }).map(stem); }

  /* ---- products named in the text: alias spans, fuzzy and joined/split words, learned phrases ---- */
  function memMap(S) {
    var m = {}, a = S && S.mem && S.mem.aliases;
    if (a) Object.keys(a).forEach(function (ph) { var t = lite(ph); if (t.length) m[t.join('')] = { sq: t.join(''), n: t.length, owners: [a[ph]], learned: true }; });
    return m;
  }
  function fuzzyAlias(sq) {
    var max = maxEdits(sq.length), best = null, bd = 9, tie = false, L, k, arr, key, dd;
    for (L = sq.length - max; L <= sq.length + max; L++) {
      arr = IDX.aliasBy[L];
      if (!arr) continue;
      for (k = 0; k < arr.length; k++) {
        key = arr[k];
        if (key.charCodeAt(0) !== sq.charCodeAt(0)) continue;
        dd = dl(sq, key, max);
        if (dd > max) continue;
        if (dd < bd) { bd = dd; best = key; tie = false; }
        else if (dd === bd && key !== best) { if (IDX.alias[key].owners.length < IDX.alias[best].owners.length) best = key; else if (IDX.alias[key].owners.join() !== IDX.alias[best].owners.join()) tie = true; }
      }
    }
    return best && !tie ? { e: IDX.alias[best], d: bd } : null;
  }
  function findMentions(T, S) {
    var n = T.length, cands = [], mem = memMap(S), i, j;
    for (i = 0; i < n; i++) {
      if (T[i] === ',') continue;
      var sq = '';
      for (j = i; j < n && j < i + 6; j++) {
        if (T[j] === ',') break;
        sq += T[j];
        var hit = mem[sq] || IDX.alias[sq] || null, dist = 0;
        if (!hit) {
          var lastT = T[j], sg = singular(lastT);
          if (sg !== lastT) { var s2 = sq.slice(0, sq.length - lastT.length) + sg; hit = mem[s2] || IDX.alias[s2] || null; if (hit) dist = 0; }
        }
        if (!hit && sq.length >= 5) {
          var single = j === i, tk = T[i];
          if (!(single && (STOP[tk] || IDX.vocab[tk])) && !/^\d/.test(sq)) { var f = fuzzyAlias(sq); if (f) { hit = f.e; dist = f.d; } }
        }
        if (hit) cands.push({ s: i, e: j + 1, n: j - i + 1, owners: hit.owners, dist: dist, key: hit.sq, learned: !!hit.learned });
      }
    }
    cands.forEach(function (c) { c.score = c.n * 10 - c.dist * 6 + (c.owners.length === 1 ? 2 : 0) + (c.learned ? 3 : 0); });
    cands.sort(function (a, b) { return b.score - a.score || a.s - b.s; });
    var taken = [], picked = [];
    cands.forEach(function (c) {
      for (var k = c.s; k < c.e; k++) if (taken[k]) return;
      for (k = c.s; k < c.e; k++) taken[k] = true;
      picked.push(c);
    });
    picked.sort(function (a, b) { return a.s - b.s; });
    // refine: "rheuma salve" + "patch" -> the patch; "zoo vite" + "gummies" -> the two Zoo-Vite gummies
    var out = [];
    picked.forEach(function (c) {
      var prev = out[out.length - 1];
      if (prev) {
        var gapOk = true;
        for (var k = prev.e; k < c.s; k++) if (!FILL[T[k]]) gapOk = false;
        if (gapOk) {
          var inter = prev.owners.filter(function (o) { return c.owners.indexOf(o) > -1; });
          if (inter.length && (prev.owners.length > 1 || c.owners.length > 1) && !(prev.owners.length === 1 && c.owners.length === 1)) {
            prev.owners = inter; prev.e = c.e; prev.n = prev.e - prev.s; prev.dist = Math.max(prev.dist, c.dist); return;
          }
        }
      }
      out.push({ s: c.s, e: c.e, n: c.n, owners: c.owners.slice(), dist: c.dist, key: c.key, learned: c.learned });
    });
    return out;
  }

  /* ---- quantity and pack words outside the product spans ---- */
  var PACKW = { single: 'single', regular: 'single', normal: 'single', standard: 'single', basic: 'single', individual: 'single', solo: 'single', twin: 'twin', twins: 'twin', double: 'twin', triple: 'triple',
    value: 'value', bulk: 'value', jumbo: 'value', economy: 'value', saver: 'value', family: 'value', bigger: 'value', biggest: 'value', largest: 'value', large: 'value', big: 'value',
    travel: 'travel', trip: 'travel', mini: 'travel', pocket: 'travel', sachet: 'travel', sachets: 'travel', portable: 'travel', smaller: 'travel', smallest: 'travel', small: 'travel', bundle: 'bundle', bundles: 'bundle' };
  function scanQtyPack(T, cover) {
    var qs = [], ps = [], n = T.length, i, t, nx, pv;
    for (i = 0; i < n; i++) {
      if (cover[i]) continue;
      t = T[i]; nx = T[i + 1]; pv = T[i - 1];
      if (/^\d{1,3}$/.test(t)) {
        if (nx && NOT_QTY_AFTER[nx]) continue;
        if (pv && /^(number|no|num|item|option|size|strength|page|p|pg|ref|code|on)$/.test(pv) && !cover[i - 1]) continue;
        if (pv === 'x' || nx === 'x') { qs.push({ i: i, v: +t, kind: 'x', unit: false, xs: pv === 'x' }); continue; }
        qs.push({ i: i, v: +t, kind: 'num', unit: !!(nx && UNITWORD[nx]), un: nx });
        continue;
      }
      if (/^\d+(?:\.\d+)?(?:g|ml|mg)$/.test(t)) { ps.push({ i: i, k: 'size', v: t }); continue; }
      if (t === 'half' && T[i + 1] === 'a' && T[i + 2] === 'dozen') { qs.push({ i: i, v: 6, kind: 'word', len: 3 }); continue; }
      if (t === 'a' && (T[i + 1] === 'dozen' || T[i + 1] === 'couple' || T[i + 1] === 'pair')) { qs.push({ i: i, v: NUMW[T[i + 1]], kind: 'word', len: 2 }); continue; }
      if (t === 'dozen' || t === 'couple' || t === 'pair' || t === 'twice' || t === 'thrice') { if (!(T[i - 1] === 'a' || T[i - 1] === 'half')) qs.push({ i: i, v: NUMW[t], kind: 'word', len: 1 }); continue; }
      if (NUMW[t] && t !== 'single' && t !== 'once' && t !== 'twice') {
        if (t === 'one' && !(cover[i + 1] || UNITWORD[nx] || nx === 'more' || nx === 'of' || /^(add|get|buy|take|want|need|have)$/.test(pv || ''))) continue;
        qs.push({ i: i, v: NUMW[t], kind: 'word', unit: !!(nx && UNITWORD[nx]), un: nx });
        continue;
      }
      if (t === 'a' || t === 'an') { if (cover[i + 1]) qs.push({ i: i, v: 1, kind: 'art' }); continue; }
      if (t === 'another' || t === 'extra' || t === 'more') { qs.push({ i: i, v: 1, kind: 'more' }); continue; }
      if (PACKW[t] && !(t === 'single' && nx === 'one')) { ps.push({ i: i, k: 'word', v: PACKW[t] }); continue; }
      if (t === 'x' && /^\d{1,3}$/.test(nx || '')) continue;
    }
    return { qs: qs, ps: ps };
  }
  /* which qty / pack tokens belong to which product mention: split at "and"/commas, else by the message's style */
  function attach(M, qp, T) {
    var att = M.map(function () { return { qs: [], ps: [] }; });
    if (!M.length) return att;
    var firstTok = Math.min.apply(null, qp.qs.concat(qp.ps).map(function (x) { return x.i; }).concat([1e9]));
    var prefix = firstTok < M[0].s;
    function owner(i, isPack) {
      if (i < M[0].s) return 0;
      if (i >= M[M.length - 1].e) return M.length - 1;
      for (var k = 0; k < M.length - 1; k++) {
        if (i >= M[k].e && i < M[k + 1].s) {
          var c = -1, z;
          for (z = M[k].e; z < M[k + 1].s; z++) if (CONNECT[T[z]]) { c = z; break; }
          if (c > -1) return i < c ? k : k + 1;
          if (isPack) return (i - M[k].e) < (M[k + 1].s - i) ? k : k + 1;
          return prefix ? k + 1 : k;
        }
      }
      return M.length - 1;
    }
    qp.qs.forEach(function (q) { att[owner(q.i, false)].qs.push(q); });
    qp.ps.forEach(function (p) { att[owner(p.i, true)].ps.push(p); });
    return att;
  }

  /* ---- pack / variant choice for one product ---- */
  function chooseVariant(p, info, S) {
    var ps = info.ps || [], qs = (info.qs || []), best = -1, bs = 0, ties = [], res = { vi: 0, via: 'default', tie: null, packQty: null };
    var sizes = [], words = {}, mult = 0, usedQ = {};
    ps.forEach(function (x) { if (x.k === 'size') sizes.push(x.v); else words[x.v] = 1; });
    // "6 bottles", "2 pack", "x 6" with a size: the number names a pack when the product has that pack
    qs.forEach(function (q) {
      var has = p.vk.some(function (v) { return v.mult === q.v; });
      if (has && ((q.unit && /^(bottles?|sachets?|packs?|boxes|box|pieces)$/.test(q.un || '')) || (q.xs && sizes.length))) { mult = q.v; usedQ[q.i] = true; }
    });
    var any = sizes.length || mult || Object.keys(words).length;
    if (!any) {
      var rem = S && S.mem && S.mem.packs && S.mem.packs[p.id];
      if (rem) for (var k = 0; k < p.vk.length; k++) if (p.vk[k].l === rem && p.vk[k].p) { res.vi = k; res.via = 'memory'; break; }
      return res;
    }
    p.vk.forEach(function (v, i) {
      var sc = 0;
      sizes.forEach(function (z) { if (v.size.indexOf(z) > -1) sc += 3; else if (v.baseSize === z) sc += 1; });
      Object.keys(words).forEach(function (wd) {
        if (v.words[wd]) sc += 4;
        else if (wd === 'value' && v.mult >= 5) sc += 2;
        else if (wd === 'twin' && v.mult === 2) sc += 3;
        else if (wd === 'triple' && v.mult === 3) sc += 3;
        else if (wd === 'bundle' && v.mult >= 2) sc += 2;
      });
      if (mult && v.mult === mult) sc += 3;
      if (sc > bs) { bs = sc; best = i; ties = [i]; } else if (sc === bs && sc > 0) ties.push(i);
    });
    res.usedQ = usedQ;
    if (best < 0) { res.via = 'nomatch'; res.none = true; return res; }
    if (ties.length > 1) { res.tie = ties; res.vi = ties[0]; res.via = 'tie'; return res; }
    res.vi = best; res.via = 'said';
    return res;
  }

  /* ---- needs (symptom words) ---- */
  function detectNeeds(T, cover) {
    var W = [], widx = [];
    T.forEach(function (x, i) { if (x !== ',') { W.push(x); widx.push(i); } });
    var st = W.map(stem), pos = {}, out = [];
    st.forEach(function (s, i) { (pos[s] = pos[s] || []).push(i); });
    IDX.needs.forEach(function (nd) {
      var best = 0, bp = null, bph = null;
      nd.ph.forEach(function (ph) {
        var L = ph.st.length, k, ok = true;
        for (k = 0; k < L; k++) if (!pos[ph.st[k]]) { ok = false; break; }
        if (!ok) return;
        var span = 1e9, chosen = null;
        pos[ph.st[0]].forEach(function (p0) {
          var ids = [p0], good = true;
          for (var z = 1; z < L; z++) {
            var near = null;
            pos[ph.st[z]].forEach(function (q) { if (ids.indexOf(q) < 0 && (near === null || Math.abs(q - p0) < Math.abs(near - p0))) near = q; });
            if (near === null) { good = false; break; }
            ids.push(near);
          }
          if (!good) return;
          var mn = Math.min.apply(null, ids), mx = Math.max.apply(null, ids);
          if (mx - mn < span) { span = mx - mn; chosen = ids; }
        });
        if (!chosen || (L > 1 && span > L + 2)) return;
        if (cover && chosen.every(function (q) { return cover[widx[q]]; })) return;   // the words are part of a product name
        var sc = L * 2 + (L > 1 && span === L - 1 ? 1 : 0);
        if (sc > best) { best = sc; bp = chosen; bph = ph.txt; }
      });
      if (best) out.push({ id: nd.id, score: best, ph: bph, pos: bp });
    });
    out.sort(function (a, b) { return b.score - a.score; });
    if (!out.length) return [];
    var keep = [out[0]], used = {};
    out[0].pos.forEach(function (q) { used[q] = 1; });
    for (var i = 1; i < out.length && keep.length < 3; i++) {
      var o = out[i];
      if (o.pos.some(function (q) { return used[q]; })) continue;
      keep.push(o); o.pos.forEach(function (q) { used[q] = 1; });
    }
    return keep;
  }
  function needById(id) { for (var i = 0; i < IDX.needs.length; i++) if (IDX.needs[i].id === id) return IDX.needs[i]; return null; }

  /* ---- categories, pages, retailers and areas named in the text ---- */
  function spanLookup(T, table, minFuzzy, skipCover) {
    var n = T.length, best = null, i, j;
    for (i = 0; i < n; i++) {
      if (T[i] === ',' || (skipCover && skipCover[i])) continue;
      var sq = '';
      for (j = i; j < n && j < i + 5; j++) {
        if (T[j] === ',' || (skipCover && skipCover[j])) break;
        sq += T[j];
        var id = table[sq], dist = 0;
        if (id === undefined && sq.length >= (minFuzzy || 6) && !(j === i && (STOP[T[i]] || IDX.vocab[T[i]]))) {
          var mx = maxEdits(sq.length), keys = Object.keys(table);
          for (var k = 0; k < keys.length; k++) { var key = keys[k]; if (key.charCodeAt(0) === sq.charCodeAt(0) && Math.abs(key.length - sq.length) <= mx && dl(sq, key, mx) <= mx) { id = table[key]; dist = 1; break; } }
        }
        if (id !== undefined) { var sc = (j - i + 1) * 10 - dist * 6; if (!best || sc > best.sc) best = { id: id, s: i, e: j + 1, sc: sc }; }
      }
    }
    return best;
  }
  function areaSearch(T) {
    var n = T.length, best = null, i, j;
    for (i = 0; i < n; i++) {
      if (T[i] === ',') continue;
      var sq = '';
      for (j = i; j < n && j < i + 4; j++) {
        if (T[j] === ',') break;
        sq += T[j];
        for (var k = 0; k < IDX.areas.length; k++) {
          var a = IDX.areas[k], dist = 0, ok = a.sq === sq;
          if (!ok && sq.length >= 6 && a.sq.charCodeAt(0) === sq.charCodeAt(0) && !(j === i && (STOP[T[i]]))) { var mx = maxEdits(sq.length); if (Math.abs(a.sq.length - sq.length) <= mx && dl(sq, a.sq, mx) <= mx) { ok = true; dist = 1; } }
          if (ok) { var sc = (j - i + 1) * 10 + a.sq.length - dist * 6; if (!best || sc > best.sc) best = { area: a, s: i, e: j + 1, sc: sc }; }
        }
      }
    }
    return best;
  }

  /* ---- ranking by words (closest matches, text answers) ---- */
  function rankByText(W, only) {
    var q = [];
    W.forEach(function (t) { if (t !== ',' && t.length > 2 && !STOP[t] && !/\d/.test(t)) { var s = stem(t); if (!GENERIC_STEMS[s] && !LEXSTEM[s]) q.push(s); } });
    q = uniq(q);
    if (!q.length) return [];
    var out = [];
    KB.products.forEach(function (p) {
      if (only && only.indexOf(p.id) < 0) return;
      var sc = 0, hit = 0;
      q.forEach(function (s) { if (p.bag[s]) { sc += IDX.idf[s] || 1; hit++; } });
      if (hit) out.push({ id: p.id, sc: sc * (0.6 + 0.4 * hit / q.length), hit: hit });
    });
    out.sort(function (a, b) { return b.sc - a.sc; });
    return out;
  }
  var LEXSTEM = {};
  'add buy order want need get give take show find look see have got sell please thanks hello help tell about know what which where when how many much any some something anything thing things item items product products one ones another also else other more most best good great nice right wrong'.split(' ').forEach(function (x) { LEXSTEM[stem(x)] = 1; });
  function searchText(W) {
    var q = [];
    W.forEach(function (t) { if (t !== ',' && t.length > 2 && !STOP[t]) { var s = stem(t); if (!GENERIC_STEMS[s] && !LEXSTEM[s]) q.push(s); } });
    q = uniq(q);
    if (!q.length) return null;
    var best = null, bs = 0;
    KB.chunks.forEach(function (c) {
      var sc = 0, hit = 0;
      q.forEach(function (s) { if (c.st[s]) { var idf = IDX.cidf[s] || 1; sc += idf; hit++; if (c.sh[s]) sc += 0.7 * idf; } });
      if (!hit) return;
      sc *= hit / q.length;
      if (hit >= 2 || (q.length === 1 && sc >= 2.2)) if (sc > bs) { bs = sc; best = c; }
    });
    return best && bs >= 2.6 ? { c: best, score: bs } : null;
  }

  /* ---- stores: retailer, area or neighbourhood, direct name matches, nearest by position ---- */
  function km(a, b) {
    var R = 6371, dLa = (b[0] - a[0]) * Math.PI / 180, dLo = (b[1] - a[1]) * Math.PI / 180;
    var x = Math.sin(dLa / 2) * Math.sin(dLa / 2) + Math.cos(a[0] * Math.PI / 180) * Math.cos(b[0] * Math.PI / 180) * Math.sin(dLo / 2) * Math.sin(dLo / 2);
    return 2 * R * Math.asin(Math.sqrt(x));
  }
  function storePick(T, S) {
    var ch = spanLookup(T, IDX.chains, 5, null), ar = areaSearch(T), cover = [], k;
    if (ch) for (k = ch.s; k < ch.e; k++) cover[k] = true;
    if (ar) for (k = ar.s; k < ar.e; k++) cover[k] = true;
    var W = [];
    T.forEach(function (x, i) { if (x !== ',' && !cover[i] && x.length > 2 && !STOP[x]) W.push(stem(x)); });
    var chain = ch ? ch.id : null, list = KB.stores.filter(function (s) { return !chain || s.ch === chain; });
    var direct = [];
    list.forEach(function (s) {
      var hit = 0;
      W.forEach(function (x) { if (s.st[x]) hit += (s.nt.indexOf(x) > -1 ? 2 : 1); });
      if (ar) { var an = ar.area.t.map(stem); an.forEach(function (x) { if (s.st[x]) hit += 2; }); }
      if (hit) direct.push({ s: s, hit: hit });
    });
    var ll = ar ? ar.area.ll : null;
    direct.forEach(function (x) { x.d = ll ? km(ll, x.s.ll) : 0; });
    direct.sort(function (a, b) { return b.hit - a.hit || a.d - b.d; });
    var near = [];
    if (ll) { near = list.map(function (s) { return { s: s, d: km(ll, s.ll) }; }).sort(function (a, b) { return a.d - b.d; }); }
    // unique malls (a mall can hold two retailers, keep the chain's own order)
    var picked = [], seen = {};
    direct.concat(near).forEach(function (x) { if (picked.length < 3 && !seen[x.s.k]) { seen[x.s.k] = 1; picked.push(x); } });
    return { chain: chain, area: ar ? ar.area.n : null, chainSpan: ch, areaSpan: ar, picks: picked.map(function (x) { return x.s.k; }), direct: direct.length, total: list.length, ll: ll };
  }

  /* ================================================================== 3. DIALOGUE: what the shopper means */
  var RE = {
    red: /\b(chest pain|pain in (my )?chest|chest (is )?(tight|hurts|crushing)|tight(ness)? (in|of) (my )?chest|heart attack|(cannot|can not|hard to|difficulty|trouble|struggling to|unable to) breath\w*|difficulty breathing|short(ness)? of breath|gasping|stopped breathing|not breathing|choking|can not breathe|stroke|face (is )?droop\w*|slurred speech|sudden (numbness|weakness|confusion)|worst headache|thunderclap|(severe|heavy|uncontrolled|non ?stop|profuse) bleeding|bleeding (heavily|a lot|badly|profusely|non ?stop)|(will not|wont|cannot) stop bleeding|vomit\w* blood|cough\w* (up )?blood|blood in (my )?(stool|urine|vomit|poo)|bloody (stool|poo|urine)|unconscious|passed out|collaps\w+|fainted|not responding|unresponsive|seizure|convuls\w+|overdos\w+|took too many|swallowed (a lot|too many|the whole|a whole)|poison\w*|suicid\w*|kill (myself|me)|end (my|it all)|want to die|self ?harm|hurt(ing)? myself|no reason to live|anaphyla\w*|allergic reaction|(swollen|swelling) (face|lips|tongue|throat)|throat (is )?closing|baby (is )?(not|turning|limp)|newborn fever|dying|i am dying|ambulance|emergency)\b/,
    selfharm: /\b(suicid\w*|kill (myself|me)|end (my|it all)|want to die|self ?harm|hurt(ing)? myself|no reason to live)\b/,
    greet: /^(hi|hello|hey|hiya|helo|hallo|howdy|greetings|hai|yo|sup|good (morning|afternoon|evening|day)|morning|afternoon|evening)\b/,
    thanks: /\b(thanks|thank you|cheers|appreciate it|much appreciated|many thanks|thank u)\b/,
    bye: /^(bye|goodbye|good bye|see you|see ya|cya|goodnight|good night|take care|that is all|that is it|nothing else|i am done|all done|that will be all|no more|nothing more|that is everything|i am good|i am all set)\b/,
    help: /^(help|menu|options|what can you do|how does this work|how do i use this|what do you do|can you help( me)?|how can you help( me)?|what can i (ask|do)|commands|instructions|guide me|i need help|need help|help me|start|hello help)$/,
    bot: /\b(are you (a |an )?(bot|robot|human|real|person|ai|machine|chatbot|automated|live|real person|pharmacist|doctor)|you are (a )?(bot|robot|human|real|ai)|who are you|what are you|is this (a )?(bot|human|live|real|robot|ai)|am i (talking|chatting|speaking) (to|with)|who (made|built|created) you|how do you (work|learn)|do you (learn|remember)|what (do|can) you know|your name|what is your name|are you (chatgpt|gpt|claude|siri|alexa)|which (ai|model))\b/,
    how: /^(how are you|how are you doing|how is it going|how do you do|whats up|what is up|how r you)$/,
    cancel: /^(cancel|never ?mind|forget it|forget that|stop|stop it|ignore that|scrap that|leave it|abort|drop it|no need|not now|skip|skip it|go back|back|cancel that|cancel it)$/,
    reset: /^(start over|restart|reset|new chat|clear chat|begin again|start again|begin|from the start|reset chat|start fresh)$/,
    yes: /^(yes|yes please|please do|sure|ok|okay|alright|all right|fine|go ahead|do it|confirm|confirmed|correct|right|exactly|that is right|that is correct|sounds good|good|please|yes go ahead|ok go ahead|yes confirm|of course|definitely|absolutely|certainly|why not|sure thing|y|can|can can|ok can|yes can|add it|add them|add that|add this|do so|proceed|go|continue|yes add|yes add it|okay add|ok add|that one|this one|that is the one|that one please|yes that one|yes that is it|yes it is|i do|please add|please add it|go on|sure add|sure add it|ok please|okay please|yes ok|yes sure)( please| lah)?$/,
    no: /^(no|no thanks|no thank you|not really|not now|no need|do not|do not do that|do not add|not that|wrong|that is wrong|that is not it|not what i meant|cancel that|do not add it|stop|no stop|no no|nah|never|not that one|none|none of them|neither)( thanks| thank you| please)?$/,
    bagCue: /\bbag\b/,
    bagShow: /\b(show|view|see|check|open|display|list|review|look at|what is in|what do i have|whats in|what have i|contents|how many (items|things)|what is my|my total|subtotal|sub total|total (so far|now)|so far|how much (is|are) (my|the) (bag|total|order))\b/,
    clear: /\b(clear|empty|reset|remove (everything|all)|delete (everything|all)|clear out|start fresh|cancel (my )?(whole |entire )?(order|bag)|cancel everything|take (everything|all) out|dump (the )?bag|empty out|wipe)\b/,
    checkout: /\b(check ?out|pay now|proceed to (payment|checkout|pay)|place (my |the |an )?order|complete (my |the )?(order|purchase)|ready to pay|buy now|i am ready to pay|pay for (it|this|these|my|everything)|let me pay|submit (my )?order|confirm (my )?order|go to (checkout|payment)|make (the |my )?payment|finali[sz]e|i want to pay|take me to (checkout|payment)|proceed|pay up)\b/,
    payq: /\b(how (do|can|to|should) (i |we )?pay|payment (method|option|type)s?|which (payment|card)|what (payment|card)|accept|paynow|credit card|debit card|visa|master ?card|amex|grab ?pay|apple pay|google pay|paypal|cash on delivery|cod\b|instal+ment|atome|hoolah|pay (by|with|using)|can i pay|do you take|bank transfer|nets|ewallet|e wallet|pay on delivery|pay later)\b/,
    remove: /\b(remove|delete|take out|take off|drop|discard|get rid of|cancel|minus|subtract|scrap|do not want|no longer want|changed my mind about|take away|cut|reduce)\b/,
    undo: /^(undo|undo that|undo it|undo last|oops|oh no|wrong one|i did not mean (that|it)|mistake|that was a mistake|go back|take that back|reverse that|revert)\b/,
    setq: /\b(change|make|set|update|adjust|edit|amend|switch|modify)\b|\b(instead|only|just)\b/,
    more: /\b(another|one more|1 more|extra|add one more|plus one|a second|one extra|more of (it|them|that|this))\b/,
    stores: /\b(where (can|do|could|should) (i |we )?(buy|get|find|purchase|see)|where (to|do you sell)|where is it sold|where can it be bought|stockists?|outlets?|branch(es)?|stores? (near|in|at|around)|any (store|stores|shop|shops|pharmacy|pharmacies|outlet|branch) (near|in|at|around|that|which|nearby)|near (me|us|here)|nearby|nearest|closest|physical (store|shop|location)|in ?store|walk ?in|which (store|pharmacy|stores|pharmacies|shop|shops|mall|malls)|find (a |the |your )?(store|shop|pharmacy|outlet|branch)|store (locator|finder|list)|pharmacies?|guardian|watsons?|nhgp|nhg|polyclinics?|fair ?price|ntuc|essentials|retailers?|supermarkets?|sell (it |this |these )?(at|in)|available (at|in)|carry (it |this )?(at|in)|stocked (at|in)|do (you|u) have (a )?(store|shop|branch|outlet|physical)|visit (the |a |your )?(store|shop)|buy (it |this |them )?(at|in|from) (a )?(store|shop|pharmacy|guardian|watsons|nhgp|fairprice)|where (is|are) (the )?(store|stores|shop|shops|pharmacy|pharmacies))\b/,
    where_buy: /\bwhere\b.*\b(buy|get|find|purchase|sell|sold|available|stock\w*)\b/,
    orderStatus: /\b(track(ing)?|where is my (order|parcel|package|delivery|item|stuff)|order status|status of (my )?order|(my|the) order (status|number|id|is (late|delayed|missing))|has my order|did my order|have i (received|got)|not (yet )?(received|arrived|delivered)|invoice|receipt|confirmation (email|mail)|cancel (my )?order|change (my )?(order|address|delivery)|modify (my )?order|amend (my )?order|order history|past orders?|previous orders?|my orders?)\b/,
    returns: /\b(returns?|refunds?|exchange|replace(ment)?|damaged|broken|wrong item|missing item|faulty|defective|money back|warranty|complain\w*|spoilt|spoiled|expired product|leaking|leaked|missing parts?)\b/,
    delivery: /\b(deliver\w*|ship\w*|courier|postage|post to|arrive|arrival|when (will|can|do) (it|i|my|you)|how long (will|does|to|is|for)|how fast|free (delivery|shipping)|delivery (fee|charge|cost|time|days|date)|same day|next day|express|island ?wide|overseas|international|abroad|malaysia|indonesia|philippines|vietnam|hong kong|australia|thailand|outside singapore|p ?o box|restricted area|self ?collect\w*|pick ?up|collect(ion)? (my|the|it|in)|minimum (order|spend|purchase)|min spend|how much (to|do i) (spend|need)|free above|free over|threshold)\b/,
    overseas: /\b(overseas|international|abroad|malaysia|indonesia|philippines|vietnam|hong kong|australia|thailand|outside singapore|other countr\w+|china|japan|korea|usa|uk|europe|dubai|brunei|taiwan|india|ship to|deliver to (my )?(friend|family|relative)? ?(in|to)? ?(overseas|another country))\b/,
    gst: /\b(gst|tax|inclusive|exclusive|incl|excl|vat|prices? include|including gst|inclusive of)\b/,
    contact: /\b(contact|call|phone|hotline|telephone|e ?mail|whatsapp|talk to|speak (to|with)|chat with|human|agent|real person|staff|someone|customer (service|care|support)|support|pharmacist|doctor|office|address|where are you|location|visit you|head ?quarters?|hq|opening hours|office hours|business hours|working hours|hours|reach you|get in touch|number|enquir\w+|inquir\w+|feedback|complain\w*)\b/,
    trade: /\b(trade|reseller|resellers|resell|wholesale|wholesaler|distributor|distributors|distribution|bulk (order|buy|purchase|price|pricing|discount)|b2b|become a (stockist|reseller|distributor)|retail partner|partner(ship)?|supply (my|our)|carry your products|stock your|import|export|oem|private label|clinic account|pharmacy account|corporate (order|gift|purchase)|trade (account|price|pricing|enquiry))\b/,
    about: /\b(about (you|hst|the company|us|your company)|who (is|are) hst|what is hst|who owns|company|history|since when|founded|founder|established|kowa|heng say tong|1994|1930|our story|where (are you|is hst) from|made by|owner|parent company|subsidiary|brands?|rheuma salve (brand|company)|how old|how long (have you|has hst)|your story|singapore (brand|company)|hst medical (is|are)|tell me about hst|what (does|do) hst|who is behind|mission|motto|higher stronger together)\b/,
    awards: /\b(awards?|winner|won|prize|recogni[sz]ed|trophy|best seller award|guardian awards?|beauty insider)\b/,
    quality: /\b(gmp|quality|certif\w+|standards?|tested|testing|regulated|approved|hsa|licen[sc]e\w*|safe to (use|take|buy)|trust(ed|worthy)?|reliable|good manufacturing|made (properly|safely)|pharmaceutical grade|authenticity)\b/,
    genuine: /\b(genuine|authentic|fake|fakes|counterfeit|original|legit|scam|real (product|stuff|deal)|is this (real|legit|original)|copy|imitation|trustworthy site|safe to buy (here|online|from you)|verified|official)\b/,
    promo: /\b(promo\w*|discounts?|offers?|sale|sales|vouchers?|coupons?|promo ?codes?|discount codes?|deals?|cheaper|cash ?back|special price|buy (1|one) get (1|one)|free gift|flash sale|clearance|member(ship)?|loyalty|points|rewards?|student discount|first order|new customer|referral|any (promotion|discount|offer)|price match|bargain|lowest price|best price)\b/,
    tele: /\b(telegram|channel|follow (you|us)|subscribe|newsletter|updates|social media|facebook|instagram|tiktok|youtube|linkedin)\b/,
    privacy: /\b(privacy|pdpa|personal data|data protection|my data|my information|cookies?|terms (and|&) conditions|terms of (sale|use|service)|t ?& ?cs?|is my (data|info)|store my|collect my|delete my data|forget me)\b/,
    notes: /\b(health notes?|blog|articles?|read(ing)?( material)?|guides?|tips|advice articles?|write ?ups?|what to read|learn more|educational)\b/,
    catalogue: /\b(catalog(ue)?s?|brochure|flip ?book|product sheets?|data sheets?|spec sheets?|pdf|leaflet|e ?book|the book|digital book|lookbook|full list|range book|magazine)\b/,
    howto: /\b(how (do|can|to|should) (i |we )?(buy|order|purchase|shop|use (this|the) (site|website|chat)|place an order|get started|add (to|things)|checkout|check out)|how does (ordering|buying|shopping|the shop|the site|checkout) work|steps to (buy|order)|ordering process|how to (buy|order))\b/,
    nav: /\b(go to|open|take me to|show me the|link (to|for)|where is the|navigate|bring me to|jump to|visit)\b/,
    giftcard: /\b(gift (card|voucher|certificate)|e ?gift)\b/,
    compare: /\b(compare|comparison|differences?|different|versus|vs|which (one )?(is|are) (better|best|stronger|cheaper|safer)|better (than|for)|between|or which|which (should|would|do) (i|you)|tell the difference|what sets|same as|similar to|alternatives? (to|for))\b/,
    strongAdd: /^(please |pls |can you |could you |kindly )?(add|buy|purchase|order|grab|get|put|include|chuck|throw|reserve|bring|send|pick|select|choose|give|i ?ll (take|have|get|go for)|i will (take|have|get|go for))\b|\b(i want|i need|i would like|i will (take|have|get)|let me (get|have|buy|take|order)|can i (get|have|buy|order)|may i (get|have|buy|order)|could i (get|have|buy|order)|give me|get me|bring me|send me|looking to buy|want to (buy|order|get|add)|going to (buy|order|get)|need to (buy|order|get)|like to (buy|order|get|add)|buy me|order me|put (it|them|that|this)? ?in (my |the )?bag|add (it|them|that|this|these|those)? ?(to|into|in) (my |the )?bag|go for|go with|settle for|take (it|them|one|two|three|this|that|these))\b/,
    addVerb: /\b(add|buy|purchase|order|grab|get|put|include|chuck|throw|reserve|bring|send|pick|select|choose|give|want|need|like|take|have|i ?ll take|looking for|interested in|go for|go with)\b/,
    qtyChange: /\b(make it|make that|set (it|that|them)? ?(to)?|change (it|that|them|the (qty|quantity|number|amount))? ?(to)?|update (it|that|them)? ?(to)?|change \w+ (to|into)|make \w+ (to|into)|(qty|quantity|amount|number) (to|of|=)|only (want|need)? ?\d|just (want|need)? ?\d|make (the )?(qty|quantity) \d|reduce (it |that |them )?to|increase (it |that |them )?to|bring (it |that |them )?(down|up) to|down to|up to \d)\b/,
    price: /\b(price|prices|pricing|cost|costs|how much|much (is|are|does|do|for)|expensive|cheap|cheaper|cheapest|sgd|dollars?|rate|charge|fee for|priced|worth|berapa|bao duo qian)\b/,
    packs: /\b(packs?|sizes?|variants?|options?|bundles?|twin|triple|value pack|travel (pack|size)|different (sizes|packs)|what sizes|which sizes|pack sizes?|how many (packs|sizes)|come in|comes in|available in|bigger|smaller|larger|multipack|multi ?pack|per box|per bottle|in a (box|pack|bottle)|item code|sku|code)\b/,
    ingredients: /\b(ingredients?|contain\w*|made (of|from|with|out of)|whats in|what is in|active|composition|formula|formulation|content|inside|extract|ginseng in|has (it )?(any )?(menthol|camphor|alcohol|sugar|gelatin|caffeine|steroid|steroids|paraben|parabens|preservatives?|colou?rings?|additives?)|sugar|alcohol|caffeine|steroid|preservatives?|additives?|gluten|dairy|lactose|soy|nuts?|shellfish|fish)\b/,
    usage: /\b(how (to|do i|should i|often|many|much to|long (do|should|can|to)) (use|take|apply|rub|consume|eat|drink|put|dose|massage|wear|store|keep)|usage|use (it|this|them)|dosage|dose|directions|instructions|apply|how often|how many times|when (to|should i|do i|can i) (take|use|apply|drink)|before or after (food|meals?)|with (food|water|milk)|empty stomach|per day|a day|daily|twice|how long (can|should|do|to)|how many (capsules|tablets|gummies|sachets|drops|vegicaps|softgels|sticks|patches|pieces|pills)|take it|use for|can be used|dose for|how to take|how to use|how much should|recommended (dose|dosage|amount|intake)|per serving|serving|morning or night|time of day|at night|bedtime)\b/,
    cautions: /\b(side effects?|safe|safety|caution\w*|warning\w*|allerg\w*|pregnan\w*|breast ?feed\w*|nursing|infant|baby|babies|child|children|kids?|toddlers?|elderly|seniors?|old (folks|people|man|lady)|medication|medicines?|interact\w*|contraindicat\w*|can (i|we|my|a|an|the|he|she|they|you) (use|take|apply|eat|drink|give|have)|can (my )?(child|kid|baby|mum|dad|mother|father|wife|husband|elderly|son|daughter|parents)|suitable|ok for|okay for|ok to|is it ok|is it okay|diabet\w*|blood pressure|hypertension|kidney|liver disease|asthma|surgery|driving|alcohol|overdose|too much|expir\w*|shelf life|storage|store it|keep it|harmful|dangerous|risk|risks|stop using|reaction|rash|irritat\w*|burn|burning|sensitive|sun ?light|drowsy|drowsiness|addictive|habit forming|dependency|long term|long-term|every day|everyday|daily use|young|age limit|how old|minimum age|from what age|what age)\b/,
    origin: /\b(made in|origin|where (is|are) (it|this|they|these) (made|from|manufactured|produced)|manufactur\w*|country|produced|from where|where from|made where|sourced?|where does it come from|imported|source of)\b/,
    halal: /\b(halal|vegan|vegetarian|gelatin|gelatine|pork|alcohol free|kosher|animal (product|ingredient|derived)|plant based|plant-based|veg)\b/,
    sheet: /\b(product sheet|data sheet|spec sheet|sheet|catalogue page|brochure|leaflet|flip ?book|in the book|page number|which page|what page|pdf)\b/,
    stock: /\b(in stock|out of stock|stock|available|availability|sold out|restock|back in stock|do you (still )?have|got stock|is it available|any stock|how many (left|in stock)|currently available)\b/,
    general: /\b(what is|what are|tell me (about|more)|info|information|details?|describe|description|about (the|this|it)|benefit|benefits|good for|what does (it|this) do|what is (it|this) for|used for|for what|purpose|reviews?|ratings?|effective|does it work|any good|worth it|how does (it|this) work|is it good|recommended|popular|best ?seller|bestsellers?|famous|what makes)\b/,
    size: /\b(how (big|large|small|heavy|tall|long)|how many (ml|g|grams?|capsules|tablets|gummies|pieces|sachets|sticks|patches|drops|softgels|vegicaps|pills)|size|weight|volume|dimensions?|what size)\b/,
    recommend: /\b(recommend\w*|suggest\w*|good for|best for|help (with|for|me|my)|something (for|to|that)|anything (for|to|that)|got any|any (product|products|remedy|remedies|supplement|supplements)|what (should|can|do|would) (i|you)|which (one )?(should|do|would|is best|is good|works)|what (is|are) (good|best|the best)|looking for|i (have|got|am having|am suffering|suffer)|my \w+ (hurts?|aches?|is (sore|hurting|aching|painful))|suffering|struggling|treat|relieve|cure|remedy|remedies|fix|solution|to help|ease|soothe|what do you have for|do you have (anything|something|any)|can you recommend|what to take|what to use|what to buy|options for|ideas? for|for my|for the)\b/,
    browse: /\b(show|see|list|browse|view|what do you (have|sell|carry|stock|offer)|what (products|items|things) (do you have|are there)|range|all (the )?(products|items|your products|categories|ranges)|categories|category|catalog|everything|full (range|list)|what (else|more)|other (products|items|things|options)|more (products|items|options)|shelf|shelves|aisle|section)\b/,
    unknownThing: /\b(tiger balm|salonpas|panadol|ponstan|voltaren|strepsils|vicks|eagle brand|axe oil|po chai|bak foong|hiruscar|durex|viagra|cialis|ozempic|wegovy|paracetamol|ibuprofen|aspirin|antibiotics?|prozac|valium|xanax|codeine|morphine|steroids?)\b/
  };
  var GREET_ONLY_MAX = 6;
  var ASPECTS = [['sheet', RE.sheet], ['stock', RE.stock], ['halal', RE.halal], ['origin', RE.origin], ['usage', RE.usage], ['ingredients', RE.ingredients], ['cautions', RE.cautions], ['packs', RE.packs], ['price', RE.price], ['size', RE.size], ['general', RE.general]];

  function mk(intent, extra) { var r = { intent: intent, items: [], slugs: [], flags: {} }; if (extra) for (var k in extra) r[k] = extra[k]; return r; }
  function lineSlug(l) { return (l.id || '').split('|')[0]; }
  function freshState() { return { last: { focus: null, list: [], aspect: null, intent: null, cat: null, area: null, chain: null, added: null, topic: null }, pending: null, bag: [], mem: { aliases: {}, packs: {}, last: [], area: null }, turn: 0, page: null }; }
  function normState(s) {
    var f = freshState();
    if (!s || typeof s !== 'object') return f;
    ['last', 'mem'].forEach(function (k) { if (s[k]) for (var z in s[k]) f[k][z] = s[k][z]; });
    f.pending = s.pending || null; f.bag = s.bag || []; f.turn = s.turn || 0; f.page = s.page || null;
    f.mem.aliases = f.mem.aliases || {}; f.mem.packs = f.mem.packs || {}; f.mem.last = f.mem.last || [];
    return f;
  }

  /* ---- "it", "the second one", "both" ... resolved against what was just shown ---- */
  function refOwners(A, S) {
    var W = A.W, t = A.t, L = (S.last.list || []).filter(function (id) { return prod(id); }), foc = S.last.focus && prod(S.last.focus) ? S.last.focus : null, i, o;
    var plain = W.filter(function (x) { return x !== ','; });
    // ordinal: "the second one", "2nd", "last", "number 2", or just "2" when a list is on screen
    for (i = 0; i < plain.length; i++) {
      var w1 = plain[i];
      if (ORD[w1] !== undefined && L.length) { var ix = ORD[w1] < 0 ? L.length - 1 : ORD[w1]; if (L[ix]) return { owners: [L[ix]], kind: 'ord', idx: ix }; }
      if ((w1 === 'number' || w1 === 'no' || w1 === 'num' || w1 === 'option' || w1 === 'item') && /^\d$/.test(plain[i + 1] || '') && L.length && L[+plain[i + 1] - 1]) return { owners: [L[+plain[i + 1] - 1]], kind: 'ord', idx: +plain[i + 1] - 1 };
    }
    if (plain.length <= 2 && /^\d$/.test(plain[plain.length - 1] || '') && L.length > 1 && L[+plain[plain.length - 1] - 1] && !/\b(add|buy|x)\b/.test(t)) return { owners: [L[+plain[plain.length - 1] - 1]], kind: 'ord', idx: +plain[plain.length - 1] - 1 };
    if (/\b(both|all (of )?(them|these|those|three|four|five|the above)|each|every one|all)\b/.test(t) && L.length) return { owners: L.slice(0, 5), kind: 'all' };
    if (/\b(cheaper|cheapest|least expensive|lowest price|budget one|cheap one)\b/.test(t) && L.length) { var c = L.slice().sort(function (a, b) { return (prod(a).min || 1e9) - (prod(b).min || 1e9); }); return { owners: [c[0]], kind: 'cheap' }; }
    if (/\b(expensive|priciest|most expensive|premium one|pricier|dearest)\b/.test(t) && L.length) { var e = L.slice().sort(function (a, b) { return (prod(b).min || 0) - (prod(a).min || 0); }); return { owners: [e[0]], kind: 'dear' }; }
    if (/\b(them|those|these|ones)\b/.test(t) && L.length > 1) return { owners: L.slice(0, 5), kind: 'all' };
    if (/\b(it|this|that|this one|that one|the same|same one|same|the one|one)\b/.test(t) && (foc || L.length)) return { owners: [foc || L[0]], kind: 'focus' };
    if (foc && /\b(this product|this item|this one|the product)\b/.test(t)) return { owners: [foc], kind: 'focus' };
    return null;
  }
  function stateRef(A, S) { return refOwners(A, S); }

  /* ---- shared pieces of the add flow ---- */
  function qtyFor(att, used) {
    var q = null, more = false;
    (att.qs || []).forEach(function (x) {
      if (used && used[x.i]) return;
      if (x.kind === 'more') { more = true; return; }
      if (q === null) q = x.v;
    });
    return { qty: q, more: more };
  }
  function narrowOwners(owners, e, A) {
    var sizes = (e.ps || []).filter(function (x) { return x.k === 'size'; }).map(function (x) { return x.v; });
    if (sizes.length) {
      var f = owners.filter(function (id) { var p = prod(id), nm = fold(p.n + ' ' + p.sz); return sizes.some(function (z) { return nm.replace(/\s/g, '').indexOf(z) > -1 || p.vk.some(function (v) { return v.size.indexOf(z) > -1; }); }); });
      if (f.length === 1) return f;
      if (f.length > 1) owners = f;
    }
    if (A && A.aud === 'child') { var k = owners.filter(function (id) { return prod(id).c === 'kids'; }); if (k.length === 1) return k; }
    return owners;
  }
  function resolveAdds(entries, S, A) {
    var items = [], asks = [], skipped = [], notes = [], hold = [];
    entries.forEach(function (e) {
      var owners = e.owners.slice();
      if (owners.length > 1) owners = narrowOwners(owners, e, A);
      var q = qtyFor(e.att, null);
      if (owners.length !== 1) {
        var ok = owners.filter(function (id) { return prod(id).buy; });
        asks.push({ type: 'which', options: owners.slice(0, 6), qty: q.qty || 1, att: e.att, buyable: ok.length });
        return;
      }
      var p = prod(owners[0]);
      if (!p.buy) { skipped.push({ slug: p.id, why: 'request' }); return; }
      var cv = chooseVariant(p, e.att, S), qq = qtyFor(e.att, cv.usedQ), qty = qq.qty || 1;
      if (cv.tie) { asks.push({ type: 'pack', slug: p.id, options: cv.tie, qty: qty }); return; }
      var vi = cv.vi;
      if (!p.vk[vi].p) { var alt = p.vk.findIndex ? p.vk.findIndex(function (v) { return v.p; }) : 0; if (alt < 0) { skipped.push({ slug: p.id, why: 'request' }); return; } vi = alt; }
      var it = { slug: p.id, vi: vi, variant: p.vk[vi].l, qty: Math.max(1, qty), via: cv.via };
      if (it.qty > MAXQ) { it.qty = MAXQ; it.clamped = true; }
      if (cv.none) it.nomatch = true;
      if (it.qty > ASKQ) hold.push(it); else items.push(it);
    });
    return { items: items, asks: asks, skipped: skipped, hold: hold };
  }
  function entriesFromMentions(A, S, M) {
    var att = attach(M, A.qp, A.T);
    return M.map(function (m, i) { return { owners: m.owners, att: att[i], m: m }; });
  }
  function pickOne(A, S, options) {
    // an ordinal, a product word, a size/format word or a price word that singles out one of `options`
    var plain = A.W, i;
    for (i = 0; i < plain.length; i++) {
      if (ORD[plain[i]] !== undefined) { var ix = ORD[plain[i]] < 0 ? options.length - 1 : ORD[plain[i]]; if (options[ix]) return options[ix]; }
    }
    if (plain.length <= 3) { var dg = plain.filter(function (x) { return /^\d$/.test(x); }); if (dg.length === 1 && options[+dg[0] - 1]) return options[+dg[0] - 1]; }
    var hit = A.M.filter(function (m) { return m.owners.some(function (o) { return options.indexOf(o) > -1; }); });
    if (hit.length) {
      var inter = hit[0].owners.filter(function (o) { return options.indexOf(o) > -1; });
      if (inter.length === 1) return inter[0];
      if (inter.length > 1) { var nn = narrowOwners(inter, { ps: (A.qp.ps || []) }, A); if (nn.length === 1) return nn[0]; }
    }
    // tokens that appear in exactly one option's name (digits included: "10mg")
    var cnt = options.map(function (id) { var p = prod(id), nt = fold(p.n + ' ' + p.sz).replace(/[^a-z0-9. ]/g, ' ').split(/\s+/), c = 0; plain.forEach(function (x) { if (x.length > 1 && !STOP[x] && !FILL[x] && nt.indexOf(x) > -1) c++; }); return c; });
    var mx = Math.max.apply(null, cnt);
    if (mx > 0 && cnt.filter(function (c) { return c === mx; }).length === 1) return options[cnt.indexOf(mx)];
    if (/\b(cheaper|cheapest|cheap|lowest|smaller|small|budget)\b/.test(A.t)) { return options.slice().sort(function (a, b) { return (prod(a).min || 1e9) - (prod(b).min || 1e9); })[0]; }
    if (/\b(expensive|priciest|bigger|big|larger|premium)\b/.test(A.t)) { return options.slice().sort(function (a, b) { return (prod(b).min || 0) - (prod(a).min || 0); })[0]; }
    return null;
  }

  /* ---- need / recommendation list ---- */
  function recommendFor(A, S, needs) {
    var list = [], why = {}, notes = [], cats = [];
    needs.forEach(function (n) {
      var nd = needById(n.id);
      nd.p.forEach(function (x, i) { if (list.indexOf(x.s) < 0) list.push(x.s); if (!why[x.s]) why[x.s] = x.why; });
      if (nd.note) notes.push(nd.note);
      nd.cats.forEach(function (c) { if (cats.indexOf(c) < 0) cats.push(c); });
    });
    // interleave when two needs: keep the first pick of each first
    if (needs.length > 1) {
      var firsts = [], rest = [];
      needs.forEach(function (n) { var nd = needById(n.id); nd.p.forEach(function (x, i) { (i === 0 ? firsts : rest).push(x.s); }); });
      list = uniq(firsts.concat(rest));
    }
    // a product or format word in the same message (balm, syrup, patch ...) goes first
    var named = [];
    A.M.forEach(function (m) { m.owners.forEach(function (o) { if (named.indexOf(o) < 0) named.push(o); }); });
    var pri = named.filter(function (o) { return list.indexOf(o) > -1; });
    if (pri.length) list = uniq(pri.concat(list));
    else if (named.length && named.length <= 4) list = uniq(named.concat(list));
    if (/\b(cheap|cheaper|cheapest|budget|affordable|low price|inexpensive|save)\b/.test(A.t)) list = list.slice().sort(function (a, b) { return (prod(a).min || 1e9) - (prod(b).min || 1e9); });
    var kids = A.aud === 'child' && needs.every(function (n) { return n.id !== 'kids' && n.id.indexOf('kids') !== 0; });
    return { list: list, why: why, notes: uniq(notes), cats: cats, kidsCaution: kids };
  }

  function audienceOf(A) { for (var i = 0; i < A.W.length; i++) if (AUD[A.W[i]]) return AUD[A.W[i]]; return null; }

  /* ---- analyse one message ---- */
  function analyze(raw, S) {
    var T = normalize(raw), W = T.filter(function (x) { return x !== ','; });
    var A = { raw: raw, T: T, W: W, t: W.join(' '), S: S };
    A.M = findMentions(T, S);
    A.cover = [];
    A.M.forEach(function (m) { for (var k = m.s; k < m.e; k++) A.cover[k] = true; });
    A.qp = scanQtyPack(T, A.cover);
    A.needs = detectNeeds(T, A.cover);
    A.aud = audienceOf(A);
    A.caution = RE_CAUTION.test(A.t);
    return A;
  }

  function isYes(A) { var t = A.t; return RE.yes.test(t) || (A.W.length <= 4 && /^(yes|ok|okay|sure|confirm|go ahead|please do|add|do it|proceed)\b/.test(t) && !A.M.length); }
  function isNo(A) { var t = A.t; return RE.no.test(t) || (A.W.length <= 4 && /^(no|nope|not|do not|stop|cancel|wrong)\b/.test(t) && !A.M.length); }

  /* ---- the add flow: product(s) + quantity + pack -> items, or one clear question ---- */
  function finishAdd(res, S, R) {
    R.items = res.items; R.skipped = res.skipped;
    res.items.forEach(function (it) { if (it.via === 'said') S.mem.packs[it.slug] = it.variant; });
    if (res.hold.length) { R.ask = { type: 'confirm', action: 'add', items: res.hold }; S.pending = { type: 'confirm', action: 'add', items: res.hold, next: res.asks }; }
    else if (res.asks.length) { var a = res.asks[0]; R.ask = a; S.pending = clone(a); S.pending.next = res.asks.slice(1); S.pending.orig = 'add'; }
    else S.pending = null;
    var ids = res.items.map(function (i) { return i.slug; }).concat(res.hold.map(function (i) { return i.slug; }));
    S.last.intent = 'add'; S.last.aspect = null;
    if (ids.length) { S.last.focus = ids[ids.length - 1]; S.last.list = uniq(ids); }
    if (R.ask && R.ask.options) { S.last.list = R.ask.options.slice(); if (R.ask.type === 'pack') S.last.focus = R.ask.slug; }
    S.last.added = res.items.map(function (i) { return { slug: i.slug, vi: i.vi, variant: i.variant, qty: i.qty }; });
    R.slugs = uniq(ids);
    return R;
  }
  function addFlow(A, S, refs) {
    var M = A.M, entries = null, R = mk('add');
    if (M.length) {
      if (M.every(function (m) { return m.owners.length > 7; })) return mk('browse', { brand: 'Heritage', slugs: M[0].owners.slice(0, 8) });
      entries = entriesFromMentions(A, S, M.filter(function (m) { return m.owners.length <= 7; }));
    } else if (refs) {
      var qq = A.qp.qs.filter(function (x) { return x.kind !== 'more'; }), q0 = qq.length ? qq[0].v : null;
      if (refs.kind === 'all') entries = refs.owners.map(function (o) { return { owners: [o], att: { qs: q0 ? [{ i: 0, v: q0, kind: 'num' }] : [], ps: [] } }; });
      else entries = [{ owners: refs.owners, att: { qs: A.qp.qs, ps: A.qp.ps } }];
    } else return null;
    var res = resolveAdds(entries, S, A);
    R.refKind = refs ? refs.kind : null;
    return finishAdd(res, S, R);
  }
  function resumeWhich(P, pick, A, S) {
    var att = P.att || { qs: [], ps: [] };
    var ps = (att.ps || []).concat(A.qp.ps || []);
    var qs = (att.qs || []).slice();
    if (!qs.length && P.qty && P.qty > 1) qs = [{ i: 0, v: P.qty, kind: 'num' }];
    var res = resolveAdds([{ owners: [pick], att: { qs: qs, ps: ps } }], S, A);
    var R = mk('add', { resumed: 'which' });
    var rest = P.next || [];
    finishAdd(res, S, R);
    if (!S.pending && rest.length) { S.pending = clone(rest[0]); S.pending.next = rest.slice(1); R.ask = rest[0]; }
    return R;
  }
  function infoR(slugs, aspect, S, extra) {
    var R = mk('info', { slugs: slugs, aspect: aspect || 'general' });
    if (extra) for (var k in extra) R[k] = extra[k];
    S.last.intent = 'info'; S.last.aspect = R.aspect;
    S.last.list = slugs.slice(); S.last.focus = slugs[0] || S.last.focus;
    return R;
  }
  function finishConfirm(P, S) {
    var R = mk(P.action === 'clear' ? 'clear' : P.action, { confirmed: true, items: P.items || [] });
    if (P.action === 'add') {
      var it = (P.items || []).map(function (i) { return { slug: i.slug, vi: i.vi, variant: i.variant, qty: i.qty, via: i.via }; });
      R.items = it; S.last.added = it.map(function (i) { return { slug: i.slug, vi: i.vi, variant: i.variant, qty: i.qty }; });
      var nx = P.next || [];
      if (nx.length) { S.pending = clone(nx[0]); S.pending.next = nx.slice(1); R.ask = nx[0]; }
    }
    return R;
  }

  function continuePending(A, S) {
    var P = S.pending, t = A.t, n = A.W.length, yes = isYes(A), no = isNo(A), R, pick, strongNew = RE.strongAdd.test(t) && A.M.length && n > 3;
    if (!P) return null;
    switch (P.type) {
      case 'confirm':
        if (yes) { S.pending = null; return finishConfirm(P, S); }
        if (no || RE.cancel.test(t)) { S.pending = null; return mk('cancel', { was: 'confirm' }); }
        if (P.action === 'add' && n <= 4) {
          var nq = A.qp.qs.filter(function (x) { return x.kind !== 'more'; });
          if (nq.length) { var items = P.items.map(function (i) { var c = clone(i); c.qty = Math.min(MAXQ, nq[0].v); return c; }); if (nq[0].v > ASKQ) { S.pending = { type: 'confirm', action: 'add', items: items }; return mk('add', { ask: { type: 'confirm', action: 'add', items: items } }); } S.pending = null; return finishConfirm({ action: 'add', items: items }, S); }
        }
        break;
      case 'which':
        if (strongNew) break;
        if (n <= 5 || !RE.strongAdd.test(t)) pick = pickOne(A, S, P.options);
        if (pick) { S.pending = null; if (P.orig === 'info') return infoR([pick], P.aspect, S); return resumeWhich(P, pick, A, S); }
        if (no || RE.cancel.test(t)) { S.pending = null; return mk('cancel', { was: 'which' }); }
        if (yes && P.options.length > 1) { return mk('add', { ask: P, again: true }); }
        break;
      case 'pack': {
        if (strongNew) break;
        var p = prod(P.slug), ps = A.qp.ps || [], ix = -1, i;
        for (i = 0; i < A.W.length; i++) if (ORD[A.W[i]] !== undefined) { var o = ORD[A.W[i]] < 0 ? P.options.length - 1 : ORD[A.W[i]]; if (P.options[o] !== undefined) ix = P.options[o]; }
        if (ix < 0 && n <= 3) { var dg = A.W.filter(function (x) { return /^\d$/.test(x); }); if (dg.length === 1 && P.options[+dg[0] - 1] !== undefined) ix = P.options[+dg[0] - 1]; }
        if (ix < 0 && ps.length) {
          var cv = chooseVariant(p, { ps: ps, qs: A.qp.qs }, S);
          if (!cv.tie && !cv.none && P.options.indexOf(cv.vi) > -1) ix = cv.vi;
          else if (cv.tie) { var inter = cv.tie.filter(function (z) { return P.options.indexOf(z) > -1; }); if (inter.length === 1) ix = inter[0]; }
        }
        if (ix < 0 && /\b(cheaper|cheapest|smaller|small|lowest)\b/.test(t)) ix = P.options.slice().sort(function (a, b) { return (p.vk[a].p || 1e9) - (p.vk[b].p || 1e9); })[0];
        if (ix < 0 && /\b(bigger|biggest|larger|largest|best value|more)\b/.test(t) && n <= 4) ix = P.options.slice().sort(function (a, b) { return (p.vk[b].p || 0) - (p.vk[a].p || 0); })[0];
        if (ix >= 0) {
          S.pending = null;
          var qty = Math.min(MAXQ, P.qty || 1), it = { slug: p.id, vi: ix, variant: p.vk[ix].l, qty: qty, via: 'said' };
          S.mem.packs[p.id] = it.variant;
          R = mk('add', { items: [it], resumed: 'pack' });
          S.last.intent = 'add'; S.last.focus = p.id; S.last.list = [p.id]; S.last.added = [{ slug: p.id, vi: ix, variant: it.variant, qty: qty }];
          var nx = P.next || [];
          if (nx.length) { S.pending = clone(nx[0]); S.pending.next = nx.slice(1); R.ask = nx[0]; }
          return R;
        }
        if (no || RE.cancel.test(t)) { S.pending = null; return mk('cancel', { was: 'pack' }); }
        break;
      }
      case 'qty': {
        var q = A.qp.qs.filter(function (x) { return x.kind !== 'more'; });
        if (q.length && n <= 5) {
          S.pending = null;
          var p2 = prod(P.slug), qv = Math.min(MAXQ, Math.max(1, q[0].v));
          var it2 = { slug: p2.id, vi: P.vi || 0, variant: p2.vk[P.vi || 0].l, qty: qv, via: 'said' };
          S.last.intent = 'add'; S.last.focus = p2.id; S.last.added = [{ slug: p2.id, vi: it2.vi, variant: it2.variant, qty: qv }];
          if (qv > ASKQ) { S.pending = { type: 'confirm', action: 'add', items: [it2] }; return mk('add', { ask: { type: 'confirm', action: 'add', items: [it2] } }); }
          return mk('add', { items: [it2], resumed: 'qty' });
        }
        if (no || RE.cancel.test(t)) { S.pending = null; return mk('cancel', { was: 'qty' }); }
        break;
      }
      case 'dym': {
        pick = null;
        if (yes && P.options.length) pick = P.options[0];
        if (!pick && n <= 5) pick = pickOne(A, S, P.options);
        if (pick) {
          S.pending = null;
          var learn = null;
          if (P.phrase && P.phrase.length >= 3) { S.mem.aliases[P.phrase] = pick; var keys = Object.keys(S.mem.aliases); if (keys.length > 80) delete S.mem.aliases[keys[0]]; learn = { phrase: P.phrase, slug: pick }; }
          var orig = P.orig || { intent: 'info' };
          var out;
          if (orig.intent === 'add') {
            var att = { qs: orig.qty && orig.qty > 1 ? [{ i: 0, v: orig.qty, kind: 'num' }] : [], ps: [] };
            out = finishAdd(resolveAdds([{ owners: [pick], att: att }], S, A), S, mk('add', { resumed: 'dym' }));
          } else out = infoR([pick], orig.aspect || 'general', S);
          out.learn = learn;
          return out;
        }
        if (no || RE.cancel.test(t)) { S.pending = null; return mk('cancel', { was: 'dym' }); }
        break;
      }
      case 'area': {
        var sp = storePick(A.T, S);
        if (sp.areaSpan || sp.chainSpan || sp.direct) { S.pending = null; return storeR(sp, A, S); }
        if (/\b(any|anywhere|all|everywhere|whole)\b/.test(t)) { S.pending = null; return storeR(sp, A, S); }
        if (no || RE.cancel.test(t)) { S.pending = null; return mk('cancel', { was: 'area' }); }
        break;
      }
      case 'infoWhich': {
        if (A.M.length) { S.pending = null; var ow = A.M[0].owners; return infoR(ow.slice(0, 4), P.aspect, S); }
        pick = n <= 5 ? pickOne(A, S, (S.last.list || [])) : null;
        if (pick) { S.pending = null; return infoR([pick], P.aspect, S); }
        if (no || RE.cancel.test(t)) { S.pending = null; return mk('cancel', { was: 'info' }); }
        break;
      }
      case 'bagclear':
        if (yes) { S.pending = null; return mk('clear', { confirmed: true }); }
        if (no || RE.cancel.test(t)) { S.pending = null; return mk('cancel', { was: 'clear' }); }
        break;
    }
    S.pending = null;
    return null;
  }

  function storeR(sp, A, S) {
    var R = mk('stores', { area: sp.area, retailer: sp.chain, stores: sp.picks, direct: sp.direct, total: sp.total, ll: sp.ll });
    if (sp.area) S.mem.area = sp.area;
    S.last.intent = 'stores'; S.last.area = sp.area || S.last.area; S.last.chain = sp.chain || null; S.last.aspect = null;
    return R;
  }

  /* ---- bag helpers on the state's bag copy ---- */
  function bagLinesFor(S, slug, vi) {
    return (S.bag || []).filter(function (l) { return lineSlug(l) === slug; });
  }
  function removeFlow(A, S, refs) {
    var R = mk('remove'), ents = [];
    if (A.M.length) A.M.forEach(function (m, i) { ents.push({ owners: m.owners, att: entriesFromMentions(A, S, A.M)[i].att }); });
    else if (refs) ents.push({ owners: refs.kind === 'all' ? refs.owners : refs.owners, att: { qs: A.qp.qs, ps: A.qp.ps } });
    else if (/\b(last|latest|recent)\b/.test(A.t) && S.bag.length) { var l = S.bag[S.bag.length - 1]; ents.push({ owners: [lineSlug(l)], att: { qs: A.qp.qs, ps: A.qp.ps } }); }
    else if (S.last.added && S.last.added.length) ents.push({ owners: S.last.added.map(function (x) { return x.slug; }), att: { qs: A.qp.qs, ps: A.qp.ps } });
    else return null;
    ents.forEach(function (e) {
      e.owners.forEach(function (o) {
        var lines = bagLinesFor(S, o), qs = qtyFor(e.att, null), any = lines.length > 0;
        if (!any) { R.missing = (R.missing || []).concat(o); return; }
        var p = prod(o), cv = e.att.ps && e.att.ps.length ? chooseVariant(p, e.att, S) : null;
        var target = lines;
        if (cv && !cv.tie && cv.via === 'said') { var lab = p.vk[cv.vi].l; var f = lines.filter(function (l) { return l.variant === lab; }); if (f.length) target = f; }
        target.forEach(function (l) { R.items.push({ slug: o, id: l.id, variant: l.variant, qty: qs.qty && !/\b(all|everything|whole)\b/.test(A.t) && A.qp.qs.length && !/\b(remove|delete|take out|cancel|get rid)\b.*\b(all|every)\b/.test(A.t) ? qs.qty : 'all' }); });
      });
    });
    R.slugs = uniq(R.items.map(function (i) { return i.slug; }));
    return R;
  }
  function setQtyFlow(A, S, refs) {
    var R = mk('qty'), ents = [], nums = A.qp.qs.filter(function (x) { return x.kind !== 'more' && x.kind !== 'art'; });
    if (!nums.length) return null;
    var val = nums[nums.length - 1].v;
    if (A.M.length) A.M.forEach(function (m) { ents.push(m.owners); });
    else if (refs && refs.owners) ents.push(refs.owners);
    else if (S.last.added && S.last.added.length) ents.push([S.last.added[S.last.added.length - 1].slug]);
    else if (S.bag.length) ents.push([lineSlug(S.bag[S.bag.length - 1])]);
    else return null;
    ents.forEach(function (owners) {
      owners.forEach(function (o) {
        var lines = bagLinesFor(S, o);
        if (!lines.length) { R.missing = (R.missing || []).concat(o); return; }
        lines.forEach(function (l) { R.items.push({ slug: o, id: l.id, variant: l.variant, qty: Math.min(MAXQ, Math.max(0, val)) }); });
      });
    });
    R.slugs = uniq(R.items.map(function (i) { return i.slug; }));
    if (val > MAXQ) R.clamped = true;
    return R;
  }

  /* ---- products named but nothing recognised: ask "did you mean" and remember the answer ---- */
  var FILLER_WORDS = { add: 1, buy: 1, want: 1, need: 1, get: 1, order: 1, please: 1, the: 1, a: 1, an: 1, some: 1, any: 1, of: 1, to: 1, my: 1, bag: 1, for: 1, me: 1, i: 1, you: 1, do: 1, have: 1, got: 1, how: 1, much: 1, is: 1, are: 1, what: 1, price: 1, cost: 1,
    thing: 1, things: 1, stuff: 1, one: 1, ones: 1, item: 1, items: 1, product: 1, products: 1, can: 1, could: 1, would: 1, like: 1, take: 1, give: 1, show: 1, tell: 1, about: 1, with: 1, and: 1, or: 1, in: 1, on: 1, it: 1, this: 1, that: 1, will: 1, am: 1, looking: 1, sell: 1, carry: 1, stock: 1,
    pieces: 1, piece: 1, x: 1, ',': 1, from: 1, your: 1, shop: 1, store: 1, there: 1, here: 1, am_: 1 };
  function contentPhrase(A) {
    var out = [];
    A.T.forEach(function (x, i) { if (x === ',' || A.cover[i] || FILLER_WORDS[x] || NUMW[x] || /^\d+$/.test(x) || /^\u00a4/.test(x) || (x.length < 3)) return; out.push(x); });
    return out.slice(0, 3).join(' ');
  }
  function suggestFor(phrase, A) {
    var sq = phrase.replace(/\s+/g, ''), res = [];
    if (sq.length >= 3) {
      Object.keys(IDX.alias).forEach(function (key) {
        if (key.charCodeAt(0) !== sq.charCodeAt(0) && key.length > 4) return;
        var mx = Math.max(1, Math.floor(Math.max(key.length, sq.length) * 0.4)), dd = dl(sq, key, mx);
        if (dd <= mx) IDX.alias[key].owners.forEach(function (o) { res.push({ id: o, d: dd + (IDX.alias[key].owners.length > 1 ? 0.5 : 0) }); });
      });
    }
    res.sort(function (a, b) { return a.d - b.d; });
    var ids = uniq(res.map(function (x) { return x.id; }));
    if (ids.length < 3) { var tx = rankByText(A.W); tx.forEach(function (x) { if (ids.length < 5 && ids.indexOf(x.id) < 0) ids.push(x.id); }); }
    return ids.slice(0, 3);
  }

  /* ================================================================== the decision */
  function decide(A, S) {
    var t = A.t, W = A.W, n = W.length, M = A.M, L = S.last, R, i;
    if (!n) return mk('help');
    var hasBag = /\bbag\b/.test(t), hasMention = M.length > 0;
    var aspect = null;
    ASPECTS.some(function (a) { if (a[1].test(t)) { aspect = a[0]; return true; } return false; });

    /* 1. red flags always win: stop selling, point to emergency care */
    if (RE.red.test(t)) { S.pending = null; return mk('redflag', { kind: RE.selfharm.test(t) ? 'selfharm' : 'emergency' }); }

    /* 2. an open question from the assistant */
    if (S.pending) { R = continuePending(A, S); if (R) return R; }

    /* 3. cancel / start over / undo */
    if (RE.reset.test(t)) { S.last = freshState().last; S.pending = null; return mk('reset'); }
    if (RE.cancel.test(t)) return mk('cancel');
    if (RE.undo.test(t) && n <= 6) return mk('undo');

    /* 4. small talk (only when nothing shoppable is in the message) */
    var shop = hasMention || A.needs.length > 0;
    if (!shop && n <= GREET_ONLY_MAX) {
      if (RE.how.test(t)) return mk('smalltalk', { kind: 'how' });
      if (RE.greet.test(t) && !RE.help.test(t)) return mk('greet');
      if (RE.thanks.test(t) && !RE.stores.test(t)) return mk('thanks');
      if (RE.bye.test(t)) return mk('bye');
      if (RE.help.test(t)) return mk('help');
      if (RE.bot.test(t)) return mk('bot');
      if (/^(ok|okay|alright|cool|great|nice|good|fine|noted|got it|i see|oh|wow|sure|yes|no|hmm|right|perfect|awesome|lovely|wonderful)( thanks| thank you)?$/.test(t)) return mk('ack');
    }
    if (RE.bot.test(t) && !hasMention && n <= 9) return mk('bot');
    if (RE.thanks.test(t) && n <= 8 && !shop && !RE.stores.test(t)) return mk('thanks');

    var strong = RE.strongAdd.test(t);
    var refs = null;
    if (!hasMention && n <= 14) refs = refOwners(A, S);

    /* 5. bag: show, clear, remove, change quantity, checkout, how to order */
    if (RE.howto.test(t) && !strong) return mk('howto');
    var bagOnly = /^(my |the |view |show |open |see |check |go to |what is in |whats in )*(bag|total|subtotal|sub total|order|items|bag total|order summary)( please| now| so far)?$/.test(t);
    if (bagOnly || (hasBag && RE.bagShow.test(t) && !strong && !RE.clear.test(t) && !hasMention && !/\b(add|put|remove|delete)\b/.test(t))) { S.last.intent = 'bag'; return mk('bag'); }
    if (RE.clear.test(t) && !hasMention && (hasBag || /\b(everything|all)\b/.test(t) || /^(clear|empty)\b/.test(t)) && !RE.strongAdd.test(t)) {
      if (!S.bag.length) return mk('clear', { empty: true });
      S.pending = { type: 'bagclear' }; return mk('clear', { ask: { type: 'confirm', action: 'clear' } });
    }
    var setq = RE.qtyChange.test(t) && A.qp.qs.some(function (x) { return x.kind === 'num' || x.kind === 'word' || x.kind === 'x'; }) && !RE.stores.test(t) && !(strong && !/\b(change|make|set|update|instead|only|just)\b/.test(t));
    if (setq && (hasMention || refs || S.bag.length || (L.added && L.added.length)) && !/\b(add|buy|order)\b/.test(t.replace(/\bmake it\b/, ''))) { R = setQtyFlow(A, S, refs); if (R) return R; }
    if (RE.remove.test(t) && !/\b(remove|get rid of)\b.*\b(pain|ache|cough|cold|stress|wrinkles|scars|acne)\b/.test(t) && (hasBag || hasMention || refs || /\b(last|latest|that|it|everything|all)\b/.test(t)) && !strong) {
      if (/\b(everything|all)\b/.test(t) && !hasMention) { if (!S.bag.length) return mk('clear', { empty: true }); S.pending = { type: 'bagclear' }; return mk('clear', { ask: { type: 'confirm', action: 'clear' } }); }
      R = removeFlow(A, S, refs); if (R) return R;
    }
    if (RE.checkout.test(t) && !(RE.payq.test(t) && /\b(how|which|what|can|do you|methods?|options?|accept)\b/.test(t)) && !hasMention) {
      if (/\bhow\b/.test(t)) return mk('howto');
      S.last.intent = 'checkout'; return mk('checkout');
    }
    if (/^(pay|payment)$/.test(t)) return mk('checkout');

    /* 6. stores */
    var sp = null;
    var storeCue = (RE.stores.test(t) || RE.where_buy.test(t)) && !(strong && hasMention && A.qp.qs.length && !/\b(where|which|near|nearest|store|stores|shop|pharmacy|guardian|watsons|nhgp)\b/.test(t));
    if (RE.trade.test(t) && !/\bwhere\b/.test(t)) { return mk('trade'); }
    if (!storeCue && n <= 6 && L.intent === 'stores') { sp = storePick(A.T, S); if (sp.areaSpan || sp.chainSpan) storeCue = true; }
    if (!storeCue && !hasMention && /\b(deliver|delivery|ship)\b/.test(t) === false && n <= 4) { var ar0 = areaSearch(A.T); if (ar0 && (ar0.e - ar0.s) >= 1 && A.W.length - (ar0.e - ar0.s) <= 2 && /\b(near|at|in|around)\b/.test(t)) storeCue = true; }
    if (storeCue && !RE.orderStatus.test(t)) {
      sp = sp || storePick(A.T, S);
      if (!sp.area && !sp.chain && !sp.direct && /\b(near me|nearby|nearest|closest|near here|around here|near us)\b/.test(t) && S.mem.area) { sp = storePick(tokenize(S.mem.area), S); }
      var R2 = storeR(sp, A, S);
      if (!sp.area && !sp.chain && !sp.direct) { R2.ask = { type: 'area' }; S.pending = { type: 'area' }; }
      if (hasMention) R2.slugs = uniq([].concat.apply([], M.map(function (m) { return m.owners; }))).slice(0, 4);
      return R2;
    }

    /* 7. topics about the shop itself (only when no product is being discussed) */
    var prodTalk = hasMention || (refs && (aspect || strong));
    if (RE.orderStatus.test(t) && !RE.checkout.test(t) && !(strong && hasMention)) return mk('order_status');
    if (RE.returns.test(t) && !prodTalk) return mk('returns');
    if (RE.promo.test(t) && !(strong && hasMention && A.qp.qs.length)) { return mk('promo', { slugs: hasMention ? M[0].owners.slice(0, 3) : [] }); }
    if (RE.delivery.test(t) && !(strong && hasMention && A.qp.qs.length && !/\b(deliver|delivery|ship|shipping|courier)\b/.test(t)) && !(prodTalk && aspect && !/\b(deliver\w*|ship\w*|courier|free delivery)\b/.test(t))) {
      return mk('delivery', { topic: RE.overseas.test(t) && !/\b(singapore|island)\b/.test(t) ? 'overseas' : (/\b(self collect\w*|pick ?up|collect\w*)\b/.test(t) ? 'collect' : 'sg'), area: (areaSearch(A.T) || {}).area ? areaSearch(A.T).area.n : null });
    }
    if (RE.payq.test(t) && !strong) return mk('payment');
    if (RE.gst.test(t) && !prodTalk) return mk('gst');
    if (RE.trade.test(t)) return mk('trade');
    if (RE.contact.test(t) && !prodTalk && !(A.needs.length && !/\b(contact|call|phone|email|talk|speak|pharmacist|human|office|address|hotline|whatsapp)\b/.test(t))) return mk('contact', { pharmacist: /\b(pharmacist|doctor)\b/.test(t) });
    if (RE.catalogue.test(t) && !hasMention) return mk('catalogue');
    if (RE.tele.test(t) && !hasMention && !A.needs.length) return mk('promo', { tele: true });
    if (RE.privacy.test(t) && !prodTalk) return mk('privacy');
    if (RE.genuine.test(t) && !(hasMention && aspect)) return mk('genuine');
    if (RE.awards.test(t) && !hasMention) return mk('awards');
    if (RE.about.test(t) && !prodTalk && !A.needs.length) return mk('about');
    if (RE.quality.test(t) && !prodTalk && !A.needs.length) return mk('quality');
    if (RE.notes.test(t) && !hasMention && !A.needs.length) return mk('notes');
    if (RE.giftcard.test(t)) return mk('giftcard');
    if (RE.nav.test(t) && !hasMention) { var pg = spanLookup(A.T, IDX.pageAlias, 5, null); if (pg) return mk('navigate', { page: pg.id }); }
    var pgOnly = n <= 3 ? spanLookup(A.T, IDX.pageAlias, 5, null) : null;
    if (pgOnly && !hasMention && pgOnly.e - pgOnly.s === n && pgOnly.id !== 'shop') return mk('navigate', { page: pgOnly.id });

    /* 8. other medicines and brands we do not sell */
    if (RE.unknownThing.test(t) && !hasMention) { var um = RE.unknownThing.exec(t); return mk('notstocked', { term: um[1], slugs: (/\bbalm\b|\bsalonpas\b|\bvicks\b|\beagle\b|\baxe\b|\bpo chai\b|\bbak foong\b/.test(um[1]) ? ['rheuma-salve-balm', 'rheuma-salve-creme', 'rheuma-salve-medi-stick'] : []) }); }

    /* 9. add to the bag */
    var addish = null;
    var hasQty = A.qp.qs.some(function (x) { return x.kind === 'num' || x.kind === 'word' || x.kind === 'x' || x.kind === 'art'; });
    var more = A.qp.qs.some(function (x) { return x.kind === 'more'; }) && RE.more.test(t);
    var qWord = /^(what|which|how|do|does|is|are|can|could|would|should|will|any|got|why|where|when|who|whats|tell)\b/.test(t);
    var verbOnly = /\b(want|need|like|take|have|get|buy|order|add|put|grab|pick|give|go for|go with)\b/.test(t);
    var ask = qWord && !strong && !/^(can|could|may) i (get|have|buy|order)\b/.test(t);
    var priceQ = (aspect === 'price' || aspect === 'stock' || aspect === 'packs' || aspect === 'general' || aspect === 'usage' || aspect === 'ingredients' || aspect === 'cautions' || aspect === 'halal' || aspect === 'origin' || aspect === 'sheet' || aspect === 'size') && !strong;
    if (hasMention) {
      if (strong || more || (!priceQ && !ask && (hasQty || (verbOnly && !/\b(about|info|details|tell|know|price|cost|much)\b/.test(t))))) addish = true;
      if (priceQ && hasQty && /\b(add|buy|order|get)\b/.test(t) && !/\b(how much|price|cost)\b/.test(t)) addish = true;
    } else if (refs && (strong || more || (hasQty && n <= 5 && !priceQ)) && !qWord) addish = true;
    if (addish) { R = addFlow(A, S, hasMention ? null : refs); if (R) return R; }
    if (!hasMention && !refs && (strong) && !A.needs.length) {
      // "add 2 zorb": a product we do not know -> did you mean
      var phrase = contentPhrase(A);
      if (phrase) {
        var sg = suggestFor(phrase, A), qq = A.qp.qs.filter(function (x) { return x.kind !== 'more'; });
        S.pending = sg.length ? { type: 'dym', phrase: phrase, options: sg, orig: { intent: 'add', qty: qq.length ? qq[0].v : 1 } } : null;
        S.last.list = sg.slice(); S.last.intent = 'dym';
        return mk('unknown', { phrase: phrase, suggest: sg, orig: 'add', qty: qq.length ? qq[0].v : 1 });
      }
    }

    /* 10. a product (or a few) with a question about it */
    var wantProducts = hasMention ? M : null;
    if (RE.compare.test(t) && (hasMention || refs)) {
      var cmp = [];
      if (M.length >= 2) M.forEach(function (m) { m.owners.slice(0, M.length === 2 && m.owners.length > 1 ? 5 : 3).forEach(function (o) { if (cmp.indexOf(o) < 0) cmp.push(o); }); });
      else if (M.length === 1 && M[0].owners.length >= 2) cmp = M[0].owners.slice(0, 6);
      else if (refs && refs.owners.length >= 2) cmp = refs.owners.slice(0, 5);
      if (cmp.length >= 2) {
        var R3 = mk('compare', { slugs: cmp.slice(0, 6) });
        S.last.intent = 'compare'; S.last.list = R3.slugs.slice(); S.last.focus = R3.slugs[0]; S.last.aspect = null;
        if (A.needs.length) R3.needs = A.needs.map(function (x) { return x.id; });
        return R3;
      }
    }
    // short follow-ups: "and the creme?", "what about the patch?" keep the last question
    var follow = /^(and|what about|how about|then|so|also|or|ok and|okay and|and what about)\b/.test(t) && n <= 7;
    if (hasMention && (aspect || (follow && L.intent === 'info' && L.aspect))) {
      var asp = aspect || L.aspect || 'general';
      var slugs = uniq([].concat.apply([], M.map(function (m) { return m.owners; }))).slice(0, 4);
      if (A.needs.length && asp === 'general' && !follow) { /* "is balm good for knee pain" */ }
      return infoR(slugs, asp, S, { caution: A.caution || (!!A.aud && A.aud !== 'elder') });
    }
    if (refs && aspect && !hasMention) {
      var owners = refs.owners.slice(0, refs.kind === 'all' ? 4 : 1);
      return infoR(owners, aspect, S, { via: 'context', caution: A.caution });
    }
    if (!hasMention && !refs && aspect && aspect !== 'general' && !A.needs.length && /\b(it|this|that|they|them|the product|how much)\b/.test(t) && !(RE.recommend.test(t))) {
      S.pending = { type: 'infoWhich', aspect: aspect };
      return mk('info', { aspect: aspect, ask: { type: 'product' } });
    }

    /* 11. needs and recommendations */
    if (A.needs.length) {
      var rec = recommendFor(A, S, A.needs);
      var fitOne = hasMention && M.length === 1 && M[0].owners.length === 1 && /\b(good|ok|okay|suitable|help|work|works|safe|effective|use|for)\b/.test(t) && (qWord || /\b(good|suitable|work|works|effective)\b/.test(t));
      if (fitOne) { var f1 = M[0].owners[0]; var R4 = infoR([f1], 'fit', S, { needs: A.needs.map(function (x) { return x.id; }), fit: rec.list.indexOf(f1) > -1, why: rec.why[f1] || '', recs: rec.list.slice(0, 3), note: rec.notes[0] || '', caution: A.caution }); return R4; }
      var R5 = mk('recommend', { needs: A.needs.map(function (x) { return x.id; }), slugs: rec.list.slice(0, 5), why: rec.why, notes: rec.notes, cats: rec.cats, caution: A.caution || rec.kidsCaution, aud: A.aud });
      S.last.intent = 'recommend'; S.last.list = R5.slugs.slice(0, 5); S.last.focus = R5.slugs[0]; S.last.aspect = null; S.last.cat = rec.cats[0] || null;
      return R5;
    }
    if (A.aud === 'child' && !hasMention && /\b(vitamin|vitamins|supplement|supplements|gummies|gummy|multivitamin|something|anything|products?)\b/.test(t)) {
      var kn = needById('kids'); var R6 = mk('recommend', { needs: ['kids'], slugs: kn.p.map(function (x) { return x.s; }), why: kn.p.reduce(function (o, x) { o[x.s] = x.why; return o; }, {}), notes: [], cats: ['kids'], caution: true, aud: 'child' });
      S.last.intent = 'recommend'; S.last.list = R6.slugs.slice(0, 5); S.last.focus = R6.slugs[0]; return R6;
    }
    var unc = null;
    (KB.uncovered || []).forEach(function (u) { var ut = lite(u).join(' '); if (!unc && (' ' + t + ' ').indexOf(' ' + ut + ' ') > -1) unc = u; });
    if (unc && !hasMention) { return mk('uncovered', { term: unc, caution: true }); }

    /* 12. browse a shelf or the whole range */
    var cat = spanLookup(A.T, IDX.catAlias, 6, A.cover);
    if (cat && !hasMention) {
      var c = catOf(cat.id);
      S.last.intent = 'browse'; S.last.cat = c.id; S.last.list = c.slugs.slice(0, 5); S.last.focus = c.slugs[0]; S.last.aspect = null;
      return mk('browse', { cat: c.id, slugs: c.slugs.slice(), caution: A.caution });
    }
    if (RE.browse.test(t) && !hasMention && /\b(products?|items|range|everything|categories|category|catalog\w*|sell|have|carry|stock|offer|shelf|shelves|things|more|else|other)\b/.test(t)) { return mk('browse', { all: true }); }
    if (/^(shop|store|products|all products|everything)$/.test(t)) return mk('browse', { all: true });

    /* 13. just a product name */
    if (hasMention) {
      var slugs2 = uniq([].concat.apply([], M.map(function (m) { return m.owners; })));
      if (M.length === 1 && M[0].owners.length > 7) return mk('browse', { brand: 'Heritage', slugs: M[0].owners.slice(0, 8) });
      return infoR(slugs2.slice(0, 4), 'general', S, { caution: A.caution, more: slugs2.length > 4 });
    }
    if (refs && n <= 4) return infoR(refs.owners.slice(0, 4), 'general', S, { via: 'context' });

    /* 14. questions answered from the site's own text */
    var fq = searchText(W);
    if (fq) { S.last.intent = 'faq'; return mk('faq', { chunk: fq.c, score: fq.score }); }

    /* 15. closest matches, or nothing */
    var phrase2 = contentPhrase(A), sg2 = suggestFor(phrase2 || W.join(' '), A);
    var tx = rankByText(W);
    if (tx.length && tx[0].sc >= 2.2 && !qWord) {
      var ids = tx.slice(0, 3).map(function (x) { return x.id; });
      S.last.intent = 'recommend'; S.last.list = ids.slice(); S.last.focus = ids[0];
      return mk('recommend', { needs: [], slugs: ids, closest: true, caution: A.caution });
    }
    S.pending = sg2.length && phrase2 && n <= 6 ? { type: 'dym', phrase: phrase2, options: sg2, orig: { intent: 'info', aspect: 'general' } } : null;
    S.last.intent = 'fallback'; if (sg2.length) S.last.list = sg2.slice();
    return mk('fallback', { phrase: phrase2, suggest: sg2 });
  }

  /* ---- public, pure: text + state -> what it means (no DOM, no storage, no bag writes) ---- */
  function understand(text, state) {
    if (!KB || !IDX) return { intent: 'loading', items: [], state: state || freshState() };
    var S = normState(clone(state)), R;
    try { R = decide(analyze(String(text == null ? '' : text), S), S); }
    catch (e) { R = mk('fallback', { error: String(e && e.message || e), suggest: [] }); }
    S.turn = (S.turn || 0) + 1;
    R.state = S;
    return R;
  }
  w.HSTChat = { load: load, understand: understand, get kb() { return KB; },
    debug: function (text, st) { var S = normState(clone(st)); var A = analyze(String(text), S); return { T: A.T, t: A.t, M: A.M, qp: A.qp, needs: A.needs, aud: A.aud, caution: A.caution, att: attach(A.M, A.qp, A.T) }; } };
})();
