/**
 * TILCOR — Parallel Korpus va Kollokatsiyalar Ma'lumotlar Moduli
 * Asosiy amaliy parallel manbalar (barcha to'qima namunalar olib tashlandi):
 * 1. Abdulhamid Cho‘lpon: "Kecha va kunduz" ↔ "Night and Day" (Christopher Fort tarjimasi)
 * 2. Ernest Hemingway: "The Old Man and the Sea" ↔ "Chol va dengiz" (Ibrohim G‘ofurov tarjimasi)
 */

const literaryCorporaMeta = [
    {
        id: "source-cholpon",
        titleUz: "Kecha va kunduz",
        titleEn: "Night and Day",
        author: "Abdulhamid Cho‘lpon",
        translator: "Christopher Fort (Academic Studies Press)",
        direction: "O‘zbekcha (asl nusxa) ➔ Inglizcha (tarjima)",
        genre: "Ijtimoiy-tarixiy roman",
        pagesUz: 272,
        pagesEn: 235,
        wordCount: "—",
        alignedPairs: "— (tekislash qayta ko‘rib chiqilmoqda)",
        identifiedCollocations: "—",
        description: "Sharq NMK, 2000 (ziyouz.com nusxasi) ↔ Academic Studies Press, 2019, ISBN 9781644690482.",
        badgeColor: "bg-indigo-50 text-indigo-700 dark:bg-indigo-950 dark:text-indigo-300 border-indigo-200"
    },
    {
        id: "source-hemingway",
        titleUz: "Chol va dengiz",
        titleEn: "The Old Man and the Sea",
        author: "Ernest Hemingway",
        translator: "Ibrohim G‘ofurov («Yosh gvardiya»)",
        direction: "Inglizcha (asl nusxa) ➔ O‘zbekcha (tarjima)",
        genre: "Falsafiy-ramziy qissa",
        pagesUz: 46,
        pagesEn: 52,
        wordCount: "—",
        alignedPairs: "— (tekislash qayta ko‘rib chiqilmoqda)",
        identifiedCollocations: "—",
        description: "Charles Scribner's Sons, 1952 ↔ Toshkent, «Yosh gvardiya», 1986.",
        badgeColor: "bg-emerald-50 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300 border-emerald-200"
    }
];


// Eski demo va namunalar arxivi (to'qima ma'lumotlar jamoatchilik uchun o'chirilgan)
const parallelCorpusData = [];
const collocationsData = [];
