import os
import zipfile
import xml.etree.ElementTree as ET
from lxml import etree
from ebooklib import epub
from PIL import Image
import io
import base64
import logging
import re
import bs4

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class BookParser:
    def __init__(self):
        self.cover_dir = os.path.join('static', 'uploads', 'covers')
        os.makedirs(self.cover_dir, exist_ok=True)
        logger.debug(f"Инициализация BookParser. Директория для обложек: {self.cover_dir}")
        
    def is_valid_epub(self, file_path):
        """Проверяет, является ли файл корректным EPUB"""
        try:
            with zipfile.ZipFile(file_path, 'r') as zf:
                # Проверяем наличие обязательных файлов
                required_files = ['mimetype', 'META-INF/container.xml']
                for file in required_files:
                    if file not in zf.namelist():
                        logger.error(f"Отсутствует обязательный файл в EPUB: {file}")
                        return False
                
                # Проверяем mimetype
                with zf.open('mimetype') as f:
                    mimetype = f.read().decode('utf-8').strip()
                    if mimetype != 'application/epub+zip':
                        logger.error(f"Неверный mimetype: {mimetype}")
                        return False
                
                return True
        except zipfile.BadZipFile:
            logger.error("Файл не является корректным ZIP-архивом")
            return False
        except Exception as e:
            logger.error(f"Ошибка при проверке EPUB: {str(e)}")
            return False
            
    def parse_book(self, file_path):
        """Парсит содержимое книги в зависимости от формата"""
        logger.debug(f"Начало парсинга книги: {file_path}")
        if file_path.lower().endswith('.fb2'):
            return self.parse_fb2(file_path)
        elif file_path.lower().endswith('.epub'):
            if not self.is_valid_epub(file_path):
                raise ValueError('Файл не является корректным EPUB')
            return self.parse_epub(file_path)
        else:
            raise ValueError('Неподдерживаемый формат файла')
            
    def parse_metadata(self, file_path):
        """Парсит метаданные книги"""
        try:
            file_type = os.path.splitext(file_path)[1].lower()
            if file_type == '.fb2':
                return self._parse_fb2_metadata(file_path)
            elif file_type == '.epub':
                return self._parse_epub_metadata(file_path)
            else:
                raise ValueError(f"Неподдерживаемый формат файла: {file_type}")
        except Exception as e:
            logger.error(f"Ошибка при парсинге метаданных: {str(e)}")
            raise

    def _parse_fb2_metadata(self, file_path):
        """Парсит метаданные из FB2 файла"""
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            try:
                content = content.decode('utf-8')
            except UnicodeDecodeError:
                content = content.decode('windows-1251')
            # Извлекаем метаданные
            title_match = re.search(r'<title-info>.*?<book-title>(.*?)</book-title>', content, re.DOTALL)
            # Собираем всех авторов
            authors = re.findall(r'<author>(.*?)</author>', content, re.DOTALL)
            author_list = []
            for author_block in authors:
                first_match = re.search(r'<first-name>(.*?)</first-name>', author_block)
                last_match = re.search(r'<last-name>(.*?)</last-name>', author_block)
                if first_match and last_match:
                    author_list.append(f"{first_match.group(1).strip()} {last_match.group(1).strip()}")
                elif first_match:
                    author_list.append(first_match.group(1).strip())
                elif last_match:
                    author_list.append(last_match.group(1).strip())
            author = ', '.join(author_list) if author_list else None
            genres_matches = re.findall(r'<title-info>.*?<genre>(.*?)</genre>', content, re.DOTALL)
            logger.debug(f"Найдены жанры в FB2: {genres_matches}")
            cover_match = re.search(r'<coverpage>.*?<image.*?href="#(.*?)".*?>', content, re.DOTALL)
            # Дополнительные метаданные
            year_match = re.search(r'<publish-info>.*?<year>(.*?)</year>', content, re.DOTALL)
            isbn_match = re.search(r'<publish-info>.*?<isbn>(.*?)</isbn>', content, re.DOTALL)
            lang_match = re.search(r'<title-info>.*?<lang>(.*?)</lang>', content, re.DOTALL)
            # Оцениваем количество страниц по количеству слов только в <body>
            body_match = re.search(r'<body.*?>(.*?)</body>', content, re.DOTALL)
            body_text = re.sub(r'<[^>]+>', '', body_match.group(1)) if body_match and body_match.group(1) else ''
            words = re.findall(r'\w+', body_text)
            pages = max(1, len(words) // 250)
            # Обрабатываем результаты
            title = title_match.group(1).strip() if title_match and title_match.group(1) else 'Без названия'
            genres = [g.strip() for g in genres_matches if g and g.strip()] if genres_matches else []
            cover_id = cover_match.group(1) if cover_match and cover_match.group(1) else None
            cover_data = None
            if cover_id:
                cover_binary_match = re.search(rf'<binary id=\"{re.escape(cover_id)}\".*?>(.*?)</binary>', content, re.DOTALL)
                if cover_binary_match and cover_binary_match.group(1):
                    try:
                        cover_data = base64.b64decode(cover_binary_match.group(1))
                    except (base64.Error, TypeError) as base64_error:
                        logger.error(f"Ошибка декодирования base64 обложки для {file_path}: {str(base64_error)}")
                        cover_data = None
            publication_year = year_match.group(1).strip() if year_match and year_match.group(1) else None
            isbn_val = isbn_match.group(1).strip() if isbn_match and isbn_match.group(1) else None
            language = lang_match.group(1).strip() if lang_match and lang_match.group(1) else None
            logger.debug(f"Извлечены метаданные FB2: title={title}, author={author}, genres={genres}, year={publication_year}, isbn={isbn_val}, lang={language}, pages={pages}")
            return {
                'title': title,
                'author': author,
                'genres': genres,
                'cover': cover_data,
                'publication_year': publication_year,
                'isbn': isbn_val,
                'language': language,
                'pages': pages
            }
        except Exception as e:
            logger.error(f"Ошибка при парсинге метаданных FB2: {str(e)}")
            raise

    def _parse_epub_metadata(self, file_path):
        """Парсит метаданные из EPUB файла"""
        try:
            with zipfile.ZipFile(file_path, 'r') as z:
                metadata_file = None
                for name in z.namelist():
                    if name.endswith('content.opf'):
                        metadata_file = name
                        break
                if not metadata_file:
                    raise ValueError("Не найден файл с метаданными в EPUB")
                content = z.read(metadata_file).decode('utf-8')
                title = re.search(r'<dc:title>(.*?)</dc:title>', content)
                # Собираем всех авторов
                authors = re.findall(r'<dc:creator[^>]*>(.*?)</dc:creator>', content)
                author = ', '.join([a.strip() for a in authors if a.strip()]) if authors else None
                genres = re.findall(r'<dc:subject>(.*?)</dc:subject>', content)
                logger.debug(f"Найдены жанры в EPUB: {genres}")
                cover_id = re.search(r'<meta name="cover" content="(.*?)"/>', content)
                year = re.search(r'<dc:date>(.*?)</dc:date>', content)
                isbn = re.search(r'<dc:identifier[^>]*>(.*?)</dc:identifier>', content)
                lang = re.search(r'<dc:language>(.*?)</dc:language>', content)
                # Оцениваем количество страниц по всем html-файлам
                all_text = ''
                for name in z.namelist():
                    if name.endswith('.xhtml') or name.endswith('.html'):
                        try:
                            html = z.read(name).decode('utf-8')
                            all_text += re.sub(r'<[^>]+>', '', html)
                        except Exception:
                            continue
                words = re.findall(r'\w+', all_text)
                pages = max(1, len(words) // 250)
                title = title.group(1).strip() if title else 'Без названия'
                genres = [g.strip() for g in genres] if genres else []
                cover_id = cover_id.group(1) if cover_id else None
                cover_data = None
                if cover_id:
                    cover_path = None
                    for name in z.namelist():
                        if name.endswith(cover_id):
                            cover_path = name
                            break
                    if cover_path:
                        cover_data = z.read(cover_path)
                publication_year = year.group(1).strip() if year else None
                isbn_val = isbn.group(1).strip() if isbn else None
                language = lang.group(1).strip() if lang else None
                logger.debug(f"Извлечены метаданные EPUB: title={title}, author={author}, genres={genres}, year={publication_year}, isbn={isbn_val}, lang={language}, pages={pages}")
                return {
                    'title': title,
                    'author': author,
                    'genres': genres,
                    'cover': cover_data,
                    'publication_year': publication_year,
                    'isbn': isbn_val,
                    'language': language,
                    'pages': pages
                }
        except Exception as e:
            logger.error(f"Ошибка при парсинге метаданных EPUB: {str(e)}")
            raise
            
    def parse_fb2(self, file_path):
        """Парсит FB2 файл и извлекает метаданные и содержимое"""
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Получаем метаданные
            title_info = root.find('.//{http://www.gribuser.ru/xml/fictionbook/2.0}title-info')
            metadata = {
                'title': '',
                'author': '',
                'genres': [],
                'cover': None
            }
            
            if title_info is not None:
                # Получаем название
                title = title_info.find('{http://www.gribuser.ru/xml/fictionbook/2.0}book-title')
                if title is not None:
                    metadata['title'] = title.text
                    
                # Получаем автора
                author = title_info.find('{http://www.gribuser.ru/xml/fictionbook/2.0}author')
                if author is not None:
                    first_name = author.find('{http://www.gribuser.ru/xml/fictionbook/2.0}first-name')
                    last_name = author.find('{http://www.gribuser.ru/xml/fictionbook/2.0}last-name')
                    if first_name is not None and last_name is not None:
                        metadata['author'] = f"{first_name.text} {last_name.text}"
                    elif first_name is not None:
                        metadata['author'] = first_name.text
                    elif last_name is not None:
                        metadata['author'] = last_name.text
                        
                # Получаем жанры
                genres = title_info.findall('{http://www.gribuser.ru/xml/fictionbook/2.0}genre')
                metadata['genres'] = [genre.text for genre in genres if genre.text]
                
                # Получаем обложку
                cover = title_info.find('{http://www.gribuser.ru/xml/fictionbook/2.0}coverpage')
                if cover is not None:
                    image = cover.find('.//{http://www.gribuser.ru/xml/fictionbook/2.0}image')
                    if image is not None:
                        href = image.get('{http://www.w3.org/1999/xlink}href')
                        if href:
                            binary = root.find(f'.//{{http://www.gribuser.ru/xml/fictionbook/2.0}}binary[@id="{href[1:]}"]')
                            if binary is not None:
                                metadata['cover'] = base64.b64decode(binary.text)
                                
            # Получаем содержимое
            body = root.find('.//{http://www.gribuser.ru/xml/fictionbook/2.0}body')
            content = []
            if body is not None:
                for section in body.findall('.//{http://www.gribuser.ru/xml/fictionbook/2.0}section'):
                    text = []
                    for p in section.findall('.//{http://www.gribuser.ru/xml/fictionbook/2.0}p'):
                        if p.text:
                            text.append(p.text)
                    if text:
                        content.append('\n'.join(text))
                        
            return metadata, '\n\n'.join(content)
        except Exception as e:
            logger.error(f"Ошибка при парсинге FB2 файла: {str(e)}")
            raise ValueError(f"Ошибка при парсинге FB2 файла: {str(e)}")
            
    def parse_epub(self, file_path):
        """Парсит EPUB файл и извлекает метаданные и только основной текст"""
        try:
            book = epub.read_epub(file_path)
            metadata = {
                'title': '',
                'author': '',
                'genres': [],
                'cover': None
            }
            # Получаем метаданные
            if book.get_metadata('DC', 'title'):
                metadata['title'] = book.get_metadata('DC', 'title')[0][0]
            if book.get_metadata('DC', 'creator'):
                metadata['author'] = book.get_metadata('DC', 'creator')[0][0]
            if book.get_metadata('DC', 'subject'):
                metadata['genres'] = [subject[0] for subject in book.get_metadata('DC', 'subject')]
            # Получаем обложку
            for item in book.get_items():
                if isinstance(item, epub.EpubImage):
                    if 'cover' in item.id.lower():
                        metadata['cover'] = item.content
                        break
            # Получаем только основной текст
            content = []
            allowed_tags = ['h1', 'h2', 'h3', 'p', 'section', 'div']
            for item in book.get_items():
                if isinstance(item, epub.EpubHtml):
                    soup = bs4.BeautifulSoup(item.get_content().decode('utf-8'), 'html.parser')
                    # Удаляем все nav, aside, footer, header, ol, ul, li, a, sup, sub, span.note и т.д.
                    for tag in soup.find_all(['nav', 'aside', 'footer', 'header', 'ol', 'ul', 'li', 'a', 'sup', 'sub', 'span']):
                        tag.decompose()
                    # Оставляем только нужные теги
                    for tag in soup.find_all(True):
                        if tag.name not in allowed_tags:
                            tag.unwrap()
                    # Добавляем только текстовые блоки
                    for tag in soup.find_all(allowed_tags):
                        text = tag.get_text(strip=True)
                        if text:
                            content.append(f'<{tag.name}>{text}</{tag.name}>')
            return metadata, '\n\n'.join(content)
        except Exception as e:
            logger.error(f"Ошибка при парсинге EPUB файла: {str(e)}")
            raise ValueError(f"Ошибка при парсинге EPUB файла: {str(e)}")
            
    def save_cover(self, cover_data, cover_path):
        """Сохраняет обложку книги"""
        try:
            logger.debug(f"Сохранение обложки для книги: {cover_path}")
            if not cover_data:
                logger.warning("Нет данных обложки для сохранения")
                return ''
            # Генерируем имя файла
            # cover_path уже содержит полный путь
            # Сохраняем изображение
            if isinstance(cover_data, bytes):
                img = Image.open(io.BytesIO(cover_data))
            elif isinstance(cover_data, str):
                try:
                    img = Image.open(io.BytesIO(base64.b64decode(cover_data)))
                except Exception as e:
                    logger.error(f"Ошибка при декодировании base64: {str(e)}")
                    return ''
            else:
                logger.error(f"Неподдерживаемый тип данных обложки: {type(cover_data)}")
                return ''
            img.save(cover_path)
            logger.debug(f"Обложка успешно сохранена: {cover_path}")
            return os.path.basename(cover_path)
        except Exception as e:
            logger.error(f"Ошибка при сохранении обложки для {cover_path}: {str(e)}")
            return ''  # Возвращаем пустую строку вместо вызова исключения 