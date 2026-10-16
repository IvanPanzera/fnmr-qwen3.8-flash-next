"""Frozen synthetic workloads: 20 task families x 15 variants x 12 domains.

Different examples, constraints, audiences and source lengths; never copied
model answers. Holdout consists of four entire task families per domain.
"""
import json,random,hashlib
from data_model import DOMAINS

TASKS={
'codice':'''Deduplicazione|Scrivi una funzione Python che deduplichi record per id conservando l'ultimo record e l'ordine della prima comparsa.
Intervalli|Scrivi una funzione JavaScript che unisca intervalli temporali sovrapposti e calcoli la durata totale.
Parsing CSV|Scrivi codice Python con csv per leggere un CSV con separatore punto e virgola e importi decimali con virgola.
Cache LRU|Implementa una piccola cache LRU in Python con get e put e capacità {a}; usa OrderedDict.
Validatore|Scrivi una funzione TypeScript che validi un oggetto ordine, distinguendo campi mancanti e tipi errati.
Ricerca|Scrivi in C una ricerca binaria che restituisca il primo indice di un valore duplicato o -1.
Grafo|Scrivi una funzione Python BFS che restituisca il cammino minimo non pesato tra due nodi, o None.
File grandi|Scrivi un generatore Python che legga un file di testo a blocchi e produca righe complete, anche se spezzate tra blocchi.
Date|Scrivi una funzione JavaScript che raggruppi eventi per giorno UTC senza dipendere dal fuso locale.
Retry|Scrivi una funzione Python asincrona con massimo {a} tentativi, backoff esponenziale e cancellazione propagata.
Aggregazione|Scrivi una funzione Rust che calcoli conteggio e somma per categoria da una sequenza di coppie.
Argomenti CLI|Scrivi un breve programma Python argparse con percorso input, formato di uscita e opzione dry-run.
Stream JSON|Scrivi codice Python che filtri record JSONL senza caricare l'intero file in memoria.
Producer consumer|Scrivi un esempio Python con queue e due thread che si arrestino ordinatamente con una sentinella.
Componenti UI|Scrivi un componente React TypeScript per una lista filtrabile con conteggio e stato vuoto.
API paginata|Scrivi una funzione Python che percorra pagine di una API con next_cursor, rilevando cursori ripetuti.
Normalizzazione|Scrivi una funzione Go che normalizzi spazi e minuscole nelle stringhe preservando i caratteri Unicode.
Test parametrico|Scrivi una funzione Python per mediana e test pytest parametrizzati, inclusi input vuoto e lunghezza pari.
Ordinamento|Scrivi una funzione C++ che ordini record prima per priorità decrescente e poi per nome crescente.
Shell sicura|Scrivi uno script PowerShell che elenchi i file più grandi in una cartella senza modificarli.''',
'debug':'''Mutazione lista|Correggi: def positive(xs):\n for x in xs:\n  if x < 0: xs.remove(x)\n return xs
Default mutabile|Correggi: def add(x, items=[]):\n items.append(x)\n return items
Divisione intera|Correggi in C la media: double mean(int total,int count) {{ return total/count; }}. Gestisci count=0.
Closure|Correggi JavaScript: const f=[]; for(var i=0;i<3;i++) f.push(()=>i); console.log(f.map(x=>x()));
Null SQL|Correggi SQL: SELECT * FROM orders WHERE shipped_at = NULL;
Join|Correggi una LEFT JOIN clienti-ordini il cui WHERE orders.status='paid' esclude i clienti senza ordini.
Date UTC|Trova il problema nel raggruppare eventi UTC con new Date(ts).getDate() e proponi una correzione verificabile.
Off by one|Correggi Python: for i in range(len(xs)+1): print(xs[i]). Spiega il caso della lista vuota.
Async|Correggi: async def fetch_all(urls): return [fetch(u) for u in urls]. fetch è asincrona.
Race condition|Due thread eseguono if key not in cache: cache[key]=expensive(). Spiega la race e correggi la duplicazione.
Risorsa file|Correggi una funzione che apre un file, può sollevare eccezioni e lo chiude soltanto prima del return.
Alias matrici|Correggi Python: grid=[[0]*{a}]*{b}; grid[0][0]=1. Le altre righe non devono cambiare.
Somma floating|Un test pretende 0.1+0.2==0.3. Correggi il test senza arrotondare indiscriminatamente tutti i dati.
Paginate|Un ciclo di paginazione riutilizza il cursor iniziale in ogni richiesta. Individua il guasto e proponi test.
Regex|Una regex per email accetta spazi e newline. Proponi un controllo pragmatico, dichiarando i limiti.
Eccezioni|Correggi Python: try: return int(s) except Exception: return 0. Occorre distinguere input invalido da zero valido.
Overflow|Una somma di importi in centesimi usa int32 e supera il limite. Suggerisci correzione e test ai bordi.
Ordine test|Un test passa da solo ma fallisce dopo un altro che modifica una variabile globale. Diagnostica e isola lo stato.
React effect|Un useEffect senza dipendenze aggiorna state a ogni render. Mostra il ciclo e una correzione minima.
Encoding|Un CSV UTF-8 con BOM produce una prima colonna dal nome inatteso. Diagnostica e correggi la lettura.''',
'dati':'''Totali SQL|Scrivi SQL PostgreSQL per totale importi e numero record per reparto, includendo soltanto lo stato approvato.
Top per gruppo|Scrivi SQL PostgreSQL per il record di importo maggiore di ciascun reparto, con pareggi risolti tramite id.
Serie temporale|Calcola media e variazione percentuale dei valori della serie; segnala denominatori nulli.
Mediana|Calcola mediana e quartili dichiarando la convenzione utilizzata.
Join clienti|Progetta una LEFT JOIN clienti-ordini che conservi tutti i clienti e restituisca zero per aggregati mancanti.
Duplicati|Individua duplicati per reparto e importo, senza confondere id diversi con record identici.
Valori mancanti|Proponi una gestione dei dati mancanti che distingua assenza, zero e valore non valido.
Finestra SQL|Scrivi SQL per somma cumulata degli importi ordinata per data, separata per reparto.
Confronto gruppi|Confronta la media degli importi dei reparti; descrivi cosa non si può inferire causalmente.
Pivot|Descrivi una tabella pivot reparto per stato con conteggi e totali e fornisci codice pandas.
Pulizia|Scrivi codice pandas per convertire importi testuali con virgola e segnalare conversioni fallite.
Outlier|Valuta gli outlier della serie usando una regola robusta e mostra soglia e casi individuati.
Percentuali|Calcola la quota di ogni reparto sul totale senza mediare percentuali con denominatori diversi.
Indici SQL|Per filtri stato/data e aggregazione per reparto, proponi indici PostgreSQL e il modo di verificarli.
Schema|Disegna uno schema relazionale normalizzato per reparti, pratiche e cambi di stato.
ETL incrementale|Proponi un ETL incrementale idempotente usando data aggiornamento e chiave primaria.
Istogramma|Proponi bin per un istogramma degli importi e spiega come evitare una rappresentazione fuorviante.
Qualità dati|Definisci cinque controlli automatici di qualità per il registro, con esempi di anomalie.
Campionamento|Proponi un campionamento stratificato per reparto e spiega come stimare il totale.
Dedup SQL|Scrivi una SELECT che scelga la versione più recente per id con row_number e ordinamento deterministico.''',
'matematica':'''Equazione|Risolvi {a}x+{b}={c}, con verifica per sostituzione.
Sistema|Risolvi x+y={a}, 2x-y={b} e verifica entrambe le equazioni.
Percentuali|Un prezzo di {c} euro aumenta del {a}% e poi diminuisce del {b}%. Calcola prezzo finale e variazione complessiva.
Probabilità|Un'urna contiene {a} palline rosse e {b} blu. Calcola la probabilità di due rosse in due estrazioni senza reinserimento.
Derivata|Deriva f(x)={a}x^3-{b}x^2+{c} e trova i punti stazionari.
Integrale|Calcola l'integrale di {a}x^2+{b} tra 0 e 2, mostrando i passaggi.
Vettori|Calcola prodotto scalare e angolo tra ({a},1,0) e (0,{b},1).
Matrice|Calcola determinante e inversa, se esiste, di [[{a},1],[2,{b}]].
Interessi|Capitale {c} euro, tasso annuo {a}% per 3 anni: confronta interesse semplice e composto.
Combinatoria|Da {a} elementi distinti scegli 2 senza ordine né ripetizione. Calcola il numero di combinazioni.
Progressione|Una progressione aritmetica parte da {a}, ragione {b}, con 12 termini. Calcola ultimo termine e somma.
Geometria|Un cilindro ha raggio {a} cm e altezza {b} cm. Calcola volume e superficie totale in forma esatta.
Logaritmi|Risolvi log2(x-{a})=3, dichiarando dominio e controllo della soluzione.
Limite|Calcola il limite per x verso 0 di sin({a}x)/x e spiega l'argomento.
Bayes|Il 2% dei pezzi è difettoso. Un test ha sensibilità 90% e falsi positivi 5%. Calcola P(difetto|positivo).
Ottimizzazione|Un rettangolo ha perimetro {c} cm. Trova le dimensioni di area massima e giustifica.
Conversione|Converti {a} m/s in km/h e {c} cm^3 in litri, esplicitando i fattori.
Numerico|Applica due iterazioni di Newton a x^2-{a}=0 partendo da x0=2; segnala possibili limiti.
Errori|Una misura è {c} ± {a} mm. Calcola errore relativo e propagazione di primo ordine sull'area di un quadrato.
Serie|Calcola la somma dei primi 8 termini della progressione geometrica con primo termine {a} e ragione 2.''',
'logica':'''Sillogismo|Tutti i moduli A sono testati. Alcuni moduli testati sono difettosi. Segue che alcuni A sono difettosi? Fornisci un controesempio se no.
Ordinamento|Anna precede Bruno, Carla segue Anna ma precede Diego, Bruno segue Diego. Trova l'ordine e verifica i vincoli.
Condizionale|Se un file è cifrato serve una chiave. Ho una chiave. Posso concludere che il file è cifrato? Spiega.
Pianificazione|Tre lavori durano {a}, {b}, {c} minuti. Il terzo dipende dai primi due, che possono procedere in parallelo. Calcola il tempo minimo.
Insiemi|In un gruppo di 100 persone, 60 conoscono A, 50 B e 30 entrambi. Quante nessuno e quante una sola lingua?
Invariante|Un processo aggiunge o sottrae 2 a un numero inizialmente pari. Può raggiungere {odd}? Dimostra la risposta.
Verità|A dice che B mente. B dice che entrambi mentono. Assumendo che ciascuno sia sempre sincero o sempre bugiardo, trova una configurazione o dimostra l'incoerenza.
Vincoli|Quattro attività P,Q,R,S: P prima di R, Q prima di R, R prima di S. Elenca tutti gli ordini validi.
Diagnosi|Tre cause possibili spiegano un guasto; ciascuna è compatibile con un sintomo comune. Perché il sintomo non identifica da solo la causa?
Controesempio|La frase tutti i numeri primi sono dispari è vera? Correggila con la minima eccezione necessaria.
Decisione|Due alternative costano {c} e {d}; la prima richiede {a} ore e la seconda {b}. Descrivi la frontiera di Pareto senza inventare preferenze.
Necessario sufficiente|Avere una password valida è necessario ma non sufficiente per l'accesso. Elenca casi compatibili e incompatibili.
Precedenze|Un incarico richiede progetto, revisione, approvazione e acquisto; revisione dopo progetto, acquisto dopo approvazione. L'approvazione può precedere revisione? Se il vincolo manca, dichiaralo.
Quantificatori|Distingui per ogni progetto esiste un responsabile da esiste un responsabile per tutti i progetti. Dai un esempio concreto.
Falso dilemma|Un testo dice: o automatizziamo tutto subito o resteremo inefficienti. Analizza l'argomento e proponi alternative logiche.
Pigeonhole|Distribuiamo 13 oggetti in 12 scatole. Dimostra che una scatola ne contiene almeno 2 senza assumere distribuzione uniforme.
Ricorsione|Definisci una regola ricorsiva per la somma da 1 a n e dimostra per induzione n(n+1)/2.
Calendario|Un evento A avviene ogni 6 giorni, B ogni 8; coincidono oggi. Quando coincidono ancora? Mostra il ragionamento.
Ambiguità|La frase tutti hanno letto almeno un documento non significa che tutti abbiano letto lo stesso documento. Spiega con una tabella minima.
Coerenza|I requisiti impongono esattamente {a} moduli e almeno {c} moduli, con c maggiore di a. Individua il conflitto e la modifica minima.''',
'ingegneria':'''Trave|Per una trave semplicemente appoggiata di luce {a} m e carico uniforme {b} kN/m calcola reazioni e momento massimo, dichiarando il modello ideale.
Circuito DC|Resistenze {a} e {b} ohm in serie alimentate a 24 V. Calcola corrente, tensioni e potenza totale.
Pompa|Portata {a} L/s, prevalenza {b} m, rendimento 70%. Stima potenza elettrica per acqua e controlla le unità.
Trasmissione termica|Parete di 10 m², U=1.2 W/(m² K), differenza {a} K. Stima la potenza dispersa nel modello stazionario.
Tolleranze|Due quote nominali {a} e {b} mm hanno tolleranza ±0.1 mm. Determina tolleranza worst-case della somma.
FMEA|Prepara una breve FMEA per una valvola che può bloccarsi aperta o chiusa; non assegnare punteggi arbitrari senza criteri.
Sensori|Progetta una procedura per tarare un sensore usando cinque punti, ripetibilità e controllo dell'isteresi.
PID|Spiega come riconoscere saturazione integrale in un PID e come funziona l'anti-windup.
Bilancio energia|Un riscaldatore da {a} kW funziona {b} ore al giorno. Calcola energia in 30 giorni e costo a 0.25 euro/kWh.
Portata tubazione|Una tubazione ha diametro interno 50 mm e velocità {a} m/s. Calcola la portata e specifica che non stai dimensionando perdite di carico.
Segnali|Un segnale contiene frequenze fino a {c} Hz. Spiega frequenza di campionamento teorica minima e margine pratico.
Rete RC|R={a} kohm e C={b} microfarad. Calcola costante di tempo e risposta a un gradino a t=tau.
Reliability|Due componenti indipendenti con affidabilità 0.98 e 0.95: confronta collegamento serie e parallelo ideale.
Distinta base|Proponi una distinta base per un piccolo quadro di controllo, distinguendo dati richiesti e ipotesi.
Verifica dimensionale|Controlla dimensionalmente F=ma, E=Pt e una formula proposta Q=v/D; correggi l'ultima per una sezione circolare.
Collaudo|Proponi un piano di collaudo funzionale di un dispositivo con ingresso analogico e due uscite digitali.
Rischi progetto|Prepara un registro sintetico dei rischi per installare un sensore in ambiente umido, con mitigazioni verificabili.
Manutenzione|Confronta manutenzione preventiva e su condizione per una pompa, indicando dati necessari per la scelta.
Requisiti|Trasforma il requisito vago il sistema deve essere rapido in tre requisiti verificabili, senza fingere che le soglie siano già approvate.
Scambio termico|Stima il calore necessario per riscaldare {a} kg d'acqua da 20 a 60 °C assumendo c=4.18 kJ/(kg K).''',
'scienze':'''Diffusione luce|Spiega la diffusione di Rayleigh e perché il cielo al tramonto appare diverso.
Osmosi|Spiega l'osmosi distinguendola dalla diffusione, con un esempio e un limite dell'analogia.
Entropia|Spiega il secondo principio e perché un frigorifero non lo viola.
Fotosintesi|Descrivi ingressi, prodotti e ruolo della luce nella fotosintesi senza confondere respirazione e fotosintesi.
Evoluzione|Spiega selezione naturale e deriva genetica con un esempio che le distingua.
Legami|Confronta legame ionico, covalente e metallico, evitando categorie troppo assolute.
Acidi basi|Spiega pH e differenza tra acido forte e soluzione concentrata.
Onde|Confronta velocità, frequenza e lunghezza d'onda; usa un esempio numerico con frequenza {c} Hz.
Gravità|Spiega perché gli astronauti in orbita sono in caduta libera anche se la gravità non è nulla.
Clima|Distingui tempo meteorologico e clima e spiega perché un singolo giorno non basta per valutare una tendenza.
Statistica scienza|Spiega correlazione e causalità e proponi un esperimento con controllo.
DNA|Spiega il flusso DNA-RNA-proteina includendo una cautela sulla semplificazione.
Vaccini concetto|Descrivi in termini generali memoria immunitaria e risposta secondaria, senza dare consigli clinici.
Geologia|Confronta rocce ignee, sedimentarie e metamorfiche e il loro ciclo.
Radioattività|Spiega il tempo di dimezzamento e calcola la frazione dopo tre dimezzamenti.
Conservazione|Spiega conservazione della massa in una reazione in un sistema chiuso e il ruolo dei gas.
Elettromagnetismo|Spiega induzione elettromagnetica e perché conta la variazione del flusso.
Metodo scientifico|Trasforma una domanda sulla crescita delle piante in un'ipotesi falsificabile e un esperimento controllato.
Pressione|Spiega perché la pressione idrostatica dipende da profondità e densità, con esempio a {a} metri.
Equilibrio|Spiega equilibrio dinamico chimico senza descriverlo come arresto delle reazioni.''',
'documenti':'''Sintesi esecutiva|Riassumi il documento in cinque punti, separando fatti, decisioni e questioni aperte.
Verbale|Trasforma le note in un verbale conciso con decisioni e azioni, senza introdurre incarichi assenti.
Confronto|Confronta i reparti sulla base del documento e indica divergenze e informazioni mancanti.
Cronologia|Ricostruisci gli eventi in ordine cronologico con riferimenti alle righe fonte.
Rischi|Estrai criticità e dipendenze dal documento, distinguendo rischi espliciti e possibili inferenze.
Sintesi breve|Riassumi in non più di 80 parole senza perdere scadenze e importi essenziali.
FAQ|Crea quattro domande e risposte fondate soltanto sul documento.
Azioni|Organizza le azioni per responsabile, indicando scadenze mancanti senza inventarle.
Ambiguità|Individua formulazioni ambigue e scrivi domande di chiarimento per il redattore.
Incongruenze|Cerca contraddizioni interne e differenze tra budget proposto e confermato.
Tabella|Riorganizza il documento in una tabella compatta mantenendo la tracciabilità delle righe.
Abstract|Produci un abstract neutrale adatto a un archivio tecnico.
Passaggio consegne|Prepara un passaggio di consegne che evidenzi attività concluse e attività ancora pendenti.
Solo evidenze|Elenca cinque affermazioni supportate dal documento e indica per ciascuna la riga fonte.
Linguaggio semplice|Riscrivi il contenuto principale per un lettore non specialista, senza aggiungere conclusioni.
Titoli|Proponi una struttura di sezioni e sottosezioni per rendere il testo consultabile.
Decision log|Costruisci un registro di decisioni distinguendo proposte da approvazioni effettive.
Sintesi comparata|Sintetizza le differenze tra stato iniziale e aggiornamenti successivi descritti nel documento.
Limiti|Indica quali domande non possono ricevere risposta dal documento e quali dati servirebbero.
Priorità|Proponi priorità motivate usando soltanto scadenze e vincoli espliciti e segnala i pareggi.''',
'estrazione':'''Filtro JSON|Restituisci soltanto un array JSON delle pratiche approvate del reparto impianti con id e importo numerico.
Date ISO|Estrai id e date trasformando le date in ISO 8601; usa null per le date mancanti. Solo JSON.
Entità|Estrai persone e reparti senza duplicati, conservando l'ordine della prima comparsa. Solo JSON.
Schema rigido|Produci JSON con chiavi records e count, senza chiavi aggiuntive; includi soltanto pratiche sospese.
Somme|Restituisci JSON con somma degli importi per reparto, escludendo record con importo mancante.
CSV|Converti i dati in CSV con colonne id,reparto,stato,importo; usa virgolette dove necessario.
Azioni JSON|Estrai azioni e responsabili in JSON, lasciando null quando un'informazione non è esplicita.
Validazione|Segnala in JSON i record senza id, con importi negativi o stati non riconosciuti; non correggere di nascosto.
Soglia importo|Estrai in JSON i record il cui importo supera {c}, ordinati per importo decrescente.
Raggruppamento|Restituisci un oggetto JSON che mappi ogni stato a un array di id.
Campi nulli|Normalizza gli importi mancanti a null e le stringhe vuote di responsabile a null, senza inventare valori.
NDJSON|Converti ogni record in una riga JSON indipendente, mantenendo i campi originali.
Conteggi|Restituisci solo JSON con conteggio delle pratiche per stato e numero complessivo.
Selezione campi|Estrai solo id e responsabile dei record strutture. Non includere gli altri campi. Solo JSON.
Massimo|Restituisci JSON del record con importo maggiore e tutti i pareggi, ignorando gli importi mancanti.
Minimo|Restituisci JSON del record approvato con importo minimo e tutti i pareggi.
Deduplicazione|Restituisci gli id unici in JSON nell'ordine originale e il numero di ripetizioni per id.
Checklist|Produci JSON con booleani per presenza di data, responsabile e importo in ciascun record.
Intersezione|Estrai id delle pratiche approvate con importo superiore a {c} e data presente. Solo JSON.
Chiavi inglesi|Trasforma i record in JSON con chiavi id,department,status,amount,owner,date; non tradurre nomi propri.''',
'traduzione':'''IT EN|Traduci il testo italiano in inglese naturale preservando numeri e nomi propri.
IT FR|Traduci il testo italiano in francese, mantenendo il registro professionale.
IT DE|Traduci il testo italiano in tedesco, mantenendo unità e scadenze.
IT ES|Traduci il testo italiano in spagnolo senza riassumerlo.
EN IT|Traduci il testo inglese in italiano naturale, senza calchi inutili.
Tecnica|Traduci in inglese il testo tecnico italiano e aggiungi tre scelte terminologiche motivate.
Formale|Traduci il testo in inglese formale adatto a una comunicazione tra aziende.
Colloquiale|Traduci il testo in inglese colloquiale senza alterare i fatti.
Parallela|Produci una tabella con frase italiana e corrispondente inglese.
Localizzazione|Localizza il testo in inglese britannico, preservando importi in euro e date non ambigue.
Glossario|Crea un glossario italiano-inglese di cinque termini presenti nel testo con significato contestuale.
Revisiona inglese|Migliora il testo inglese per chiarezza e grammatica e indica due correzioni principali.
Semplice|Traduci in inglese B1 con frasi brevi senza perdere le informazioni operative.
Ambiguità|Traduci in inglese e segnala un'eventuale ambiguità dell'originale anziché risolverla arbitrariamente.
Titoli|Traduci in inglese proponendo anche un titolo informativo coerente con il contenuto.
Sintassi|Spiega due differenze sintattiche tra testo italiano e tua traduzione inglese.
Terminologia coerente|Traduci in francese usando sempre lo stesso termine per lo stesso concetto tecnico.
Sottotitoli|Traduci in inglese in righe brevi adatte a sottotitoli, senza omettere informazioni.
Pronomi|Traduci in spagnolo prestando attenzione a riferimenti pronominali e responsabilità esplicite.
Tono cortese|Traduci in inglese con tono cortese ma fermo, senza introdurre minacce o impegni.''',
'professionale':'''Email sollecito|Scrivi un'email cortese per chiedere aggiornamenti su una consegna in ritardo.
Agenda|Prepara un'agenda di riunione con obiettivi e decisioni attese.
Stato progetto|Scrivi un aggiornamento di progetto distinguendo fatto, rischio e prossima azione.
Proposta|Scrivi una proposta di intervento con obiettivo, ambito e dati ancora da confermare.
Rifiuto cortese|Scrivi un rifiuto motivato di una richiesta fuori ambito, proponendo un'alternativa realistica.
Passaggio consegne|Prepara un messaggio di passaggio di consegne chiaro e sintetico.
Richiesta chiarimenti|Scrivi una richiesta di chiarimento su requisiti ambigui con domande numerate.
Decisione|Redigi una nota che motivi una decisione, distinguendo criteri e ipotesi.
Comunicazione ritardo|Comunica un ritardo, assumendo responsabilità senza inventare una nuova data garantita.
Presentazione|Prepara l'apertura di una presentazione tecnica per dirigenti non specialisti.
Checklist|Scrivi una checklist operativa per verificare una consegna documentale.
Verbale azioni|Redigi un breve verbale con azioni, responsabili e scadenze fornite.
Sintesi proposta|Riassumi una proposta in 100 parole orientate al beneficio del destinatario.
Feedback|Formula un feedback costruttivo su un elaborato incompleto, con azioni verificabili.
Istruzioni|Scrivi istruzioni operative numerate per un collega che subentra nel progetto.
Escalation|Prepara una nota di escalation che descriva impatto e decisione richiesta senza toni accusatori.
Oggetto email|Proponi tre oggetti di email e scrivi il messaggio più appropriato.
Negoziazione|Scrivi una risposta che proponga una riduzione dell'ambito per rispettare il budget.
Report settimanale|Prepara un report settimanale breve con avanzamento, impedimenti e prossimi passi.
Invito|Scrivi un invito a una revisione di progetto specificando preparazione e risultato atteso.''',
'creativa':'''Racconto|Scrivi un micro-racconto con un conflitto e una conclusione non banale.
Dialogo|Scrivi un dialogo tra due personaggi con obiettivi opposti, facendo emergere il conflitto dalle battute.
Incipit|Scrivi l'incipit di un racconto senza spiegare subito il mistero.
Poesia|Scrivi una poesia breve in versi liberi usando immagini concrete.
Descrizione|Descrivi un luogo attraverso suoni, odori e dettagli senza elencare aggettivi.
Fantascienza|Scrivi una scena di fantascienza in cui una tecnologia comune ha una conseguenza inattesa.
Giallo|Scrivi una scena investigativa con un indizio visibile ma interpretabile in due modi.
Fiaba|Scrivi una fiaba breve con una scelta difficile e una morale implicita.
Commedia|Scrivi una scena comica fondata su un equivoco che si chiarisce alla fine.
Monologo|Scrivi un monologo che riveli un desiderio nascosto senza nominarlo direttamente.
Prima persona|Racconta una scoperta in prima persona con un narratore non del tutto affidabile.
Seconda persona|Scrivi una breve scena in seconda persona con un bivio concreto.
Lettera|Scrivi una lettera immaginaria che faccia intuire una storia precedente.
Finale alternativo|Scrivi due finali brevi, uno aperto e uno risolutivo, per la situazione proposta.
Vincolo lessicale|Scrivi una scena senza usare le parole bello, strano e improvvisamente.
Ambientazione|Descrivi un luogo familiare come se fosse visto per la prima volta da un visitatore inesperto.
Soggetto|Proponi un soggetto cinematografico con protagonista, ostacolo e posta in gioco.
Flashback|Scrivi una scena che contenga un breve flashback chiaramente distinguibile dal presente.
Cambio tono|Racconta la stessa situazione prima con tono comico e poi malinconico, in due brevi paragrafi.
Oggetto narrante|Fai raccontare la situazione a un oggetto inanimato, mantenendo coerente il punto di vista.'''
}
NAMES=['Anna','Bruno','Carla','Diego','Elena','Fabio','Giulia','Irene','Luca','Marta','Nadia','Paolo','Rita','Sara','Tommaso']
AUDIENCES=['studente delle superiori','collega tecnico','lettore non specialista','studente universitario','responsabile di progetto']
PLACES=['biblioteca di montagna','stazione sulla costa','laboratorio notturno','mercato coperto','osservatorio astronomico','archivio comunale','piccolo teatro','porto fluviale','serra abbandonata','officina di biciclette','museo vuoto','rifugio innevato','condominio in città','traghetto in viaggio','scuola di musica']
def rows(rng,n,v):
    return [dict(id=f'P{v:02d}-{i:03d}',reparto=['impianti','strutture','edilizia'][i%3],stato=['approvato','sospeso','in revisione','approvato'][i%4],
                 importo=None if i%11==10 else rng.randrange(100,9500),responsabile=NAMES[(i+v)%15],data=None if i%7==6 else f'2026-11-{1+(i+v)%28:02d}') for i in range(n)]
def context(domain,rng,v,a,b,c):
    n=[4,10,22][v%3];rs=rows(rng,n,v)
    if domain in ('dati','estrazione'):
        return 'Registro:\n'+json.dumps(rs,ensure_ascii=False)+'\nSerie di misure: '+str([rng.randrange(0,90) for _ in range(n)]) if domain=='dati' else 'Registro:\n'+json.dumps(rs,ensure_ascii=False)
    if domain=='documenti':
        return 'Documento (dati fittizi):\n'+'\n'.join(f'Riga {i+1}. Il responsabile {r["responsabile"]} del reparto {r["reparto"]} segnala pratica {r["id"]}, stato {r["stato"]}, budget '+('non indicato' if r['importo'] is None else str(r['importo'])+' euro')+', scadenza '+(r['data'] or 'da definire')+'. La revisione dipende dalla disponibilità del disegno aggiornato.' for i,r in enumerate(rs))+f'\nRiga {n+1}. La proposta di anticipare tutte le scadenze non è stata approvata. Gli importi indicati sono preventivi, non consuntivi.'
    if domain=='traduzione':
        it=f'{NAMES[v]} coordina la revisione del progetto presso la {PLACES[v]}. La consegna di {a} disegni è prevista per il {v+1} novembre 2026. Il budget disponibile è di {c} euro. Mancano ancora {b} verifiche. La data resta subordinata alla ricezione dei documenti; non è una conferma definitiva.'
        en=f'{NAMES[v]} coordinate the project review at a local workshop. We has {a} drawings to check before November {v+1}, 2026. The available budget is EUR {c}. The delivery date depends on the missing documents and is not yet confirmed.'
        return 'Testo italiano: '+it+'\nTesto inglese (per i compiti che lo richiedono): '+en
    if domain=='professionale':return f'Contesto: progetto {PLACES[v]}, referente {NAMES[v]}, {a} elaborati previsti e {b} ancora da verificare, budget {c} euro, riunione il {v+1} novembre 2026. Mancano i disegni del fornitore. La consegna proposta non è stata confermata. Non inventare accordi ulteriori.'
    if domain=='creativa':return f'Situazione: {NAMES[v]} arriva in una {PLACES[v]} e trova un oggetto che ricorda un impegno dimenticato. Inserisci il numero {a} in modo naturale. '+['Tono sobrio, nessun elemento magico.','Tono fantastico, dettagli materiali precisi.','Tono intimista, nessuna spiegazione conclusiva.'][v%3]
    if domain=='codice':return f'Caso applicativo: strumenti interni per {PLACES[v]}. Dati di esempio, se pertinenti: '+str([rng.randrange(-a,b+1) for _ in range([5,12,25][v%3])])+'. Prevedi input vuoto, duplicati e gestione degli errori. Restituisci codice e un piccolo esempio di chiamata.'
    if domain=='debug':return f'La correzione serve a un {AUDIENCES[v%5]}. Mostra la causa, una modifica minima e '+str(1+v%3)+' test, inclusi i casi ai bordi. Non sostituire il problema con una riscrittura estranea.'
    if domain in ('scienze','ingegneria'):return f'Destinatario: {AUDIENCES[v%5]}. '+['Usa un esempio numerico e controlla le unità.','Spiega assunzioni e un limite del modello.','Distingui dato noto e ipotesi, con un esempio concreto.'][v%3]
    return f'Destinatario: {AUDIENCES[v%5]}. '+['Mostra passaggi essenziali e una verifica indipendente.','Presenta il risultato prima dei passaggi e indica le ipotesi.','Spiega il ragionamento a un lettore non specialista senza omettere la verifica.'][v%3]

def requests():
    by_domain={}
    for di,(domain,_) in enumerate(DOMAINS):
        families=[]
        for s in TASKS[domain].splitlines():
            if '|' in s:families.append(s.split('|',1))
            else:families[-1][1]+='\n'+s
        assert len(families)==20,(domain,len(families))
        out=[]
        for v in range(15):
            for fi,(title,task) in enumerate(families):
                seed=20261008+di*10000+fi*100+v;rng=random.Random(seed)
                a=rng.randrange(3,15);b=rng.randrange(3,12);c=rng.randrange(120,900);d=c+rng.randrange(-80,90)
                prompt=task.format(a=a,b=b,c=c,d=d,odd=2*a+1)+'\n\n'+context(domain,rng,v,a,b,c)
                prompt+='\n\nRisposta concisa: massimo circa 120 parole, oppure il codice o i dati richiesti. Non includere ragionamento interno.'
                out.append(dict(id=f'{domain}-{v*20+fi+1:03d}',domain=domain,title=f'{title} · scenario {v+1:02d}',family=fi,variant=v,seed=seed,
                    split='holdout' if fi in (4,9,14,19) else 'train',prompt=prompt,max_new=384,prompt_sha256=hashlib.sha256(prompt.encode()).hexdigest()))
        # Shuffle within a domain, then interleave domains: any budget stop is balanced.
        random.Random(20261008+di).shuffle(out);by_domain[domain]=out
    result=[by_domain[d][i] for i in range(300) for d,_ in DOMAINS]
    assert len(result)==3600 and len({r['prompt_sha256'] for r in result})==3600
    return result
