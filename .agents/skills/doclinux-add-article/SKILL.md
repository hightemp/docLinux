---
name: doclinux-add-article
description: Add or import articles into the docLinux repository while maintaining article files, sources, tags, README navigation, and a topic-pure category hierarchy. Use when creating a new article, importing or translating an external article, or registering an existing article in the catalog. Do not use for edits that do not add or recategorize articles.
---

# Add an article to docLinux

Work only in a repository that contains `README.md`, `articles/`, and `tags/`. Read the current catalog before choosing a location; do not infer its structure from tags alone.

## Article file

1. Create the file under `articles/` with a descriptive English `snake_case.md` name. Allow only lowercase ASCII letters, digits, and underscores.
2. Start with one Russian H1 title.
3. Put exactly one source line immediately after the title:

   ```markdown
   Источник: [Название оригинала](https://example.com/original)
   ```

   Prefer the original publication or primary documentation. Verify a missing source instead of inventing one. Preserve the source URL when translating or reformatting an existing article.
4. Use clean Markdown. Translate prose when requested, but preserve commands, code, paths, options, protocol names, and URLs. Keep intentional HTML only inside examples or fenced code blocks.
5. End the article with a thematic break and one or more tag links:

   ```markdown
   ---

   [docker](/tags/docker.md)
   [сеть](/tags/networking.md)
   ```

Do not add the `НЕ ПЕРЕВЕДЕНО` tag to a translated article.

## README category hierarchy

Treat every non-link list item in the article catalog as a category and every `/articles/` link as an article leaf.

Maintain these invariants:

- An article must be below at least one category; never put an article at the catalog root.
- The immediate children of a category must be all subcategories or all articles. Never mix a subcategory and an article at the same level.
- A category must cover one cohesive topic. If its children can be separated into distinct subjects, create narrower subcategories and move the articles into them.
- Prefer another nesting level over a broad category that mixes technologies or concerns.
- A singleton subcategory is valid and required when it prevents an otherwise ungrouped article from sitting beside subcategories.
- Category items are plain text. Only article leaves are links.
- Add every article exactly once.

Valid:

```markdown
- Контейнеры
  - Сети Docker
    - [Сети bridge и overlay](/articles/docker_networks.md)
  - Хранилище Docker
    - [Именованные тома](/articles/docker_volumes.md)
```

Invalid because one parent mixes an article with a subcategory:

```markdown
- Контейнеры
  - [Именованные тома](/articles/docker_volumes.md)
  - Сети Docker
    - [Сети bridge и overlay](/articles/docker_networks.md)
```

Before adding a new category, check whether a precise existing category fits. Before reusing a category, inspect all its immediate children for topical purity. Reorganize the smallest necessary subtree when the new article exposes an existing mixed category.

## Tags and indexes

For each article tag:

1. Use an existing tag when its meaning matches. Name a new tag file with an English `snake_case.md` slug.
2. Create or update `tags/<slug>.md` with exactly one backlink in this form:

   ```markdown
   * [Название статьи](/articles/article_slug.md)
   ```

3. Ensure the README tag index contains the label and `/tags/<slug>.md` path once.
4. Avoid near-duplicate tags that differ only in case, number, spelling, or language.

If the article implements an item from `missing_topics.md`, remove that item from the backlog. Remove an empty parent category only when it has no remaining topics.

## Verification

Run the bundled validator from the repository root:

```bash
python3 .agents/skills/doclinux-add-article/scripts/validate_catalog.py --article articles/article_slug.md
```

Then run `git diff --check`. Also review the rendered nesting visually; the validator can detect mixed node types, but it cannot decide whether a category is semantically too broad.
