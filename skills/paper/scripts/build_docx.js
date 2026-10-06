#!/usr/bin/env node
/**
 * build_docx.js: gera um manuscrito .docx no padrão de submissão de journal biomédico.
 *
 *   node build_docx.js manifesto.json saida.docx
 *
 * Layout produzido: página de rosto separada (sem numeração de linhas), corpo em
 * espaçamento duplo com numeração contínua de linhas e número de página, abstract
 * estruturado, palavras-chave, IMRaD, declarações, referências numeradas e legendas.
 *
 * Trechos no formato [FALTA: ...] saem em vermelho e negrito: são pedidos de dado que
 * não podem passar despercebidos na revisão do autor.
 *
 * SCHEMA DO MANIFESTO (todos os campos opcionais exceto title e sections):
 * {
 *   "title":        "Título do manuscrito",
 *   "runningTitle": "Título curto (<= 50 caracteres)",
 *   "authors": [
 *     { "name": "Nome Completo do Autor", "affiliations": [1,2], "orcid": "0000-0000-0000-0000",
 *       "corresponding": true }
 *   ],
 *   "affiliations": ["Departamento X, Universidade Y, Cidade, País", "..."],
 *   "correspondence": { "name": "...", "address": "...", "email": "...", "phone": "..." },
 *   "counts": { "abstract": 248, "main": 3150, "tables": 3, "figures": 2, "references": 41 },
 *   "abstract": [ { "heading": "Background", "text": "..." }, ... ],
 *   "keywords": ["prediction model", "calibration", "fairness"],
 *   "sections": [
 *     { "heading": "Introduction", "level": 1, "paragraphs": ["...", "..."] },
 *     { "heading": "Methods", "level": 1, "paragraphs": ["..."] },
 *     { "heading": "Study population", "level": 2, "paragraphs": ["..."] }
 *   ],
 *   "declarations": [ { "heading": "Funding", "text": "..." }, ... ],
 *   "references": ["Collins GS, Moons KGM, ... BMJ 2024;385:e078378.", "..."],
 *   "tableLegends":  ["Table 1. Baseline characteristics ..."],
 *   "figureLegends": ["Figure 1. Calibration plot ..."],
 *   "font": "Times New Roman",     // padrão
 *   "fontSize": 12,                // pt
 *   "lineSpacing": "double",       // "double" | "1.5" | "single"
 *   "pageSize": "A4",              // "A4" | "letter"
 *   "lineNumbers": true            // padrão true
 * }
 */

const fs = require("fs");
const path = require("path");

// `docx` costuma estar instalado global; resolver os dois casos.
function loadDocx() {
  try { return require("docx"); } catch (_) {}
  try {
    const root = require("child_process")
      .execSync("npm root -g", { encoding: "utf8" }).trim();
    return require(path.join(root, "docx"));
  } catch (e) {
    console.error("erro: lib 'docx' nao encontrada. rode: npm install -g docx");
    process.exit(1);
  }
}

const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType,
  PageBreak, Footer, PageNumber, LineNumberRestartFormat, PageOrientation,
  convertInchesToTwip,
} = loadDocx();

// ---------- entrada ----------

const [, , manifestPath, outPath] = process.argv;
if (!manifestPath || !outPath) {
  console.error("uso: node build_docx.js manifesto.json saida.docx");
  process.exit(1);
}
const m = JSON.parse(fs.readFileSync(manifestPath, "utf8"));
if (!m.title) { console.error("erro: manifesto sem 'title'"); process.exit(1); }
if (!Array.isArray(m.sections) || m.sections.length === 0) {
  console.error("erro: manifesto sem 'sections'"); process.exit(1);
}

const FONT = m.font || "Times New Roman";
const SIZE = (m.fontSize || 12) * 2;          // half-points
const SPACING = { double: 480, "1.5": 360, single: 240 }[m.lineSpacing || "double"] || 480;
const LINE_NUMBERS = m.lineNumbers !== false;

const PAGE = (m.pageSize || "A4").toLowerCase() === "letter"
  ? { width: 12240, height: 15840 }
 : { width: 11906, height: 16838 };

// ---------- helpers ----------

// Quebra o texto em runs, destacando [FALTA: ...] em vermelho e negrito.
function runs(text, base = {}) {
  const out = [];
  const re = /\[FALTA:[^\]]*\]/g;
  let last = 0, mt;
  while ((mt = re.exec(text)) !== null) {
    if (mt.index > last) {
      out.push(new TextRun({ text: text.slice(last, mt.index), font: FONT, size: SIZE, ...base }));
    }
    out.push(new TextRun({ text: mt[0], font: FONT, size: SIZE, bold: true, color: "C00000" }));
    last = mt.index + mt[0].length;
  }
  if (last < text.length) {
    out.push(new TextRun({ text: text.slice(last), font: FONT, size: SIZE, ...base }));
  }
  return out.length ? out: [new TextRun({ text: "", font: FONT, size: SIZE })];
}

// A página de rosto não leva numeração de linha. w:lnNumType é por seção, mas o
// LibreOffice trata numeração como ajuste de documento e vaza para a primeira seção;
// suprimir por parágrafo (w:suppressLineNumbers) funciona no Word e no LibreOffice.
let SUPPRESS = false;

function p(text, opts = {}) {
  const { bold, italics, align, spaced = true, indent, heading, before, after } = opts;
  return new Paragraph({
    children: runs(String(text ?? ""), { bold, italics }),
    alignment: align,
    heading,
    suppressLineNumbers: SUPPRESS || undefined,
    spacing: {
      line: spaced ? SPACING: 240,
      before: before ?? 0,
      after: after ?? (spaced ? 0: 120),
    },
    indent: indent ? { firstLine: convertInchesToTwip(0.5) }: undefined,
  });
}

function blank() { return p("", { spaced: false }); }

function h(text, level = 1) {
  return new Paragraph({
    children: [new TextRun({
      text, font: FONT, size: SIZE, bold: true, italics: level >= 2, color: "000000",
    })],
    heading: level === 1 ? HeadingLevel.HEADING_1: HeadingLevel.HEADING_2,
    suppressLineNumbers: SUPPRESS || undefined,
    spacing: { line: SPACING, before: 240, after: 120 },
  });
}

function sup(n) {
  return new TextRun({ text: String(n), font: FONT, size: SIZE, superScript: true });
}

// ---------- página de rosto ----------

SUPPRESS = true;
const title = [];
title.push(p(m.title, { bold: true, align: AlignmentType.CENTER, spaced: false }));
title.push(blank());

if (Array.isArray(m.authors) && m.authors.length) {
  const kids = [];
  m.authors.forEach((a, i) => {
    if (i) kids.push(new TextRun({ text: ", ", font: FONT, size: SIZE }));
    kids.push(new TextRun({ text: a.name, font: FONT, size: SIZE }));
    (a.affiliations || []).forEach((n, j) => {
      kids.push(sup((j ? ",": "") + n));
    });
    if (a.corresponding) kids.push(sup("*"));
  });
  title.push(new Paragraph({
    children: kids, alignment: AlignmentType.CENTER,
    suppressLineNumbers: true, spacing: { line: 240, after: 200 },
  }));
}

if (Array.isArray(m.affiliations) && m.affiliations.length) {
  m.affiliations.forEach((aff, i) => {
    title.push(new Paragraph({
      children: [sup(i + 1), new TextRun({ text: " " + aff, font: FONT, size: SIZE })],
      suppressLineNumbers: true,
      spacing: { line: 240, after: 40 },
    }));
  });
  title.push(blank());
}

const orcids = (m.authors || []).filter(a => a.orcid);
if (orcids.length) {
  title.push(p("ORCID", { bold: true, spaced: false }));
  orcids.forEach(a => title.push(p(`${a.name}: ${a.orcid}`, { spaced: false })));
  title.push(blank());
}

if (m.runningTitle) {
  title.push(p(`Running title: ${m.runningTitle}`, { spaced: false }));
}

if (m.correspondence) {
  const c = m.correspondence;
  title.push(blank());
  title.push(p("* Corresponding author", { bold: true, spaced: false }));
  [c.name, c.address, c.email, c.phone].filter(Boolean).forEach(l => title.push(p(l, { spaced: false })));
}

if (m.counts) {
  const c = m.counts, bits = [];
  if (c.abstract) bits.push(`Abstract: ${c.abstract} words`);
  if (c.main) bits.push(`Main text: ${c.main} words`);
  if (c.tables != null) bits.push(`Tables: ${c.tables}`);
  if (c.figures != null) bits.push(`Figures: ${c.figures}`);
  if (c.references != null) bits.push(`References: ${c.references}`);
  if (bits.length) { title.push(blank()); title.push(p(bits.join(" · "), { spaced: false })); }
}

SUPPRESS = false;

// ---------- corpo ----------

const body = [];

if (Array.isArray(m.abstract) && m.abstract.length) {
  body.push(h("Abstract"));
  m.abstract.forEach(part => {
    if (part.heading) {
      body.push(new Paragraph({
        children: [
          new TextRun({ text: part.heading + ". ", font: FONT, size: SIZE, bold: true }),
          ...runs(part.text || ""),
        ],
        spacing: { line: SPACING, after: 60 },
      }));
    } else {
      body.push(p(part.text || ""));
    }
  });
}

if (Array.isArray(m.keywords) && m.keywords.length) {
  body.push(blank());
  body.push(new Paragraph({
    children: [
      new TextRun({ text: "Keywords: ", font: FONT, size: SIZE, bold: true }),
      new TextRun({ text: m.keywords.join("; "), font: FONT, size: SIZE }),
    ],
    spacing: { line: SPACING },
  }));
}

if ((m.abstract && m.abstract.length) || (m.keywords && m.keywords.length)) {
  body.push(new Paragraph({ children: [new PageBreak()] }));
}

m.sections.forEach(sec => {
  if (sec.heading) body.push(h(sec.heading, sec.level || 1));
  (sec.paragraphs || []).forEach((t, i) => body.push(p(t, { indent: i > 0 })));
});

if (Array.isArray(m.declarations) && m.declarations.length) {
  body.push(new Paragraph({ children: [new PageBreak()] }));
  body.push(h("Declarations"));
  m.declarations.forEach(d => {
    body.push(new Paragraph({
      children: [
        new TextRun({ text: (d.heading || "") + (d.heading ? ". ": ""), font: FONT, size: SIZE, bold: true }),
        ...runs(d.text || ""),
      ],
      spacing: { line: SPACING, after: 60 },
    }));
  });
}

if (Array.isArray(m.references) && m.references.length) {
  body.push(new Paragraph({ children: [new PageBreak()] }));
  body.push(h("References"));
  m.references.forEach((r, i) => body.push(p(`${i + 1}. ${r}`)));
}

if (Array.isArray(m.tableLegends) && m.tableLegends.length) {
  body.push(new Paragraph({ children: [new PageBreak()] }));
  body.push(h("Table legends"));
  m.tableLegends.forEach(t => { body.push(p(t)); body.push(blank()); });
}

if (Array.isArray(m.figureLegends) && m.figureLegends.length) {
  if (!(m.tableLegends || []).length) body.push(new Paragraph({ children: [new PageBreak()] }));
  body.push(h("Figure legends"));
  m.figureLegends.forEach(f => { body.push(p(f)); body.push(blank()); });
}

// ---------- documento ----------

const footer = new Footer({
  children: [new Paragraph({
    alignment: AlignmentType.CENTER,
    suppressLineNumbers: true,
    children: [new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: SIZE })],
  })],
});

const pageProps = {
  size: { width: PAGE.width, height: PAGE.height, orientation: PageOrientation.PORTRAIT },
  margin: {
    top: convertInchesToTwip(1), bottom: convertInchesToTwip(1),
    left: convertInchesToTwip(1), right: convertInchesToTwip(1),
  },
};

// Os estilos internos de heading do docx-js saem em azul; manuscrito é preto.
const headingStyle = (id) => ({
  id, name: id, basedOn: "Normal", quickFormat: true,
  run: { font: FONT, size: SIZE, bold: true, color: "000000" },
});

const doc = new Document({
  creator: (m.authors && m.authors[0] && m.authors[0].name) || "",
  title: m.title,
  styles: {
    default: { document: { run: { font: FONT, size: SIZE, color: "000000" } } },
    paragraphStyles: [headingStyle("Heading1"), headingStyle("Heading2"), headingStyle("Heading3")],
  },
  sections: [
    { properties: { page: pageProps }, footers: { default: footer }, children: title },
    {
      properties: {
        page: pageProps,
        ...(LINE_NUMBERS ? {
          lineNumbers: { countBy: 1, restart: LineNumberRestartFormat.CONTINUOUS, distance: 360 },
        }: {}),
      },
      footers: { default: footer },
      children: body,
    },
  ],
});

Packer.toBuffer(doc).then(buf => {
  fs.mkdirSync(path.dirname(path.resolve(outPath)), { recursive: true });
  fs.writeFileSync(outPath, buf);
  const falta = JSON.stringify(m).match(/\[FALTA:/g);
  console.log(`ok: ${outPath}`);
  if (falta) console.log(`atencao: ${falta.length} marcador(es) [FALTA: ...] no manuscrito`);
}).catch(e => { console.error("falha ao gerar docx:", e); process.exit(1); });
