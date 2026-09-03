# О красивых диффах в git

Источник: [On the Matter of Beautiful git Diffs](https://nathanleclaire.com/blog/2016/06/28/on-the-matter-of-beautiful-git-diffs/)

28 июня 2016

`git` в наши дни — один из моих самых любимых инструментов. Мне нравится в нём почти всё: DAG, то, как он облегчает мне жизнь, защищая изменения, и даже CLI-Workflow (стоит привыкнуть к его изначально странным повадкам — и всё, он прекрасен; много ли вы знаете инструментов, работающих так быстро?). Мне кажется, он вдохновляет инженеров на творческое мышление благодаря хорошо спроектированному ядру и железобетонной надёжности.

Но наверняка кто-то из вас говорит: «`git` — это круто, но что насчёт _диффов_, Нэйт? Они могли бы выглядеть куда лучше. Например, если бы подсвечивалась зелёным изменённая часть строки, а не строка целиком».

Эта статья — для вас!

## Скачайте `diff-highlight` из contrib-репозитория git

[diff-highlight](https://github.com/git/git/blob/master/contrib/diff-highlight/diff-highlight) — это потрясающе! Perl-скрипт, написанный ровно для решения упомянутой выше проблемы.

Скрипт — аккуратная небольшая Perl-программа, использующая довольно простой алгоритм для вычисления более точных диффов, если _ханки_ (последовательные секции диффа в коде) сбалансированы по количеству удалённых и добавленных строк в данной секции. Вот, например, главный цикл:

```perl
while (<>) {
    if (!$in_hunk) {
        print;
        $in_hunk = /^$COLOR*\@/;
    }
    elsif (/^$COLOR*-/) {
        push @removed, $_;
    }
    elsif (/^$COLOR*\+/) {
        push @added, $_;
    }
    else {
        show_hunk(\@removed, \@added);
        @removed = ();
        @added = ();

        print;
        $in_hunk = /^$COLOR*[\@ ]/;
    }

    # Most of the time there is enough output to keep things streaming,
    # but for something like "git log -Sfoo", you can get one early
    # commit and then many seconds of nothing. We want to show
    # that one commit as soon as possible.
    #
    # Since we can receive arbitrary input, there's no optimal
    # place to flush. Flushing on a blank line is a heuristic that
    # happens to match git-log output.
    if (!length) {
        local $| = 1;
    }
}
```

Взгляните на первый блок `else` выше: цикл проходит по всем строкам (`while (<>) {`) и печатает своего рода «потоковый» результат, когда условия в блоке `else` сходятся, после чего сбрасывает массивы `@removed` и `@added`.

Если скрипт вам подошёл, поменяйте его права на исполнение и передавайте ему вывод команд `git` по конвейеру, например `git diff` или `git log -p`.

## Настройте git config

Если вам нравятся такие диффы так же, как мне, и вы хотите видеть их всегда, настройте пейджер в `~/.gitconfig`:

```text
[core]
    pager = diff-highlight | less -RFX
```

(опции less: `-R` — сохранять цвета, `-F` — выходить сразу, если вывод влезает в один экран, `-X` — эту я честно скопировал по инерции).

Ещё есть настройки, помогающие уменьшить шум в диффах:

```text
[diff]
    algorithm = minimal
    compactionHeuristic = true
    renames = true
```

(`compactionHeuristic` появилась в git 2.9)

Вишенка на торте — настройки цвета диффов. Я использую «матричные» зелёный и красный, но при желании можно включить и другие схемы:

```text
[color "diff"]
        frag = magenta bold
        old = red bold
        new = green bold
        whitespace = red reverse

[color "diff-highlight"]
        oldNormal = red bold
        oldHighlight = "red bold 52"
        newNormal = "green bold"
        newHighlight = "green bold 22"
```

Сохраните это в `~/.gitconfig` — и матричные цвета будут у вас.

Я пробовал инструмент diff-so-fancy, но для моего вкуса это перебор. Я _люблю_ свои плюсы и минусы. К тому же он показался медленноватым для моего крайне нетерпеливого workflow `git log -p` / `git diff`.

## Финиш

Наслаждайтесь своими диффами и, как всегда, оставайтесь дерзкими, Интернет.

  * Nathan

**********

[git](/tags/git.md)