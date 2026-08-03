# Patch de la page v6 vers la v7. Applique treize modifications
# nommees, chacune sur un texte qui doit apparaitre une fois et une
# seule : au moindre doute, le script s'arrete sans rien ecrire.
# Le passage .github/workflows/page-v7.yml verifie ensuite l'empreinte
# du resultat et refuse de graver si elle ne correspond pas a la page
# validee au banc.
import io, sys, os
CHEMIN = os.environ.get('PAGE', 'index.html')
s = open(CHEMIN, encoding='utf-8').read()
faits = []

def rep(vieux, neuf, nom):
    global s
    n = s.count(vieux)
    if n != 1:
        print('ECHEC %-28s : %d occurrence(s)' % (nom, n)); sys.exit(1)
    s = s.replace(vieux, neuf)
    faits.append(nom)

# 1. Mode d'emploi des colonnes
rep("""          <li><b>1M, 3M, 6M, 1A</b> : ce que la valeur a gagne ou perdu sur un mois, trois mois, six mois, un an.</li>""",
"""          <li><b>Vs haut 5 ans</b> : le meme ecart, mesure sur cinq ans. Une valeur peut etre au sommet de son annee et rester loin de son sommet de 2021.</li>
          <li><b>1M, 3M, 6M, 1A, 3A, 5A</b> : ce que la valeur a gagne ou perdu sur un mois, trois mois, six mois, un an, trois ans, cinq ans. Une case vide veut dire que la source ne remonte pas si loin.</li>
          <li><b>Cote depuis</b> : annee du premier cours detenu par la source. Ce n'est pas une date d'introduction : elle affiche 1962 pour les vieilles valeurs americaines, qui est le plancher de la source, et repart a l'annee du changement quand un produit change de code ou de place.</li>
          <li><b>SRI</b> (ETF seulement) : indicateur de risque reglementaire de 1 a 7, lu dans le document d'informations cles de l'emetteur. Releve a la main, vide tant que le releve n'est pas fait.</li>
          <li><b>Etoiles</b> (ETF seulement) : note Morningstar de 1 a 5, avis attribue a Morningstar. Releve a la main : la source de cours ne publie ces notes que pour les fonds a valeur liquidative, jamais pour les ETF.</li>""",
    'aide colonnes')

# 2. Colonnes
rep("""const COLS=[
  {k:'n',  t:'Valeur'},
  {k:'c',  t:'Prix'},
  {k:'h',  t:'Vs haut 1 an'},
  {k:'m',  t:'Vs moy. 200 j'},
  {k:'p1', t:'1M'},
  {k:'p3', t:'3M'},
  {k:'p6', t:'6M'},
  {k:'p12',t:'1A'},
  {k:'sec',t:'Secousse/j'}
];""",
"""/* Colonnes du tableau. Les deux dernieres ne sortent que pour la
   famille ETF : SRI et etoiles sont des releves manuels tenus dans
   radar/NOTES.csv, ils ne concernent que les produits geres. */
const COLS_BASE=[
  {k:'n',  t:'Valeur'},
  {k:'c',  t:'Prix'},
  {k:'h',  t:'Vs haut 1 an'},
  {k:'h5', t:'Vs haut 5 ans'},
  {k:'m',  t:'Vs moy. 200 j'},
  {k:'p1', t:'1M'},
  {k:'p3', t:'3M'},
  {k:'p6', t:'6M'},
  {k:'p12',t:'1A'},
  {k:'p36',t:'3A'},
  {k:'p60',t:'5A'},
  {k:'sec',t:'Secousse/j'},
  {k:'ftd',t:'Cote depuis'}
];
const COLS_ETF=[{k:'sri',t:'SRI'},{k:'et',t:'Etoiles'}];
function cols(){return rdr.famille==='etf'?COLS_BASE.concat(COLS_ETF):COLS_BASE;}""",
    'colonnes')

# 3. Tri des colonnes non numeriques
rep("""  v.sort((a,b)=>{
    if(k==='n') return sn*a.n.localeCompare(b.n,'fr');
    const x=a[k],y=b[k];""",
"""  v.sort((a,b)=>{
    if(k==='n') return sn*a.n.localeCompare(b.n,'fr');
    if(k==='ftd'){
      const u=a.ftd||'', w=b.ftd||'';
      if(!u&&!w) return 0;
      if(!u) return 1;
      if(!w) return -1;
      return sn*(u<w?-1:u>w?1:0);
    }
    if(k==='sri'||k==='et'){
      const u=parseFloat(a[k]), w=parseFloat(b[k]);
      if(isNaN(u)&&isNaN(w)) return 0;
      if(isNaN(u)) return 1;
      if(isNaN(w)) return -1;
      return sn*(u-w);
    }
    const x=a[k],y=b[k];""",
    'tri')

# 4. Ce que couvre la courbe, lu dans le balayage
rep("""function courbeSvg(x){""",
"""/* Ce que couvre la courbe gravee : le balayage ecrit sa profondeur et
   son pas depuis le 02/08/2026. Repli sur l'ancien format si un
   fichier plus ancien est servi. */
function profondeurCourbe(){
  const r=etat.radar||{};
  const duree={'5y':'cinq ans','2y':'deux ans','1y':'un an'}[r.profondeur]||'un an';
  const n=r.pas_courbe||10;
  const mots={10:'dix',20:'vingt',30:'trente'};
  return {duree:duree, pas:(mots[n]||n)+' jours de bourse'};
}
function etoiles(n){
  const v=parseFloat(n);
  if(isNaN(v)) return ech(String(n));
  return '\\u2605'.repeat(Math.max(0,Math.min(5,Math.round(v))));
}

function courbeSvg(x){""",
    'profondeur et etoiles')

rep("""  return '<svg viewBox="0 0 '+W+' '+H+'" role="img" aria-label="Cours d\\u2019un an de '+ech(x.n)+'">'+g+""",
"""  return '<svg viewBox="0 0 '+W+' '+H+'" role="img" aria-label="Cours sur '+profondeurCourbe().duree+' de '+ech(x.n)+'">'+g+""",
    'etiquette courbe')

# 5. Phrase d'etat : les cinq ans
rep("""  if(x.p6!=null) p.push('six mois '+fmtPct(x.p6));
  return p.join(', ')+'.';""",
"""  if(x.p6!=null) p.push('six mois '+fmtPct(x.p6));
  if(x.p60!=null) p.push('cinq ans '+fmtPct(x.p60));
  return p.join(', ')+'.';""",
    'phrase etat')

# 6. Detail d'une valeur : anciennete, etoiles, legende de courbe
rep("""    '<div class="qd">'+ech(x.s)+' \\u00b7 '+ech(x.o)+(x.t?' \\u00b7 '+ech(x.t):'')+' \\u00b7 '+x.j+' jours de cours'+(x.sri?' \\u00b7 SRI '+ech(x.sri):'')+'</div>'+""",
"""    '<div class="qd">'+ech(x.s)+' \\u00b7 '+ech(x.o)+(x.t?' \\u00b7 '+ech(x.t):'')+' \\u00b7 '+x.j+' jours de cours'+
      (x.ftd?' \\u00b7 cote depuis le '+dfCourt.format(dISO(x.ftd)):'')+
      (x.sri?' \\u00b7 SRI '+ech(x.sri):'')+(x.et?' \\u00b7 '+etoiles(x.et):'')+'</div>'+""",
    'detail en-tete')

rep("""    '<p class="qd">Annee ecoulee, un point tous les dix jours de bourse.</p>';""",
"""    '<p class="qd">'+(function(c){return c.duree.charAt(0).toUpperCase()+c.duree.slice(1)+', un point tous les '+c.pas+'.';})(profondeurCourbe())+
     (x.h5!=null&&x.h!=null&&Math.abs(x.h5-x.h)>0.05?' Plus haut de cinq ans : '+fmtPct(x.h5)+'.':'')+'</p>';""",
    'legende courbe')

# 7. Tableau : entetes et cellules construites depuis cols()
rep("""  for(const c of COLS){
    const trie=(c.k===rdr.tri);""",
"""  for(const c of cols()){
    const trie=(c.k===rdr.tri);""",
    'entetes')

rep("""  for(const x of vues){
    const ouv=(x.s===rdr.ouverte);
    const auHaut=(x.h!=null&&x.h>=-1);
    h+='<tr class="ligne'+(ouv?' ouverte':'')+'" data-s="'+ech(x.s)+'">'+
      '<td><span class="radar-nom" title="'+ech(x.n)+'">'+ech(x.n)+'</span><span class="radar-badge">'+ech(x.o)+'</span>'+
      (auHaut?'<span class="radar-haut">au plus haut</span>':'')+
      '<div class="qd mono">'+ech(x.s)+(x.t?' <span class="radar-theme">'+ech(x.t)+'</span>':'')+'</div></td>'+
      '<td class="mono">'+nf2.format(x.c)+' '+ech(x.d)+'</td>'+
      pc(x.h)+pc(x.m)+pc(x.p1)+pc(x.p3)+pc(x.p6)+pc(x.p12)+
      '<td class="mono">'+nf1.format(x.sec)+' %</td></tr>';
    if(ouv) h+='<tr class="detail"><td colspan="'+COLS.length+'">'+detailValeur(x)+'</td></tr>';
  }""",
"""  const lst=cols();
  for(const x of vues){
    const ouv=(x.s===rdr.ouverte);
    h+='<tr class="ligne'+(ouv?' ouverte':'')+'" data-s="'+ech(x.s)+'">';
    for(const c of lst) h+=celluleRadar(x,c,pc);
    h+='</tr>';
    if(ouv) h+='<tr class="detail"><td colspan="'+lst.length+'">'+detailValeur(x)+'</td></tr>';
  }""",
    'lignes du tableau')

rep("""function rendreRadarTable(){""",
"""/* Une cellule du tableau. Le nom porte le badge d'origine, le theme et
   la mention "au plus haut" ; les autres colonnes sont des nombres. */
function celluleRadar(x,c,pc){
  if(c.k==='n'){
    const auHaut=(x.h!=null&&x.h>=-1);
    return '<td><span class="radar-nom" title="'+ech(x.n)+'">'+ech(x.n)+'</span><span class="radar-badge">'+ech(x.o)+'</span>'+
      (auHaut?'<span class="radar-haut">au plus haut</span>':'')+
      '<div class="qd mono">'+ech(x.s)+(x.t?' <span class="radar-theme">'+ech(x.t)+'</span>':'')+'</div></td>';
  }
  if(c.k==='c')   return '<td class="mono">'+nf2.format(x.c)+' '+ech(x.d)+'</td>';
  if(c.k==='sec') return '<td class="mono">'+nf1.format(x.sec)+' %</td>';
  if(c.k==='ftd') return '<td class="mono">'+(x.ftd?ech(x.ftd.slice(0,4)):'\\u00b7')+'</td>';
  if(c.k==='sri') return '<td class="mono">'+(x.sri?ech(x.sri):'\\u00b7')+'</td>';
  if(c.k==='et')  return '<td class="mono">'+(x.et?etoiles(x.et):'\\u00b7')+'</td>';
  return pc(x[c.k]);
}

function rendreRadarTable(){""",
    'cellule')

# 8. Marche par theme : mediane cinq ans
rep("""  let h='<table><thead><tr><th>Theme</th><th>Valeurs</th><th>1M median</th><th>3M median</th><th>6M median</th><th>Plus forte sur 6 mois</th></tr></thead><tbody>';""",
"""  let h='<table><thead><tr><th>Theme</th><th>Valeurs</th><th>1M median</th><th>3M median</th><th>6M median</th><th>5A median</th><th>Plus forte sur 6 mois</th></tr></thead><tbody>';""",
    'entete themes')

rep("""    h+='<tr class="cliq" data-t="'+ech(a.t)+'"><td>'+ech(a.t)+'</td><td class="mono">'+a.n+'</td>'+pc(a.m1)+pc(a.m3)+pc(a.m6)+""",
"""    h+='<tr class="cliq" data-t="'+ech(a.t)+'"><td>'+ech(a.t)+'</td><td class="mono">'+a.n+'</td>'+pc(a.m1)+pc(a.m3)+pc(a.m6)+pc(a.m60)+""",
    'lignes themes')

open(CHEMIN, 'w', encoding='utf-8').write(s)
print('applique :', ', '.join(faits))
print('octets :', len(s.encode('utf-8')))

# celluleRadar est rangee aupres de detailValeur, avec les autres
# fonctions qui fabriquent du HTML, et non au milieu des rendus.
s = open(CHEMIN, encoding='utf-8').read()
d = s.index("/* Une cellule du tableau.")
f = s.index("function rendreRadarTable(){")
bloc = s[d:f]
s = s[:d] + s[f:]
s = s.replace("function rendreRadarFamilles(){", bloc + "function rendreRadarFamilles(){", 1)
open(CHEMIN, 'w', encoding='utf-8').write(s)
print('celluleRadar rangee ; octets finaux :', len(s.encode('utf-8')))
