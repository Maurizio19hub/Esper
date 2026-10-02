// Documenti di esempio per la modalità demo (dati simulati).
import type { DocKind, DocStatus } from '../types';
import { blueprintArt, catArt, screenshotArt, sunsetArt } from './art';

export interface SeedDoc {
  name: string;
  kind: DocKind;
  size: number;
  tags: string[];
  daysAgo: number;
  pages?: number;
  /** Testo unico (verrà suddiviso in chunk). */
  text?: string;
  /** Testo per pagina (PDF). */
  pagesText?: string[];
  /** Per le immagini: testo OCR e/o descrizione visiva. */
  ocr?: string;
  visual?: string;
  art?: () => string;
  status?: DocStatus;
  error?: string;
}

export const SEED: SeedDoc[] = [
  {
    name: 'Contratto di locazione - Via Roma 12.pdf',
    kind: 'pdf',
    size: 412_000,
    pages: 8,
    tags: ['casa', 'contratti', 'importante'],
    daysAgo: 90,
    pagesText: [
      "CONTRATTO DI LOCAZIONE AD USO ABITATIVO. Tra il sig. Mario Rossi (locatore) e la sig.ra Giulia Bianchi (conduttore) si stipula la locazione dell'appartamento sito in Torino, Via Roma 12, piano 3, interno 7, composto da quattro vani più servizi.",
      "Il canone annuo è fissato in euro 9.600, pagabile in rate mensili anticipate di euro 800 da versare entro il giorno 5 di ogni mese tramite bonifico bancario. A garanzia degli obblighi il conduttore versa un deposito cauzionale pari a tre mensilità.",
      "La durata del contratto è di quattro anni, rinnovabili per ulteriori quattro, ai sensi della legge 431/1998. La disdetta deve essere comunicata con preavviso di sei mesi tramite raccomandata. Le spese condominiali ordinarie sono a carico del conduttore.",
    ],
  },
  {
    name: 'Ricetta tiramisù della nonna.md',
    kind: 'markdown',
    size: 2_100,
    tags: ['cucina', 'ricette'],
    daysAgo: 40,
    text: `# Tiramisù della nonna

Un dolce al cucchiaio senza cottura, perfetto per le cene con gli amici.

## Ingredienti

- 500 g di mascarpone
- 4 uova fresche
- 120 g di zucchero
- 300 g di savoiardi
- caffè ristretto zuccherato
- cacao amaro in polvere

## Preparazione

Separa i tuorli dagli albumi. Monta i tuorli con lo zucchero fino a ottenere una crema chiara, poi incorpora il mascarpone. Monta gli albumi a neve ferma e aggiungili delicatamente alla crema.

Inzuppa velocemente i savoiardi nel caffè freddo e disponili a strati alternati con la crema. Lascia riposare in frigorifero almeno sei ore e spolvera di cacao prima di servire.`,
  },
  {
    name: 'Appunti - Reti neurali e backpropagation.md',
    kind: 'markdown',
    size: 5_400,
    tags: ['studio', 'ai'],
    daysAgo: 21,
    text: `# Reti neurali: appunti di lezione

Una rete neurale è composta da strati di neuroni artificiali. Ogni neurone calcola una somma pesata dei suoi ingressi e applica una funzione di attivazione non lineare, come ReLU o sigmoide.

## Addestramento

L'addestramento consiste nel minimizzare una funzione di perdita sui dati di esempio. La backpropagation calcola il gradiente della perdita rispetto ai pesi applicando la regola della catena, strato per strato, dall'uscita verso l'ingresso.

Il gradiente viene poi usato dalla discesa del gradiente stocastica (SGD) o da varianti come Adam per aggiornare i pesi. Un learning rate troppo alto fa divergere l'addestramento, uno troppo basso lo rallenta.

## Transformer

I transformer sostituiscono la ricorrenza con il meccanismo di attention: ogni token pesa gli altri token della sequenza. Sono alla base dei modelli di embedding e dei grandi modelli linguistici.`,
  },
  {
    name: 'Fattura 2024-0381 - Idraulico Bertoni.pdf',
    kind: 'pdf',
    size: 98_000,
    pages: 1,
    tags: ['fatture', 'casa'],
    daysAgo: 150,
    pagesText: [
      "FATTURA n. 2024-0381 del 12/03/2024. Bertoni Impianti Idraulici S.r.l., P.IVA 01234567890. Intervento di sostituzione del rubinetto miscelatore e riparazione di una perdita sotto il lavello della cucina. Manodopera: 2 ore, euro 90,00. Materiali: euro 64,50. Imponibile euro 154,50, IVA 22% euro 33,99. Totale da pagare euro 188,49 entro 30 giorni.",
    ],
  },
  {
    name: 'Tramonto a Cala Gonone.jpg',
    kind: 'image',
    size: 2_300_000,
    tags: ['foto', 'vacanze'],
    daysAgo: 60,
    art: sunsetArt,
    visual: 'Fotografia di un tramonto sul mare: cielo arancione e viola, il sole si abbassa sull’orizzonte e si riflette sull’acqua, scogliera scura in primo piano.',
  },
  {
    name: 'Schema impianto elettrico cucina.png',
    kind: 'image',
    size: 640_000,
    tags: ['casa', 'schemi'],
    daysAgo: 75,
    art: blueprintArt,
    ocr: 'QUADRO PRINCIPALE. Linea 1: prese cucina 16A. Linea 2: forno 25A. Linea 3: illuminazione 10A. Interruttore differenziale 30 mA. Sezione cavi 2,5 mm².',
    visual: 'Schema tecnico su sfondo blu, in stile blueprint, con un quadro elettrico collegato a più linee e punti di derivazione.',
  },
  {
    name: 'Diario di viaggio - Lisbona.txt',
    kind: 'text',
    size: 8_900,
    tags: ['viaggi', 'diario'],
    daysAgo: 110,
    text: `Giorno 1. Siamo arrivati a Lisbona nel primo pomeriggio. Il volo è stato puntuale e il tram 28 ci ha portati fino all'Alfama, dove abbiamo lasciato le valigie in hotel.

Giorno 2. Mattinata a Belém: la torre, il monastero dei Jerónimos e, naturalmente, i pastéis de nata nella pasticceria storica. Nel pomeriggio siamo saliti al belvedere di Santa Luzia per ammirare i tetti rossi e il fiume.

Giorno 3. Gita a Sintra tra palazzi colorati e foreste di nebbia. Il Palácio da Pena è il posto più surreale in cui io sia mai stato. Cena con baccalà e vinho verde in un localino del Bairro Alto.`,
  },
  {
    name: 'Manuale caldaia Vaillant ecoTEC.pdf',
    kind: 'pdf',
    size: 3_200_000,
    pages: 64,
    tags: ['casa', 'manuali'],
    daysAgo: 200,
    pagesText: [
      "La pressione dell'impianto di riscaldamento deve essere compresa tra 1,0 e 2,0 bar a freddo. Se la pressione scende sotto 0,8 bar il display mostra l'errore F22: aprire il rubinetto di carico e ripristinare la pressione, quindi sbloccare la caldaia.",
      "Manutenzione ordinaria: la caldaia deve essere controllata una volta l'anno da un tecnico abilitato. Il controllo include la pulizia dello scambiatore, la verifica dei fumi e il controllo del vaso di espansione.",
    ],
  },
  {
    name: 'Idee per la tesi magistrale.md',
    kind: 'markdown',
    size: 3_300,
    tags: ['studio', 'tesi', 'ai'],
    daysAgo: 14,
    text: `# Idee per la tesi

## Ricerca semantica su archivi personali

Confrontare ricerca per parole chiave e ricerca vettoriale su un archivio di documenti eterogenei. Gli embedding permettono di trovare documenti pertinenti anche senza parole in comune con la query.

Domanda di ricerca: quanto migliora il recall usando una ricerca ibrida (BM25 più embedding) rispetto ai due metodi separati?

## Valutazione

Costruire un piccolo insieme di prova con coppie domanda-documento e misurare il recall@10. Valutare l'effetto della dimensione dei chunk e del modello di embedding multilingue.`,
  },
  {
    name: 'Borges - Appunti su La Biblioteca di Babele.md',
    kind: 'markdown',
    size: 2_800,
    tags: ['letteratura', 'appunti'],
    daysAgo: 30,
    text: `# La Biblioteca di Babele

Il racconto di Borges descrive l'universo come una biblioteca infinita di gallerie esagonali, che contiene tutti i libri possibili di quattrocentodieci pagine.

La maggior parte dei volumi è sequenza casuale di lettere senza senso. Eppure la certezza che da qualche parte esista il libro che giustifica tutto spinge i bibliotecari a una ricerca disperata.

Il tema del catalogo perfetto e dell'impossibilità di orientarsi in un archivio infinito è sorprendentemente attuale: ogni sistema di ricerca è un tentativo di domare Babele.`,
  },
  {
    name: 'Referto visita cardiologica.pdf',
    kind: 'pdf',
    size: 156_000,
    pages: 2,
    tags: ['salute', 'importante'],
    daysAgo: 45,
    pagesText: [
      "Referto di visita cardiologica con elettrocardiogramma a riposo. Ritmo sinusale regolare, frequenza 68 bpm, pressione arteriosa 120/78 mmHg. Non si rilevano alterazioni del tratto ST. Si consiglia attività fisica aerobica regolare e controllo annuale.",
    ],
  },
  {
    name: 'Piano di allenamento autunno.md',
    kind: 'markdown',
    size: 1_400,
    tags: ['sport'],
    daysAgo: 8,
    text: `# Piano di allenamento

Obiettivo: correre dieci chilometri sotto i cinquanta minuti entro dicembre.

- Lunedì: corsa leggera 5 km
- Mercoledì: ripetute 6 x 800 m con recupero di 2 minuti
- Venerdì: palestra, esercizi per gambe e core
- Domenica: lungo lento da 8 a 12 km

Ogni quattro settimane una settimana di scarico per recuperare.`,
  },
  {
    name: 'Screenshot errore login.png',
    kind: 'image',
    size: 188_000,
    tags: ['lavoro', 'bug'],
    daysAgo: 3,
    art: screenshotArt,
    ocr: 'Errore 401: credenziali non valide. Riprova o reimposta la password. Accedi.',
    visual: 'Schermata di una finestra di login con due campi e un messaggio di errore in rosso.',
  },
  {
    name: 'Il gatto sul divano.jpg',
    kind: 'image',
    size: 1_700_000,
    tags: ['foto'],
    daysAgo: 12,
    art: catArt,
    visual: 'Fotografia di un gatto arancione che dorme comodamente su un divano marrone, in un salotto.',
  },
  {
    name: 'Bilancio familiare 2025.pdf',
    kind: 'pdf',
    size: 245_000,
    pages: 5,
    tags: ['finanze'],
    daysAgo: 20,
    pagesText: [
      'Riepilogo spese annuali: affitto euro 9.600, utenze euro 1.450, alimentari euro 4.800, trasporti euro 1.900, tempo libero euro 2.100. Le entrate complessive ammontano a euro 31.200.',
      "Obiettivo di risparmio: mettere da parte il 15% delle entrate, pari a circa euro 4.680, in un fondo di emergenza. Da rivedere a giugno la voce relativa all'energia.",
    ],
  },
  {
    name: 'Scansione contratto auto.pdf',
    kind: 'pdf',
    size: 5_100_000,
    pages: 3,
    tags: ['auto'],
    daysAgo: 5,
    pagesText: [],
    status: 'error',
    error: 'Nessun testo estraibile: la scansione è troppo sfocata e l’OCR non ha riconosciuto caratteri.',
  },
  {
    name: 'Relazione trimestrale Q3.pdf',
    kind: 'pdf',
    size: 1_050_000,
    pages: 12,
    tags: ['lavoro'],
    daysAgo: 0,
    pagesText: [
      'Relazione del terzo trimestre: i ricavi crescono del 12% rispetto al trimestre precedente, trainati dalla nuova linea di prodotti. I costi operativi restano stabili e il margine operativo sale al 18%.',
    ],
    status: 'queued',
  },
];
