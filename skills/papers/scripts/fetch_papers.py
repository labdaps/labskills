#!/usr/bin/env python3
"""
fetch_papers.py: Varre arXiv, PubMed e medRxiv em paralelo buscando papers
de IA/ML aplicada a medicina publicados nos últimos N dias.

Uso:
    python3 fetch_papers.py --topic "LLM for EHR extraction" --days 7

Saída: markdown formatado no stdout, pronto pra repassar ao usuário.
Logs de progresso vão no stderr.
"""

import argparse
import json
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone

# ------------------------------------------------------------
# Keywords para filtrar relevância metodológica e clínica
# ------------------------------------------------------------

AI_KEYWORDS = [
    # Gerais
    "machine learning", "deep learning", "artificial intelligence",
    "neural network", "reinforcement learning",
    "supervised learning", "unsupervised learning", "self-supervised",
    "semi-supervised", "transfer learning", "federated learning",
    "meta-learning", "few-shot", "zero-shot", "in-context learning",
    # Arquiteturas
    "transformer", "attention mechanism", "convolutional",
    "recurrent neural", "cnn ", "rnn ", "lstm", "gru ",
    "autoencoder", "gan ", "diffusion model", "variational",
    # LLMs
    "large language model", " llm ", " llms ",
    "foundation model", "pretrained", "pre-trained",
    "fine-tuning", "fine-tuned", "instruction-tuned",
    "retrieval-augmented", "rag ", " rag,", " rag.",
    "embedding", "sentence embedding", "word embedding",
    # Modelos
    "bert", "gpt-", "gpt ", "llama", "mistral", "claude ",
    "gemini", "clip ", " vit ", "vision transformer",
    # Clássicos
    "random forest", "xgboost", "gradient boosting",
    "support vector machine",
    # Áreas
    "computer vision", "natural language processing", " nlp ",
    "image segmentation", "object detection",
    "named entity recognition", "text classification",
    # Modelos preditivos/validação
    "predictive model", "prediction model", "risk prediction",
]

MEDICAL_KEYWORDS = [
    "medical", "medicine", "clinical", "clinic",
    "health", "healthcare", "health care",
    "patient", "hospital", "hospitalization",
    "disease", "diagnosis", "diagnostic", "prognosis", "prognostic",
    "ehr", "emr", "electronic health record", "electronic medical record",
    "radiology", "radiological", "pathology", "pathological",
    "cardiology", "oncology", "neurology", "psychiatry",
    "icu", "intensive care", "emergency department", "ambulatory",
    "primary care", "drug ", "pharmaceutical", "therapy",
    "therapeutic", "treatment", "outcome", "mortality",
    "morbidity", "readmission", "physician", "clinician",
    "surgery", "surgical", "medical imaging", "ultrasound",
    "ct scan", " mri ", "x-ray", "ecg", "ekg",
    "biomedical", "biomarker",
    "covid", "cancer", "tumor", "sepsis", "diabetes",
    "cardiovascular", "pulmonary", "kidney", "liver",
]

HEADERS = {"User-Agent": "papers-skill/1.0 (github.com/labdaps/labskills)"}


# ------------------------------------------------------------
# Utilidades
# ------------------------------------------------------------

def log(msg):
    print(msg, file=sys.stderr)


def http_get(url, timeout=30):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="replace")


def normalize_text(s):
    if not s:
        return ""
    return re.sub(r"\s+", " ", s).strip()


def lower(s):
    return (s or "").lower()


def contains_any(text, keywords):
    t = " " + lower(text) + " "
    return any(kw in t for kw in keywords)


STOPWORDS = {
    "a", "o", "e", "de", "da", "do", "em", "para", "com", "sobre",
    "na", "no", "os", "as", "dos", "das", "por",
    "the", "of", "in", "for", "on", "with", "about", "and", "or",
    "to", "from", "at", "as", "is", "are", "be", "an",
}


def topic_terms(topic):
    """Extrai termos significativos (>2 chars, sem stopwords)."""
    words = re.findall(r"[A-Za-zÀ-ÿ0-9]+", topic)
    return [w.lower() for w in words if len(w) > 2 and w.lower() not in STOPWORDS]


def matches_topic(text, terms, min_matches=1):
    """Retorna True se pelo menos `min_matches` termos aparecem no texto."""
    if not terms:
        return True
    t = lower(text)
    hits = sum(1 for term in terms if term in t)
    return hits >= min_matches


# ------------------------------------------------------------
# arXiv
# ------------------------------------------------------------

def fetch_arxiv(topic, date_start, date_end, max_results=25):
    cats = "cat:cs.AI OR cat:cs.LG OR cat:cs.CL OR cat:cs.CV OR cat:stat.ML OR cat:q-bio.QM"
    ds = date_start.strftime("%Y%m%d") + "0000"
    de = date_end.strftime("%Y%m%d") + "2359"
    terms = topic_terms(topic)

    if terms:
        topic_query = " AND ".join(f'all:"{t}"' for t in terms[:4])
    else:
        topic_query = f'all:"{topic}"'

    query = f'({topic_query}) AND ({cats}) AND submittedDate:[{ds} TO {de}]'
    url = (
        "http://export.arxiv.org/api/query?"
        f"search_query={urllib.parse.quote(query)}"
        f"&start=0&max_results={max_results}"
        "&sortBy=submittedDate&sortOrder=descending"
    )

    try:
        xml_data = http_get(url, timeout=30)
    except Exception as e:
        log(f"⚠️ arXiv indisponível: {e}")
        return []

    ns = {"atom": "http://www.w3.org/2005/Atom",
          "arxiv": "http://arxiv.org/schemas/atom"}
    try:
        root = ET.fromstring(xml_data)
    except ET.ParseError as e:
        log(f"⚠️ arXiv parse error: {e}")
        return []

    papers = []
    for entry in root.findall("atom:entry", ns):
        id_el = entry.find("atom:id", ns)
        title_el = entry.find("atom:title", ns)
        summary_el = entry.find("atom:summary", ns)
        published_el = entry.find("atom:published", ns)
        authors = [
            a.find("atom:name", ns).text
            for a in entry.findall("atom:author", ns)
            if a.find("atom:name", ns) is not None
        ]
        categories = [
            c.get("term") for c in entry.findall("atom:category", ns)
            if c.get("term")
        ]
        doi_el = entry.find("arxiv:doi", ns)

        abs_url = id_el.text.strip() if id_el is not None else ""
        arxiv_id = abs_url.rsplit("/", 1)[-1].split("v")[0] if abs_url else ""
        title = normalize_text(title_el.text if title_el is not None else "")
        abstract = normalize_text(summary_el.text if summary_el is not None else "")
        pub = published_el.text[:10] if published_el is not None else ""
        doi = (doi_el.text if doi_el is not None
               else f"10.48550/arXiv.{arxiv_id}" if arxiv_id else "")

        combined = f"{title} {abstract}"
        # arXiv é CS: precisa garantir contexto médico + IA
        if not contains_any(combined, MEDICAL_KEYWORDS):
            continue
        if not contains_any(combined, AI_KEYWORDS):
            continue

        papers.append({
            "source": "arXiv",
            "venue": ", ".join(categories[:2]) if categories else "arXiv",
            "title": title,
            "authors": authors,
            "date": pub,
            "doi": doi,
            "url": abs_url,
            "abstract": abstract,
        })
    return papers


# ------------------------------------------------------------
# PubMed (E-utilities)
# ------------------------------------------------------------

def fetch_pubmed(topic, date_start, date_end, max_results=25):
    ds = date_start.strftime("%Y/%m/%d")
    de = date_end.strftime("%Y/%m/%d")
    ai_filter = (
        '("artificial intelligence"[MeSH Terms] OR "machine learning"[MeSH Terms] '
        'OR "deep learning"[tiab] OR "neural network"[tiab] OR "neural networks"[tiab] '
        'OR "large language model"[tiab] OR "large language models"[tiab] '
        'OR "foundation model"[tiab] OR "LLM"[tiab] OR "transformer"[tiab] '
        'OR "natural language processing"[tiab])'
    )
    query = f'({topic}) AND {ai_filter} AND ("{ds}"[PDAT]: "{de}"[PDAT])'
    esearch_url = (
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?"
        f"db=pubmed&term={urllib.parse.quote(query)}"
        f"&retmode=json&retmax={max_results}&sort=date"
    )
    try:
        resp = http_get(esearch_url, timeout=30)
        ids = json.loads(resp).get("esearchresult", {}).get("idlist", [])
    except Exception as e:
        log(f"⚠️ PubMed esearch indisponível: {e}")
        return []

    if not ids:
        return []

    efetch_url = (
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?"
        f"db=pubmed&id={','.join(ids)}&retmode=xml"
    )
    time.sleep(0.4)  # rate limit NCBI: 3 req/s sem API key
    try:
        xml_data = http_get(efetch_url, timeout=60)
    except Exception as e:
        log(f"⚠️ PubMed efetch indisponível: {e}")
        return []

    try:
        root = ET.fromstring(xml_data)
    except ET.ParseError as e:
        log(f"⚠️ PubMed parse error: {e}")
        return []

    month_map = {
        "jan": "01", "feb": "02", "mar": "03", "apr": "04",
        "may": "05", "jun": "06", "jul": "07", "aug": "08",
        "sep": "09", "oct": "10", "nov": "11", "dec": "12",
    }
    papers = []
    for article in root.findall(".//PubmedArticle"):
        title_el = article.find(".//ArticleTitle")
        title = normalize_text(
            "".join(title_el.itertext()) if title_el is not None else ""
        )

        abstract_parts = []
        for ab in article.findall(".//Abstract/AbstractText"):
            label = ab.get("Label")
            txt = "".join(ab.itertext())
            abstract_parts.append(f"{label}: {txt}" if label else txt)
        abstract = normalize_text(" ".join(abstract_parts))

        authors = []
        for a in article.findall(".//Author"):
            ln = a.find("LastName")
            fn = a.find("ForeName")
            initials = a.find("Initials")
            if ln is not None and ln.text:
                name = ln.text
                if fn is not None and fn.text:
                    name = f"{ln.text} {fn.text}"
                elif initials is not None and initials.text:
                    name = f"{ln.text} {initials.text}"
                authors.append(name)
            else:
                coll = a.find("CollectiveName")
                if coll is not None and coll.text:
                    authors.append(coll.text)

        journal_el = article.find(".//Journal/Title")
        venue = normalize_text(
            journal_el.text if journal_el is not None else "PubMed"
        )

        # Data: tentar ArticleDate primeiro (mais preciso), depois PubDate
        pub_date = None
        for path in [".//ArticleDate", ".//PubDate"]:
            pd = article.find(path)
            if pd is None:
                continue
            y = pd.findtext("Year")
            m = pd.findtext("Month") or "01"
            d = pd.findtext("Day") or "01"
            if y:
                m_norm = month_map.get(m[:3].lower(),
                                       m.zfill(2) if m.isdigit() else "01")
                pub_date = f"{y}-{m_norm}-{d.zfill(2)}"
                break

        pmid_el = article.find(".//PMID")
        pmid = pmid_el.text if pmid_el is not None else ""
        doi = ""
        for id_el in article.findall(".//ArticleId"):
            if id_el.get("IdType") == "doi":
                doi = id_el.text or ""
                break
        url = (f"https://doi.org/{doi}" if doi
               else f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/")

        if not pub_date:
            pub_date = date_end.strftime("%Y-%m-%d")

        papers.append({
            "source": "PubMed",
            "venue": venue,
            "title": title,
            "authors": authors,
            "date": pub_date,
            "doi": doi or f"PMID:{pmid}",
            "url": url,
            "abstract": abstract,
        })

    return papers


# ------------------------------------------------------------
# medRxiv
# ------------------------------------------------------------

def fetch_medrxiv(topic, date_start, date_end, max_results=25):
    ds = date_start.strftime("%Y-%m-%d")
    de = date_end.strftime("%Y-%m-%d")
    terms = topic_terms(topic)

    all_items = []
    cursor = 0
    for _ in range(6):  # até 600 preprints
        url = f"https://api.biorxiv.org/details/medrxiv/{ds}/{de}/{cursor}"
        try:
            resp = http_get(url, timeout=30)
            data = json.loads(resp)
        except Exception as e:
            log(f"⚠️ medRxiv indisponível: {e}")
            break
        items = data.get("collection", [])
        if not items:
            break
        all_items.extend(items)
        total = 0
        msgs = data.get("messages", [])
        if msgs and isinstance(msgs, list):
            total = int(msgs[0].get("total", 0) or 0)
        cursor += len(items)
        if cursor >= total or len(items) < 100:
            break
        time.sleep(0.3)

    papers = []
    for it in all_items:
        title = normalize_text(it.get("title", ""))
        abstract = normalize_text(it.get("abstract", ""))
        combined = f"{title} {abstract}"
        # medRxiv já é biomédico: filtrar por AI + topic
        if not contains_any(combined, AI_KEYWORDS):
            continue
        if not matches_topic(combined, terms, min_matches=1):
            continue

        authors = [a.strip() for a in re.split(r"[;,]", it.get("authors", ""))
                   if a.strip()]
        doi = it.get("doi", "") or ""
        papers.append({
            "source": "medRxiv",
            "venue": it.get("category") or "medRxiv (preprint)",
            "title": title,
            "authors": authors,
            "date": it.get("date", "") or "",
            "doi": doi,
            "url": f"https://doi.org/{doi}" if doi else "",
            "abstract": abstract,
        })

    # Dedup interno por DOI (versões múltiplas do mesmo preprint)
    seen = set()
    deduped = []
    for p in sorted(papers, key=lambda x: x["date"], reverse=True):
        key = (p["doi"] or "").lower()
        if key and key in seen:
            continue
        if key:
            seen.add(key)
        deduped.append(p)
    return deduped[:max_results]


# ------------------------------------------------------------
# Dedup + render
# ------------------------------------------------------------

def norm_title(t):
    return re.sub(r"[^a-z0-9]+", "", lower(t))[:80]


def dedupe(papers):
    seen_doi, seen_title, out = set(), set(), []
    for p in papers:
        doi = (p.get("doi") or "").lower().strip()
        tkey = norm_title(p["title"])
        if doi and doi in seen_doi:
            continue
        if tkey and tkey in seen_title:
            continue
        if doi:
            seen_doi.add(doi)
        if tkey:
            seen_title.add(tkey)
        out.append(p)
    return out


def format_authors(authors):
    if not authors:
        return "-"
    if len(authors) <= 5:
        return ", ".join(authors)
    return ", ".join(authors[:3]) + ", et al."


def truncate(text, max_chars=350):
    if not text:
        return "-"
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rsplit(" ", 1)[0] + "..."


def render_markdown(papers, topic, date_start, date_end):
    if not papers:
        return (f"**0 papers encontrados** para *{topic}* "
                f"entre {date_start} e {date_end}.\n\n"
                f"Sugestões: ampliar a janela (`--days 14` ou `--days 30`), "
                f"simplificar o tópico, ou tentar sinônimos em inglês.")

    lines = [
        f"**{len(papers)} paper(s) encontrado(s)** · tópico: *{topic}* · "
        f"janela: {date_start} → {date_end}",
        "",
    ]
    for i, p in enumerate(papers, 1):
        doi = p.get("doi", "")
        url = p.get("url", "")
        doi_line = f"[{doi}]({url})" if url else (doi or "-")
        lines.append(f"### {i}. {p['title']}")
        lines.append(f"**Autores:** {format_authors(p['authors'])}  ")
        lines.append(f"**Fonte:** {p['source']} · {p['venue']} · {p['date']}  ")
        lines.append(f"**DOI/ID:** {doi_line}  ")
        lines.append(f"**Abstract:** {truncate(p.get('abstract', ''))}")
        lines.append("")
    return "\n".join(lines)


# ------------------------------------------------------------
# Main
# ------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(
        description="Varre arXiv + PubMed + medRxiv por papers de IA em medicina."
    )
    ap.add_argument("--topic", required=True,
                    help="Tópico/keywords (idealmente em inglês)")
    ap.add_argument("--days", type=int, default=7,
                    help="Janela em dias (padrão 7)")
    ap.add_argument("--max-per-source", type=int, default=25,
                    help="Limite por fonte antes do merge")
    ap.add_argument("--no-arxiv", action="store_true")
    ap.add_argument("--no-pubmed", action="store_true")
    ap.add_argument("--no-medrxiv", action="store_true")
    args = ap.parse_args()

    today = datetime.now(timezone.utc).date()
    date_start = today - timedelta(days=args.days)
    date_end = today

    log(f"🔎 Buscando: topic='{args.topic}' · "
        f"janela={date_start} → {date_end}")

    tasks = {}
    with ThreadPoolExecutor(max_workers=3) as ex:
        if not args.no_arxiv:
            tasks[ex.submit(fetch_arxiv, args.topic, date_start,
                            date_end, args.max_per_source)] = "arXiv"
        if not args.no_pubmed:
            tasks[ex.submit(fetch_pubmed, args.topic, date_start,
                            date_end, args.max_per_source)] = "PubMed"
        if not args.no_medrxiv:
            tasks[ex.submit(fetch_medrxiv, args.topic, date_start,
                            date_end, args.max_per_source)] = "medRxiv"

        all_papers = []
        for fut in as_completed(tasks):
            src = tasks[fut]
            try:
                res = fut.result()
                log(f"✓ {src}: {len(res)} paper(s)")
                all_papers.extend(res)
            except Exception as e:
                log(f"⚠️ {src} falhou: {e}")

    deduped = dedupe(all_papers)
    deduped.sort(key=lambda p: p.get("date", ""), reverse=True)

    out = render_markdown(deduped, args.topic,
                          date_start.isoformat(), date_end.isoformat())
    print(out)


if __name__ == "__main__":
    main()
