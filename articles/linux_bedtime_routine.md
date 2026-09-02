# Режим сна Linux

Источник: [Linux's Bedtime Routine](https://tookmund.com/2024/09/hibernation-preparation)

2024-09-08

  * [hibernate](https://tookmund.com/tags#hibernate)

Как Linux переходит из бодрствующего состояния в гибернацию? Как ему затем удаётся восстановить всё состояние? Эти вопросы заставили меня прочитать непомерно много кода на C в попытках понять, как именно проходится эта граница между аппаратурой и программным обеспечением.

Это исследование будет разбито на несколько частей; первая пройдёт путь от запуска гибернации до синхронизации всех файловых систем с диском.

Статья написана по версии Linux 6.9.9, исходники которой можно найти во многих местах, но удобнее всего навигировать по ним через Bootlin Elixir Cross-Referencer:

<https://elixir.bootlin.com/linux/v6.9.9/source>

Каждый фрагмент кода начинается со ссылки на этот ресурс, указывающей путь к файлу и номер строки начала фрагмента.

## Точка входа в исследование: `/sys/power/state` и `/sys/power/disk`

Эти два системных файла существуют, чтобы [облегчить отладку гибернации](https://www.kernel.org/doc/html/latest/power/basic-pm-debugging.html), и потому напрямую управляют используемым состоянием. Запись определённых значений в файл `state` управляет точным используемым режимом сна, а `disk` — конкретным режимом гибернации[1](#1).

Это крайне удобно как отправная точка для понимания работы этих систем: мы можем просто проследить, что происходит при записи в них.

### Функции Show и Store

Оба этих файла определены с помощью макроса `power_attr`:

[kernel/power/power.h:80](https://elixir.bootlin.com/linux/v6.9.9/source/kernel/power/power.h#L80)
```c
#define power_attr(_name) \
static struct kobj_attribute _name##_attr = {   \
    .attr   = {             \
        .name = __stringify(_name), \
        .mode = 0644,           \
    },                  \
    .show   = _name##_show,         \
    .store  = _name##_store,        \
}

```
`show` вызывается при чтении, `store` — при записи.

`state_show` для наших целей довольно скучен: он просто выводит все доступные состояния сна.

[kernel/power/main.c:657](https://elixir.bootlin.com/linux/v6.9.9/source/kernel/power/main.c#L657)
```c
/*
 * state - control system sleep states.
 *
 * show() returns available sleep state labels, which may be "mem", "standby",
 * "freeze" and "disk" (hibernation).
 * See Documentation/admin-guide/pm/sleep-states.rst for a description of
 * what they mean.
 *
 * store() accepts one of those strings, translates it into the proper
 * enumerated value, and initiates a suspend transition.
 */
static ssize_t state_show(struct kobject *kobj, struct kobj_attribute *attr,
			  char *buf)
{
	char *s = buf;
#ifdef CONFIG_SUSPEND
	suspend_state_t i;

	for (i = PM_SUSPEND_MIN; i < PM_SUSPEND_MAX; i++)
		if (pm_states[i])
			s += sprintf(s,"%s ", pm_states[i]);

#endif
	if (hibernation_available())
		s += sprintf(s, "disk ");
	if (s != buf)
		/* convert the last space to a newline */
		*(s-1) = '\n';
	return (s - buf);
}

```
А вот `state_store` даёт нам точку входа. Если в файл `state` записана строка «disk», вызывается `hibernate()`. Это наш вход в систему.

[kernel/power/main.c:715](https://elixir.bootlin.com/linux/v6.9.9/source/kernel/power/main.c#L715)
```c
static ssize_t state_store(struct kobject *kobj, struct kobj_attribute *attr,
			   const char *buf, size_t n)
{
	suspend_state_t state;
	int error;

	error = pm_autosleep_lock();
	if (error)
		return error;

	if (pm_autosleep_state() > PM_SUSPEND_ON) {
		error = -EBUSY;
		goto out;
	}

	state = decode_state(buf, n);
	if (state < PM_SUSPEND_MAX) {
		if (state == PM_SUSPEND_MEM)
			state = mem_sleep_current;

		error = pm_suspend(state);
	} else if (state == PM_SUSPEND_MAX) {
		error = hibernate();
	} else {
		error = -EINVAL;
	}

 out:
	pm_autosleep_unlock();
	return error ? error : n;
}

```
[kernel/power/main.c:688](https://elixir.bootlin.com/linux/v6.9.9/source/kernel/power/main.c#L688)
```c
static suspend_state_t decode_state(const char *buf, size_t n)
{
#ifdef CONFIG_SUSPEND
	suspend_state_t state;
#endif
	char *p;
	int len;

	p = memchr(buf, '\n', n);
	len = p ? p - buf : n;

	/* Check hibernation first. */
	if (len == 4 && str_has_prefix(buf, "disk"))
		return PM_SUSPEND_MAX;

#ifdef CONFIG_SUSPEND
	for (state = PM_SUSPEND_MIN; state < PM_SUSPEND_MAX; state++) {
		const char *label = pm_states[state];

		if (label && len == strlen(label) && !strncmp(buf, label, len))
			return state;
	}
#endif

	return PM_SUSPEND_ON;
}

```
Можно было бы догадаться об этом просто по именам функций? Конечно, но так мы точно знаем, что перед вызовом этой функции не происходит ничего другого.

### Autosleep

Наш первый крюк в сторону — система autosleep. В проверке состояния выше вы могли заметить, что ядро берёт `pm_autosleep_lock` перед проверкой текущего состояния.

autosleep — механизм [родом из Android](https://lwn.net/Articles/479841/), который переводит всю систему в suspend или гибернацию всякий раз, когда она ничего активно не делает.

В большинстве десктопных конфигураций он не включён, поскольку предназначен в первую очередь для мобильных систем и инвертирует стандартное поведение suspend и гибернации.

Система реализована как workqueue[2](#2), которая проверяет текущее число событий пробуждения, процессы и драйверы, которым нужно выполниться[3](#3), и если их нет, система переводится в autosleep-состояние — обычно suspend. Однако это может быть и гибернация, если так настроено через `/sys/power/autosleep` аналогично использованию `/sys/power/state` для ручного включения гибернации.

[kernel/power/main.c:841](https://elixir.bootlin.com/linux/v6.9.9/source/kernel/power/main.c#L841)
```c
static ssize_t autosleep_store(struct kobject *kobj,
			       struct kobj_attribute *attr,
			       const char *buf, size_t n)
{
	suspend_state_t state = decode_state(buf, n);
	int error;

	if (state == PM_SUSPEND_ON
	    && strcmp(buf, "off") && strcmp(buf, "off\n"))
		return -EINVAL;

	if (state == PM_SUSPEND_MEM)
		state = mem_sleep_current;

	error = pm_autosleep_set_state(state);
	return error ? error : n;
}

power_attr(autosleep);
#endif /* CONFIG_PM_AUTOSLEEP */

```
[kernel/power/autosleep.c:24](https://elixir.bootlin.com/linux/v6.9.9/source/kernel/power/autosleep.c#L24)
```c
static DEFINE_MUTEX(autosleep_lock);
static struct wakeup_source *autosleep_ws;

static void try_to_suspend(struct work_struct *work)
{
	unsigned int initial_count, final_count;

	if (!pm_get_wakeup_count(&initial_count, true))
		goto out;

	mutex_lock(&autosleep_lock);

	if (!pm_save_wakeup_count(initial_count) ||
		system_state != SYSTEM_RUNNING) {
		mutex_unlock(&autosleep_lock);
		goto out;
	}

	if (autosleep_state == PM_SUSPEND_ON) {
		mutex_unlock(&autosleep_lock);
		return;
	}
	if (autosleep_state >= PM_SUSPEND_MAX)
		hibernate();
	else
		pm_suspend(autosleep_state);

	mutex_unlock(&autosleep_lock);

	if (!pm_get_wakeup_count(&final_count, false))
		goto out;

	/*
	 * If the wakeup occurred for an unknown reason, wait to prevent the
	 * system from trying to suspend and waking up in a tight loop.
	 */
	if (final_count == initial_count)
		schedule_timeout_uninterruptible(HZ / 2);

 out:
	queue_up_suspend_work();
}

static DECLARE_WORK(suspend_work, try_to_suspend);

void queue_up_suspend_work(void)
{
	if (autosleep_state > PM_SUSPEND_ON)
		queue_work(autosleep_wq, &suspend_work);
}

```
## Шаги гибернации

### Конфигурация ядра для гибернации

Важно отметить, что большинство специфичных для гибернации функций ниже ничего не делают, если в вашем Kconfig[4](#4) не определён `CONFIG_HIBERNATION`. Например, сама функция `hibernate`, если `CONFIG_HIBERNATE` не задан, определена так:

[include/linux/suspend.h:407](https://elixir.bootlin.com/linux/v6.9.9/source/include/linux/suspend.h#L407)
```c
static inline int hibernate(void) { return -ENOSYS; }

```
### Проверка доступности гибернации

Начнём с подтверждения того, что мы вообще можем выполнить гибернацию, — через функцию `hibernation_available`.

[kernel/power/hibernate.c:742](https://elixir.bootlin.com/linux/v6.9.9/source/kernel/power/hibernate.c#L742)
```c
if (!hibernation_available()) {
	pm_pr_dbg("Hibernation not available.\n");
	return -EPERM;
}

```
[kernel/power/hibernate.c:92](https://elixir.bootlin.com/linux/v6.9.9/source/kernel/power/hibernate.c#L92)
```c
bool hibernation_available(void)
{
	return nohibernate == 0 &&
		!security_locked_down(LOCKDOWN_HIBERNATION) &&
		!secretmem_active() && !cxl_mem_active();
}

```
`nohibernate` управляется из командной строки ядра и устанавливается либо параметром `nohibernate`, либо `hibernate=no`.

`security_locked_down` — хук для Linux Security Modules, запрещающий гибернацию. Он используется, чтобы не допустить гибернации на незашифрованное устройство хранения, как описано в справочной странице [`kernel_lockdown(7)`](https://man7.org/linux/man-pages/man7/kernel_lockdown.7.html). Любопытно, что любой из уровней lockdown — integrity или confidentiality — блокирует гибернацию, потому что возможность гибернации позволяет извлечь из памяти практически что угодно и даже перезагрузиться в модифицированный образ ядра.

`secretmem_active` проверяет, активно ли какое-либо использование `memfd_secret`, и если да — запрещает гибернацию. `memfd_secret` возвращает файловый дескриптор, который можно отобразить в процесс, но который целенаправленно не отображён в адресное пространство ядра. Гибернация с памятью, к которой даже ядро не должно иметь доступа, раскрыла бы эту памяти любому, кто может получить доступ к образу гибернации. Судя по всему, эта функция секретной памяти была [спорной](https://lwn.net/Articles/865256/), хотя и не столь спорной, как опасения по производительности из-за фрагментации при разотображении памяти ядра ([которая в итоге не стала реальной проблемой](https://lwn.net/Articles/865256/)).

`cxl_mem_active` просто проверяет, активна ли какая-либо память CXL. Полное объяснение есть в [коммите, вводящем эту проверку](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=9ea4dcf49878bb9546b8fa9319dcbdc9b7ee20f8), но есть и краткое пояснение в `cxl_mem_probe`, который устанавливает соответствующий флаг при инициализации устройства памяти CXL.

[drivers/cxl/mem.c:186](https://elixir.bootlin.com/linux/v6.9.9/source/drivers/cxl/mem.c#L186)
```c
* The kernel may be operating out of CXL memory on this device,
* there is no spec defined way to determine whether this device
* preserves contents over suspend, and there is no simple way
* to arrange for the suspend image to avoid CXL memory which
* would setup a circular dependency between PCI resume and save
* state restoration.

```
### Проверка сжатия

Следующая проверка — включена ли поддержка сжатия, и если да, доступен ли запрошенный алгоритм.

[kernel/power/hibernate.c:747](https://elixir.bootlin.com/linux/v6.9.9/source/kernel/power/hibernate.c#L747)
```c
/*
 * Query for the compression algorithm support if compression is enabled.
 */
if (!nocompress) {
	strscpy(hib_comp_algo, hibernate_compressor, sizeof(hib_comp_algo));
	if (crypto_has_comp(hib_comp_algo, 0, 0) != 1) {
		pr_err("%s compression is not available\n", hib_comp_algo);
		return -EOPNOTSUPP;
	}
}

```
Флаг `nocompress` устанавливается через параметр командной строки `hibernate`, значением `hibernate=nocompress`.

Если сжатие включено, `hibernate_compressor` копируется в `hib_comp_algo`. Это синхронизирует текущий запрошенный параметр сжатия (`hibernate_compressor`) с текущим параметром сжатия (`hib_comp_algo`).

Оба значения — символьные массивы размером `CRYPTO_MAX_ALG_NAME` (128 в этом ядре).

[kernel/power/hibernate.c:50](https://elixir.bootlin.com/linux/v6.9.9/source/kernel/power/hibernate.c#L50)
```c
static char hibernate_compressor[CRYPTO_MAX_ALG_NAME] = CONFIG_HIBERNATION_DEF_COMP;

/*
 * Compression/decompression algorithm to be used while saving/loading
 * image to/from disk. This would later be used in 'kernel/power/swap.c'
 * to allocate comp streams.
 */
char hib_comp_algo[CRYPTO_MAX_ALG_NAME];

```
`hibernate_compressor` по умолчанию равен `lzo`, если этот алгоритм включён, иначе `lz4`, если включён он[5](#5). Его можно переопределить параметром `hibernate.compressor` значением `lzo` или `lz4`.

[kernel/power/Kconfig:95](https://elixir.bootlin.com/linux/v6.9.9/source/kernel/power/Kconfig#L95)
```c
choice
	prompt "Default compressor"
	default HIBERNATION_COMP_LZO
	depends on HIBERNATION

config HIBERNATION_COMP_LZO
	bool "lzo"
	depends on CRYPTO_LZO

config HIBERNATION_COMP_LZ4
	bool "lz4"
	depends on CRYPTO_LZ4

endchoice

config HIBERNATION_DEF_COMP
	string
	default "lzo" if HIBERNATION_COMP_LZO
	default "lz4" if HIBERNATION_COMP_LZ4
	help
	  Default compressor to be used for hibernation.

```
[kernel/power/hibernate.c:1425](https://elixir.bootlin.com/linux/v6.9.9/source/kernel/power/hibernate.c#L1425)
```c
static const char * const comp_alg_enabled[] = {
#if IS_ENABLED(CONFIG_CRYPTO_LZO)
	COMPRESSION_ALGO_LZO,
#endif
#if IS_ENABLED(CONFIG_CRYPTO_LZ4)
	COMPRESSION_ALGO_LZ4,
#endif
};

static int hibernate_compressor_param_set(const char *compressor,
		const struct kernel_param *kp)
{
	unsigned int sleep_flags;
	int index, ret;

	sleep_flags = lock_system_sleep();

	index = sysfs_match_string(comp_alg_enabled, compressor);
	if (index >= 0) {
		ret = param_set_copystring(comp_alg_enabled[index], kp);
		if (!ret)
			strscpy(hib_comp_algo, comp_alg_enabled[index],
				sizeof(hib_comp_algo));
	} else {
		ret = index;
	}

	unlock_system_sleep(sleep_flags);

	if (ret)
		pr_debug("Cannot set specified compressor %s\n",
			 compressor);

	return ret;
}
static const struct kernel_param_ops hibernate_compressor_param_ops = {
	.set    = hibernate_compressor_param_set,
	.get    = param_get_string,
};

static struct kparam_string hibernate_compressor_param_string = {
	.maxlen = sizeof(hibernate_compressor),
	.string = hibernate_compressor,
};

```
Затем мы проверяем через `crypto_has_comp`, поддерживается ли запрошенный алгоритм. Если нет — выходим из всей операции с `EOPNOTSUPP`.

В рамках `crypto_has_comp` выполняется любая нужная инициализация алгоритма: загрузка модулей ядра и запуск кода инициализации по мере необходимости[6](#6).

### Берём блокировки

Следующий шаг — захват блокировок сна и гибернации через `lock_system_sleep` и `hibernate_acquire`.

[kernel/power/hibernate.c:758](https://elixir.bootlin.com/linux/v6.9.9/source/kernel/power/hibernate.c#L758)
```c
sleep_flags = lock_system_sleep();
/* The snapshot device should not be opened while we're running */
if (!hibernate_acquire()) {
	error = -EBUSY;
	goto Unlock;
}

```
Сначала `lock_system_sleep` помечает текущий поток как не подлежащий заморозке (not freezable) — это станет важно позже[7](#7). Затем он захватывает `system_transistion_mutex`, который блокирует создание снапшотов и изменение способа их создания, возобновление из образа гибернации, вход в любое состояние suspend и перезагрузку.

#### Маска GFP

Ядро также выдаёт предупреждение, если маска `gfp` изменяется через `pm_restore_gfp_mask` или `pm_restrict_gfp_mask` без удержания `system_transistion_mutex`.

Флаги GFP говорят ядру, как ему разрешено обрабатывать запрос памяти.

[include/linux/gfp_types.h:12](https://elixir.bootlin.com/linux/v6.9.9/source/include/linux/gfp_types.h#L12)
```c
 * GFP flags are commonly used throughout Linux to indicate how memory
 * should be allocated.  The GFP acronym stands for get_free_pages(),
 * the underlying memory allocation function.  Not every GFP flag is
 * supported by every function which may allocate memory.

```
В случае гибернации нас интересуют флаги `IO` и `FS` — это операторы reclaimed-памяти, то есть способы, которыми системе разрешено пытаться освободить память, чтобы удовлетворить конкретный запрос.

[include/linux/gfp_types.h:176](https://elixir.bootlin.com/linux/v6.9.9/source/include/linux/gfp_types.h#L176)
```c
 * Reclaim modifiers
 * -----------------
 * Please note that all the following flags are only applicable to sleepable
 * allocations (e.g. %GFP_NOWAIT and %GFP_ATOMIC will ignore them).
 *
 * %__GFP_IO can start physical IO.
 *
 * %__GFP_FS can call down to the low-level FS. Clearing the flag avoids the
 * allocator recursing into the filesystem which might already be holding
 * locks.

```
`gfp_allowed_mask` задаёт, какие флаги разрешено устанавливать в данный момент.

Как поясняет комментарий ниже, запрет этих флагов позволяет избежать ситуаций, когда ядру нужно выполнить ввод-вывод для выделения памяти (например, чтение/запись swap[8](#8)), но нужные устройства в данный момент недоступны.

[kernel/power/main.c:24](https://elixir.bootlin.com/linux/v6.9.9/source/kernel/power/main.c#L24)
```c
/*
 * The following functions are used by the suspend/hibernate code to temporarily
 * change gfp_allowed_mask in order to avoid using I/O during memory allocations
 * while devices are suspended.  To avoid races with the suspend/hibernate code,
 * they should always be called with system_transition_mutex held
 * (gfp_allowed_mask also should only be modified with system_transition_mutex
 * held, unless the suspend/hibernate code is guaranteed not to run in parallel
 * with that modification).
 */
static gfp_t saved_gfp_mask;

void pm_restore_gfp_mask(void)
{
	WARN_ON(!mutex_is_locked(&system_transition_mutex));
	if (saved_gfp_mask) {
		gfp_allowed_mask = saved_gfp_mask;
		saved_gfp_mask = 0;
	}
}

void pm_restrict_gfp_mask(void)
{
	WARN_ON(!mutex_is_locked(&system_transition_mutex));
	WARN_ON(saved_gfp_mask);
	saved_gfp_mask = gfp_allowed_mask;
	gfp_allowed_mask &= ~(__GFP_IO | __GFP_FS);
}

```
#### Флаги сна

Захватив `system_transition_mutex`, ядро возвращает и сохраняет предыдущее состояние флагов потока в `sleep_flags`. Позже это используется, чтобы убрать `PF_NOFREEZE`, если он ранее не был установлен у текущего потока.

[kernel/power/main.c:52](https://elixir.bootlin.com/linux/v6.9.9/source/kernel/power/main.c#L52)
```c
unsigned int lock_system_sleep(void)
{
	unsigned int flags = current->flags;
	current->flags |= PF_NOFREEZE;
	mutex_lock(&system_transition_mutex);
	return flags;
}
EXPORT_SYMBOL_GPL(lock_system_sleep);

```
[include/linux/sched.h:1633](https://elixir.bootlin.com/linux/v6.9.9/source/include/linux/sched.h#L1633)
```c
#define PF_NOFREEZE		0x00008000	/* This thread should not be frozen */

```
Затем мы захватываем специфичный для гибернации семафор, чтобы никто не мог открыть снапшот или возобновиться из него, пока мы выполняем гибернацию. Кроме того, эта блокировка используется для защиты `hibernate_quiet_exec`, который применяется драйвером `nvdimm` для активации его прошивки при замороженных процессах и устройствах, гарантируя, что в этот момент не работает ничего другого[9](#9).

[kernel/power/hibernate.c:82](https://elixir.bootlin.com/linux/v6.9.9/source/kernel/power/hibernate.c#L82)
```c
bool hibernate_acquire(void)
{
	return atomic_add_unless(&hibernate_atomic, -1, 0);
}

```
### Подготовка консоли

Далее ядро вызывает `pm_prepare_console`. Эта функция что-то делает, только если установлен `CONFIG_VT_CONSOLE_SLEEP`.

Она готовит виртуальный терминал к состоянию suspend, при необходимости переключаясь на консоль, используемую только для состояния сна.

[kernel/power/console.c:130](https://elixir.bootlin.com/linux/v6.9.9/source/kernel/power/console.c#L130)
```c
void pm_prepare_console(void)
{
	if (!pm_vt_switch())
		return;

	orig_fgconsole = vt_move_to_console(SUSPEND_CONSOLE, 1);
	if (orig_fgconsole < 0)
		return;

	orig_kmsg = vt_kmsg_redirect(SUSPEND_CONSOLE);
	return;
}

```
Прежде всего проверяется, действительно ли нам нужно переключать VT:

[kernel/power/console.c:94](https://elixir.bootlin.com/linux/v6.9.9/source/kernel/power/console.c#L94)
```c
/*
 * There are three cases when a VT switch on suspend/resume are required:
 *   1) no driver has indicated a requirement one way or another, so preserve
 *      the old behavior
 *   2) console suspend is disabled, we want to see debug messages across
 *      suspend/resume
 *   3) any registered driver indicates it needs a VT switch
 *
 * If none of these conditions is present, meaning we have at least one driver
 * that doesn't need the switch, and none that do, we can avoid it to make
 * resume look a little prettier (and suspend too, but that's usually hidden,
 * e.g. when closing the lid on a laptop).
 */
static bool pm_vt_switch(void)
{
	struct pm_vt_switch *entry;
	bool ret = true;

	mutex_lock(&vt_switch_mutex);
	if (list_empty(&pm_vt_switch_list))
		goto out;

	if (!console_suspend_enabled)
		goto out;

	list_for_each_entry(entry, &pm_vt_switch_list, head) {
		if (entry->required)
			goto out;
	}

	ret = false;
out:
	mutex_unlock(&vt_switch_mutex);
	return ret;
}

```
Условия, при которых выполняется переключение, объяснены в комментарии над функцией, но мы также пройдём по шагам здесь.

Во-первых, мы берём `vt_switch_mutex`, чтобы при просмотре списка его никто не изменил.

Затем мы просматриваем `pm_vt_switch_list`. Этот список указывает драйверы, которым требуется переключение во время suspend. Они регистрируют это требование (или его отсутствие) через `pm_vt_switch_required`.

[kernel/power/console.c:31](https://elixir.bootlin.com/linux/v6.9.9/source/kernel/power/console.c#L31)
```c
/**
 * pm_vt_switch_required - indicate VT switch at suspend requirements
 * @dev: device
 * @required: if true, caller needs VT switch at suspend/resume time
 *
 * The different console drivers may or may not require VT switches across
 * suspend/resume, depending on how they handle restoring video state and
 * what may be running.
 *
 * Drivers can indicate support for switchless suspend/resume, which can
 * save time and flicker, by using this routine and passing 'false' as
 * the argument.  If any loaded driver needs VT switching, or the
 * no_console_suspend argument has been passed on the command line, VT
 * switches will occur.
 */
void pm_vt_switch_required(struct device *dev, bool required)

```
Далее мы проверяем `console_suspend_enabled`. Он устанавливается в false параметром ядра `no_console_suspend`, но по умолчанию равен true.

Наконец, если в `pm_vt_switch_list` есть записи, мы проверяем, требуется ли какой-либо из них VT-переключение.

Только если ни одно из этих условий не выполняется, мы возвращаем false.

Если VT-переключение всё же требуется, мы сначала переносим текущий активный виртуальный терминал/консоль[10](#10) (`vt_move_to_console`), а затем текущее место вывода сообщений ядра (`vt_kmsg_redirect`) в `SUSPEND_CONSOLE`. `SUSPEND_CONSOLE` — последняя запись в списке возможных консолей, и, судя по всему, это просто «чёрная дыра» для сброса сообщений.

[kernel/power/console.c:16](https://elixir.bootlin.com/linux/v6.9.9/source/kernel/power/console.c#L16)
```c
#define SUSPEND_CONSOLE	(MAX_NR_CONSOLES-1)

```
Любопытно, что это разные функции, потому что можно использовать `TIOCL_SETKMSGREDIRECT` (`ioctl`[11](#11)), чтобы отправлять сообщения ядра на конкретный виртуальный терминал, но по умолчанию это та же консоль, что и активная в данный момент.

Расположения ранее активной консоли и прежнего места сообщений ядра сохраняются в `orig_fgconsole` и `orig_kmsg`, чтобы восстановить состояние консоли и сообщений ядра после пробуждения машины. Любопытно, что `orig_fgconsole` также сохраняет ошибки, поэтому перед работой с сообщениями ядра при suspend и resume нужно проверять, что он не меньше нуля.

[drivers/tty/vt/vt_ioctl.c:1268](https://elixir.bootlin.com/linux/v6.9.9/source/drivers/tty/vt/vt_ioctl.c#L1268)
```c
/* Perform a kernel triggered VT switch for suspend/resume */

static int disable_vt_switch;

int vt_move_to_console(unsigned int vt, int alloc)
{
	int prev;

	console_lock();
	/* Graphics mode - up to X */
	if (disable_vt_switch) {
		console_unlock();
		return 0;
	}
	prev = fg_console;

	if (alloc && vc_allocate(vt)) {
		/* we can't have a free VC for now. Too bad,
		 * we don't want to mess the screen for now. */
		console_unlock();
		return -ENOSPC;
	}

	if (set_console(vt)) {
		/*
		 * We're unable to switch to the SUSPEND_CONSOLE.
		 * Let the calling function know so it can decide
		 * what to do.
		 */
		console_unlock();
		return -EIO;
	}
	console_unlock();
	if (vt_waitactive(vt + 1)) {
		pr_debug("Suspend: Can't switch VCs.");
		return -EINTR;
	}
	return prev;
}

```
В отличие от большинства других функций блокировки, которые мы видели, `console_lock` должен сперва убедиться, что нигде нет паники и нет необходимости вываливать дамп в консоль, и только затем брать семафор консоли и устанавливать пару флагов.

#### Паники

Паники отслеживаются через атомарное целое, в которое записывается id процессора, находящегося в состоянии паники.

[kernel/printk/printk.c:2649](https://elixir.bootlin.com/linux/v6.9.9/source/kernel/printk/printk.c#L2649)
```c
/**
 * console_lock - block the console subsystem from printing
 *
 * Acquires a lock which guarantees that no consoles will
 * be in or enter their write() callback.
 *
 * Can sleep, returns nothing.
 */
void console_lock(void)
{
	might_sleep();

	/* On panic, the console_lock must be left to the panic cpu. */
	while (other_cpu_in_panic())
		msleep(1000);

	down_console_sem();
	console_locked = 1;
	console_may_schedule = 1;
}
EXPORT_SYMBOL(console_lock);

```
[kernel/printk/printk.c:362](https://elixir.bootlin.com/linux/v6.9.9/source/kernel/printk/printk.c#L362)
```c
/*
 * Return true if a panic is in progress on a remote CPU.
 *
 * On true, the local CPU should immediately release any printing resources
 * that may be needed by the panic CPU.
 */
bool other_cpu_in_panic(void)
{
	return (panic_in_progress() && !this_cpu_in_panic());
}

```
[kernel/printk/printk.c:345](https://elixir.bootlin.com/linux/v6.9.9/source/kernel/printk/printk.c#L345)
```c
static bool panic_in_progress(void)
{
	return unlikely(atomic_read(&panic_cpu) != PANIC_CPU_INVALID);
}

```
[kernel/printk/printk.c:350](https://elixir.bootlin.com/linux/v6.9.9/source/kernel/printk/printk.c#L350)
```c
/* Return true if a panic is in progress on the current CPU. */
bool this_cpu_in_panic(void)
{
	/*
	 * We can use raw_smp_processor_id() here because it is impossible for
	 * the task to be migrated to the panic_cpu, or away from it. If
	 * panic_cpu has already been set, and we're not currently executing on
	 * that CPU, then we never will be.
	 */
	return unlikely(atomic_read(&panic_cpu) == raw_smp_processor_id());
}

```
`console_locked` — отладочное значение, показывающее, что блокировка должна удерживаться, и наше первое указание на то, что вся система виртуальных терминалов сложнее, чем может показаться на первый взгляд.

[kernel/printk/printk.c:373](https://elixir.bootlin.com/linux/v6.9.9/source/kernel/printk/printk.c#L373)
```c
/*
 * This is used for debugging the mess that is the VT code by
 * keeping track if we have the console semaphore held. It's
 * definitely not the perfect debug tool (we don't know if _WE_
 * hold it and are racing, but it helps tracking those weird code
 * paths in the console code where we end up in places I want
 * locked without the console semaphore held).
 */
static int console_locked;

```
`console_may_schedule` показывает, разрешено ли нам спать и планировать другую работу, пока мы удерживаем эту блокировку. Как мы увидим позже, подсистема виртуальных терминалов не реентерабельна, поэтому здесь полно всевозможных ухищрений, чтобы мы не покидали важные участки кода, которые нельзя безопасно возобновить.

#### Отключение VT-переключения

Как поясняет комментарий ниже, когда графический вывод в любом случае обрабатывает другая программа, всё это делать не нужно, поэтому ядро предоставляет выключатель для всей этой механики. Любопытно, что им, судя по всему, пользуются лишь три драйвера, так что требуемая аппаратная поддержка вряд ли широко распространена.
```c
drivers/gpu/drm/omapdrm/dss
drivers/video/fbdev/geode
drivers/video/fbdev/omap2

```
[drivers/tty/vt/vt_ioctl.c:1308](https://elixir.bootlin.com/linux/v6.9.9/source/drivers/tty/vt/vt_ioctl.c#L1308)
```c
/*
 * Normally during a suspend, we allocate a new console and switch to it.
 * When we resume, we switch back to the original console.  This switch
 * can be slow, so on systems where the framebuffer can handle restoration
 * of video registers anyways, there's little point in doing the console
 * switch.  This function allows you to disable it by passing it '0'.
 */
void pm_set_vt_switch(int do_switch)
{
	console_lock();
	disable_vt_switch = !do_switch;
	console_unlock();
}
EXPORT_SYMBOL(pm_set_vt_switch);

```
Остальная часть функции `vt_switch_console` довольно обычна: она просто выделяет при необходимости место для создания запрошенного виртуального терминала, а затем устанавливает текущий виртуальный терминал через `set_console`.

#### Виртуальный терминал: set_console

С `set_console` мы (как будто мы ещё не были в этом) начинаем погружаться в безумие подсистемы виртуальных терминалов. Как упоминалось ранее, изменения её состояния нужно делать очень осторожно, так как одновременные события могли бы устроить полный хаос.

Всё это к тому, что вызов `set_console` на самом деле не выполняет никакой работы по изменению состояния текущей консоли. Вместо этого он фиксирует желаемые изменения, а затем планирует эту работу.

[drivers/tty/vt/vt.c:3153](https://elixir.bootlin.com/linux/v6.9.9/source/drivers/tty/vt/vt.c#L3153)
```c
int set_console(int nr)
{
	struct vc_data *vc = vc_cons[fg_console].d;

	if (!vc_cons_allocated(nr) || vt_dont_switch ||
		(vc->vt_mode.mode == VT_AUTO && vc->vc_mode == KD_GRAPHICS)) {

		/*
		 * Console switch will fail in console_callback() or
		 * change_console() so there is no point scheduling
		 * the callback
		 *
		 * Existing set_console() users don't check the return
		 * value so this shouldn't break anything
		 */
		return -EINVAL;
	}

	want_console = nr;
	schedule_console_callback();

	return 0;
}

```
Проверка `vc->vc_mode == KD_GRAPHICS` — это то место, где большинство графических десктопов выходят из этого изменения, поскольку они находятся в графическом режиме и не нуждаются в переключении на suspend-консоль.

`vt_dont_switch` — флаг, используемый `ioctl`[11](#11) `VT_LOCKSWITCH` и `VT_UNLOCKSWITCH`, чтобы система не переключала виртуальные терминалы, когда пользователь явно их заблокировал.

`VT_AUTO` — флаг, указывающий, что включено автоматическое переключение виртуальных терминалов[12](#12), и потому намеренное переключение на suspend-терминал не требуется.

Однако если вы действительно работаете в виртуальном терминале, то мы сообщаем системе о желании переключиться на запрошенный виртуальный терминал через переменную `want_console` и планируем callback через `schedule_console_callback`.

[drivers/tty/vt/vt.c:315](https://elixir.bootlin.com/linux/v6.9.9/source/drivers/tty/vt/vt.c#L315)
```c
void schedule_console_callback(void)
{
	schedule_work(&console_work);
}

```
`console_work` — это workqueue[2](#2), которая выполнит поставленную задачу асинхронно.

#### Console Callback

[drivers/tty/vt/vt.c:3109](https://elixir.bootlin.com/linux/v6.9.9/source/drivers/tty/vt/vt.c#L3109)
```c
/*
 * This is the console switching callback.
 *
 * Doing console switching in a process context allows
 * us to do the switches asynchronously (needed when we want
 * to switch due to a keyboard interrupt).  Synchronization
 * with other console code and prevention of re-entrancy is
 * ensured with console_lock.
 */
static void console_callback(struct work_struct *ignored)
{
	console_lock();

	if (want_console >= 0) {
		if (want_console != fg_console &&
		    vc_cons_allocated(want_console)) {
			hide_cursor(vc_cons[fg_console].d);
			change_console(vc_cons[want_console].d);
			/* we only changed when the console had already
			   been allocated - a new console is not created
			   in an interrupt routine */
		}
		want_console = -1;
	}
...

```
`console_callback` сначала смотрит, требуется ли смена консоли через `want_console`, и затем переключается на неё, если это не текущая консоль и она уже выделена. Предварительно мы убираем состояние курсора с помощью `hide_cursor`.

[drivers/tty/vt/vt.c:841](https://elixir.bootlin.com/linux/v6.9.9/source/drivers/tty/vt/vt.c#L841)
```c
static void hide_cursor(struct vc_data *vc)
{
	if (vc_is_sel(vc))
		clear_selection();

	vc->vc_sw->con_cursor(vc, false);
	hide_softcursor(vc);
}

```
Полное погружение в драйвер `tty` — задача для другого раза, но это должно дать общее представление о том, как эта система взаимодействует с гибернацией.

### Уведомление цепочки вызовов управления питанием

[kernel/power/hibernate.c:767](https://elixir.bootlin.com/linux/v6.9.9/source/kernel/power/hibernate.c#L767)
```c
pm_notifier_call_chain_robust(PM_HIBERNATION_PREPARE, PM_POST_HIBERNATION)

```
Это вызовет цепочку callback'ов управления питанием, передавая сначала `PM_HIBERNATION_PREPARE`, а затем `PM_POST_HIBERNATION` при запуске или при ошибке с другим callback'ом.

[kernel/power/main.c:98](https://elixir.bootlin.com/linux/v6.9.9/source/kernel/power/main.c#L98)
```c
int pm_notifier_call_chain_robust(unsigned long val_up, unsigned long val_down)
{
	int ret;

	ret = blocking_notifier_call_chain_robust(&pm_chain_head, val_up, val_down, NULL);

	return notifier_to_errno(ret);
}

```
Notifier управления питанием — блокирующая цепочка notifier'ов, то есть обладает следующими свойствами.

[include/linux/notifier.h:23](https://elixir.bootlin.com/linux/v6.9.9/source/include/linux/notifier.h#L23)
```c
 *	Blocking notifier chains: Chain callbacks run in process context.
 *		Callouts are allowed to block.

```
Цепочка callback'ов — связный список, каждая запись которого содержит приоритет и вызываемую функцию. Функция формально принимает значение данных, но для цепочки управления питанием оно всегда `NULL`.

[include/linux/notifier.h:49](https://elixir.bootlin.com/linux/v6.9.9/source/include/linux/notifier.h#L49)
```c
struct notifier_block;

typedef	int (*notifier_fn_t)(struct notifier_block *nb,
			unsigned long action, void *data);

struct notifier_block {
	notifier_fn_t notifier_call;
	struct notifier_block __rcu *next;
	int priority;
};

```
Голова связного списка защищена семафором чтения-записи.

[include/linux/notifier.h:65](https://elixir.bootlin.com/linux/v6.9.9/source/include/linux/notifier.h#L65)
```c
struct blocking_notifier_head {
	struct rw_semaphore rwsem;
	struct notifier_block __rcu *head;
};

```
Поскольку список приоритизирован, добавление в него требует прохода по нему, пока не найден элемент с более низким[13](#13) приоритетом, перед которым и вставляется текущий элемент.

[kernel/notifier.c:252](https://elixir.bootlin.com/linux/v6.9.9/source/kernel/notifier.c#L252)
```c
/*
 *	Blocking notifier chain routines.  All access to the chain is
 *	synchronized by an rwsem.
 */

static int __blocking_notifier_chain_register(struct blocking_notifier_head *nh,
					      struct notifier_block *n,
					      bool unique_priority)
{
	int ret;

	/*
	 * This code gets used during boot-up, when task switching is
	 * not yet working and interrupts must remain disabled.  At
	 * such times we must not call down_write().
	 */
	if (unlikely(system_state == SYSTEM_BOOTING))
		return notifier_chain_register(&nh->head, n, unique_priority);

	down_write(&nh->rwsem);
	ret = notifier_chain_register(&nh->head, n, unique_priority);
	up_write(&nh->rwsem);
	return ret;
}

```
[kernel/notifier.c:20](https://elixir.bootlin.com/linux/v6.9.9/source/kernel/notifier.c#L20)
```c
/*
 *	Notifier chain core routines.  The exported routines below
 *	are layered on top of these, with appropriate locking added.
 */

static int notifier_chain_register(struct notifier_block **nl,
				   struct notifier_block *n,
				   bool unique_priority)
{
	while ((*nl) != NULL) {
		if (unlikely((*nl) == n)) {
			WARN(1, "notifier callback %ps already registered",
			     n->notifier_call);
			return -EEXIST;
		}
		if (n->priority > (*nl)->priority)
			break;
		if (n->priority == (*nl)->priority && unique_priority)
			return -EBUSY;
		nl = &((*nl)->next);
	}
	n->next = *nl;
	rcu_assign_pointer(*nl, n);
	trace_notifier_register((void *)n->notifier_call);
	return 0;
}

```
Каждый callback может вернуть один из набора вариантов.

[include/linux/notifier.h:18](https://elixir.bootlin.com/linux/v6.9.9/source/include/linux/notifier.h#L18)
```c
#define NOTIFY_DONE		0x0000		/* Don't care */
#define NOTIFY_OK		0x0001		/* Suits me */
#define NOTIFY_STOP_MASK	0x8000		/* Don't call further */
#define NOTIFY_BAD		(NOTIFY_STOP_MASK|0x0002)
						/* Bad/Veto action */

```
При уведомлении цепочки, если функция возвращает `STOP` или `BAD`, предыдущие части цепочки вызываются снова с `PM_POST_HIBERNATION`[14](#14), и возвращается ошибка.

[kernel/notifier.c:107](https://elixir.bootlin.com/linux/v6.9.9/source/kernel/notifier.c#L107)
```c
/**
 * notifier_call_chain_robust - Inform the registered notifiers about an event
 *                              and rollback on error.
 * @nl:		Pointer to head of the blocking notifier chain
 * @val_up:	Value passed unmodified to the notifier function
 * @val_down:	Value passed unmodified to the notifier function when recovering
 *              from an error on @val_up
 * @v:		Pointer passed unmodified to the notifier function
 *
 * NOTE:	It is important the @nl chain doesn't change between the two
 *		invocations of notifier_call_chain() such that we visit the
 *		exact same notifier callbacks; this rules out any RCU usage.
 *
 * Return:	the return value of the @val_up call.
 */
static int notifier_call_chain_robust(struct notifier_block **nl,
				     unsigned long val_up, unsigned long val_down,
				     void *v)
{
	int ret, nr = 0;

	ret = notifier_call_chain(nl, val_up, v, -1, &nr);
	if (ret & NOTIFY_STOP_MASK)
		notifier_call_chain(nl, val_down, v, nr-1, NULL);

	return ret;
}

```
Каждый из этих callback'ов, как правило, весьма специфичен для драйвера, поэтому здесь мы прекратим их обсуждение.

### Синхронизация файловых систем

Следующий шаг — убедиться, что все файловые системы синхронизированы с диском.

Это выполняется простой вспомогательной функцией, замеряющей, сколько занимает полная операция синхронизации `ksys_sync`.

[kernel/power/main.c:69](https://elixir.bootlin.com/linux/v6.9.9/source/kernel/power/main.c#L69)
```c
void ksys_sync_helper(void)
{
	ktime_t start;
	long elapsed_msecs;

	start = ktime_get();
	ksys_sync();
	elapsed_msecs = ktime_to_ms(ktime_sub(ktime_get(), start));
	pr_info("Filesystems sync: %ld.%03ld seconds\n",
		elapsed_msecs / MSEC_PER_SEC, elapsed_msecs % MSEC_PER_SEC);
}
EXPORT_SYMBOL_GPL(ksys_sync_helper);

```
`ksys_sync` пробуждает набор потоков-флашеров и поручает им записать каждую файловую систему: сначала их inode'ы[15](#15), затем файловую систему целиком и, наконец, все блочные устройства, чтобы все страницы оказались записаны на диск.

[fs/sync.c:87](https://elixir.bootlin.com/linux/v6.9.9/source/fs/sync.c#L87)
```c
/*
 * Sync everything. We start by waking flusher threads so that most of
 * writeback runs on all devices in parallel. Then we sync all inodes reliably
 * which effectively also waits for all flusher threads to finish doing
 * writeback. At this point all data is on disk so metadata should be stable
 * and we tell filesystems to sync their metadata via ->sync_fs() calls.
 * Finally, we writeout all block devices because some filesystems (e.g. ext2)
 * just write metadata (such as inodes or bitmaps) to block device page cache
 * and do not sync it on their own in ->sync_fs().
 */
void ksys_sync(void)
{
	int nowait = 0, wait = 1;

	wakeup_flusher_threads(WB_REASON_SYNC);
	iterate_supers(sync_inodes_one_sb, NULL);
	iterate_supers(sync_fs_one_sb, &nowait);
	iterate_supers(sync_fs_one_sb, &wait);
	sync_bdevs(false);
	sync_bdevs(true);
	if (unlikely(laptop_mode))
		laptop_sync_completion();
}

```
Здесь прослеживается интересный паттерн: `iterate_supers` запускает и `sync_inodes_one_sb`, и затем `sync_fs_one_sb` для каждой известной файловой системы[16](#16). Он также вызывает и `sync_fs_one_sb`, и `sync_bdevs` дважды: сначала не дожидаясь завершения операций, а затем снова — с ожиданием[17](#17).

Когда включён `laptop_mode`, система выполняет дополнительные операции синхронизации файловых систем после заданной задержки без записей.

[mm/page-writeback.c:111](https://elixir.bootlin.com/linux/v6.9.9/source/mm/page-writeback.c#L111)
```c
/*
 * Flag that puts the machine in "laptop mode". Doubles as a timeout in jiffies:
 * a full sync is triggered after this time elapses without any disk activity.
 */
int laptop_mode;

EXPORT_SYMBOL(laptop_mode);

```
Однако при запуске операции синхронизации файловых систем система добавляет дополнительный таймер, чтобы запланировать ещё записи после задержки `laptop_mode`. При гибернации состояние системы вообще не должно меняться, поэтому мы отменяем эти таймеры.

[mm/page-writeback.c:2198](https://elixir.bootlin.com/linux/v6.9.9/source/mm/page-writeback.c#L2198)
```c
/*
 * We're in laptop mode and we've just synced. The sync's writes will have
 * caused another writeback to be scheduled by laptop_io_completion.
 * Nothing needs to be written back anymore, so we unschedule the writeback.
 */
void laptop_sync_completion(void)
{
	struct backing_dev_info *bdi;

	rcu_read_lock();

	list_for_each_entry_rcu(bdi, &bdi_list, bdi_list)
		del_timer(&bdi->laptop_mode_wb_timer);

	rcu_read_unlock();
}

```
Кстати, функция `ksys_sync` — это то, что просто вызывается при использовании системного вызова `sync`.

[fs/sync.c:111](https://elixir.bootlin.com/linux/v6.9.9/source/fs/sync.c#L111)
```c
SYSCALL_DEFINE0(sync)
{
	ksys_sync();
	return 0;
}

```
## Конец подготовки

На этом система завершила подготовку к гибернации. Это несколько условная граница, но далее система начнёт полную заморозку userspace, затем выгрузит память в образ и, наконец, выполнит гибернацию. Всё это будет рассмотрено в будущих статьях!

  1. Режимы гибернации выходят за рамки этой статьи; смотрите [предыдущую статью](https://tookmund.com/2022/01/hibernate-docs) с обзорным описанием разных типов гибернации. ↩

  2. Workqueue — механизм выполнения асинхронных задач. Полное их описание — тема для другого раза, но документация ядра доступна здесь: <https://www.kernel.org/doc/html/v6.9/core-api/workqueue.html> ↩

  3. Это некоторое упрощение, но поскольку это не главный фокус статьи, описание оставлено на высоком уровне. ↩

  4. Kconfig — система конфигурации сборки Linux, задающая множество макросов для включения/отключения различных возможностей. ↩

  5. Kconfig выбирает [первый найденный вариант по умолчанию](https://www.kernel.org/doc/html/v6.9/kbuild/kconfig-language.html) ↩

  6. Включая проверку, находится ли алгоритм в состоянии «larval» («личинка»)? Судя по всему, это означает, что он требует дополнительной настройки, но интересный выбор названия для такого состояния. ↩

  7. Конкретно — когда мы дойдём до заморозки процессов, что будет в следующей статье серии. ↩

  8. Swap выходит за рамки этой статьи, но вкратце это буфер на диске, который ядро использует для хранения неиспользуемой в данный момент памяти, чтобы освободить место для других задач. Подробнее см. [Swap Management](https://www.kernel.org/doc/gorman/html/understand/understand014.html). ↩

  9. Код для этого длинный и побочный, поэтому здесь не приводится. Если вам любопытны детали, смотрите [kernel/power/hibernate.c:858](https://elixir.bootlin.com/linux/v6.9.9/source/kernel/power/hibernate.c#L858) о `hibernate_quiet_exec` и [drivers/nvdimm/core.c:451](https://elixir.bootlin.com/linux/v6.9.9/source/drivers/nvdimm/core.c#L451) о том, как это используется в `nvdimm`. ↩

  10. Досадно, что этот код, похоже, использует термины «консоль» и «виртуальный терминал» как взаимозаменяемые. ↩

  11. `ioctl` — специальные специфичные для устройства операции ввода-вывода, позволяющие выполнять действия за пределами стандартных файловых взаимодействий read/write/seek и т.д. ↩

  12. Мне не совсем ясно, как работает этот флаг — эта подсистема особенно сложна. ↩

  13. В данном случае большее число — более высокий приоритет. ↩

  14. Или что угодно, переданное вызывающим как `val_down`, но здесь мы конкретно рассматриваем использование при гибернации. ↩

  15. Inode обозначает конкретный файл или каталог в файловой системе. Подробнее см. [Wikipedia](https://en.wikipedia.org/wiki/Inode). ↩

  16. Каждая активная файловая система регистрируется в ядре структурой, известной как superblock, которая содержит ссылки на все inode'ы файловой системы, а также указатели на функции для выполнения различных требуемых операций, таких как sync. ↩

  17. Я привожу минимум кода в этом разделе, поскольку не планирую сейчас глубоко погружаться в код файловых систем. ↩

**********

[ядро](/tags/kernel.md)
[Linux](/tags/linux.md)
[hibernation](/tags/hibernation.md)
