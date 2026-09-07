#!/usr/bin/env python3

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import validate_catalog as validator


class ValidateCatalogTest(unittest.TestCase):
    def test_article_path_requires_strict_snake_case(self) -> None:
        self.assertIsNotNone(validator.SAFE_ARTICLE_RE.fullmatch("articles/linux_memory_2.md"))
        for path in (
            "articles/Linux_memory.md",
            "articles/linux-memory.md",
            "articles/_linux_memory.md",
            "articles/linux__memory.md",
            "articles/linux_memory_.md",
            "articles/linux memory.md",
        ):
            with self.subTest(path=path):
                self.assertIsNone(validator.SAFE_ARTICLE_RE.fullmatch(path))

    def test_source_url_normalization_ignores_transport_and_tracking(self) -> None:
        first = "https://www.Example.com/article/?b=2&utm_source=test&a=1#section"
        second = "http://example.com/article?a=1&b=2"
        self.assertEqual(
            validator.normalize_source_url(first),
            validator.normalize_source_url(second),
        )
        self.assertEqual(
            validator.normalize_source_url("https://example.com/"),
            validator.normalize_source_url("http://www.example.com"),
        )

    def test_short_exact_body_is_a_duplicate(self) -> None:
        tokens = ("короткий", "но", "полностью", "одинаковый", "текст")
        self.assertEqual(validator.content_overlap(tokens, tokens), 1.0)

    def test_duplicate_search_uses_title_source_and_body(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            articles = repo / "articles"
            articles.mkdir()
            words = " ".join(f"слово{index}" for index in range(200))
            existing = (
                "# Тестовая статья: Linux\n\n"
                "Источник: [Original](https://www.example.com/article/?utm_source=test)\n\n"
                f"{words}\n\n---\n\n[tag](/tags/tag.md)\n"
            )
            (articles / "existing.md").write_text(existing, encoding="utf-8")

            candidate = existing.replace("# Тестовая статья: Linux", "# Другое название")
            matches = validator.find_duplicates(
                repo,
                title="тестовая статья — linux",
                source_url="http://example.com/article",
                text=candidate,
            )

            self.assertEqual([path.name for path in matches.titles], ["existing.md"])
            self.assertEqual([path.name for path in matches.sources], ["existing.md"])
            self.assertEqual([path.name for path, _ in matches.contents], ["existing.md"])
            self.assertEqual(matches.contents[0][1], 1.0)

            errors: list[str] = []
            validator.validate_candidate(
                repo,
                "articles/bad-name.md",
                "тестовая статья — linux",
                "http://example.com/article",
                errors,
            )
            self.assertTrue(any("Некорректный путь кандидата" in item for item in errors))
            self.assertTrue(any("Дубликат нормализованного заголовка" in item for item in errors))
            self.assertTrue(any("Дубликат исходного URL" in item for item in errors))


if __name__ == "__main__":
    unittest.main()
