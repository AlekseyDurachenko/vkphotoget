# vkphotoget
Скрипт для скачивание фотографий из социальной сети ВКонтакте 
с сохранением метаданных.

# Завииимости
* exiftool
* python3

## Ubuntu/Debian
```bash
apt-get install exiftool python3
```

# Запуск
```bash
usage: vkphotoget.py [-h] [--version] [--verbose]
                     [--access_token ACCESS_TOKEN] [--dst DST]
                     url

Downloading the photos from the VKontakte social network

positional arguments:
  url                   the url of the photo album

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  --verbose             print various debugging information
  --access_token ACCESS_TOKEN
                        your access token
  --dst DST             the output directory
```

* если не задать токен доступа (--access_token ACCESS_TOKEN), 
то скрипт попытается считать его из файла "~/.vk_access_token". 
В случае отсутсвия файла скрипт будет загружать фотографии в
обычном режиме.

* если не задать выходной каталог (--dst DST), фотографии будут сохраняться
в текущем каталоге.

# ACCESS TOKEN
Токен доступа нужен в том случае, если доступ к фотоальбому ограничен
настройками приватности.

## Получение ACCESS TOKEN
* Во-первых, вам необходимо зарегистрировать новое приложение типа 
**Standalone-приложение** (http://vk.com/editapp?act=create), 
или использовать уже имеющееся. 
Так или иначе вам потребуется его уникальный **APP_ID**. 
* После того, как вам стал известен ваш **APP_ID** следует пройти 
OAuth авторизацию для получения access_token.

### Через браузер
* перейдите по ссылке (заменив APP_ID на ID вашего приложения, 
полученного на предыдущем шаге): 
https://oauth.vk.com/authorize?client_id=APP_ID&scope=friends,photos,groups,offline&display=page&redirect_uri=https://oauth.vk.com/blank.html&response_type=token& 
* далее, следуя указаниям, пройдите авторизацию
* В случае успешной авторизации в адресной строке вы увидите 
access_token=XXXYYYZZZ. Это и есть ваш ключ приложения.
    
**Примечание! Перед получением access_token следует выйти из ВКонтакте или открыть приватную вкладку.**

### Через утилиту vkoauth (http://alekseydurachenko.github.io/vkoauth/)
* введите ID вашего приложения;
* выберите следующие разрешения: friends, photos, groups, offline;
* пройдите авторизацию приложения
* в поле access_token должен появиться ваш ключ приложения

# Что сделано на текущий момент
* **Поддерживаемые ссылки:**
  * Фотоальбом: https://vk.com/albumXXXXXX_YYYYYYYYY
  * Фотоальбом: https://vk.com/idUUUUUUUUU?z=albumXXXXXXX_YYYYYYYY
  
* **Сохраняемы метаданные:**
  * Имя автора (тот, кто загрузит фотографию) "exiftool -artist=XXX"
  * Название фотоальбома "exiftool -title=XXX"
  * Текст подписи фотографии "exiftool -description=XXX"
  * Время загрузки файла "exiftool -AllDates=XXX" (Примечание:
   к сожалению, узнать реальную дату съемки фотографии невозможно)

# Что в планах:
* **Поддерживаемые ссылки:**
  * Специальные фотоальбомы
  * Отдельные фотографии
  * Все фотоальбомы указанного пользователя или группы
* **Сохраняемые метаданные:**
  * GPS координаты снимка
  * Отметки людей

# История изменений
## v.0.1.0
* Первая публичная версия
