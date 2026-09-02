#!/usr/bin/env python3
"""Validate docLinux README hierarchy and a newly added article."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path


ARTICLE_LINK_RE = re.compile(
    r"^\[([^\]]+)\]\((/articles/[a-z0-9_]+\.md)\)$"
)
TAG_LINK_RE = re.compile(r"^\[([^\]]+)\]\((/tags/[a-z0-9_]+\.md)\)$")
SOURCE_RE = re.compile(r"^Источник: \[[^\]]+\]\(https?://[^\s)]+\)$")
SAFE_ARTICLE_RE = re.compile(r"^articles/[a-z0-9_]+\.md$")


@dataclass
class Node:
    kind: str
    text: str
    indent: int
    line: int
    target: str | None = None
    children: list["Node"] = field(default_factory=list)


def error(errors: list[str], message: str) -> None:
    errors.append(message)


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
        error(errors, f"Некорректный путь статьи: {article_arg}")
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
    h1 = [line[2:].strip() for line in lines if line.startswith("# ")]
    if len(h1) != 1:
        error(errors, f"{normalized}: ожидается ровно один заголовок H1")
        title = None
    else:
        title = h1[0]

    sources = [index for index, line in enumerate(lines, 1) if SOURCE_RE.fullmatch(line)]
    if len(sources) != 1:
        error(errors, f"{normalized}: ожидается ровно одна корректная строка «Источник»")
    elif sources[0] > 12:
        error(errors, f"{normalized}:{sources[0]}: источник должен быть в начале статьи")

    catalog_target = f"/{normalized}"
    catalog_matches = [node for node in catalog_articles if node.target == catalog_target]
    if len(catalog_matches) != 1:
        error(errors, f"README.md: статья {catalog_target} должна встречаться ровно один раз")
    elif title and catalog_matches[0].text != title.replace("`", ""):
        error(errors, f"README.md:{catalog_matches[0].line}: название ссылки не совпадает с H1")

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
    args = parser.parse_args()

    repo = args.repo.resolve()
    errors: list[str] = []
    for required in ("README.md", "articles", "tags"):
        if not (repo / required).exists():
            error(errors, f"Не найден обязательный путь: {required}")

    catalog_articles, tag_index = validate_catalog(repo, errors)
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
