#!/usr/bin/env python3
"""Validate docLinux README hierarchy and a newly added article."""

from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import parse_qsl, unquote, urlencode, urlsplit


ARTICLE_LINK_RE = re.compile(
    r"^\[(.+)\]\((/articles/[a-z0-9_-]+\.md)\)$"
)
TAG_LINK_RE = re.compile(r"^\[([^\]]+)\]\((/tags/[a-z0-9_]+\.md)\)$")
SOURCE_RE = re.compile(
    r"^Источник: \[(?P<title>[^\]]+)\]\((?P<url>https?://[^\s)]+)\)$"
)
SAFE_ARTICLE_RE = re.compile(r"^articles/[a-z0-9]+(?:_[a-z0-9]+)*\.md$")
TRACKING_QUERY_KEYS = {"fbclid", "gclid", "mc_cid", "mc_eid", "yclid"}
CONTENT_SHINGLE_SIZE = 5
CONTENT_MINIMUM_TOKENS = 120
CONTENT_MINIMUM_SHARED_SHINGLES = 50
CONTENT_DUPLICATE_THRESHOLD = 0.25


@dataclass
class Node:
    kind: str
    text: str
    indent: int
    line: int
    target: str | None = None
    children: list["Node"] = field(default_factory=list)


@dataclass
class DuplicateMatches:
    titles: list[Path] = field(default_factory=list)
    sources: list[Path] = field(default_factory=list)
    contents: list[tuple[Path, float]] = field(default_factory=list)


def error(errors: list[str], message: str) -> None:
    errors.append(message)


def lines_outside_fences(lines: list[str]) -> list[tuple[int, str]]:
    result: list[tuple[int, str]] = []
    fence_character: str | None = None
    for index, line in enumerate(lines, 1):
        fence = re.match(r"^\s*(`{3,}|~{3,})", line)
        if fence:
            character = fence.group(1)[0]
            if fence_character is None:
                fence_character = character
            elif fence_character == character:
                fence_character = None
            continue
        if fence_character is None:
            result.append((index, line))
    return result


def normalize_title(title: str) -> str:
    normalized = unicodedata.normalize("NFKC", title).casefold().replace("`", "")
    return " ".join(
        "".join(character if character.isalnum() else " " for character in normalized).split()
    )


def normalize_source_url(url: str) -> str:
    parsed = urlsplit(url.strip())
    host = (parsed.hostname or "").casefold()
    if host.startswith("www."):
        host = host[4:]
    port = parsed.port
    if port and not (
        (parsed.scheme.casefold() == "http" and port == 80)
        or (parsed.scheme.casefold() == "https" and port == 443)
    ):
        host = f"{host}:{port}"

    path = re.sub(r"/{2,}", "/", unquote(parsed.path))
    if path == "/":
        path = ""
    else:
        path = path.rstrip("/")
    query = [
        (key, value)
        for key, value in parse_qsl(parsed.query, keep_blank_values=True)
        if not key.casefold().startswith("utm_") and key.casefold() not in TRACKING_QUERY_KEYS
    ]
    normalized_query = urlencode(sorted(query))
    return f"{host}{path}" + (f"?{normalized_query}" if normalized_query else "")


def extract_article_title(text: str) -> str | None:
    headings = [
        line[2:].strip()
        for _, line in lines_outside_fences(text.splitlines())
        if line.startswith("# ")
    ]
    return headings[0] if len(headings) == 1 else None


def extract_source_url(text: str) -> str | None:
    matches = [
        match
        for _, line in lines_outside_fences(text.splitlines())
        if (match := SOURCE_RE.fullmatch(line))
    ]
    return matches[0].group("url") if len(matches) == 1 else None


def article_body_tokens(text: str) -> tuple[str, ...]:
    body = text.rsplit("\n---\n", 1)[0]
    prose = []
    for _, line in lines_outside_fences(body.splitlines()):
        if line.startswith("# ") or line.startswith("Источник:"):
            continue
        prose.append(line)
    normalized = unicodedata.normalize("NFKC", "\n".join(prose)).casefold()
    normalized = re.sub(r"https?://\S+", " ", normalized)
    return tuple(re.findall(r"\w+", normalized, flags=re.UNICODE))


def content_overlap(left: tuple[str, ...], right: tuple[str, ...]) -> float:
    if left == right and len(left) >= CONTENT_SHINGLE_SIZE:
        return 1.0
    if min(len(left), len(right)) < CONTENT_MINIMUM_TOKENS:
        return 0.0

    size = CONTENT_SHINGLE_SIZE
    left_shingles = {left[index : index + size] for index in range(len(left) - size + 1)}
    right_shingles = {right[index : index + size] for index in range(len(right) - size + 1)}
    shared = len(left_shingles & right_shingles)
    if shared < CONTENT_MINIMUM_SHARED_SHINGLES:
        return 0.0
    return shared / min(len(left_shingles), len(right_shingles))


def find_duplicates(
    repo: Path,
    *,
    title: str | None = None,
    source_url: str | None = None,
    text: str | None = None,
    exclude: Path | None = None,
) -> DuplicateMatches:
    matches = DuplicateMatches()
    normalized_title = normalize_title(title) if title else None
    normalized_url = normalize_source_url(source_url) if source_url else None
    tokens = article_body_tokens(text) if text else None
    excluded = exclude.resolve() if exclude else None

    for candidate in sorted((repo / "articles").glob("*.md")):
        if excluded and candidate.resolve() == excluded:
            continue
        candidate_text = candidate.read_text(encoding="utf-8")
        candidate_title = extract_article_title(candidate_text)
        candidate_url = extract_source_url(candidate_text)

        if (
            normalized_title
            and candidate_title
            and normalize_title(candidate_title) == normalized_title
        ):
            matches.titles.append(candidate)
        if normalized_url and candidate_url and normalize_source_url(candidate_url) == normalized_url:
            matches.sources.append(candidate)
        if tokens is not None:
            overlap = content_overlap(tokens, article_body_tokens(candidate_text))
            if overlap >= CONTENT_DUPLICATE_THRESHOLD:
                matches.contents.append((candidate, overlap))

    return matches


def report_duplicates(repo: Path, matches: DuplicateMatches, errors: list[str]) -> None:
    if matches.titles:
        paths = ", ".join(str(path.relative_to(repo)) for path in matches.titles)
        error(errors, f"Дубликат нормализованного заголовка: {paths}")
    if matches.sources:
        paths = ", ".join(str(path.relative_to(repo)) for path in matches.sources)
        error(errors, f"Дубликат исходного URL: {paths}")
    for path, overlap in matches.contents:
        error(
            errors,
            f"Возможный дубликат содержимого ({overlap:.0%} совпадения): {path.relative_to(repo)}",
        )


def validate_candidate(
    repo: Path,
    path: str | None,
    title: str | None,
    source_url: str | None,
    errors: list[str],
) -> None:
    if path is not None:
        normalized_path = path.removeprefix("./")
        if not SAFE_ARTICLE_RE.fullmatch(normalized_path):
            error(
                errors,
                f"Некорректный путь кандидата: {path}; ожидается articles/<english_snake_case>.md",
            )
        elif (repo / normalized_path).exists():
            error(errors, f"Файл кандидата уже существует: {normalized_path}")
    title_to_check = title
    if title is not None and not title.strip():
        error(errors, "Заголовок кандидата не должен быть пустым")
        title_to_check = None
    source_url_to_check = source_url
    if source_url is not None:
        parsed = urlsplit(source_url)
        try:
            parsed.port
        except ValueError:
            valid_url = False
        else:
            valid_url = parsed.scheme.casefold() in {"http", "https"} and bool(parsed.netloc)
        if not valid_url:
            error(errors, f"Некорректный URL кандидата: {source_url}")
            source_url_to_check = None
    if title_to_check is None and source_url_to_check is None:
        return
    report_duplicates(
        repo,
        find_duplicates(repo, title=title_to_check, source_url=source_url_to_check),
        errors,
    )


def parse_catalog(readme: Path, errors: list[str]) -> tuple[Node, list[Node], str]:
    text = readme.read_text(encoding="utf-8")
    article_part, separator, tag_part = text.partition("\n---\n")
    if not separator:
        error(errors, "README.md: не найден разделитель перед индексом тегов")
        tag_part = ""

    root = Node("root", "ROOT", -1, 0)
    stack = [root]
    articles: list[Node] = []

    for line_number, line in enumerate(article_part.splitlines(), 1):
        match = re.match(r"^( *)(?:-) (.+)$", line)
        if not match:
            continue
        indent = len(match.group(1))
        body = match.group(2).strip()
        article_match = ARTICLE_LINK_RE.fullmatch(body)
        node = Node(
            kind="article" if article_match else "category",
            text=article_match.group(1) if article_match else body,
            indent=indent,
            line=line_number,
            target=article_match.group(2) if article_match else None,
        )

        while stack[-1].indent >= indent:
            stack.pop()
        parent = stack[-1]
        parent.children.append(node)

        if node.kind == "article":
            articles.append(node)
            if parent.kind == "root":
                error(errors, f"README.md:{line_number}: статья находится вне категории")
        else:
            if body.startswith("["):
                error(errors, f"README.md:{line_number}: категория не должна быть ссылкой")
            stack.append(node)

    def inspect(parent: Node) -> None:
        if parent.kind == "category" and not parent.children:
            error(errors, f"README.md:{parent.line}: пустая категория «{parent.text}»")
        child_kinds = {child.kind for child in parent.children}
        if parent.kind != "root" and len(child_kinds) > 1:
            error(
                errors,
                f"README.md:{parent.line}: категория «{parent.text}» смешивает статьи и подкатегории",
            )
        for child in parent.children:
            if child.kind == "category":
                inspect(child)

    inspect(root)
    return root, articles, tag_part


def validate_catalog(repo: Path, errors: list[str]) -> tuple[list[Node], str]:
    readme = repo / "README.md"
    if not readme.is_file():
        error(errors, "README.md не найден")
        return [], ""

    _, articles, tag_part = parse_catalog(readme, errors)
    seen: dict[str, int] = {}
    for node in articles:
        assert node.target is not None
        seen[node.target] = seen.get(node.target, 0) + 1
        if not (repo / node.target.lstrip("/")).is_file():
            error(errors, f"README.md:{node.line}: отсутствует {node.target}")
    for target, count in seen.items():
        if count > 1:
            error(errors, f"README.md: ссылка {target} встречается {count} раз")
    return articles, tag_part


def validate_article(
    repo: Path,
    article_arg: str,
    catalog_articles: list[Node],
    tag_index: str,
    errors: list[str],
) -> None:
    normalized = article_arg.removeprefix("./")
    if not SAFE_ARTICLE_RE.fullmatch(normalized):
        error(
            errors,
            f"Некорректный путь статьи: {article_arg}; ожидается articles/<english_snake_case>.md",
        )
        return

    article = repo / normalized
    if not article.is_file():
        error(errors, f"Статья не найдена: {normalized}")
        return
    text = article.read_text(encoding="utf-8")
    if not text.strip():
        error(errors, f"Статья пуста: {normalized}")
        return

    lines = text.splitlines()
    prose_lines = lines_outside_fences(lines)
    h1 = [line[2:].strip() for _, line in prose_lines if line.startswith("# ")]
    if len(h1) != 1:
        error(errors, f"{normalized}: ожидается ровно один заголовок H1")
        title = None
    else:
        title = h1[0]

    source_lines = [(index, line) for index, line in prose_lines if line.startswith("Источник:")]
    source_matches = [
        (index, match)
        for index, line in source_lines
        if (match := SOURCE_RE.fullmatch(line))
    ]
    if len(source_lines) != 1 or len(source_matches) != 1:
        error(errors, f"{normalized}: ожидается ровно одна корректная строка «Источник»")
        source_url = None
    else:
        source_index, source_match = source_matches[0]
        source_url = source_match.group("url")
        if source_index > 12:
            error(errors, f"{normalized}:{source_index}: источник должен быть в начале статьи")

    catalog_target = f"/{normalized}"
    catalog_matches = [node for node in catalog_articles if node.target == catalog_target]
    if len(catalog_matches) != 1:
        error(errors, f"README.md: статья {catalog_target} должна встречаться ровно один раз")
    elif title and catalog_matches[0].text != title.replace("`", ""):
        error(errors, f"README.md:{catalog_matches[0].line}: название ссылки не совпадает с H1")

    report_duplicates(
        repo,
        find_duplicates(
            repo,
            title=title,
            source_url=source_url,
            text=text,
            exclude=article,
        ),
        errors,
    )

    if "\n---\n" not in text:
        error(errors, f"{normalized}: перед тегами нужен разделитель ---")
        return
    footer = text.rsplit("\n---\n", 1)[1]
    tags = [TAG_LINK_RE.fullmatch(line.strip()) for line in footer.splitlines()]
    tags = [match for match in tags if match]
    if not tags:
        error(errors, f"{normalized}: не найдено ни одного тега в футере")
        return

    for match in tags:
        label, target = match.groups()
        tag_file = repo / target.lstrip("/")
        if not tag_file.is_file():
            error(errors, f"{normalized}: отсутствует файл тега {target}")
            continue
        if title:
            backlink = f"* [{title.replace('`', '')}]({catalog_target})"
            if backlink not in tag_file.read_text(encoding="utf-8").splitlines():
                error(errors, f"{tag_file.relative_to(repo)}: отсутствует ссылка «{backlink}»")
        if f"[{label}]({target})" not in tag_index:
            error(errors, f"README.md: тег [{label}]({target}) отсутствует в индексе")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--article", help="Путь вида articles/article_slug.md")
    parser.add_argument("--candidate-path", help="Планируемый путь новой статьи")
    parser.add_argument("--candidate-title", help="Планируемый русский H1")
    parser.add_argument("--candidate-source-url", help="URL оригинала до импорта")
    args = parser.parse_args()

    repo = args.repo.resolve()
    errors: list[str] = []
    for required in ("README.md", "articles", "tags"):
        if not (repo / required).exists():
            error(errors, f"Не найден обязательный путь: {required}")

    catalog_articles, tag_index = validate_catalog(repo, errors)
    candidate_values = (
        args.candidate_path,
        args.candidate_title,
        args.candidate_source_url,
    )
    if any(value is not None for value in candidate_values):
        if not all(value is not None for value in candidate_values):
            error(
                errors,
                "Для preflight нужны одновременно --candidate-path, --candidate-title "
                "и --candidate-source-url",
            )
        else:
            validate_candidate(repo, *candidate_values, errors)
    if args.article:
        validate_article(repo, args.article, catalog_articles, tag_index, errors)

    if errors:
        for item in errors:
            print(f"ERROR: {item}", file=sys.stderr)
        return 1
    print(f"OK: каталог содержит {len(catalog_articles)} статей")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
