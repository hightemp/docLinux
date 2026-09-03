# v1.24_ЕСИА и ГОСТ Р 34.10-2012 сертификаты

Источник: [v1.24_ЕСИА и ГОСТ Р 34.10-2012 сертификаты](https://docs.eltex-co.ru/pages/viewpage.action?pageId=318866284)

*     * [ _В_ ложения (0)  ](/pages/viewpageattachments.action?pageId=318866284 "Просмотреть вложения")

```text
* [ История Страницы  ](/pages/viewpreviousversions.action?pageId=318866284)

* [ Информация о странице  ](/pages/viewinfo.action?pageId=318866284)
* Решённые комментарии
* [ Открыть в иерархии  ](/pages/reorderpages.action?key=doc&openId=318866284#selectedPageInHierarchy)
* [ Просмотреть исходный  ](/plugins/viewsource/viewpagesrc.action?pageId=318866284)
* [ Экспорт в PDF  ](/spaces/flyingpdf/pdfpageexport.action?pageId=318866284&atl_token=548f46cabce809591684a33bc46a642c06ce3252)
* [ Экспорт в Word  ](/exportword?pageId=318866284)
* Export to HTML
* Export to PDF
```

  1. [Страницы](/collector/pages.action?key=doc)
  2. **…**
  3. [Eltex Documentation](/display/doc/Eltex+Documentation)
  4. [Архив](/pages/viewpage.action?pageId=11337743)
  5. [SoftWLC. Архив](/pages/viewpage.action?pageId=26282438)
  6. [v1.24_SoftWLC](/display/doc/v1.24_SoftWLC)
  7. [v1.24_Инструкции по установке и настройке](/pages/viewpage.action?pageId=318865493)
  8. [v1.24_Настройка авторизации](/pages/viewpage.action?pageId=318866275)
  9. [v1.24_Интеграция с ЕСИА](/pages/viewpage.action?pageId=318866276)

  *
  * [Ссылки JIRA]()

#  [v1.24_ЕСИА и ГОСТ Р 34.10-2012 сертификаты](/pages/viewpage.action?pageId=318866284)

  * Создатель  [Сервисный центр Wi-Fi](    /display/~wifi
), отредактировано [нояб. 14, 2022](/pages/diffpagesbyversion.action?pageId=318866284&selectedPageVersions=1&selectedPageVersions=2 "Показать изменения")

### Введение

С 1 апреля 2020 года ЕСИА запрещает использование RSA-шифрования. В качестве замены предлагается ГОСТ Р 34.10-2012. Это требует получения ГОСТ-сертификата от аккредитованного удостоверяющего центра.
В большинстве такие сертификаты сгенерированы с помощью ПО КриптоПРО и открытие их с помощью любых других утилит (openssl, bouncycastle) не представляется возможным. Попытки открыть экспортированный из КриптоПРО PKCS#12 контейнер с помощью OpenSSL завершаются подобной ошибкой:

```bash
$ openssl pkcs12 -in container.pfx
Enter Import Password:
Bag Attributes
    localKeyID: 01 00 00 00
    friendlyName: 20200313-114830-#  ! (/) " &▒""-!" 2012
    Microsoft CSP Name: Crypto-Pro GOST R 34.10-2012 Cryptographic Service Provider
Error outputting keys and certificates
140403870810560:error:06074079:digital envelope routines:EVP_PBE_CipherInit:unknown pbe algorithm:../crypto/evp/evp_pbe.c:95:TYPE=1.2.840.113549.1.12.1.80
140403870810560:error:23077073:PKCS12 routines:PKCS12_pbe_crypt:pkcs12 algor cipherinit error:../crypto/pkcs12/p12_decr.c:41:
140403870810560:error:2306A075:PKCS12 routines:PKCS12_item_decrypt_d2i:pkcs12 pbe crypt error:../crypto/pkcs12/p12_decr.c:94:
```

Для решения этой проблемы потребуется дополнительное ПО, а также по отдельности экспортированные компоненты сертификата.

### Настройка OpenSSL

В статье рассматривается OpenSSL 1.1.1 11 Sep 2018 и Ubuntu 18.04.

**Для упрощения работы с ГОСТ шифрованием существует готовый Docker контейнер с OpenSSL + Gost engine.**

Можно воспользоваться готовыми docker-образами с OpennSSL + Gost engine: <https://hub.docker.com/r/rnix/openssl-gost/>

Для начала нужно установить пакет с gost engine:

```text
apt install libengine-gost-openssl1.1
```

После этого для включения поддержки требуется отредактировать файл конфигурации openssl: /etc/ssl/openssl.cnf:

В начало файла добавить:

**/etc/ssl/openssl.cnf**

```text
openssl_conf = openssl_def
```

Затем добавить в конец:

**/etc/ssl/openssl.cnf**

```text
[openssl_def]
engines = engine_section
[engine_section]
gost = gost_section
[gost_section]
default_algorithms = ALL
engine_id = gost
CRYPT_PARAMS = id-Gost28147-89-CryptoPro-A-ParamSet
```

После этого можно проверить наличие ГОСТ-шифров командой:

```text
openssl ciphers | tr ":" "\n" | grep -i gost
```

Если в выводе команды присутствует GOST2012, значит можно продолжать.

### Конвертация экспортированных из КриптоПРО составляющих в PKCS#12 контейнер

Для выполнения этого пункта потребуется наличие всех составляющих, экспортированных из КриптоПРО:

```text
header.key
masks2.key
masks.key
name.key
primary2.key
primary.key
```

Извлеките образ и запустите контейнер с установленным текущим каталогом в интерактивном режиме:

```text
docker run --rm -i -t -v `pwd`:`pwd` -w `pwd` rnix/openssl-gost bash
```

Скачайте и распакуйте уже готовые скомпилированные двоичные файлы **get-cpcert-bin.tar.gz:** <https://github.com/kov-serg/get-cpcert/releases/download/v1.0.1/get-cpcert-bin.tar.gz>

Перейдите в директорию get-cpcert-bin/bin/, добавьте папку с файлами, экспортированными из КриптоПРО ключами;

Выполняем команду в ​docker-контейнере:

```text
./get-cpcert <PATH> <PASSWORD> > result.pem
```

Где <PATH> — папка с файлами, экспортированными из КриптоПРО, а <PASSWORD> — пароль к ним. В результате выполнения команды будет получен файл result.pem, содержащий сертификат и приватный ключ.

Теперь можно создать PKCS#12 контейнер, который понимает Конструктор Порталов:

```text
openssl pkcs12 -engine gost -export -in result.pem -out result.pfx
```

После этого result.pfx можно загружать в Конструктор Порталов. Поддержка ГОСТ в КП и Портале обеспечена в версиях 1.11 и 1.15+.

  * Нет меток

Обзор

Инструменты контента

Приложения

**********

[ГОСТ](/tags/gost.md)
